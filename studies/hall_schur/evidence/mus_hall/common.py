"""Shared helpers: weak-PHP encoding on a bipartite graph, exhaustive SAT
oracles over clause subsets, MUS enumeration, Hall-witness utilities.

Graph representation: adj = tuple of ints, adj[x] = bitmask of neighbours of
pigeon x among holes 0..nY-1.
"""
import itertools
import numpy as np


def popcount(v):
    return bin(v).count("1")


def bits(v):
    out, i = [], 0
    while v:
        if v & 1:
            out.append(i)
        v >>= 1
        i += 1
    return out


def encode(nX, nY, adj):
    """Return (nv, clauses, meta, var).

    clauses: list of int lists (DIMACS lits).  meta[i] = ('P', x) or
    ('H', y, x1, x2).  var[(x, y)] = DIMACS var.
    """
    var = {}
    for x in range(nX):
        for y in range(nY):
            if adj[x] >> y & 1:
                var[(x, y)] = len(var) + 1
    clauses, meta = [], []
    for x in range(nX):
        clauses.append([var[(x, y)] for y in range(nY) if adj[x] >> y & 1])
        meta.append(('P', x))
    for y in range(nY):
        nb = [x for x in range(nX) if adj[x] >> y & 1]
        for x1, x2 in itertools.combinations(nb, 2):
            clauses.append([-var[(x1, y)], -var[(x2, y)]])
            meta.append(('H', y, x1, x2))
    return len(var), clauses, meta, var


def sat_masks(nv, clauses):
    """For every assignment, bitmask of satisfied clauses; return the set of
    inclusion-maximal such masks (= the MSSes).  Exhaustive over 2^nv."""
    m = len(clauses)
    assert m <= 63
    A = np.arange(1 << nv, dtype=np.int64)
    acc = np.zeros(1 << nv, dtype=np.int64)
    for i, c in enumerate(clauses):
        s = np.zeros(1 << nv, dtype=bool)
        for l in c:
            b = (A >> (abs(l) - 1)) & 1
            s |= (b == 1) if l > 0 else (b == 0)
        acc |= s.astype(np.int64) << i
    uniq = sorted(set(int(v) for v in np.unique(acc)), key=popcount, reverse=True)
    mss = []
    for u in uniq:
        if not any(u & ~k == 0 for k in mss):
            mss.append(u)
    return mss


def is_sat(mask, mss):
    return any(mask & ~k == 0 for k in mss)


def is_mus(mask, mss):
    if is_sat(mask, mss):
        return False
    return all(is_sat(mask & ~(1 << b), mss) for b in bits(mask))


def minimal_hitting_sets(sets):
    """Berge's algorithm; sets = list of bitmasks (non-empty)."""
    hs = [0]
    for C in sorted(sets, key=popcount):
        new = set()
        for h in hs:
            if h & C:
                new.add(h)
            else:
                for b in bits(C):
                    new.add(h | (1 << b))
        new = sorted(new, key=popcount)
        kept = []
        for h in new:
            if not any(k & ~h == 0 for k in kept):
                kept.append(h)
        hs = kept
    return hs


def all_muses_duality(m, mss):
    """MUSes = minimal hitting sets of the MCSes (complements of MSSes)."""
    full = (1 << m) - 1
    if full in mss:
        return []
    mcs = [full & ~k for k in mss]
    return sorted(minimal_hitting_sets(mcs))


def all_muses_exhaustive(m, mss):
    """Independent check: evaluate SAT for all 2^m clause subsets via downward
    closure of the MSSes, then MUS = UNSAT subset whose every one-clause
    removal is SAT."""
    N = 1 << m
    sat = np.zeros(N, dtype=bool)
    sat[np.array(mss, dtype=np.int64)] = True
    for b in range(m):
        r = sat.reshape(-1, 2, 1 << b)
        r[:, 0, :] |= r[:, 1, :]
    ismus = ~sat
    for b in range(m):
        r = ismus.reshape(-1, 2, 1 << b)
        s = sat.reshape(-1, 2, 1 << b)
        r[:, 1, :] &= s[:, 0, :]
    return sorted(int(v) for v in np.nonzero(ismus)[0])


def nbhd(adj, S):
    n = 0
    for x in S:
        n |= adj[x]
    return n


def hall_violators(nX, adj):
    out = []
    for r in range(1, nX + 1):
        for S in itertools.combinations(range(nX), r):
            if popcount(nbhd(adj, S)) < len(S):
                out.append(frozenset(S))
    return out


def minimal_hall_witnesses(nX, adj):
    V = hall_violators(nX, adj)
    return [S for S in V if not any(T < S for T in V)]


def has_saturating_matching(P, adj, forbidden_holes=0):
    """Is there a matching saturating pigeon list P using holes not in
    forbidden_holes? (augmenting paths)"""
    match = {}

    def aug(x, seen):
        for y in bits(adj[x] & ~forbidden_holes):
            if y in seen:
                continue
            seen.add(y)
            if y not in match or aug(match[y], seen):
                match[y] = x
                return True
        return False

    return all(aug(x, set()) for x in P)


def induced_mask(meta, S):
    mask = 0
    for i, md in enumerate(meta):
        if md[0] == 'P' and md[1] in S:
            mask |= 1 << i
        elif md[0] == 'H' and md[2] in S and md[3] in S:
            mask |= 1 << i
    return mask


def criterion_induced_is_mus(adj, S):
    """Claimed characterisation: induced CNF of minimal witness S is an MUS
    iff for every hole y in N(S) and pair x1<x2 in N(y)∩S, S\\{x1,x2} has a
    matching into N(S)\\{y}."""
    NS = nbhd(adj, S)
    for y in bits(NS):
        nb = sorted(x for x in S if adj[x] >> y & 1)
        for x1, x2 in itertools.combinations(nb, 2):
            rest = [x for x in S if x not in (x1, x2)]
            if not has_saturating_matching(rest, adj, 1 << y):
                return False
    return True


def hole_clause_necessary_criterion(adj, S, y, x1, x2):
    rest = [x for x in S if x not in (x1, x2)]
    return has_saturating_matching(rest, adj, 1 << y)


def canonical(nX, nY, adj):
    best = None
    for p in itertools.permutations(range(nY)):
        rows = []
        for r in adj:
            v = 0
            for y in range(nY):
                if r >> y & 1:
                    v |= 1 << p[y]
            rows.append(v)
        t = tuple(sorted(rows))
        if best is None or t < best:
            best = t
    return best


def all_graph_classes(nX, nY):
    seen = {}
    for adj in itertools.product(range(1 << nY), repeat=nX):
        c = canonical(nX, nY, adj)
        seen[c] = seen.get(c, 0) + 1
    return seen  # canonical adj -> number of labelled graphs in class
