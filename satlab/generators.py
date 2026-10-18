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


def graph_php_cnf(adj, n_right):
    """Encodage pigeonnier « faible » sur un graphe biparti.

    adj[x] = trous voisins du pigeon x. Une variable par arête ; clauses
    « au moins un trou par pigeon » et « au plus un pigeon par trou », sans
    clauses « au plus un trou par pigeon ». Renvoie (num_vars, clauses, var)
    où var[(x, y)] est la variable de l'arête x–y.
    """
    var = {}
    for x, ys in enumerate(adj):
        for y in sorted(ys):
            var[(x, y)] = len(var) + 1
    clauses = [[var[(x, y)] for y in sorted(ys)] for x, ys in enumerate(adj)]
    by_hole = {}
    for (x, y), v in var.items():
        by_hole.setdefault(y, []).append(v)
    for y in sorted(by_hole):
        for a, b in itertools.combinations(by_hole[y], 2):
            clauses.append([-a, -b])
    return len(var), clauses, var


def bipartite_php(n, m, p, witness=0, seed=0):
    """Pigeonnier faible sur un graphe biparti aléatoire G(n pigeons, m trous, p).

    witness=k >= 1 implante un témoin de Hall : les pigeons 0..k-1 ne voient que
    les trous 0..k-2 (biparti complet K_{k,k-1}), ce qui rend la formule UNSAT.
    Le statut attendu est calculé par couplage maximum (théorème de Hall),
    sans solveur SAT : c'est un oracle indépendant.
    """
    from .matching import hall_violator, minimal_hall_violator

    if witness > n or witness - 1 > m:
        raise ValueError("témoin de taille %d impossible avec %d pigeons et %d trous"
                         % (witness, n, m))
    rng = random.Random(seed)
    adj = []
    for x in range(n):
        if x < witness:
            adj.append(list(range(witness - 1)))
        else:
            adj.append([y for y in range(m) if rng.random() < p])
    nv, clauses, _ = graph_php_cnf(adj, m)
    unsat = hall_violator(adj, m) is not None
    mhv = minimal_hall_violator(adj, m) if unsat else None
    cnf = CNF(nv, clauses, ["graph PHP n=%d m=%d p=%g witness=%d seed=%d" % (
        n, m, p, witness, seed)])
    meta = _meta("bipartite_php", "UNSAT" if unsat else "SAT", seed, n=n, m=m, p=p,
                 witness=witness, edges=nv,
                 min_hall_witness=len(mhv) if mhv else 0)
    meta["adj"] = adj
    return cnf, meta


# Nombres de Schur connus : S(k) = plus grand N tel que {1..N} admet une
# k-coloration sans solution monochrome de x + y = z. S(4) = 44 (Baumert,
# 1965) ; S(5) = 160 (Heule, 2017).
SCHUR_NUMBERS = {1: 1, 2: 4, 3: 13, 4: 44, 5: 160}


def schur(n, k=3, amo=True, seed=0):
    """Schur(n, k) : colorer 1..n en k couleurs sans x + y = z monochrome.

    Variable (i, c) = (i-1)·k + c + 1 : la numérotation ne dépend pas de n,
    donc Schur(n, k) est une sous-CNF de Schur(n', k) pour n <= n'. Clauses :
    au moins une couleur par entier, au plus une (si amo), et pour chaque
    x <= y avec x + y = z <= n et chaque couleur, ¬(x,c) ∨ ¬(y,c) ∨ ¬(z,c)
    (2 littéraux si x = y). La graine ne fait que mélanger l'ordre des
    clauses.
    """
    rng = random.Random(seed)

    def v(i, c):
        return (i - 1) * k + c + 1

    clauses = [[v(i, c) for c in range(k)] for i in range(1, n + 1)]
    if amo:
        clauses += [[-v(i, a), -v(i, b)] for i in range(1, n + 1)
                    for a, b in itertools.combinations(range(k), 2)]
    for z in range(2, n + 1):
        for x in range(1, z // 2 + 1):
            for c in range(k):
                clauses.append(sorted({-v(x, c), -v(z - x, c), -v(z, c)}, key=abs))
    if seed:
        rng.shuffle(clauses)
    expected = None
    if k in SCHUR_NUMBERS:
        expected = "SAT" if n <= SCHUR_NUMBERS[k] else "UNSAT"
    cnf = CNF(n * k, clauses, ["Schur(%d, %d) amo=%s seed=%d" % (n, k, amo, seed)])
    return cnf, _meta("schur", expected, seed, n=n, k=k, amo=amo)


FAMILIES = {
    "random_ksat": random_ksat,
    "planted_ksat": planted_ksat,
    "pigeonhole": pigeonhole,
    "tseitin": tseitin,
    "coloring": coloring,
    "bipartite_php": bipartite_php,
    "schur": schur,
}


def generate(family, seed=0, **params):
    return FAMILIES[family](seed=seed, **params)
