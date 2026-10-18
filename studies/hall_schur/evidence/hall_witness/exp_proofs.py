"""Part (1)+(2): sub-CNF monotonicity checks and explicit-proof verification.

A. Complete PHP, m+1 pigeons, m holes, m = 2..9: explicit proof checked by satlab.checker
   and drat-trim; lemma count compared with closed form 2^{m-1}(m+2)-1.
B. >=20 random graphs (n<=30 pigeons) with a planted witness S (|S| = k = 4..8): the explicit
   proof built from S alone (P = S, ordered) is checked against the FULL CNF.  Also: sub-CNF is a
   literal subset of the full CNF; for k<=5 brute-force confirms sub-CNF UNSAT; full CNF minus
   the S-clauses... (not needed).  Also report the inclusion-minimal witness found by matching.
"""
import random
import sys
import time
from math import comb

sys.path.insert(0, "/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/hall_witness")
from hallcore import *  # noqa
from satlab import checker
from satlab.reference import brute_force

WD = "/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/hall_witness/tmp"


def stats(steps):
    lem = [l for d, l in steps if not d]
    return len(lem), sum(len(l) for l in lem), sum(1 for d, _ in steps if d)


print("== A. complete PHP^{m+1}_m ==")
print("m  lemmas  closed_form  lemma_lits  deletions  satlab  drat  t_s")
for m in range(2, 10):
    t0 = time.time()
    adj = {x: set(range(m)) for x in range(m + 1)}
    nv, cl, var = encode(m + 1, m, adj)
    steps = explicit_proof(adj, list(range(m + 1)), var)
    ok1, msg = checker.check_proof(nv, cl, checker._parse_proof(proof_text(steps)))
    ok2 = drat_check(nv, cl, steps, WD, "php%d" % m)
    L, lits, dels = stats(steps)
    cf = 2 ** (m - 1) * (m + 2) - 1
    print("%d  %6d  %11d  %10d  %9d  %s  %s  %.2f" % (m, L, cf, lits, dels, ok1, ok2, time.time() - t0))
    assert ok1 and ok2 and L == cf

print("\n== B. planted witnesses in larger random graphs ==")
print("id n k p_in nv ncl | subcnf_subset sub_bf | |N(S)| lemmas bound(2^{m-1}(m+2)-1) lits satlab drat | minwit_size")
rng = random.Random(12345)
rows = []
cases = []
for k in range(4, 9):
    for rep in range(5):
        n = rng.choice([12, 16, 20, 24, 30])
        p_in = 1.0 if rep < 3 else 0.6
        cases.append((n, k, p_in))
for cid, (n, k, p_in) in enumerate(cases):
    nY, adj, S, T, R = planted_graph(n, k, rng, p_in=p_in)
    nv, cl, var = encode(n, nY, adj)
    sub, NS = sub_cnf(adj, S, var)
    full = set(tuple(c) for c in cl)
    subset = all(tuple(c) in full for c in sub)
    sub_bf = "-"
    subvars = sorted({abs(l) for c in sub for l in c})
    if len(subvars) <= 22:
        ren = {v: i + 1 for i, v in enumerate(subvars)}
        sat, _, cnt = brute_force(len(subvars), [[(1 if l > 0 else -1) * ren[abs(l)] for l in c] for c in sub], count=True)
        sub_bf = "UNSAT" if (not sat and cnt == 0) else "SAT!"
    m = len(NS)
    # P: any |N(S)|+1 pigeons of S (here: all of S since |N(S)| = k-1 or less -> take first m+1)
    P = sorted(S)[: m + 1]
    assert set().union(*(adj[p] for p in P)) <= NS
    # if N(P) is strictly smaller than NS, recompute with T' = N(P) and fewer pigeons
    NP = set().union(*(adj[p] for p in P))
    P = P[: len(NP) + 1]
    NP = set().union(*(adj[p] for p in P))
    while len(P) != len(NP) + 1:
        P = P[: len(NP) + 1]
        NP = set().union(*(adj[p] for p in P))
    steps = explicit_proof(adj, P, var)
    ok1, msg = checker.check_proof(nv, cl, checker._parse_proof(proof_text(steps)))
    ok2 = drat_check(nv, cl, steps, WD, "pl%d" % cid)
    L, lits, dels = stats(steps)
    mm = len(NP)
    bound = 2 ** (mm - 1) * (mm + 2) - 1
    mw = minimal_witness(n, adj)
    print("%2d %2d %d %.1f %4d %5d | %s %s | %d %5d %5d %7d %s %s | %d" % (
        cid, n, k, p_in, nv, len(cl), subset, sub_bf, mm, L, bound, lits, ok1, ok2, len(mw)))
    assert subset and ok1 and ok2 and L <= bound and sub_bf != "SAT!"
    rows.append((k, mm, L))
print("\nALL CHECKS PASSED; instances:", len(cases))
