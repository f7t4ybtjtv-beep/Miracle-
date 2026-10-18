import sys, random, itertools
sys.path.insert(0, '.')
from mylib import *
from satlab.reference import brute_force

def restrict(cls, assign):
    """assign: dict var->bool. Returns set of frozenset clauses after restriction."""
    out = set()
    for c in cls:
        sat = False; rem = []
        for l in c:
            v = assign.get(abs(l))
            if v is None: rem.append(l)
            elif v == (l > 0): sat = True; break
        if not sat: out.add(frozenset(rem))
    return out

rng = random.Random(20261018)
print("id n k p_in q nv ncl | FS_subset FS_bf | m lemmas bound satlab drat res | restr==FS")
ok_all = True; idx = 0
for k in range(4, 9):
    for (n, p_in, q) in [(12, 1.0, 0.5), (20, 0.6, 0.5), (30, 1.0, 0.3), (24, 0.6, 0.5), (30, 0.5, 0.5), (16, 0.7, 0.4)]:
        adj, S, T = planted(n, k, p_in, q, rng)
        nv, cls, var = encode(adj, rng)
        Fset = set(frozenset(c) for c in cls)
        # F_S built independently from scratch on induced graph
        sub = {x: set(adj[x]) for x in S}
        assert all(adj[x] <= set(T) for x in S)
        _, cS, varS = encode(sub)
        # translate F_S into full-var numbering
        inv = {v: e for e, v in varS.items()}
        FS = set(frozenset((1 if l > 0 else -1) * var[inv[abs(l)]] for l in c) for c in cS)
        subset = FS <= Fset
        bf = '-'
        if len(varS) <= 22:
            bf = brute_force(len(varS), cS, count=True)[2]
        m = len(T)
        P = S[:]; rng.shuffle(P); P = P[:m + 1]
        L = explicit_drup(adj, P, T)
        pr = lemmas_to_dimacs(L, var)
        bound = 2 ** (m - 1) * (m + 2) - 1
        sl = satlab_check(nv, cls, pr)[0]
        dr = drat_check(nv, cls, pr, "pl%d" % idx)
        rs, em = resolution_proof(adj, P, T)
        # restriction: matching of R into Y \ T
        R = [x for x in adj if x not in S]
        radj = {x: adj[x] - set(T) for x in R}
        M = max_matching(radj)
        restr = '-'
        if len(M) == len(R):
            assign = {}
            for x in R:
                for y in adj[x]:
                    assign[var[(x, y)]] = (M[x] == y)
            restr = restrict(cls, assign) == FS
        good = subset and bf in ('-', 0) and sl and dr and em and len(pr) <= bound and restr is True
        ok_all &= good
        print(idx, n, k, p_in, q, nv, len(cls), '|', subset, bf, '|', m, len(pr), bound, sl, dr, rs, '|', restr, flush=True)
        idx += 1
print("ALL OK" if ok_all else "FAILURE", idx)
