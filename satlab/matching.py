"""Couplages bipartis : oracle polynomial pour l'encodage pigeonnier sur graphe.

Un graphe biparti est donné par `adj` : adj[x] = liste des trous voisins du
pigeon x (x dans 0..len(adj)-1, trous dans 0..n_right-1).

- max_matching        : couplage maximum (chemins augmentants, O(V·E))
- hall_violator       : témoin de Hall S (|N(S)| < |S|) ou None
- minimal_hall_violator : témoin minimal pour l'inclusion
- count_perfect_matchings / count_saturating_matchings : DP sur les
  sous-ensembles de trous (exponentiel en n_right, pour les petits graphes)

Ces fonctions n'utilisent aucun solveur SAT : elles servent de contre-test
indépendant (théorème de Hall) pour les statuts SAT/UNSAT.
"""


def max_matching(adj, n_right):
    """Renvoie match_left (trou de chaque pigeon ou None)."""
    match_right = [None] * n_right
    match_left = [None] * len(adj)

    def augment(x, seen):
        for y in adj[x]:
            if y in seen:
                continue
            seen.add(y)
            if match_right[y] is None or augment(match_right[y], seen):
                match_right[y] = x
                match_left[x] = y
                return True
        return False

    for x in range(len(adj)):
        augment(x, set())
    return match_left


def neighbourhood(adj, pigeons):
    return {y for x in pigeons for y in adj[x]}


def hall_violator(adj, n_right):
    """Témoin de Hall via König : pigeons atteignables par chemins alternés
    depuis un pigeon non couplé. Renvoie un ensemble trié, ou None."""
    match_left = max_matching(adj, n_right)
    free = [x for x, y in enumerate(match_left) if y is None]
    if not free:
        return None
    match_right = {y: x for x, y in enumerate(match_left) if y is not None}
    seen_left, seen_right = {free[0]}, set()
    stack = [free[0]]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seen_right:
                seen_right.add(y)
                x2 = match_right[y]          # couplage maximum : y est couplé
                if x2 not in seen_left:
                    seen_left.add(x2)
                    stack.append(x2)
    return sorted(seen_left)


def minimal_hall_violator(adj, n_right):
    """Témoin de Hall minimal pour l'inclusion (ou None).

    Suppression gloutonne : on retire un pigeon tant que le reste n'admet
    toujours aucun couplage saturant. Le résultat T n'a pas de couplage
    saturant mais toutes ses parties propres en ont un ; par le théorème de
    Hall, le sous-ensemble violant de T est donc T lui-même.
    """
    S = hall_violator(adj, n_right)
    if S is None:
        return None
    T = list(S)
    i = 0
    while i < len(T):
        trial = T[:i] + T[i + 1:]
        sub = [adj[x] for x in trial]
        if None in max_matching(sub, n_right):
            T = trial
        else:
            i += 1
    return T


def _count_injective(adj, n_right):
    """Nombre d'injections pigeon -> trou voisin (DP sur masques de trous)."""
    ways = {0: 1}
    for x in range(len(adj)):
        nxt = {}
        for mask, w in ways.items():
            for y in adj[x]:
                if not mask >> y & 1:
                    m2 = mask | 1 << y
                    nxt[m2] = nxt.get(m2, 0) + w
        ways = nxt
    return sum(ways.values())


def count_saturating_matchings(adj, n_right):
    """Couplages qui couvrent tous les pigeons."""
    return _count_injective(adj, n_right)


def count_perfect_matchings(adj, n_right):
    """Couplages parfaits (= permanent de la matrice d'adjacence) ; 0 si
    le graphe n'est pas équilibré."""
    if len(adj) != n_right:
        return 0
    return _count_injective(adj, n_right)
