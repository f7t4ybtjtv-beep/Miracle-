"""Preuve DRUP explicite d'insatisfiabilité à partir d'un témoin de Hall.

Pour l'encodage pigeonnier faible sur un graphe biparti (voir
generators.graph_php_cnf), soit S un témoin de Hall (|N(S)| < |S|),
T = N(S), m = |T|, et p_1..p_{m+1} des pigeons de S. Pour H ⊆ T avec
|H| = j - 1, on note

    D(j, H) = ∨_{i <= j} ∨_{h ∈ N(p_i) \\ H} e(p_i, h)
              (« les pigeons 1..j ne logent pas tous dans H »).

D(1, ∅) est la clause du pigeon p_1. Pour j = 1..m et chaque H ⊆ T de taille
j, on émet E(j+1, H, h) = D(j+1, H) ∨ ¬e(p_{j+1}, h) pour chaque h ∈ H voisin
de p_{j+1}, puis D(j+1, H). Chaque lemme est RUP (propagation des clauses de
trou sur h, puis D(j, H \\ {h}) ; puis clause du pigeon p_{j+1}), et
D(m+1, T) est la clause vide.

Taille : au plus Σ_j C(m, j)(j + 1) = 2^{m-1}(m + 2) - 1 lemmes (égalité sur
le biparti complet), donc 2^{O(k)} pour un témoin de taille k, et
polynomiale si k = O(log n). Comme la formule du témoin est une sous-CNF de
la formule complète, la même preuve réfute la formule complète.
"""

import itertools

from .generators import graph_php_cnf
from .matching import minimal_hall_violator, neighbourhood


def hall_witness_proof(adj, n_right, witness=None):
    """Renvoie (witness, lignes DRUP) ; témoin minimal calculé si absent."""
    if witness is None:
        witness = minimal_hall_violator(adj, n_right)
        if witness is None:
            raise ValueError("pas de témoin de Hall : la formule est satisfiable")
    T = sorted(neighbourhood(adj, witness))
    m = len(T)
    if m >= len(witness):
        raise ValueError("%s n'est pas un témoin de Hall" % (witness,))
    _, _, var = graph_php_cnf(adj, n_right)
    pigeons = list(witness)[:m + 1]
    nbr = [set(adj[p]) for p in pigeons]

    def D(j, H):
        return [var[(pigeons[i], h)] for i in range(j) for h in sorted(nbr[i] - H)]

    lines = []
    for j in range(1, m + 1):
        p = pigeons[j]
        for Hs in itertools.combinations(T, j):
            H = set(Hs)
            d = D(j + 1, H)
            for h in Hs:
                if h in nbr[j]:
                    lines.append(" ".join(map(str, d + [-var[(p, h)]])) + " 0")
            if d:
                lines.append(" ".join(map(str, d)) + " 0")
    lines.append("0")
    return list(witness), lines


def lemma_bound(m):
    """Nombre de lemmes sur le biparti complet K_{m+1,m} (borne supérieure)."""
    return 2 ** (m - 1) * (m + 2) - 1 if m else 1
