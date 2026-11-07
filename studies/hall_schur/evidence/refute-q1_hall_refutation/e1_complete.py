import sys, time, random
from math import comb
sys.path.insert(0, '.')
from mylib import *
print("m lemmas closed lits closed_lits satlab drat naive res_steps res_bound(sumC(m,j)j(j+1)) emptyRes")
for m in range(2, 13):
    adj = {x: set(range(m)) for x in range(m + 1)}
    rng = random.Random(m)
    nv, cls, var = encode(adj, rng)
    P = list(range(m + 1)); rng.shuffle(P)
    L = explicit_drup(adj, P, list(range(m)))
    pr = lemmas_to_dimacs(L, var)
    nl = len(pr); lits = sum(len(c) for c in pr)
    cf = 2 ** (m - 1) * (m + 2) - 1
    cl = sum(comb(m, j) * ((j + 1) ** 2 * (m - j) + j) for j in range(1, m + 1))
    sl = dr = nv_ = rs = em = '-'
    if m <= 10:
        sl = satlab_check(nv, cls, pr)[0]
        dr = drat_check(nv, cls, pr, "php%d" % m)
    if m <= 6:
        nv_ = naive_rup_check(cls, pr)[0]
    if m <= 10:
        rs, em = resolution_proof(adj, P, list(range(m)))
    rb = sum(comb(m, j) * j * (j + 1) for j in range(1, m + 1))
    print(m, nl, cf, lits, cl, sl, dr, nv_, rs, rb, em, flush=True)
