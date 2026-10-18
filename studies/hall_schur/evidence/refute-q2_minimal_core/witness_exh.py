"""Exhaustive over all labelled bipartite graphs |X|=n, |Y|=m (2^(nm) each). For every minimal Hall witness S:
 - induced CNF UNSAT? every pigeon clause necessary? per-hole-clause necessity vs matching criterion; MUS?
Oracle: sat_choice (cross-checked against own DPLL on a sample of first-seen canonical classes).
Caching by canonical form of the whole graph (results are isomorphism invariant)."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import *

def analyse(adj, nY, xcheck):
    res = dict(w=0, mus=0, unsat_fail=0, pig_unnec=0, crit_mis=0, hole_tested=0, nonmus=[])
    for S in minimal_witnesses(adj):
        cl = induced_clauses(adj, S)
        res['w'] += 1
        sat = sat_choice
        if sat(adj, cl):
            res['unsat_fail'] += 1
        NS = nbrs(adj, S)
        assert popc(NS) == len(S) - 1
        allnec = True
        for i, c in enumerate(cl):
            rest = cl[:i] + cl[i + 1:]
            nec = sat(adj, rest)
            if xcheck:
                assert nec == sat_generic(adj, rest)
            if c[0] == 'P':
                if not nec: res['pig_unnec'] += 1
            else:
                _, y, a, b = c
                crit = has_matching(adj, [x for x in S if x not in (a, b)], NS & ~(1 << y))
                res['hole_tested'] += 1
                if crit != nec: res['crit_mis'] += 1
            allnec &= nec
        if allnec:
            res['mus'] += 1
        else:
            res['nonmus'].append((len(S) + popc(NS), sum(popc(adj[x]) for x in S), tuple(adj[x] & NS for x in S)))
    return res

def run(pairs):
    tot = {}
    cache = {}
    smallest = None
    t0 = time.time()
    for n, m in pairs:
        agg = dict(w=0, mus=0, unsat_fail=0, pig_unnec=0, crit_mis=0, hole_tested=0)
        for code in range(1 << (n * m)):
            adj = tuple((code >> (m * x)) & ((1 << m) - 1) for x in range(n))
            key = (n, m, canon(adj, m))
            if key not in cache:
                cache[key] = analyse(adj, m, xcheck=(len(cache) % 7 == 0))
                for s in cache[key]['nonmus']:
                    cand = (s[0], s[1], n, m, adj)
                    if smallest is None or cand[:2] < smallest[:2]:
                        smallest = cand
            r = cache[key]
            for k in agg: agg[k] += r[k]
        print((n, m), agg, "%.1fs" % (time.time() - t0), flush=True)
        tot[(n, m)] = agg
    return tot, smallest

if __name__ == "__main__":
    pairs = [(n, m) for n in range(1, 6) for m in range(0, 5) if n * m <= 16]
    tot, smallest = run(pairs)
    def cum(pred):
        w = sum(v['w'] for k, v in tot.items() if pred(*k)); mu = sum(v['mus'] for k, v in tot.items() if pred(*k))
        return mu, w, mu / w
    print("cum |X|<=4,|Y|<=3:", cum(lambda n, m: n <= 4 and m <= 3))
    print("cum |X|<=4,|Y|<=4:", cum(lambda n, m: n <= 4 and m <= 4))
    print("cum |X|<=5,|Y|<=3:", cum(lambda n, m: n <= 5 and m <= 3))
    print("smallest non-MUS (|S|+|N(S)|, |E(S)|, n, m, adj):", smallest)
    print("totals of failure counters:", {k: sum(v[k] for v in tot.values()) for k in ['unsat_fail', 'pig_unnec', 'crit_mis', 'hole_tested']})
