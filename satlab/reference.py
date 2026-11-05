"""Solveurs de référence, volontairement simples et indépendants du CDCL.

Ils servent d'oracles pour les contre-tests : une divergence de statut entre
le CDCL et l'un d'eux signale un bogue.
"""

import itertools


def brute_force(num_vars, clauses, count=False):
    """Énumère les 2^n affectations. Renvoie (sat, modèle, nb_modèles|None)."""
    if num_vars > 24:
        raise ValueError("force brute limitée à 24 variables")
    first, total = None, 0
    for bits in itertools.product((False, True), repeat=num_vars):
        if all(any(bits[abs(l) - 1] == (l > 0) for l in c) for c in clauses):
            if first is None:
                first = [v + 1 if b else -(v + 1) for v, b in enumerate(bits)]
                if not count:
                    return True, first, None
            total += 1
    return first is not None, first, (total if count else None)


def dpll(num_vars, clauses, node_limit=None):
    """DPLL récursif (propagation unitaire + littéral pur, sans apprentissage).

    Renvoie (statut, modèle, nb_nœuds) avec statut ∈ {True, False, None}.
    """
    nodes = [0]

    def simplify(cls, lit):
        out = []
        for c in cls:
            if lit in c:
                continue
            if -lit in c:
                c = [l for l in c if l != -lit]
                if not c:
                    return None
            out.append(c)
        return out

    def rec(cls, assignment):
        nodes[0] += 1
        if node_limit is not None and nodes[0] > node_limit:
            raise TimeoutError
        while True:
            unit = next((c[0] for c in cls if len(c) == 1), None)
            if unit is None:
                lits = {l for c in cls for l in c}
                unit = next((l for l in lits if -l not in lits), None)
                if unit is None:
                    break
            assignment = assignment + [unit]
            cls = simplify(cls, unit)
            if cls is None:
                return None
        if not cls:
            return assignment
        # branche sur la variable la plus fréquente dans les plus courtes clauses
        shortest = min(len(c) for c in cls)
        freq = {}
        for c in cls:
            if len(c) == shortest:
                for l in c:
                    freq[l] = freq.get(l, 0) + 1
        lit = max(sorted(freq), key=lambda l: freq[l])
        for choice in (lit, -lit):
            sub = simplify(cls, choice)
            if sub is not None:
                r = rec(sub, assignment + [choice])
                if r is not None:
                    return r
        return None

    cls = [sorted(set(c)) for c in clauses if not any(-l in c for l in c)]
    if any(not c for c in cls):
        return False, None, 0
    try:
        res = rec(cls, [])
    except TimeoutError:
        return None, None, nodes[0]
    if res is None:
        return False, None, nodes[0]
    assigned = {abs(l): l for l in res}
    model = [assigned.get(v, -v) for v in range(1, num_vars + 1)]
    return True, model, nodes[0]
