#!/usr/bin/env python3
"""Vérifie les affirmations du document « famille SAT des injections impossibles
sur graphes cycliques » (C_n degré 2, D_n degré 3), avec satlab seul puis drat-trim.

    python3 studies/sat_cyclic_injections/verify.py [--drat CHEMIN]

Chaque section échoue par assertion si une affirmation est fausse. Les
certificats DRUP sont écrits dans out/ (ignoré par git).
"""

import argparse
import itertools
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from satlab import checker, matching  # noqa: E402
from satlab.dimacs import CNF  # noqa: E402
from satlab.generators import graph_php_cnf  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def family_c(n):
    """C_n : pigeons 0..n-1, N(i) = {i, i+1 mod n} ; pigeon n, N(n) = {0, 1}."""
    return [[i, (i + 1) % n] for i in range(n)] + [[0, 1]]


def family_d(n):
    """D_n : N(i) = {i, i+1, i+3} mod n ; pigeon n, N(n) = {0, 2, 4}."""
    return [sorted({i, (i + 1) % n, (i + 3) % n}) for i in range(n)] + [[0, 2, 4]]


def build(adj, n):
    nv, clauses, var = graph_php_cnf(adj, n)
    return nv, clauses, var


def is_matching(adj, n_holes, pigeons, m):
    """m : pigeon -> trou. Vérifie : arêtes de G, trous distincts, pigeons = ensemble donné."""
    if set(m) != set(pigeons):
        return False
    holes = list(m.values())
    if len(set(holes)) != len(holes):
        return False
    return all(m[p] in adj[p] and 0 <= m[p] < n_holes for p in pigeons)


def run_drat(drat, cnf_text, proof_text, tag):
    os.makedirs(OUT, exist_ok=True)
    base = os.path.join(OUT, tag)
    with open(base + ".cnf", "w") as f:
        f.write(cnf_text)
    with open(base + ".drup", "w") as f:
        f.write(proof_text)
    res = subprocess.run([drat, base + ".cnf", base + ".drup", "-t", "600"],
                         capture_output=True, text=True)
    return "s VERIFIED" in res.stdout.replace("\r", "\n")


# ---------------------------------------------------------------- §2 Hall
def check_hall_exhaustive(fam, name, ns):
    report = {}
    for n in ns:
        adj = fam(n)
        viol = []
        for r in range(1, len(adj) + 1):
            for S in itertools.combinations(range(len(adj)), r):
                if None in matching.max_matching([adj[x] for x in S], n):
                    viol.append(S)
        assert viol == [tuple(range(n + 1))], (name, n, viol[:3])
        report[n] = len(viol)
    print("%s Hall, exhaustif : une seule violation (U entier) pour n = %s" % (name, list(ns)))
    return report


def check_constructive_matchings(fam, name, ns):
    """Vérifie, pour TOUT n dans ns et tout pigeon omis, le couplage décrit dans le document."""
    for n in ns:
        adj = fam(n)
        # omission du pigeon supplémentaire : i -> i
        m = {i: i for i in range(n)}
        assert is_matching(adj, n, range(n), m), (name, n, "omission de n")
        for i in range(n):
            m = {n: 0}
            m.update({j: j + 1 for j in range(i)})
            m.update({j: j for j in range(i + 1, n)})
            pigeons = [p for p in range(n + 1) if p != i]
            assert is_matching(adj, n, pigeons, m), (name, n, "omission de", i)
    print("%s : couplages constructifs valides pour n dans %s, tout pigeon omis" % (name, list(ns)))


# ---------------------------------------------------------------- §3 C_n
def c_refutation(n):
    """Réfutation linéaire décrite dans le document, construite pas à pas.
    Renvoie (nv, clauses, lignes DRUP, nombre d'étapes de résolution, largeur max)."""
    adj = family_c(n)
    nv, clauses, var = build(adj, n)
    cset = {frozenset(c) for c in clauses}
    a = lambda i: var[(i, i)]                      # noqa: E731
    b = lambda i: var[(i, (i + 1) % n)]            # noqa: E731
    c0, c1 = var[(n, 0)], var[(n, 1)]

    P = {i: frozenset({a(i), b(i)}) for i in range(n)}
    P[n] = frozenset({c0, c1})
    H = {j: frozenset({-a(j), -b((j - 1) % n)}) for j in range(n)}
    extra = [frozenset({-c0, -a(0)}), frozenset({-c0, -b(n - 1)}),
             frozenset({-c1, -a(1)}), frozenset({-c1, -b(0)})]
    axioms = list(P.values()) + list(H.values()) + extra
    assert len(axioms) == 2 * n + 5 and nv == 2 * n + 2
    assert all(ax in cset for ax in axioms), "axiome absent de la CNF"

    lines, steps = [], [0]

    def res(X, Y, piv):
        assert piv in X and -piv in Y, (sorted(X), sorted(Y), piv)
        R = (X - {piv}) | (Y - {-piv})
        assert not any(-l in R for l in R), "tautologie"
        steps[0] += 1
        lines.append(" ".join(map(str, sorted(R, key=abs))) + " 0")
        return R

    I = {}
    for j in range(n):                                   # I_j = (¬a_j ∨ a_{j-1})
        I[j] = res(P[(j - 1) % n], H[j], b((j - 1) % n))
        assert I[j] == frozenset({a((j - 1) % n), -a(j)})
    X = res(P[n - 1], frozenset({-c0, -b(n - 1)}), b(n - 1))      # a_{n-1} ∨ ¬c0
    for k in range(n - 1, 0, -1):
        X = res(X, I[k], a(k))
    X = res(X, frozenset({-c0, -a(0)}), a(0))                     # ¬c0
    assert X == frozenset({-c0})
    Y = res(P[0], frozenset({-c1, -b(0)}), b(0))                  # a_0 ∨ ¬c1
    Y = res(Y, I[0], a(0))
    for k in range(n - 1, 1, -1):
        Y = res(Y, I[k], a(k))
    Y = res(Y, frozenset({-c1, -a(1)}), a(1))                     # ¬c1
    assert Y == frozenset({-c1})
    Z = res(P[n], X, c0)                                          # c1
    E = res(Z, Y, c1)                                             # vide
    assert E == frozenset()
    lines.append("0")
    width = max(len(l.split()) - 1 for l in lines[:-1])
    return nv, clauses, "\n".join(lines) + "\n", steps[0], width


def check_c_refutation(drat, ns):
    rows = {}
    for n in ns:
        nv, clauses, proof, steps, width = c_refutation(n)
        assert steps == 3 * n + 4 and width <= 2, (n, steps, width)
        ok_py, msg = checker.check_proof(nv, clauses, checker._parse_proof(proof))
        cnf_text = CNF(nv, clauses).to_dimacs()
        ok_drat = run_drat(drat, cnf_text, proof, "c%d" % n) if drat else None
        assert ok_py and ok_drat in (True, None), (n, msg)
        rows[n] = dict(variables=nv, axioms=len(clauses), steps=steps, width=width,
                       checker=ok_py, drat_trim=ok_drat, lines=proof.count("\n"))
    print("C_n, réfutation explicite (3n+4 étapes, largeur 2) : valide pour n = %s" % list(ns))
    return rows


# ---------------------------------------------------------------- §4 D_n
def primal_fill_width(adj, n, order_fn):
    """Largeur d'élimination (max |voisinage| au moment d'éliminer) sur le graphe primal,
    avec remplissage. order_fn(adj) renvoie la liste des variables dans l'ordre."""
    nv, clauses, var = build(adj, n)
    owner = {v: x for (x, y), v in var.items()}
    nbr = {v: set() for v in range(1, nv + 1)}
    for c in clauses:
        for u in c:
            for w in c:
                if u != w:
                    nbr[abs(u)].add(abs(w))
    width = 0
    for v in order_fn(adj, var):
        N = nbr.pop(v)
        width = max(width, len(N))
        for u in N:
            nbr[u].discard(v)
            nbr[u] |= (N - {u})
    return width


def d_order(adj, var):
    """3,4,…,n-1 puis 0,1,2 puis le pigeon supplémentaire (ordre du document)."""
    n = len(adj) - 1
    order = list(range(3, n)) + [0, 1, 2, n]
    return [var[(p, j)] for p in order for j in adj[p]]


def dp_refutation(adj, n, order_fn):
    """Élimination de Davis–Putnam avec dédoublonnage ; renvoie (nv, clauses, DRUP, nb_résolvantes,
    largeur max des clauses produites). Conserve tous les axiomes (pas de suppressions)."""
    nv, clauses, var = build(adj, n)
    db = {frozenset(c) for c in clauses}
    lines, count, maxw = [], 0, 0
    for v in order_fn(adj, var):
        pos = [c for c in db if v in c]
        neg = [c for c in db if -v in c]
        rest = {c for c in db if v not in c and -v not in c}
        new = set()
        for p in pos:
            for q in neg:
                R = (p - {v}) | (q - {-v})
                if any(-l in R for l in R) or R in rest or R in new:
                    continue
                new.add(R)
                count += 1
                maxw = max(maxw, len(R))
                lines.append(" ".join(map(str, sorted(R, key=abs))) + " 0")
        db = rest | new
        if frozenset() in db:
            break
    lines.append("0")
    assert frozenset() in db, "pas de clause vide : formule non réfutée par DP"
    return nv, clauses, "\n".join(lines) + "\n", count, maxw


def check_d_structure(ns):
    rows = {}
    for n in ns:
        adj = family_d(n)
        nv, clauses, var = build(adj, n)
        assert nv == 3 * n + 3, (n, nv)
        assert len(clauses) == 4 * n + 10, (n, len(clauses))
        assert max(len(c) for c in clauses) == 3 or n < 0
        rows[n] = dict(variables=nv, clauses=len(clauses),
                       max_clause_width=max(len(c) for c in clauses))
    print("D_n : 3n+3 variables, 4n+10 clauses, largeur initiale ≤ 3 : vérifié pour n = %s" % list(ns))
    return rows


def check_d_elimination_width(ns):
    rows = {}
    for n in ns:
        w = primal_fill_width(family_d(n), n, d_order)
        rows[n] = dict(max_neighbours=w, bag=w + 1)
        assert w + 1 <= 24, (n, w)
    print("D_n : largeur d'élimination (ordre du document) : bag max = %s pour n = %s"
          % (sorted({r["bag"] for r in rows.values()}), list(ns)))
    return rows


def check_d_dp_proofs(drat, ns):
    rows = {}
    for n in ns:
        adj = family_d(n)
        nv, clauses, proof, count, maxw = dp_refutation(adj, n, d_order)
        ok_py, msg = checker.check_proof(nv, clauses, checker._parse_proof(proof))
        ok_drat = run_drat(drat, CNF(nv, clauses).to_dimacs(), proof, "d%d" % n) if drat else None
        assert ok_py and ok_drat in (True, None), (n, msg)
        rows[n] = dict(resolvents=count, max_width=maxw, checker=ok_py, drat_trim=ok_drat)
    print("D_n, DP avec dédoublonnage : preuve valide pour n = %s" % list(ns))
    for n in ns:
        r = rows[n]
        print("   n=%d : %d résolvantes, largeur %d" % (n, r["resolvents"], r["max_width"]))
    return rows


# ---------------------------------------------------------------- §6 expansion
def boundary(adj, S, n):
    """Trous ayant exactement un voisin dans S."""
    return sorted(h for h in range(n) if sum(1 for p in S if h in adj[p]) == 1)


def width_bounded_refutation(adj, n, w):
    """Saturation par résolution restreinte à la largeur <= w (algorithme du « given clause »).
    Renvoie (nb clauses distinctes produites, nb de paires testées, certificat DRUP ordonné
    ou None). Le certificat ne contient que les ancêtres de la clause vide."""
    nv, clauses, _ = build(adj, n)
    store, parents, by_lit, seen = [], [], {}, {}
    def add(cl, par):
        if cl in seen:
            return None
        seen[cl] = len(store)
        store.append(cl)
        parents.append(par)
        for l in cl:
            by_lit.setdefault(l, []).append(seen[cl])
        return seen[cl]
    for c in clauses:
        add(frozenset(c), None)
    pairs = 0
    queue = list(range(len(store)))
    qi = 0
    empty = None
    while qi < len(store) and empty is None:
        i = qi
        qi += 1
        C = store[i]
        for l in C:
            for j in list(by_lit.get(-l, [])):
                if j > i and False:
                    continue
                D = store[j]
                pairs += 1
                R = (C - {l}) | (D - {-l})
                if any(-x in R for x in R) or len(R) > w:
                    continue
                k = add(R, (i, j, l))
                if k is not None and not R:
                    empty = k
                    break
            if empty is not None:
                break
    if empty is None:
        return len(store) - len(clauses), pairs, None, None
    # ancêtres de la clause vide, en ordre topologique (indices croissants)
    needed, stack = set(), [empty]
    while stack:
        k = stack.pop()
        if k in needed or parents[k] is None:
            continue
        needed.add(k)
        i, j, _ = parents[k]
        stack.extend([i, j])
    order = sorted(needed)
    lines = [" ".join(map(str, sorted(store[k], key=abs))) + " 0" for k in order]
    cert_steps = len(order)
    cert_nv, cert_cl = nv, clauses
    return len(store) - len(clauses), pairs, "\n".join(lines) + "\n", cert_steps


def check_d6_width3(drat):
    adj = family_d(6)
    generated, pairs, proof, steps = width_bounded_refutation(adj, 6, 3)
    assert proof is not None, "pas de réfutation de largeur 3 pour D_6"
    nv, clauses, _ = build(adj, 6)
    ok_py, msg = checker.check_proof(nv, clauses, checker._parse_proof(proof + "0\n"))
    ok_drat = run_drat(drat, CNF(nv, clauses).to_dimacs(), proof + "0\n", "d6w3") if drat else None
    assert ok_py and ok_drat in (True, None), msg
    print("D_6, largeur 3 : réfutation trouvée ; %d clauses produites, %d paires testées, "
          "certificat de %d étapes (checker=%s, drat=%s)" % (generated, pairs, steps, ok_py, ok_drat))
    return dict(generated=generated, pairs=pairs, certificate_steps=steps,
                checker=ok_py, drat_trim=ok_drat)


def check_expansion(ns):
    for n in ns:
        ac = family_c(n)
        for k in range(1, n):
            B = boundary(ac, range(k), n)
            assert B == sorted({0, k}), ("C", n, k, B)
        ad = family_d(n)
        for k in range(3, n - 2):
            B = boundary(ad, range(k), n)
            assert B == [0, k + 1, k + 2], ("D", n, k, B)
    print("Frontières : C_n = {0,k} (ratio 2/k) ; D_n = {0,k+1,k+2} (ratio 3/k) pour n = %s" % list(ns))


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drat", default=os.environ.get("DRAT_TRIM"),
                    help="chemin vers drat-trim (sinon seule la vérification satlab est faite)")
    args = ap.parse_args()
    results = {}

    results["hall_C_exhaustive"] = check_hall_exhaustive(family_c, "C_n", range(6, 13))
    results["hall_D_exhaustive"] = check_hall_exhaustive(family_d, "D_n", range(6, 13))
    check_constructive_matchings(family_c, "C_n", range(6, 201))
    check_constructive_matchings(family_d, "D_n", range(6, 201))

    results["c_structure"] = {n: dict(zip(("variables", "axioms"),
                                          (2 * n + 2, 2 * n + 5))) for n in (6, 12, 50)}
    results["c_refutation"] = check_c_refutation(args.drat, list(range(2, 13)) + [50])
    results["d_structure"] = check_d_structure([6, 8, 10, 12, 50])
    results["d_width"] = check_d_elimination_width([6, 8, 10, 12, 20, 50, 100, 200])
    results["d_dp"] = check_d_dp_proofs(args.drat, [6, 8, 10, 12, 16, 20])
    results["d6_width3"] = check_d6_width3(args.drat)
    check_expansion(list(range(6, 16)))

    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(results, f, indent=1, default=str)
    print("\nOK — toutes les assertions passent ; results.json écrit.")


if __name__ == "__main__":
    main()
