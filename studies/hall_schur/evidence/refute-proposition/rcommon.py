"""Independent helpers (refute-proposition). Different algorithms from pm-balanced:
- clause generator built from a biadjacency matrix given as list-of-rows bitmasks, edge vars
  numbered column-major (y outer, x inner) -- different variable order from the other agent.
- perm_naive: definition, sum over all permutations (itertools.permutations).
- models_choice: enumerate per-hole choices (none or one neighbour) -> exactly the
  assignments satisfying all AMO clauses; count those that also satisfy ALO.
- models_bits: brute force over all 2^|E| edge subsets using bitmask clause tests.
"""
import itertools


def edges_of(nx, ny, rows):
    # rows[x] = bitmask over Y. Column-major numbering.
    E = []
    for y in range(ny):
        for x in range(nx):
            if (rows[x] >> y) & 1:
                E.append((x, y))
    return E


def cnf(nx, ny, rows):
    E = edges_of(nx, ny, rows)
    vid = {e: i + 1 for i, e in enumerate(E)}
    cls = []
    for x in range(nx):
        cls.append([vid[(x, y)] for y in range(ny) if (x, y) in vid])
    for y in range(ny):
        nb = [x for x in range(nx) if (x, y) in vid]
        for a, b in itertools.combinations(nb, 2):
            cls.append([-vid[(a, y)], -vid[(b, y)]])
    return len(E), cls, E


def perm_naive(n, rows):
    t = 0
    for p in itertools.permutations(range(n)):
        if all((rows[i] >> p[i]) & 1 for i in range(n)):
            t += 1
    return t


def xsat_matchings(nx, ny, rows):
    # injective maps X -> Y along edges, by permutations of size nx from Y
    t = 0
    for p in itertools.permutations(range(ny), nx):
        if all((rows[i] >> p[i]) & 1 for i in range(nx)):
            t += 1
    return t


def models_choice(nx, ny, rows):
    nbrs = [[x for x in range(nx) if (rows[x] >> y) & 1] for y in range(ny)]
    opts = [[None] + nb for nb in nbrs]
    full = (1 << nx) - 1
    c = 0
    for ch in itertools.product(*opts):
        hit = 0
        for x in ch:
            if x is not None:
                hit |= 1 << x
        if hit == full:
            c += 1
    return c


def models_bits(nv, cls):
    pos = []
    neg = []
    for c in cls:
        if all(l > 0 for l in c):
            m = 0
            for l in c:
                m |= 1 << (l - 1)
            pos.append(m)
        else:
            assert len(c) == 2 and c[0] < 0 and c[1] < 0
            neg.append((1 << (-c[0] - 1)) | (1 << (-c[1] - 1)))
    cnt = 0
    for s in range(1 << nv):
        ok = True
        for m in pos:
            if not s & m:
                ok = False
                break
        if ok:
            for m in neg:
                if s & m == m:
                    ok = False
                    break
        if ok:
            cnt += 1
    return cnt
