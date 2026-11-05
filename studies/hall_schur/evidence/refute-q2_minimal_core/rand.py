"""Own random test (seed 777): graphs nX in 6..9, nY in 3..nX-1, edge prob in {.3,.45,.6}.
A: every minimal witness: pigeon necessity + hole criterion vs sat_choice; DPLL cross-check every 5th witness.
B: deletion-based MUS extraction of the FULL encoding (random clause order), check (i),(ii),(iii)."""
import os, sys, random, itertools, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import *
rng = random.Random(777)
t0 = time.time()
A = dict(graphs=0, w=0, mus=0, maxS=0, pig_fail=0, crit_mis=0, holes=0, xcheck=0)
B = dict(mus=0, bad_hole=0, not_strict=0, d1_not_minwit=0, minwit_not_d1=0, hist={}, maxP=0, verify_fail=0)
def d(adj, T): return len(T) - popc(nbrs(adj, T))
while time.time() - t0 < 150:
    nX = rng.randint(6, 9); nY = rng.randint(3, nX - 1); p = rng.choice([.3, .45, .6])
    adj = tuple(sum(1 << y for y in range(nY) if rng.random() < p) for _ in range(nX))
    A['graphs'] += 1
    mw = minimal_witnesses(adj)
    for S in mw:
        cl = induced_clauses(adj, S); NS = nbrs(adj, S)
        A['w'] += 1; A['maxS'] = max(A['maxS'], len(S))
        xc = A['w'] % 5 == 0
        assert not sat_choice(adj, cl)
        if xc: assert not sat_generic(adj, cl); A['xcheck'] += 1
        allnec = True
        for i, c in enumerate(cl):
            rest = cl[:i] + cl[i+1:]
            nec = sat_choice(adj, rest)
            if xc: assert nec == sat_generic(adj, rest)
            if c[0] == 'P':
                A['pig_fail'] += (not nec)
            else:
                A['holes'] += 1
                crit = has_matching(adj, [x for x in S if x not in (c[2], c[3])], NS & ~(1 << c[1]))
                A['crit_mis'] += (crit != nec)
            allnec &= nec
        A['mus'] += allnec
    full = full_clauses(adj, nY)
    if sat_choice(adj, full): continue
    for _ in range(2):
        F = full[:]; rng.shuffle(F); i = 0
        while i < len(F):
            G = F[:i] + F[i+1:]
            if not sat_choice(adj, G): F = G
            else: i += 1
        if not is_mus(adj, F): B['verify_fail'] += 1
        B['mus'] += 1
        P = tuple(sorted(c[1] for c in F if c[0] == 'P')); B['maxP'] = max(B['maxP'], len(P))
        B['bad_hole'] += sum(1 for c in F if c[0] == 'H' and not (c[2] in P and c[3] in P))
        dP = d(adj, P); B['hist'][dP] = B['hist'].get(dP, 0) + 1
        if any(d(adj, T) >= dP for r in range(len(P)) for T in itertools.combinations(P, r)): B['not_strict'] += 1
        ismw = list(P) in mw
        B['d1_not_minwit'] += (dP == 1 and not ismw); B['minwit_not_d1'] += (ismw and dP != 1)
print("A", A); print("B", B); print("time %.1f" % (time.time() - t0))
print("A fraction %d/%d = %.4f" % (A['mus'], A['w'], A['mus'] / A['w']))
