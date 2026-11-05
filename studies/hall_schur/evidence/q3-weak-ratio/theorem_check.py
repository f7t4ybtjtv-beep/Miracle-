"""Exhaustive check of the general bounds over ALL bipartite graphs (labelled)
with |X|=n, |Y|=m, n*m <= LIMIT edges-slots.

Claims checked for every graph G (k = |N(X)| - |X|):
  C0  models == 0  <=>  matchings == 0
  C1  if matchings > 0:  (3/2)^k <= models/matchings <= (n+1)^k
  C2  if matchings > 0:  models == matchings  <=>  k == 0
  C3  if n == m: models == matchings (always)
  C4  equality models/matchings == (3/2)^k  <=>  for every X-saturating matching M,
      the M-free holes in N(X) all have degree 1 and have pairwise distinct neighbours
  C5  f(c) = (2^{c+1}-1)/(c+1) >= (3/2)^c for c = 0..200 (exact rationals)
satlab brute_force cross-check of the model count on all graphs with n*m <= BF_LIMIT.
"""
import itertools, sys, time
from fractions import Fraction
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from weak_ratio import weak_cnf, own_models, own_matchings
from satlab.reference import brute_force

LIMIT, BF_LIMIT = 16, 10

def matchings_list(n, nbr):
    out = []
    def rec(x, used, cur):
        if x == n:
            out.append(tuple(cur)); return
        for y in nbr[x]:
            if not used >> y & 1:
                cur.append(y); rec(x + 1, used | 1 << y, cur); cur.pop()
    rec(0, 0, [])
    return out

def main():
    t0 = time.time()
    for c in range(201):
        assert Fraction(2 ** (c + 1) - 1, c + 1) >= Fraction(3, 2) ** c
    print("C5 OK for c=0..200")
    pairs = [(n, m) for n in range(1, 9) for m in range(1, 17) if n * m <= LIMIT]
    tot = {"graphs": 0, "bf": 0, "eq_cases": 0}
    minratio_by_k = {}
    for n, m in pairs:
        slots = [(x, y) for x in range(n) for y in range(m)]
        cnt = 0
        for mask in range(1 << len(slots)):
            E = {slots[i] for i in range(len(slots)) if mask >> i & 1}
            mods = own_models(n, m, E)
            mt = own_matchings(n, m, E)
            if n * m <= BF_LIMIT:
                nv, cls = weak_cnf(n, m, E)
                if nv == 0:
                    bfc = 1 if all(cls) else 0  # no vars: model iff no clause (empty clause = unsat)
                    bfc = 0 if any(len(c) == 0 for c in cls) else 1
                else:
                    _, _, bfc = brute_force(nv, cls, count=True)
                assert bfc == mods, (n, m, E, bfc, mods)
                tot["bf"] += 1
            k = len({y for _, y in E}) - n
            assert (mods == 0) == (mt == 0)                       # C0
            if n == m:
                assert mods == mt                                 # C3
            if mt:
                r = Fraction(mods, mt)
                assert Fraction(3, 2) ** k <= r <= (n + 1) ** k   # C1
                assert (r == 1) == (k == 0)                       # C2
                q = r / Fraction(3, 2) ** k
                minratio_by_k[k] = min(minratio_by_k.get(k, q), q)
                nbr = [[y for y in range(m) if (x, y) in E] for x in range(n)]
                NX = {y for _, y in E}
                cond = True
                for M in matchings_list(n, nbr):
                    free = NX - set(M)
                    owners = []
                    for y in free:
                        ny = [x for x in range(n) if (x, y) in E]
                        if len(ny) != 1: cond = False; break
                        owners.append(ny[0])
                    if not cond or len(set(owners)) != len(owners):
                        cond = False; break
                assert (q == 1) == cond, (n, m, E)                # C4
                tot["eq_cases"] += (q == 1)
            cnt += 1
        tot["graphs"] += cnt
        print(f"n={n} m={m}: {cnt} graphs OK  (t={time.time()-t0:.1f}s)")
    print("totals", tot)
    print("min over graphs of ratio/(3/2)^k, per k:", {k: str(v) for k, v in sorted(minratio_by_k.items())})
    print(f"time {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
