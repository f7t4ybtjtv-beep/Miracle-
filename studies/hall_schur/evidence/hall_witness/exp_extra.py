"""Extra checks for part (3).

E1. Restriction transfer: for planted graphs (X\\S matchable into Y\\T, edges X\\S->T allowed),
    the restriction rho (planted matching M on X\\S true, every other edge at a pigeon of X\\S false)
    turns the full CNF into EXACTLY the sub-CNF F_S (as a set of clauses), for all 100 instances.
E2. Counterexample to "lower bound always transfers": G = K_{9,8} disjoint-union K_{2,1}.
    The full CNF has a 1-lemma DRUP refutation (from the K_{2,1} witness), checked by satlab and
    drat-trim, and CDCL needs few conflicts; yet it contains PHP^9_8 as a sub-CNF.
E3. Closed form for lemma literal count of the explicit proof on complete PHP^{m+1}_m:
    sum_{j=1}^m C(m,j) [ (j+1)^2 (m-j) + j ]  checked for m=2..12 against the generator.
"""
import random
import sys
from math import comb, log2

sys.path.insert(0, "/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/hall_witness")
from hallcore import *  # noqa
from satlab import checker
from satlab.cdcl import CDCLSolver

WD = "/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/hall_witness/tmp"

# E1
rng = random.Random(4242)
cnt = 0
for it in range(100):
    k = rng.randint(3, 8)
    n = rng.randint(k + 1, 40)
    nY, adj, S, T, R = planted_graph(n, k, rng, p_in=rng.choice([1.0, 0.7]))
    nv, cl, var = encode(n, nY, adj)
    rest = list(range(k, n))
    M = max_matching(rest, {x: adj[x] & set(R) for x in rest})
    assert len(M) == len(rest)
    rho = {}
    for x in rest:
        for y in adj[x]:
            rho[var[(x, y)]] = (M[x] == y)
    red = set()
    for c in cl:
        if any((l > 0) == rho[abs(l)] for l in c if abs(l) in rho):
            continue  # satisfied
        red.add(tuple(sorted(l for l in c if abs(l) not in rho)))
    sub, _ = sub_cnf(adj, S, var)
    assert red == set(tuple(sorted(c)) for c in sub), it
    cnt += 1
print("E1 restriction F|rho == F_S exactly: %d/100 instances" % cnt)

# E2
k = 9
adj = {x: set(range(k - 1)) for x in range(k)}
adj[k] = {k - 1}
adj[k + 1] = {k - 1}
nX, nY = k + 2, k
nv, cl, var = encode(nX, nY, adj)
steps = explicit_proof(adj, [k, k + 1], var)
ok1, msg = checker.check_proof(nv, cl, checker._parse_proof(proof_text(steps)))
ok2 = drat_check(nv, cl, steps, WD, "e2")
r = CDCLSolver(nv, cl, seed=0).solve()
sub, _ = sub_cnf(adj, set(range(k)), var)
print("E2 K_{9,8} + K_{2,1}: nv=%d ncl=%d, contains PHP^9_8 sub-CNF: %s; explicit proof lemmas=%d satlab=%s drat=%s; CDCL %s conflicts=%d"
      % (nv, len(cl), all(c in cl for c in sub), sum(1 for d, _ in steps if not d), ok1, ok2, r.status, r.stats["conflicts"]))
assert ok1 and ok2

# E3
print("E3 m lemmas lits closed_lits lits/(m^3 2^m) log2(lemmas)/m")
for m in range(2, 13):
    adj = {x: set(range(m)) for x in range(m + 1)}
    nv, cl, var = encode(m + 1, m, adj)
    steps = explicit_proof(adj, list(range(m + 1)), var, delete=False)
    L = len(steps)
    lits = sum(len(l) for _, l in steps)
    cf = sum(comb(m, j) * ((j + 1) ** 2 * (m - j) + j) for j in range(1, m + 1))
    assert lits == cf and L == 2 ** (m - 1) * (m + 2) - 1
    print("  %2d %6d %9d %9d %.3f %.3f" % (m, L, lits, cf, lits / (m ** 3 * 2 ** m), log2(L) / m))
print("E3 closed forms hold for m=2..12")
