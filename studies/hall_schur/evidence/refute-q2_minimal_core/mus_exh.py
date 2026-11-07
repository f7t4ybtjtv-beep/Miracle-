"""Enumerate ALL MUSes of the full encoding for every iso class of graphs with given (n,m).
Method: MSS family from 'partial choice' assignments (each pigeon: no true edge or exactly one), keep maximal
satisfied-clause masks; F' UNSAT <=> F' not contained in any MSS <=> F' hits every MCS (complement of MSS).
MUSes = minimal transversals of the MCS hypergraph, computed by Berge's algorithm. Each MUS re-verified with
sat_choice (UNSAT, every one-removal SAT). For classes with few clauses, additionally a duality-free check:
scan all 2^m clause subsets with sat_choice and compare the set of minimal UNSAT subsets."""
import os, sys, time, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import *

def mss_masks(adj, cl):
    n = len(adj)
    idx = {c: i for i, c in enumerate(cl)}
    hole_cl = {}
    for c in cl:
        if c[0] == 'H':
            hole_cl.setdefault(c[1], []).append(c)
    allm = (1 << len(cl)) - 1
    masks = set()
    for ch in itertools.product(*[[None] + holes_of(a) for a in adj]):
        msk = allm
        for x in range(n):
            if ch[x] is None:
                msk &= ~(1 << idx[('P', x)])
        for y, cs in hole_cl.items():
            for c in cs:
                if ch[c[2]] == y and ch[c[3]] == y:
                    msk &= ~(1 << idx[c])
        masks.add(msk)
    # maximal
    ms = sorted(masks, key=popc, reverse=True)
    maxi = []
    for a in ms:
        if not any((a | b) == b for b in maxi):
            maxi.append(a)
    return maxi

def min_transversals(edges):
    tr = [0]
    for e in sorted(edges, key=popc):
        new = set()
        for t in tr:
            if t & e:
                new.add(t)
            else:
                b = e
                while b:
                    low = b & -b
                    new.add(t | low)
                    b ^= low
        new = sorted(new, key=popc)
        res = []
        for t in new:
            if not any((r | t) == t for r in res):
                res.append(t)
        tr = res
    return tr

def all_mus(adj, nY):
    cl = full_clauses(adj, nY)
    allm = (1 << len(cl)) - 1
    mss = mss_masks(adj, cl)
    if mss == [allm]:
        return cl, []
    mcs = [allm & ~s for s in mss]
    return cl, min_transversals(mcs)

def brute_mus(adj, nY):
    cl = full_clauses(adj, nY)
    m = len(cl)
    unsat = [False] * (1 << m)
    for s in range(1 << m):
        # monotone: superset of unsat is unsat; check via a submask with one bit removed
        b = s
        hit = False
        while b:
            low = b & -b
            if unsat[s ^ low]:
                hit = True; break
            b ^= low
        unsat[s] = True if hit else (not sat_choice(adj, [cl[i] for i in range(m) if s >> i & 1]))
    mus = []
    for s in range(1 << m):
        if unsat[s]:
            b = s; mn = True
            while b:
                low = b & -b
                if unsat[s ^ low]:
                    mn = False; break
                b ^= low
            if mn: mus.append(s)
    return sorted(mus)

def connected(adj, P):
    if not P: return True
    seenx = {P[0]}; stack = [P[0]]; seeny = set()
    while stack:
        x = stack.pop()
        for y in holes_of(adj[x]):
            if y not in seeny:
                seeny.add(y)
                for z in P:
                    if adj[z] >> y & 1 and z not in seenx:
                        seenx.add(z); stack.append(z)
    return len(seenx) == len(P)

def d(adj, T):
    return len(T) - popc(nbrs(adj, T))

def analyse(adj, nY, brute_limit):
    n = len(adj)
    cl, mus = all_mus(adj, nY)
    st = dict(mus=len(mus), nonminwit=0, bad_hole=0, not_strict=0, verify_fail=0, d1_not_minwit=0,
              minwit_not_d1=0, minwit_without_mus=0, d1_hole_outside_induced=0, brute_checked=0, brute_mismatch=0,
              sd_sets=0, sd_with_mus=0, sd_conn=0, sd_conn_with_mus=0, hist={}, uniq_H_fail=0)
    mw = [tuple(w) for w in minimal_witnesses(adj)]
    psets = set()
    for msk in mus:
        F = [cl[i] for i in range(len(cl)) if msk >> i & 1]
        if not is_mus(adj, F):
            st['verify_fail'] += 1
        P = tuple(sorted(c[1] for c in F if c[0] == 'P'))
        psets.add(P)
        for c in F:
            if c[0] == 'H' and not (c[2] in P and c[3] in P):
                st['bad_hole'] += 1
        dP = d(adj, P)
        st['hist'][dP] = st['hist'].get(dP, 0) + 1
        for r in range(len(P)):
            for T in itertools.combinations(P, r):
                if d(adj, T) >= dP:
                    st['not_strict'] += 1
        ismw = P in mw
        if not ismw: st['nonminwit'] += 1
        if dP == 1 and not ismw: st['d1_not_minwit'] += 1
        if ismw and dP != 1: st['minwit_not_d1'] += 1
        if ismw:
            ind = set(induced_clauses(adj, P))
            if not all(c in ind for c in F): st['d1_hole_outside_induced'] += 1
    for w in mw:
        if w not in psets: st['minwit_without_mus'] += 1
    # every minimal witness: number of MUS with that pigeon set (uniqueness of H?)
    for w in mw:
        k = sum(1 for msk in mus if tuple(sorted(cl[i][1] for i in range(len(cl)) if msk >> i & 1 and cl[i][0] == 'P')) == w)
        if k != 1: st['uniq_H_fail'] += 1
    # strict-deficiency-max sets
    for r in range(1, n + 1):
        for P in itertools.combinations(range(n), r):
            dP = d(adj, P)
            if dP < 1: continue
            if all(d(adj, T) < dP for rr in range(r) for T in itertools.combinations(P, rr)):
                st['sd_sets'] += 1
                c = connected(adj, list(P))
                st['sd_conn'] += c
                if P in psets:
                    st['sd_with_mus'] += 1; st['sd_conn_with_mus'] += c
    if len(cl) <= brute_limit:
        st['brute_checked'] = 1
        if brute_mus(adj, nY) != sorted(mus):
            st['brute_mismatch'] = 1
    return st

if __name__ == "__main__":
    pairs = eval(sys.argv[1]); brute_limit = int(sys.argv[2])
    t0 = time.time()
    cache = {}
    iso = {}; lab = {}
    smallest = None
    for n, m in pairs:
        L = dict(mus=0, nonminwit=0)
        for code in range(1 << (n * m)):
            adj = tuple((code >> (m * x)) & ((1 << m) - 1) for x in range(n))
            key = (n, m, canon(adj, m))
            if key not in cache:
                cache[key] = analyse(adj, m, brute_limit)
                if cache[key]['nonminwit']:
                    cand = (n + m, sum(map(popc, adj)), n, m, adj)
                    if smallest is None or cand[:2] < smallest[:2]: smallest = cand
            L['mus'] += cache[key]['mus']; L['nonminwit'] += cache[key]['nonminwit']
        lab[(n, m)] = L
        print((n, m), "labelled MUS", L, "iso classes so far", len(cache), "%.1fs" % (time.time() - t0), flush=True)
    agg = {}
    for st in cache.values():
        for k, v in st.items():
            if k == 'hist':
                h = agg.setdefault('hist', {})
                for kk, vv in v.items(): h[kk] = h.get(kk, 0) + vv
            else:
                agg[k] = agg.get(k, 0) + v
    print("iso classes", len(cache))
    print("aggregate over iso-class representatives:", agg)
    print("smallest graph with MUS whose pigeon set is not a minimal witness (n+m,|E|,n,m,adj):", smallest)
