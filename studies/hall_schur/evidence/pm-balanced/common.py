"""Shared helpers: encoding, independent permanent (Ryser + subset DP), generic #DPLL counter,
inclusion-exclusion formula for unbalanced model count, brute-force matching enumeration."""
import itertools

def encode(nx, ny, adj):
    """adj: set of (x,y). Returns (nv, clauses, var) with var[(x,y)] -> 1-based id.
    Edges ordered lexicographically."""
    edges = sorted(adj)
    var = {e: i + 1 for i, e in enumerate(edges)}
    clauses = []
    for x in range(nx):
        clauses.append([var[(x, y)] for y in range(ny) if (x, y) in adj])  # may be empty
    for y in range(ny):
        nb = [x for x in range(nx) if (x, y) in adj]
        for i in range(len(nb)):
            for j in range(i + 1, len(nb)):
                clauses.append([-var[(nb[i], y)], -var[(nb[j], y)]])
    return len(edges), clauses, var

def adj_from_mask(n, m, mask):
    return {(x, y) for x in range(n) for y in range(m) if (mask >> (x * m + y)) & 1}

def perm_dp(n, adj):
    """Permanent via DP over subsets of Y: f[S] = #ways to match x_0..x_{|S|-1} onto S."""
    f = [0] * (1 << n)
    f[0] = 1
    for S in range(1 << n):
        if f[S] == 0:
            continue
        x = bin(S).count("1")
        if x >= n:
            continue
        for y in range(n):
            if not (S >> y) & 1 and (x, y) in adj:
                f[S | (1 << y)] += f[S]
    return f[(1 << n) - 1]

def perm_ryser(n, adj):
    """Ryser: perm(A) = (-1)^n sum_{S subset cols} (-1)^{|S|} prod_i sum_{j in S} a_ij."""
    tot = 0
    for S in range(1, 1 << n):
        p = 1
        for i in range(n):
            r = sum(1 for j in range(n) if (S >> j) & 1 and (i, j) in adj)
            p *= r
            if p == 0:
                break
        tot += (-1) ** bin(S).count("1") * p
    return (-1) ** n * tot

def count_xsat_matchings(nx, ny, adj):
    """Count X-saturating matchings by direct recursion (injective choice of y per x)."""
    def rec(x, used):
        if x == nx:
            return 1
        return sum(rec(x + 1, used | (1 << y)) for y in range(ny)
                   if (x, y) in adj and not (used >> y) & 1)
    return rec(0, 0)

def ie_model_count(nx, ny, adj):
    """Models = partial maps f: Y -> X with f(y) in N(y), image = X (surjective).
    Inclusion-exclusion over S subset X missed: sum_S (-1)^|S| prod_y (1 + |N(y) \\ S|)."""
    tot = 0
    for S in range(1 << nx):
        p = 1
        for y in range(ny):
            p *= 1 + sum(1 for x in range(nx) if (x, y) in adj and not (S >> x) & 1)
        tot += (-1) ** bin(S).count("1") * p
    return tot

def dpll_count(nv, clauses):
    """Generic exact #SAT by DPLL branching with unit propagation; free vars counted 2^k.
    Knows nothing about matchings."""
    def rec(cls, assigned_count):
        # unit propagation
        cls = [list(c) for c in cls]
        assigned = set()
        while True:
            if any(len(c) == 0 for c in cls):
                return 0
            unit = next((c[0] for c in cls if len(c) == 1), None)
            if unit is None:
                break
            assigned.add(abs(unit))
            new = []
            for c in cls:
                if unit in c:
                    continue
                new.append([l for l in c if l != -unit])
            cls = new
        k = assigned_count + len(assigned)
        if not cls:
            return 1 << (nv - k)
        v = abs(cls[0][0])
        tot = 0
        for lit in (v, -v):
            new = []
            for c in cls:
                if lit in c:
                    continue
                new.append([l for l in c if l != -lit])
            tot += rec(new, k + 1)
        return tot
    # NOTE: variables assigned along a branch are tracked by count; correct because each var
    # is assigned at most once per branch (propagated/branched vars vanish from clauses).
    return rec(clauses, 0)
