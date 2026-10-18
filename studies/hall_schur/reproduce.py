#!/usr/bin/env python3
"""Reproduit et vérifie (assertions) les résultats de NOTE.md avec satlab seul.

    python3 studies/hall_schur/reproduce.py        # ~1-2 min, écrit results.json

Chaque section recalcule ses nombres par au moins deux méthodes
indépendantes (force brute / formule / couplage / CDCL certifié) et
échoue bruyamment en cas de désaccord.
"""

import itertools
import json
import math
import os
import random
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from satlab import cdcl, checker, core, generators, hallproof, matching, reference  # noqa: E402

OUT = {}


def all_graphs(nx, ny):
    """Tous les graphes bipartis étiquetés nx x ny (listes d'adjacence)."""
    cells = [(x, y) for x in range(nx) for y in range(ny)]
    for bits in range(1 << len(cells)):
        adj = [[] for _ in range(nx)]
        for i, (x, y) in enumerate(cells):
            if bits >> i & 1:
                adj[x].append(y)
        yield adj


def weak_models_ie(adj, ny):
    """Modèles de l'encodage faible par inclusion-exclusion (sans solveur) :
    applications partielles Y -> X le long des arêtes, surjectives sur X."""
    nx = len(adj)
    nbr_y = [[x for x in range(nx) if y in adj[x]] for y in range(ny)]
    total = 0
    for r in range(nx + 1):
        for S in itertools.combinations(range(nx), r):
            Sset = set(S)
            prod = 1
            for y in range(ny):
                prod *= 1 + sum(1 for x in nbr_y[y] if x not in Sset)
            total += (-1) ** r * prod
    return total


def matchable(adj, pigeons, holes):
    sub = [[y for y in adj[x] if y in holes] for x in pigeons]
    return None not in matching.max_matching(sub, max(holes, default=-1) + 1) if pigeons else True


def minimal_witnesses(adj, ny):
    nx = len(adj)
    out = []
    for r in range(1, nx + 1):
        for S in itertools.combinations(range(nx), r):
            N = matching.neighbourhood(adj, S)
            if len(N) >= len(S):
                continue
            if all(matchable(adj, [x for x in S if x != z], set(range(ny))) for z in S):
                out.append(list(S))
    return out


def induced_is_mus_criterion(adj, S):
    """Critère exact (NOTE §Q2) : chaque clause de trou est nécessaire ssi
    S \\ {x1,x2} se couple dans N(S) \\ {y}."""
    N = matching.neighbourhood(adj, S)
    for y in N:
        on_y = [x for x in S if y in adj[x]]
        for x1, x2 in itertools.combinations(on_y, 2):
            if not matchable(adj, [x for x in S if x not in (x1, x2)], N - {y}):
                return False
    return True


def induced_cnf(adj, S):
    return generators.graph_php_cnf([adj[x] for x in S], max(max(adj[x], default=0) for x in S) + 1)


def section(name):
    print("\n== " + name, flush=True)
    return time.perf_counter()


# --------------------------------------------------------------------------
t = section("Proposition : cas équilibré, modèles = couplages parfaits")
res = {}
for n in (1, 2, 3, 4):
    graphs = mism = models_total = 0
    for adj in all_graphs(n, n):
        graphs += 1
        pm = matching.count_perfect_matchings(adj, n)
        ie = weak_models_ie(adj, n)
        if n <= 3:
            nv, cl, _ = generators.graph_php_cnf(adj, n)
            bf = reference.brute_force(nv, cl, count=True)[2]
            mism += bf != ie
        mism += pm != ie
        models_total += ie
    # identité de contrôle : Σ_G perm(G) = n! · 2^(n² - n)
    assert models_total == math.factorial(n) * 2 ** (n * n - n), n
    assert mism == 0, (n, mism)
    res[n] = dict(graphs=graphs, mismatches=mism, total_models=models_total)
    print("n=%d : %d graphes, %d désaccords, Σ modèles = %d" % (n, graphs, mism, models_total))
unb = 0
for nx, ny in [(2, 1), (3, 2), (4, 3), (3, 1)]:
    for adj in all_graphs(nx, ny):
        assert weak_models_ie(adj, ny) == 0
        unb += 1
print("|X| > |Y| : %d graphes, tous UNSAT (0 modèle)" % unb)
OUT["proposition"] = dict(balanced=res, unbalanced_graphs_all_unsat=unb,
                          seconds=round(time.perf_counter() - t, 1))

# --------------------------------------------------------------------------
t = section("Q1 : preuve DRUP explicite depuis un témoin de Hall")
sizes = {}
for m in range(1, 9):
    adj = [list(range(m)) for _ in range(m + 1)]
    nv, cl, _ = generators.graph_php_cnf(adj, m)
    _, lines = hallproof.hall_witness_proof(adj, m)
    ok, _ = checker.check_proof(nv, cl, checker._parse_proof("\n".join(lines)))
    assert ok and len(lines) == 2 ** (m - 1) * (m + 2) - 1, m
    sizes[m] = len(lines)
print("K_{m+1,m}, lignes DRUP (m=1..8) :", list(sizes.values()))
planted = []
for s in range(30):
    rng = random.Random(s)
    n, k = rng.randint(10, 30), rng.randint(3, 7)
    cnf, meta = generators.bipartite_php(n, n + 2, 0.5, witness=k, seed=s)
    w, lines = hallproof.hall_witness_proof(meta["adj"], n + 2)
    m = len(matching.neighbourhood(meta["adj"], w))
    ok, _ = checker.check_proof(cnf.num_vars, cnf.clauses, checker._parse_proof("\n".join(lines)))
    assert ok and len(lines) <= hallproof.lemma_bound(m)
    planted.append(dict(n=n, k=k, witness=len(w), lines=len(lines), vars=cnf.num_vars))
print("30 graphes à témoin implanté : preuve du témoin valide sur la formule complète")
# transfert : K_{9,8} + K_{2,1} disjoint contient PHP(9,8) mais se réfute trivialement
adj = [list(range(8)) for _ in range(9)] + [[8], [8]]
nv, cl, _ = generators.graph_php_cnf(adj, 9)
ok_trivial, _ = checker.check_proof(nv, cl, checker._parse_proof("0"))
assert ok_trivial
OUT["q1"] = dict(complete_php_lines=sizes, planted=planted,
                 counterexample_transfer="K_{9,8} ⊔ K_{2,1} : la clause vide est RUP",
                 seconds=round(time.perf_counter() - t, 1))

# --------------------------------------------------------------------------
t = section("Q2 : la CNF d'un témoin minimal est-elle un MUS ?")
# exemple de la discussion et plus petit contre-exemple
ex4 = [[0, 2], [0, 2], [0, 1], [0, 1]]
ex3 = [[0], [0, 1], [0, 1]]
for adj, ny in ((ex4, 3), (ex3, 2)):
    assert minimal_witnesses(adj, ny) == [list(range(len(adj)))]
    nv, cl, _ = generators.graph_php_cnf(adj, ny)
    assert not core.is_mus(nv, cl) and not induced_is_mus_criterion(adj, list(range(len(adj))))
print("contre-exemples à 4 et 3 pigeons : témoin minimal, CNF induite non minimale")
fractions = {}
for nx, ny in [(3, 2), (3, 3), (4, 2), (4, 3)]:
    tot = mus = checked = 0
    for adj in all_graphs(nx, ny):
        for S in minimal_witnesses(adj, ny):
            tot += 1
            crit = induced_is_mus_criterion(adj, S)
            mus += crit
            if (nx, ny) != (4, 3) or tot % 7 == 0:   # critère comparé au test MUS direct
                nv, cl, _ = induced_cnf(adj, S)
                assert crit == core.is_mus(nv, cl), (adj, S)
                checked += 1
    fractions["%dx%d" % (nx, ny)] = dict(mus=mus, witnesses=tot, criterion_checked_by_cdcl=checked)
    print("%dx%d : %d/%d témoins minimaux à CNF induite MUS (%d vérifiés par CDCL)"
          % (nx, ny, mus, tot, checked))
expected = {"3x2": (79, 85), "3x3": (285, 303), "4x2": (560, 656), "4x3": (4113, 5457)}
for key, (a, b) in expected.items():
    assert (fractions[key]["mus"], fractions[key]["witnesses"]) == (a, b), key
# MUS de déficience 2 : pigeons {a,b,c,d}, témoin minimal {a,b} seulement
adj = [[0], [0], [0, 1], [0, 1]]
nv, cl, var = generators.graph_php_cnf(adj, 2)
e = lambda x, y: var[(x, y)]  # noqa: E731
mus_d2 = [[e(0, 0)], [e(1, 0)], [e(2, 0), e(2, 1)], [e(3, 0), e(3, 1)],
          [-e(0, 0), -e(2, 0)], [-e(1, 0), -e(3, 0)], [-e(2, 1), -e(3, 1)]]
assert core.is_mus(nv, mus_d2)
# caractérisation par la déficience, testée sur des MUS extraits aléatoirement
# (graph_php_cnf : les |X| premières clauses sont les clauses de pigeon)
viol = n_mus = 0
deficiency_hist = {}
for s in range(400):
    rng = random.Random(s)
    if s % 2:   # moitié biaisée vers |X| >> |Y| : déficiences élevées
        nx, ny = rng.randint(4, 7), rng.randint(1, 3)
    else:
        nx, ny = rng.randint(2, 6), rng.randint(1, 4)
    adj = [[y for y in range(ny) if rng.random() < 0.6] for _ in range(nx)]
    nv, cl, var = generators.graph_php_cnf(adj, ny)
    if nv > 20 or reference.brute_force(nv, cl)[0]:
        continue
    order = list(range(len(cl)))
    rng.shuffle(order)
    idx = core.shrink_to_mus(nv, cl, order)
    owner = {v: x for (x, y), v in var.items()}
    P = [i for i in idx if i < nx]
    holes_ok = all(owner[-cl[i][0]] in P and owner[-cl[i][1]] in P for i in idx if i >= nx)
    d = lambda T: len(T) - len(matching.neighbourhood(adj, T))  # noqa: E731
    strict = d(P) >= 1 and all(d(T) < d(P) for r in range(1, len(P))
                               for T in itertools.combinations(P, r))
    is_minwit = P in minimal_witnesses(adj, ny)
    viol += (not holes_ok) or (not strict) or ((d(P) == 1) != is_minwit)
    n_mus += 1
    deficiency_hist[d(P)] = deficiency_hist.get(d(P), 0) + 1
# balayage ciblé : tous les graphes 4x2, 12 ordres de suppression chacun
for gi, adj in enumerate(all_graphs(4, 2)):
    nv, cl, var = generators.graph_php_cnf(adj, 2)
    if reference.brute_force(nv, cl)[0]:
        continue
    owner = {v: x for (x, y), v in var.items()}
    seen = set()
    for r in range(12):
        order = list(range(len(cl)))
        random.Random(1000 * gi + r).shuffle(order)
        idx = tuple(core.shrink_to_mus(nv, cl, order))
        if idx in seen:
            continue
        seen.add(idx)
        P = [i for i in idx if i < 4]
        holes_ok = all(owner[-cl[i][0]] in P and owner[-cl[i][1]] in P for i in idx if i >= 4)
        d = lambda T: len(T) - len(matching.neighbourhood(adj, T))  # noqa: E731
        strict = d(P) >= 1 and all(d(T) < d(P) for k in range(1, len(P))
                                   for T in itertools.combinations(P, k))
        viol += (not holes_ok) or (not strict) or ((d(P) == 1) != (P in minimal_witnesses(adj, 2)))
        n_mus += 1
        deficiency_hist[d(P)] = deficiency_hist.get(d(P), 0) + 1
assert viol == 0, viol
assert any(k >= 2 for k in deficiency_hist)   # le test n'est pas vide
print("caractérisation par la déficience : %d MUS extraits, 0 violation, déficiences %s"
      % (n_mus, dict(sorted(deficiency_hist.items()))))
OUT["q2"] = dict(fractions_exhaustive=fractions, deficiency2_mus_example=True,
                 random_mus_checked=n_mus, random_mus_deficiency=deficiency_hist, seconds=round(time.perf_counter() - t, 1))

# --------------------------------------------------------------------------
t = section("Q3 : écart modèles / couplages saturants quand |X| < |Y|")
for n in range(1, 6):     # n étoiles disjointes K_{1,2}
    adj = [[2 * i, 2 * i + 1] for i in range(n)]
    nv, cl, _ = generators.graph_php_cnf(adj, 2 * n)
    assert reference.brute_force(nv, cl, count=True)[2] == 3 ** n == weak_models_ie(adj, 2 * n)
    assert matching.count_saturating_matchings(adj, 2 * n) == 2 ** n


def stirling2(a, b):
    return sum((-1) ** j * math.comb(b, j) * (b - j) ** a for j in range(b + 1)) // math.factorial(b)


for n in range(1, 5):
    for m in range(n, 9):
        adj = [list(range(m)) for _ in range(n)]
        models = math.factorial(n) * stirling2(m + 1, n + 1)
        assert models == weak_models_ie(adj, m)
        if n * m <= 16:
            nv, cl, _ = generators.graph_php_cnf(adj, m)
            assert reference.brute_force(nv, cl, count=True)[2] == models
        if m == n + 1:
            assert models == math.factorial(n + 1) * (n + 2) // 2
bounds_checked = 0
for nx, ny in [(1, 3), (2, 3), (2, 4), (3, 4), (2, 5)]:
    for adj in all_graphs(nx, ny):
        sm = matching.count_saturating_matchings(adj, ny)
        mod = weak_models_ie(adj, ny)
        if sm == 0:
            assert mod == 0
            continue
        k = len(matching.neighbourhood(adj, range(nx))) - nx
        assert 1.5 ** k * sm <= mod + 1e-9 and mod <= (nx + 1) ** k * sm
        assert (mod == sm) == (k == 0)
        bounds_checked += 1
print("étoiles (3/2)^n, K_{n,m} = n!·S(m+1,n+1), bornes (3/2)^k ≤ ratio ≤ (|X|+1)^k "
      "sur %d graphes" % bounds_checked)
OUT["q3"] = dict(bounds_checked_graphs=bounds_checked, seconds=round(time.perf_counter() - t, 1))

# --------------------------------------------------------------------------
t = section("Schur(N,3) : audit du JSON fourni")
counts = {}
for N in (14, 15, 20, 30, 40, 50):
    c, _ = generators.schur(N)
    assert c.num_clauses == 4 * N + 3 * (N * N // 4) and c.num_vars == 3 * N
    counts[N] = c.num_clauses
c13, _ = generators.schur(13)
r13 = cdcl.solve(c13)
assert r13.status == "SAT" and checker.check_model(c13.num_vars, c13.clauses, r13.model)[0]
coloring = {i: next(c for c in range(3) if r13.model[(i - 1) * 3 + c] > 0) for i in range(1, 14)}
for x in range(1, 14):
    for y in range(x, 14 - x):
        assert not (coloring[x] == coloring[y] == coloring[x + y])
c14, _ = generators.schur(14)
r14 = cdcl.solve(c14)
steps = checker._parse_proof("\n".join(r14.proof))
reuse = {}
for N in (14, 15, 20, 30, 40, 50):
    cN, _ = generators.schur(N)
    reuse[N] = checker.check_proof(cN.num_vars, cN.clauses, steps)[0]
    assert reuse[N]
assert cdcl.solve(generators.schur(14, amo=False)[0]).status == "UNSAT"
mus = core.shrink_to_mus(c14.num_vars, c14.clauses)
amo_in_mus = sum(1 for i in mus if len(c14.clauses[i]) == 2 and
                 (abs(c14.clauses[i][0]) - 1) // 3 == (abs(c14.clauses[i][1]) - 1) // 3)
assert amo_in_mus == 0
print("comptes = 4N + 3⌊N²/4⌋ ; S(13) SAT (coloration vérifiée), S(14) UNSAT ;"
      " preuve de N=14 (%d lignes) valide pour N=14..50 ; MUS de %d clauses, 0 AMO"
      % (len(r14.proof), len(mus)))
OUT["schur"] = dict(clause_counts=counts, schur13_coloring=coloring,
                    proof_lines_n14=len(r14.proof), proof_reuse_verified=reuse,
                    amo_free_unsat=True, one_mus_size=len(mus), amo_in_mus=amo_in_mus,
                    seconds=round(time.perf_counter() - t, 1))

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json"), "w") as f:
    json.dump(OUT, f, indent=1, ensure_ascii=False, default=str)
print("\nOK — toutes les assertions passent ; results.json écrit.")
