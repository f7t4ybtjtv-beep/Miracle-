"""Familles d'instances à graine déterministe.

Chaque générateur renvoie (CNF, méta) où méta contient la famille, les
paramètres d'appel (mêmes noms que les arguments, plus d'éventuelles
grandeurs dérivées sous un autre nom, ex. `edges`), la graine et, quand il est connu par construction, le statut
attendu ("SAT"/"UNSAT"/None). Le statut attendu sert de contre-test : il est
justifié mathématiquement, pas par le solveur.
"""

import itertools
import random

from .dimacs import CNF


def _meta(family, expected, seed, **params):
    return dict(family=family, params=params, seed=seed, expected=expected)


def random_ksat(n, m, k=3, seed=0):
    """k-SAT aléatoire uniforme : m clauses de k variables distinctes."""
    rng = random.Random(seed)
    clauses = []
    for _ in range(m):
        vs = rng.sample(range(1, n + 1), k)
        clauses.append([v if rng.random() < 0.5 else -v for v in vs])
    cnf = CNF(n, clauses, ["random %d-SAT n=%d m=%d seed=%d" % (k, n, m, seed)])
    return cnf, _meta("random_ksat", None, seed, n=n, m=m, k=k, ratio=round(m / n, 4))


def planted_ksat(n, m, k=3, seed=0):
    """k-SAT avec solution cachée : SAT par construction.

    Une affectation secrète est tirée ; on ne garde que les clauses qu'elle
    satisfait (rejet). Le modèle caché est renvoyé dans méta["hidden"].
    """
    rng = random.Random(seed)
    hidden = {v: rng.random() < 0.5 for v in range(1, n + 1)}
    clauses = []
    while len(clauses) < m:
        vs = rng.sample(range(1, n + 1), k)
        c = [v if rng.random() < 0.5 else -v for v in vs]
        if any(hidden[abs(l)] == (l > 0) for l in c):
            clauses.append(c)
    cnf = CNF(n, clauses, ["planted %d-SAT n=%d m=%d seed=%d" % (k, n, m, seed)])
    meta = _meta("planted_ksat", "SAT", seed, n=n, m=m, k=k, ratio=round(m / n, 4))
    meta["hidden"] = [v if hidden[v] else -v for v in range(1, n + 1)]
    return cnf, meta


def pigeonhole(holes, seed=0):
    """PHP(h+1, h) : h+1 pigeons dans h trous. UNSAT (principe des tiroirs).

    Exige des preuves par résolution de taille 2^Ω(h) (Haken, 1985).
    La graine ne sert qu'à permuter clauses et littéraux (même instance
    logique) afin de mesurer la variance due à l'ordre.
    """
    rng = random.Random(seed)
    p = holes + 1

    def x(i, j):
        return i * holes + j + 1

    clauses = [[x(i, j) for j in range(holes)] for i in range(p)]
    for j in range(holes):
        for i1, i2 in itertools.combinations(range(p), 2):
            clauses.append([-x(i1, j), -x(i2, j)])
    if seed:
        rng.shuffle(clauses)
        for c in clauses:
            rng.shuffle(c)
    cnf = CNF(p * holes, clauses, ["PHP %d->%d seed=%d" % (p, holes, seed)])
    return cnf, _meta("pigeonhole", "UNSAT", seed, holes=holes, pigeons=p)


def random_regular_graph(n, d, rng):
    """Graphe d-régulier simple aléatoire (modèle de configuration + rejet)."""
    if (n * d) % 2:
        raise ValueError("n*d doit être pair")
    for _ in range(10000):
        stubs = [v for v in range(n) for _ in range(d)]
        rng.shuffle(stubs)
        edges = set()
        ok = True
        for a, b in zip(stubs[::2], stubs[1::2]):
            e = (min(a, b), max(a, b))
            if a == b or e in edges:
                ok = False
                break
            edges.add(e)
        if ok:
            return sorted(edges)
    raise RuntimeError("échec de génération du graphe régulier")


def tseitin(n, d=3, seed=0):
    """Formule de Tseitin sur un graphe d-régulier aléatoire, charge impaire.

    Une variable par arête ; pour chaque sommet, la parité des arêtes
    incidentes égale sa charge. Somme des charges impaire => UNSAT (chaque
    arête est comptée deux fois). Sur expanseurs, la résolution exige une
    taille 2^Ω(n) (Urquhart 1987 ; Ben-Sasson & Wigderson 2001).
    """
    rng = random.Random(seed)
    edges = random_regular_graph(n, d, rng)
    var = {e: i + 1 for i, e in enumerate(edges)}
    charge = [0] * n
    charge[rng.randrange(n)] = 1        # total impair
    inc = [[] for _ in range(n)]
    for e, v in var.items():
        inc[e[0]].append(v)
        inc[e[1]].append(v)
    clauses = []
    for u in range(n):
        vs = inc[u]
        # interdit chaque affectation locale de mauvaise parité
        for signs in itertools.product((0, 1), repeat=len(vs)):
            if sum(signs) % 2 != charge[u]:
                clauses.append([-v if s else v for v, s in zip(vs, signs)])
    cnf = CNF(len(edges), clauses, ["Tseitin n=%d d=%d seed=%d" % (n, d, seed)])
    return cnf, _meta("tseitin", "UNSAT", seed, n=n, d=d, edges=len(edges))


def coloring(n, k, avg_degree, seed=0):
    """k-coloration d'un graphe G(n, p) avec p = avg_degree/(n-1)."""
    rng = random.Random(seed)
    p = avg_degree / (n - 1)
    edges = [(a, b) for a in range(n) for b in range(a + 1, n) if rng.random() < p]

    def x(v, c):
        return v * k + c + 1

    clauses = [[x(v, c) for c in range(k)] for v in range(n)]
    for v in range(n):
        for c1, c2 in itertools.combinations(range(k), 2):
            clauses.append([-x(v, c1), -x(v, c2)])
    for a, b in edges:
        for c in range(k):
            clauses.append([-x(a, c), -x(b, c)])
    cnf = CNF(n * k, clauses, ["%d-coloring G(%d, d=%g) seed=%d" % (k, n, avg_degree, seed)])
    return cnf, _meta("coloring", None, seed, n=n, k=k,
                      avg_degree=avg_degree, edges=len(edges))


FAMILIES = {
    "random_ksat": random_ksat,
    "planted_ksat": planted_ksat,
    "pigeonhole": pigeonhole,
    "tseitin": tseitin,
    "coloring": coloring,
}


def generate(family, seed=0, **params):
    return FAMILIES[family](seed=seed, **params)
