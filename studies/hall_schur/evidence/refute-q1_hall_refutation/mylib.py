"""Independent implementation (refuter). Graphs as dict pigeon -> set(holes)."""
import itertools, random, subprocess, os, tempfile

DRAT = "/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/ext/drat-trim/drat-trim"
OUT = os.path.dirname(os.path.abspath(__file__))

def encode(adj, rng=None):
    """adj: dict x -> set of y. Returns (nv, clauses, var) with var[(x,y)]. Variable ids shuffled if rng."""
    edges = sorted((x, y) for x in adj for y in adj[x])
    if rng is not None:
        rng.shuffle(edges)
    var = {e: i + 1 for i, e in enumerate(edges)}
    cls = []
    for x in sorted(adj):
        cls.append([var[(x, y)] for y in sorted(adj[x])])
    holes = {}
    for x in adj:
        for y in adj[x]:
            holes.setdefault(y, []).append(x)
    for y in sorted(holes):
        xs = sorted(holes[y])
        for a, b in itertools.combinations(xs, 2):
            cls.append([-var[(a, y)], -var[(b, y)]])
    return len(edges), cls, var

def max_matching(adj):
    """Kuhn's augmenting-path algorithm. Returns dict pigeon->hole."""
    match_h = {}
    def aug(x, seen):
        for y in adj[x]:
            if y in seen: continue
            seen.add(y)
            if y not in match_h or aug(match_h[y], seen):
                match_h[y] = x
                return True
        return False
    for x in adj:
        aug(x, set())
    return {x: y for y, x in match_h.items()}

def explicit_drup(adj, P, T):
    """P: list of m+1 pigeons with N(P) subset T, |T|=m. Returns list of lemma clauses (lists of edge tuples, signs)."""
    m = len(T)
    assert len(P) == m + 1 and all(adj[p] <= set(T) for p in P)
    lemmas = []
    def D(j, H):  # pigeons P[0..j-1]
        return [(1, (P[i], h)) for i in range(j) for h in sorted(adj[P[i]]) if h not in H]
    done = False
    for j in range(1, m + 1):
        for H in itertools.combinations(sorted(T), j):
            Hs = set(H)
            d = D(j + 1, Hs)
            p = P[j]
            for h in H:
                if h in adj[p]:
                    lemmas.append(d + [(-1, (p, h))])
            lemmas.append(d)
            if not d:
                done = True
                break
        if done: break
    return lemmas

def lemmas_to_dimacs(lemmas, var):
    return [[s * var[e] for s, e in L] for L in lemmas]

def write_cnf(path, nv, cls):
    with open(path, "w") as f:
        f.write("p cnf %d %d\n" % (nv, len(cls)))
        for c in cls:
            f.write(" ".join(map(str, c)) + " 0\n")

def write_proof(path, lines):
    with open(path, "w") as f:
        for c in lines:
            f.write(" ".join(map(str, c)) + (" 0\n" if c else "0\n"))

def drat_check(nv, cls, proof, tag):
    d = os.path.join(OUT, "tmp"); os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, tag + ".cnf"); pp = os.path.join(d, tag + ".drup")
    write_cnf(cp, nv, cls); write_proof(pp, proof)
    r = subprocess.run([DRAT, cp, pp], capture_output=True, text=True, timeout=170)
    return "s VERIFIED" in r.stdout

def satlab_check(nv, cls, proof):
    from satlab import checker
    text = "\n".join(" ".join(map(str, c)) + (" 0" if c else "0") for c in proof)
    return checker.check_proof(nv, cls, checker._parse_proof(text))

def naive_rup_check(cls, proof):
    """Very naive RUP checker (fixpoint over all clauses). Small instances only."""
    db = [list(c) for c in cls]
    for L in proof:
        assign = {}
        for l in L:
            assign[abs(l)] = (l < 0)  # negation: literal l false
        conflict = False
        changed = True
        while changed and not conflict:
            changed = False
            for c in db:
                unassigned = []; sat = False
                for l in c:
                    v = assign.get(abs(l))
                    if v is None: unassigned.append(l)
                    elif v == (l > 0): sat = True; break
                if sat: continue
                if not unassigned: conflict = True; break
                if len(unassigned) == 1:
                    l = unassigned[0]; assign[abs(l)] = (l > 0); changed = True
        if not conflict:
            return False, L
        db.append(list(L))
        if not L:
            return True, None
    return False, "no empty clause"

def planted(n, k, p_in, q, rng, slack=2):
    """n pigeons, holes: (k-1) witness holes + (n-k+slack) others. S gets edges only into T."""
    X = list(range(n)); rng.shuffle(X)
    S = X[:k]; R = X[k:]
    nh = (k - 1) + (n - k + slack)
    Y = list(range(nh)); rng.shuffle(Y)
    T = Y[:k - 1]; U = Y[k - 1:]
    adj = {x: set() for x in range(n)}
    while True:
        for x in S:
            adj[x] = {y for y in T if rng.random() < p_in}
        if all(adj[x] for x in S) and set().union(*(adj[x] for x in S)) == set(T):
            break
    Um = U[:]; rng.shuffle(Um)
    for x, y in zip(R, Um):
        adj[x].add(y)
    for x in R:
        for y in Y:
            if rng.random() < q:
                adj[x].add(y)
    return adj, S, T

def resolution_proof(adj, P, T):
    """Genuine resolution refutation following the hand proof. Each step checked to be an exact resolvent.
    Returns number of resolution steps; raises on failure."""
    m = len(T)
    def lit(s, x, h): return (s, (x, h))
    axioms = set()
    for x in adj:
        axioms.add(frozenset(lit(1, x, h) for h in adj[x]))
    holes = {}
    for x in adj:
        for y in adj[x]: holes.setdefault(y, []).append(x)
    for y, xs in holes.items():
        for a, b in itertools.combinations(sorted(xs), 2):
            axioms.add(frozenset([lit(-1, a, y), lit(-1, b, y)]))
    known = set(axioms)
    steps = [0]
    def resolve(C1, C2, piv):  # piv = edge; C1 has +piv, C2 has -piv
        assert C1 in known and C2 in known, "premise unknown"
        assert (1, piv) in C1 and (-1, piv) in C2
        R = (C1 - {(1, piv)}) | (C2 - {(-1, piv)})
        # no tautology check needed for correctness of soundness, but check anyway
        for s, e in R: assert (-s, e) not in R, "tautology"
        known.add(frozenset(R)); steps[0] += 1
        return frozenset(R)
    def Dset(j, H):
        return frozenset(lit(1, P[i], h) for i in range(j) for h in adj[P[i]] if h not in H)
    Dc = {frozenset(): frozenset(lit(1, P[0], h) for h in adj[P[0]])}  # subclause of D(1,{})
    assert Dc[frozenset()] in known
    for j in range(1, m + 1):
        newD = {}
        for H in itertools.combinations(sorted(T), j):
            Hs = frozenset(H); p = P[j]
            target = Dset(j + 1, Hs)
            Fh = {}
            result = None
            for h in H:
                if h not in adj[p]: continue
                C = Dc[Hs - {h}]
                for i in range(j):
                    if (1, (P[i], h)) in C:
                        hc = frozenset([lit(-1, P[i], h), lit(-1, p, h)])
                        C = resolve(C, hc, (P[i], h))
                Fh[h] = C
                if (-1, (p, h)) not in C:
                    assert C <= target
                    result = C  # already subsumes D(j+1,H)
            if result is None:
                C = frozenset(lit(1, p, h) for h in adj[p])
                for h in H:
                    if h in adj[p]:
                        C = resolve(C, Fh[h], (p, h))
                result = C
            assert result <= target, (j, H)
            newD[Hs] = result
            if not result:
                return steps[0], True
        Dc = newD
    return steps[0], (frozenset() in known)
