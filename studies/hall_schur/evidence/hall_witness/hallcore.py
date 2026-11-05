"""Shared helpers: G-PHP encoding, Hall witness finding, explicit DRUP proof generator.

Encoding (as specified): one var per edge (x,y); pigeon clause OR_{y in N(x)} e(x,y);
hole clause (-e(x1,y) | -e(x2,y)) for every y and pair x1<x2 of neighbours of y.
"""
import itertools
import os
import random
import subprocess

DRAT = "/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/ext/drat-trim/drat-trim"


def encode(nX, nY, adj):
    """adj: dict x -> set of y. Returns (nv, clauses, var) with var[(x,y)] -> id."""
    var = {}
    for x in range(nX):
        for y in sorted(adj[x]):
            var[(x, y)] = len(var) + 1
    clauses = []
    for x in range(nX):
        clauses.append([var[(x, y)] for y in sorted(adj[x])])
    for y in range(nY):
        nb = [x for x in range(nX) if y in adj[x]]
        for x1, x2 in itertools.combinations(nb, 2):
            clauses.append([-var[(x1, y)], -var[(x2, y)]])
    return len(var), clauses, var


def sub_cnf(adj, S, var):
    """Clauses of the encoding restricted to pigeons S and holes N(S), in global var ids."""
    S = sorted(S)
    T = set().union(*(adj[x] for x in S)) if S else set()
    cl = [[var[(x, y)] for y in sorted(adj[x])] for x in S]
    for y in sorted(T):
        nb = [x for x in S if y in adj[x]]
        for x1, x2 in itertools.combinations(nb, 2):
            cl.append([-var[(x1, y)], -var[(x2, y)]])
    return cl, T


# ---------------- matching / Hall witness ----------------
def max_matching(pigeons, adj):
    """Kuhn augmenting paths. Returns dict x->y for matched pigeons in `pigeons`."""
    match_y = {}

    def aug(x, seen):
        for y in sorted(adj[x]):
            if y in seen:
                continue
            seen.add(y)
            if y not in match_y or aug(match_y[y], seen):
                match_y[y] = x
                return True
        return False

    for x in pigeons:
        aug(x, set())
    return {x: y for y, x in match_y.items()}


def witness_in(pigeons, adj):
    """Return a Hall violator S within `pigeons` (|N(S)| = |S|-1), or None if matchable."""
    m = max_matching(pigeons, adj)
    free = [x for x in pigeons if x not in m]
    if not free:
        return None
    match_y = {y: x for x, y in m.items()}
    u = free[0]
    S, seenY, stack = {u}, set(), [u]
    while stack:
        x = stack.pop()
        for y in adj[x]:
            if y not in seenY:
                seenY.add(y)
                x2 = match_y[y]  # every reached y is matched (else augmenting path)
                if x2 not in S:
                    S.add(x2)
                    stack.append(x2)
    assert len(seenY) == len(S) - 1
    return S


def minimal_witness(nX, adj):
    """Inclusion-minimal Hall violator (critical: |N(S)| = |S|-1), or None."""
    S = witness_in(list(range(nX)), adj)
    if S is None:
        return None
    changed = True
    while changed:
        changed = False
        for x in sorted(S):
            W = sorted(S - {x})
            S2 = witness_in(W, adj)
            if S2 is not None:
                S = S2
                changed = True
                break
    return S


# ---------------- explicit proof ----------------
def explicit_proof(adj, P, var, delete=True):
    """DRUP proof from pigeons P (ordered list, |P| = |T|+1) and holes T = N(P).

    Level j (1..|T|+1), H subset of T with |H| = j-1:
      D(j,H) = OR_{i<j-th} OR_{h in N(p_i) \\ H} e(p_i,h)  ("p_1..p_j not all inside H").
    D(1,{}) is the pigeon clause of p_1 (input).  For level j+1 and each H (|H|=j):
      E(j+1,H,h) = D(j+1,H) | -e(p_{j+1},h)   for h in H with an edge (p_{j+1},h)
      D(j+1,H)
    D(|T|+1, T) is the empty clause.  Returns list of (is_delete, lits).
    """
    T = sorted(set().union(*(adj[p] for p in P)))
    m = len(T)
    assert len(P) == m + 1, (len(P), m)

    def D(j, H):
        return [var[(P[i], h)] for i in range(j) for h in sorted(adj[P[i]]) if h not in H]

    steps = []
    prev = []  # D clauses of the previous level (not inputs)
    for j in range(1, m + 1):
        p = P[j]
        cur, Es = [], []
        for Hc in itertools.combinations(T, j):
            H = set(Hc)
            d = D(j + 1, H)
            for h in Hc:
                if h in adj[p]:
                    e = d + [-var[(p, h)]]
                    steps.append((False, e))
                    Es.append(e)
            steps.append((False, d))
            cur.append(d)
            if not d:
                return steps
        if delete:
            for c in prev + Es:
                steps.append((True, c))
        prev = cur
    raise AssertionError("did not reach empty clause")


def proof_text(steps):
    return "".join(("d " if d else "") + " ".join(map(str, l)) + (" 0\n" if l else "0\n")
                   for d, l in steps)


def cnf_text(nv, clauses):
    return "p cnf %d %d\n" % (nv, len(clauses)) + "".join(" ".join(map(str, c)) + " 0\n" for c in clauses)


def drat_check(nv, clauses, steps, workdir, tag):
    os.makedirs(workdir, exist_ok=True)
    f = os.path.join(workdir, tag + ".cnf")
    p = os.path.join(workdir, tag + ".drup")
    with open(f, "w") as fh:
        fh.write(cnf_text(nv, clauses))
    with open(p, "w") as fh:
        fh.write(proof_text(steps))
    r = subprocess.run([DRAT, f, p, "-t", "200"], capture_output=True, text=True, timeout=300)
    ok = "s VERIFIED" in r.stdout
    os.remove(f)
    os.remove(p)
    return ok


# ---------------- planted graphs ----------------
def planted_graph(n, k, rng, p_in=1.0, p_rest=0.5, p_cross=0.5, extra_holes=2):
    """Pigeons 0..n-1, S = {0..k-1}; holes T = {0..k-2}; rest holes k-1 .. k-2+(n-k+extra).

    S -> T with prob p_in (every pigeon of S keeps >=1 edge), no edges S -> Y\\T.
    X\\S -> Y\\T with prob p_rest, then a planted perfect matching of X\\S into Y\\T is added.
    X\\S -> T with prob p_cross.
    """
    T = list(range(k - 1))
    R = list(range(k - 1, k - 1 + (n - k) + extra_holes))
    nY = len(T) + len(R)
    adj = {x: set() for x in range(n)}
    for x in range(k):
        for y in T:
            if rng.random() < p_in:
                adj[x].add(y)
        if not adj[x]:
            adj[x].add(rng.choice(T))
    perm = R[:]
    rng.shuffle(perm)
    for idx, x in enumerate(range(k, n)):
        adj[x].add(perm[idx])
        for y in R:
            if rng.random() < p_rest:
                adj[x].add(y)
        for y in T:
            if rng.random() < p_cross:
                adj[x].add(y)
    return nY, adj, set(range(k)), set(T), R
