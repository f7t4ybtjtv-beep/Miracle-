#!/usr/bin/env python3
"""Vérifie la famille « Tseitin sur prismes » T_k et des réfutations de longueur 32k − 33.

    python3 studies/prism_tseitin/verify.py [--drat CHEMIN]

Graphe : prisme C_k x K_2 (2k sommets, 3k arêtes = 3k variables, 8k clauses).
Charge : 1 au sommet 0, 0 ailleurs (somme impaire : insatisfiable).

Ce script ne démontre pas la borne pour tout k : il vérifie des réfutations explicites
pour k = 3..60 et k = 100, avec un ordre d'élimination périodique dont l'accroissement
vaut exactement 32 par colonne. La démonstration pour tout k est dans STATIONNAIRE.md ;
ce script contrôle ses comptes par étape, sans en vérifier la preuve.
"""
import argparse
import itertools
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from satlab import cdcl, checker  # noqa: E402
from satlab.dimacs import CNF  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# ordre périodique (trouvé par recherche sur k = 9..11, puis vérifié pour k = 3..60 et 100)
OFFS = (1, 1, 0)     # décalage en colonnes des types (rail haut, rail bas, barreau)
PERM = (2, 0, 1)     # ordre des types au sein d'une colonne


def prism(k):
    """Renvoie (nombre de sommets, liste d'arêtes). Sommets : t_i = i, u_i = k+i."""
    edges = []
    for i in range(k):
        edges.append((i, (i + 1) % k))            # rail supérieur
        edges.append((k + i, k + (i + 1) % k))    # rail inférieur
        edges.append((i, k + i))                  # barreau
    return 2 * k, edges


def tseitin_cnf(k):
    nv_graph, edges = prism(k)
    charge = [0] * nv_graph
    charge[0] = 1
    inc = {v: [] for v in range(nv_graph)}
    for e, (a, b) in enumerate(edges):
        inc[a].append(e + 1)
        inc[b].append(e + 1)
    clauses = []
    for v in range(nv_graph):
        vs = inc[v]
        assert len(vs) == 3
        for bits in itertools.product((0, 1), repeat=3):
            if sum(bits) % 2 != charge[v]:          # affectation interdite
                clauses.append([-x if b else x for x, b in zip(vs, bits)])
    return len(edges), clauses


def is_unsat_by_parity(k):
    """Argument algébrique : chaque arête compte deux fois, la somme des charges est impaire."""
    _, edges = prism(k)
    deg = {}
    for a, b in edges:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    assert all(d == 3 for d in deg.values())
    return sum([1] + [0] * (2 * k - 1)) % 2 == 1


def periodic_order(k):
    """Variables (1-indexées) dans l'ordre d'élimination périodique."""
    keys = []
    for i in range(k):
        for t in range(3):
            keys.append(((i + OFFS[t]) * 3 + PERM.index(t), 3 * i + t + 1))
    return [v for _, v in sorted(keys)]


def dp_refutation_ordered(nv, clauses, order):
    """Élimination de Davis–Putnam dans l'ordre donné, avec dédoublonnage.
    Renvoie (nombre de résolvantes, largeur max, lignes DRUP ; la clause vide finale est incluse)."""
    db = {frozenset(c) for c in clauses}
    lines, count, maxw = [], 0, 0
    for v in order:
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
    assert frozenset() in db, "pas de clause vide"
    lines.append("0")
    return count, maxw, "\n".join(lines) + "\n"


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drat", default=os.environ.get("DRAT_TRIM"))
    args = ap.parse_args()
    results = {"family": {}, "table_fit": {}, "dp": {}}

    # 1. famille : comptes, insatisfiabilité
    for k in (3, 4, 5, 6):
        nv, cl = tseitin_cnf(k)
        assert nv == 3 * k and len(cl) == 8 * k, (k, nv, len(cl))
        assert is_unsat_by_parity(k)
        res = cdcl.CDCLSolver(nv, cl).solve()
        assert res.status == "UNSAT"
        ok, msg = checker.check_proof(nv, cl, checker._parse_proof("\n".join(res.proof)))
        assert ok, msg
        results["family"][k] = dict(variables=nv, clauses=len(cl), cdcl_proof_lines=len(res.proof))
    print("Famille : 3k variables, 8k clauses, UNSAT (parité + CDCL certifié) pour k = 3..6")

    # 2. le tableau de l'énoncé : 71, 351, 751, 1951 suivent 40k − 49 (ordre par colonnes)
    table = {3: 71, 10: 351, 20: 751, 50: 1951}
    for k, v in table.items():
        assert v == 40 * k - 49, (k, v)
    results["table_fit"] = {k: dict(reported=v, formula_40k_49=40 * k - 49) for k, v in table.items()}
    print("Tableau de l'énoncé : 71, 351, 751, 1951 = 40k − 49 exactement, pour k = 3, 10, 20, 50")

    # 3. borne 32k − 33 : réfutations explicites, ordre périodique, vérifiées
    ks = list(range(3, 61)) + [100]
    for k in ks:
        nv, cl = tseitin_cnf(k)
        order = periodic_order(k)
        assert sorted(order) == list(range(1, nv + 1))
        count, maxw, proof = dp_refutation_ordered(nv, cl, order)
        assert count == 32 * k - 33, (k, count)
        ok, msg = checker.check_proof(nv, cl, checker._parse_proof(proof))
        assert ok, (k, msg)
        drat_ok = None
        if args.drat and k in (3, 4, 5, 10, 50):
            drat_ok = run_drat(args.drat, CNF(nv, cl).to_dimacs(), proof, "prism%d" % k)
            assert drat_ok, k
        results["dp"][k] = dict(resolvents=count, max_width=maxw, bound=32 * k - 33,
                                checker=ok, drat_trim=drat_ok)
    # 4. la démonstration (STATIONNAIRE.md) prédit chaque compte par étape : vérification
    def predicted(k):
        pred = [8]                                   # R_0
        for _ in range(1, k - 1):                    # blocs stationnaires j = 1..k-2
            pred += [8, 16, 8]                       # R_j, T_{j-1}, B_{j-1}
        return pred + [8, 8, 4, 2, 1]                # queue : R_{k-1}, T_{k-2}, B_{k-2}, T_{k-1}, B_{k-1}
    for k in ks:
        nv, cl = tseitin_cnf(k)
        db = {frozenset(c) for c in cl}
        seq = []
        for v in periodic_order(k):
            pos = [c for c in db if v in c]
            neg = [c for c in db if -v in c]
            rest = {c for c in db if v not in c and -v not in c}
            new = set()
            for p_ in pos:
                for q_ in neg:
                    R = (p_ - {v}) | (q_ - {-v})
                    if any(-l in R for l in R) or R in rest or R in new:
                        continue
                    new.add(R)
            seq.append(len(new))
            db = rest | new
            if frozenset() in db:
                break
        assert seq == predicted(k), (k, seq[:6], predicted(k)[:6])
    print("Comptes par étape conformes à STATIONNAIRE.md (motif 8 ; 8,16,8 ; queue 8,8,4,2,1) pour k = 3..60 et 100")
    print("Ordre périodique : %d réfutations, accroissement 32 par colonne ; "
          "longueur = 32k − 33 exactement pour k = 3..60 et 100 (checker validé)" % len(ks))
    print("  largeur maximale observée : %d" % max(results["dp"][k]["max_width"] for k in ks))

    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(results, f, indent=1, default=str)
    print("\nOK — assertions passées ; results.json écrit.")


if __name__ == "__main__":
    main()
