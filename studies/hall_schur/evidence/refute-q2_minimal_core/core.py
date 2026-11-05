"""Independent re-implementation (refuter). Graph = tuple of hole bitmasks, one per pigeon.
Clauses are symbolic: ('P', x) or ('H', y, x1, x2) with x1<x2.
SAT oracle A ("choice"): a set of clauses is SAT iff there is a choice f(x) in N(x) for each pigeon x whose
pigeon clause is present, such that no present hole clause ('H',y,x1,x2) has f(x1)=f(x2)=y.
 (Justification: any model can be reduced to one true edge per such pigeon, other vars 0; hole clauses
  are all-negative so reducing true vars never breaks them; pigeon clauses of absent pigeons need nothing.)
SAT oracle B ("generic"): plain DIMACS-style CNF + own tiny DPLL with unit propagation, used as a cross-check.
"""
import itertools

def popc(v):
    return bin(v).count("1")

def nbrs(adj, S):
    m = 0
    for x in S:
        m |= adj[x]
    return m

def holes_of(mask):
    out = []
    y = 0
    while mask >> y:
        if mask >> y & 1:
            out.append(y)
        y += 1
    return out

def full_clauses(adj, nY):
    cl = [('P', x) for x in range(len(adj))]
    for y in range(nY):
        xs = [x for x in range(len(adj)) if adj[x] >> y & 1]
        for a, b in itertools.combinations(xs, 2):
            cl.append(('H', y, a, b))
    return cl

def induced_clauses(adj, S):
    S = sorted(S)
    cl = [('P', x) for x in S]
    ys = holes_of(nbrs(adj, S))
    for y in ys:
        xs = [x for x in S if adj[x] >> y & 1]
        for a, b in itertools.combinations(xs, 2):
            cl.append(('H', y, a, b))
    return cl

def sat_choice(adj, clauses):
    """Oracle A: backtracking over choice functions."""
    pig = sorted({c[1] for c in clauses if c[0] == 'P'})
    conf = {}
    for c in clauses:
        if c[0] == 'H':
            _, y, a, b = c
            conf.setdefault((a, y), set()).add(b)
            conf.setdefault((b, y), set()).add(a)
    # order pigeons by degree
    pig.sort(key=lambda x: popc(adj[x]))
    occ = {}  # y -> set of pigeons placed at y
    def rec(i):
        if i == len(pig):
            return True
        x = pig[i]
        for y in holes_of(adj[x]):
            bad = conf.get((x, y), ())
            here = occ.get(y, ())
            if any(z in bad for z in here):
                continue
            occ.setdefault(y, set()).add(x)
            if rec(i + 1):
                return True
            occ[y].discard(x)
        return False
    return rec(0)

# ---- Oracle B: generic CNF ----
def to_cnf(adj, clauses):
    var = {}
    for x in range(len(adj)):
        for y in holes_of(adj[x]):
            var[(x, y)] = len(var) + 1
    cnf = []
    for c in clauses:
        if c[0] == 'P':
            cnf.append([var[(c[1], y)] for y in holes_of(adj[c[1]])])
        else:
            _, y, a, b = c
            cnf.append([-var[(a, y)], -var[(b, y)]])
    return len(var), cnf

def dpll(nv, cnf):
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
    def rec(cls):
        while True:
            unit = next((c[0] for c in cls if len(c) == 1), None)
            if unit is None:
                break
            cls = simplify(cls, unit)
            if cls is None:
                return False
        if not cls:
            return True
        lit = cls[0][0]
        for l in (lit, -lit):
            r = simplify(cls, l)
            if r is not None and rec(r):
                return True
        return False
    if any(len(c) == 0 for c in cnf):
        return False
    return rec([list(c) for c in cnf])

def sat_generic(adj, clauses):
    nv, cnf = to_cnf(adj, clauses)
    return dpll(nv, cnf)

def is_mus(adj, clauses, sat=sat_choice):
    if sat(adj, clauses):
        return False
    for i in range(len(clauses)):
        if not sat(adj, clauses[:i] + clauses[i + 1:]):
            return False
    return True

def redundant_clauses(adj, clauses, sat=sat_choice):
    return [c for i, c in enumerate(clauses) if not sat(adj, clauses[:i] + clauses[i + 1:])]

def minimal_witnesses(adj):
    """All inclusion-minimal S with |N(S)|<|S|, by checking ALL proper subsets."""
    n = len(adj)
    wit = [m for m in range(1 << n)
           if popc(nbrs(adj, [x for x in range(n) if m >> x & 1])) < popc(m)]
    ws = set(wit)
    out = []
    for m in wit:
        # any proper nonempty submask a witness?
        sub = (m - 1) & m
        ok = True
        while sub:
            if sub in ws:
                ok = False
                break
            sub = (sub - 1) & m
        if ok:
            out.append([x for x in range(n) if m >> x & 1])
    return out

def has_matching(adj, pigeons, allowed):
    """Kuhn's augmenting paths: match all pigeons into holes in bitmask allowed."""
    match = {}
    def aug(x, seen):
        for y in holes_of(adj[x] & allowed):
            if y in seen:
                continue
            seen.add(y)
            if y not in match or aug(match[y], seen):
                match[y] = x
                return True
        return False
    return all(aug(x, set()) for x in pigeons)

def canon(adj, nY):
    best = None
    for perm in itertools.permutations(range(nY)):
        t = tuple(sorted(sum(1 << perm[y] for y in holes_of(a)) for a in adj))
        if best is None or t < best:
            best = t
    return best
