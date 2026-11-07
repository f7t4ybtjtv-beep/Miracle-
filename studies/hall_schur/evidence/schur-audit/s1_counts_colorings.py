"""(1) clause-count formula, (2) Schur(13,3) SAT / Schur(14,3) UNSAT by exhaustive
backtracking over colorings, (3) literal sub-CNF inclusion F14 subset FN."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schur_common import schur_cnf, all_clauses, var
from satlab.checker import check_model

CASES = {14: (42, 203), 15: (45, 228), 20: (60, 380), 30: (90, 795),
         40: (120, 1360), 50: (150, 2075)}

print("== (1) counts ==")
for N, (v_json, c_json) in CASES.items():
    nv, alo, amo, tri = schur_cnf(N)
    formula = N + 3 * N + 3 * sum(z // 2 for z in range(2, N + 1))
    closed = 4 * N + 3 * (N * N // 4)
    print("N=%d vars=%d (json %d) clauses=%d [ALO %d AMO %d TRI %d] formula=%d closed=%d json=%d match=%s"
          % (N, nv, v_json, len(alo) + len(amo) + len(tri), len(alo), len(amo), len(tri),
             formula, closed, c_json,
             nv == v_json and len(alo) + len(amo) + len(tri) == formula == closed == c_json))
# formula vs closed form for many N
bad = [N for N in range(1, 501)
       if N + 3 * N + 3 * sum(z // 2 for z in range(2, N + 1)) != 4 * N + 3 * (N * N // 4)]
print("closed form 4N+3*floor(N^2/4) agrees for N=1..500:", not bad)
# duplicate clauses?
for N in CASES:
    nv, cl = all_clauses(N)
    print("N=%d distinct clauses=%d" % (N, len({tuple(c) for c in cl})))

print("== (2) exhaustive sum-free 3-colorings of [1..n] (x=y allowed) ==")


def count_colorings(n):
    col = [None] * (n + 1)
    cnt = [0]
    first = [None]

    def ok(z, c):
        # new element z with color c: check x+y=z with x<=y<z, and x+x... all
        for x in range(1, z // 2 + 1):
            if col[x] == c and col[z - x] == c:
                return False
        return True

    def rec(z):
        if z > n:
            cnt[0] += 1
            if first[0] is None:
                first[0] = col[1:]
            return
        for c in range(3):
            if ok(z, c):
                col[z] = c
                rec(z + 1)
                col[z] = None
    rec(1)
    return cnt[0], first[0]


for n in range(1, 15):
    c, f = count_colorings(n)
    print("n=%d colorings=%d" % (n, c))

col13 = {1: 0, 4: 0, 7: 0, 10: 0, 13: 0, 2: 1, 3: 1, 11: 1, 12: 1, 5: 2, 6: 2, 8: 2, 9: 2}
classes = [sorted(i for i in col13 if col13[i] == c) for c in range(3)]
print("explicit coloring of [1..13]:", classes)
viol = [(x, y) for x in range(1, 14) for y in range(x, 14) if x + y <= 13
        and col13[x] == col13[y] == col13[x + y]]
print("monochromatic x+y=z (x<=y) violations:", viol)
model = [var(i, c) if col13[i] == c else -var(i, c) for i in range(1, 14) for c in range(3)]
nv, cl = all_clauses(13)
print("satlab.checker.check_model on Schur(13,3):", check_model(nv, cl, model))

print("== (3) literal sub-CNF inclusion ==")
_, c14 = all_clauses(14)
s14 = {tuple(c) for c in c14}
for N in range(14, 61):
    nv, cN = all_clauses(N)
    sN = {tuple(c) for c in cN}
    restricted = {c for c in sN if max(abs(l) for l in c) <= 42}
    if not (s14 <= sN and restricted == s14):
        print("FAIL at", N)
print("for N=14..60: F14 subset FN and {C in FN : vars(C) <= 42} == F14 : checked")
