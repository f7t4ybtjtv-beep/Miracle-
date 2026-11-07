"""Q3: weak-PHP model counts vs X-saturating matchings.

Counters used (independent of each other):
  A. satlab.reference.brute_force(count=True) on the weak CNF (<=24 vars).
  B. own_models(): direct recursive enumeration of tuples of pairwise disjoint
     nonempty hole sets S_x subset N(x) (no CNF involved).
  C. own_matchings(): recursive count of X-saturating matchings.
Closed forms are compared against these.
"""
import itertools, math, sys, time
from fractions import Fraction
from satlab.reference import brute_force

def weak_cnf(n, m, E):
    """E: set of (x,y), x in range(n), y in range(m). Returns nv, clauses, varmap."""
    edges = sorted(E)
    var = {e: i + 1 for i, e in enumerate(edges)}
    cls = []
    for x in range(n):
        cls.append([var[(x, y)] for y in range(m) if (x, y) in var])
    for y in range(m):
        nb = [x for x in range(n) if (x, y) in var]
        for a, b in itertools.combinations(nb, 2):
            cls.append([-var[(a, y)], -var[(b, y)]])
    return len(edges), cls

def own_models(n, m, E):
    nbr = [[y for y in range(m) if (x, y) in E] for x in range(n)]
    def rec(x, used):
        if x == n:
            return 1
        avail = [y for y in nbr[x] if not used >> y & 1]
        tot = 0
        for r in range(1, len(avail) + 1):
            for S in itertools.combinations(avail, r):
                mask = used
                for y in S:
                    mask |= 1 << y
                tot += rec(x + 1, mask)
        return tot
    return rec(0, 0)

def own_matchings(n, m, E):
    nbr = [[y for y in range(m) if (x, y) in E] for x in range(n)]
    def rec(x, used):
        if x == n:
            return 1
        return sum(rec(x + 1, used | 1 << y) for y in nbr[x] if not used >> y & 1)
    return rec(0, 0)

def excess(n, m, E):
    return len({y for (_, y) in E}) - n   # k = |N(X)| - |X|

def stirling2(a, b):
    S = [[0] * (b + 1) for _ in range(a + 1)]
    S[0][0] = 1
    for i in range(1, a + 1):
        for j in range(1, min(i, b) + 1):
            S[i][j] = j * S[i - 1][j] + S[i - 1][j - 1]
    return S[a][b]

def complete_models_formula(n, m):
    return sum((-1) ** j * math.comb(n, j) * (n + 1 - j) ** m for j in range(n + 1))

def complete_models_dp(n, m):
    # functions [m] -> {0..n} hitting all of 1..n; DP on number of pigeons hit.
    dp = [0] * (n + 1); dp[0] = 1
    for _ in range(m):
        nd = [0] * (n + 1)
        for h, c in enumerate(dp):
            if not c: continue
            nd[h] += c * (1 + h)          # unused or an already-hit pigeon
            if h < n: nd[h + 1] += c * (n - h)  # a new pigeon
        dp = nd
    return dp[n]

def disjoint_union(blocks):
    """blocks: list of (n_i, m_i, E_i). Returns (n, m, E)."""
    E, ox, oy = set(), 0, 0
    for n, m, Eb in blocks:
        E |= {(x + ox, y + oy) for (x, y) in Eb}
        ox += n; oy += m
    return ox, oy, E

def Knm(n, m):
    return {(x, y) for x in range(n) for y in range(m)}

BF_MAX = 20
def check(n, m, E, use_bf=True):
    nv, cls = weak_cnf(n, m, E)
    b = own_models(n, m, E)
    a = None
    if use_bf and nv <= BF_MAX:
        _, _, a = brute_force(nv, cls, count=True)
        assert a == b, (n, m, a, b)
    return nv, a, b, own_matchings(n, m, E)

def main():
    secs = sys.argv[1] if len(sys.argv) > 1 else 'adc'
    t0 = time.time()
    if 'a' in secs: sec_a()
    if 'd' in secs: sec_d()
    if 'c' in secs: sec_c()
    print(f'time {time.time()-t0:.1f}s')

def sec_a():
    print("== (a) n disjoint K_{1,2}: expect models 3^n, matchings 2^n ==")
    for n in range(1, 13):
        N, M, E = disjoint_union([(1, 2, Knm(1, 2))] * n)
        nv, a, b, mt = check(N, M, E, use_bf=(n <= 12))
        assert b == 3 ** n and mt == 2 ** n
        print(f"n={n:2d} vars={nv:2d} bf={a} own={b} 3^n={3**n} match={mt} ratio={Fraction(b,mt)} k={excess(N,M,E)}")

def sec_d():
    print("== (d) n disjoint K_{1,d}: expect (2^d-1)^n vs d^n ==")
    for d in range(1, 7):
        for n in range(1, 7):
            if (2 ** d - 1) ** n > 5_000_000: continue
            N, M, E = disjoint_union([(1, d, Knm(1, d))] * n)
            nv, a, b, mt = check(N, M, E)
            assert b == (2 ** d - 1) ** n and mt == d ** n
            print(f"d={d} n={n} vars={nv:2d} bf={a} own={b} match={mt} ratio={float(b/mt):.4f} closed=((2^d-1)/d)^n={((2**d-1)/d)**n:.4f}")

    print("== (d) multiplicativity on mixed disjoint unions ==")
    comps = [(1, 2, Knm(1, 2)), (2, 3, Knm(2, 3)), (2, 2, {(0, 0), (0, 1), (1, 1)}), (1, 3, Knm(1, 3)), (2, 4, {(0,0),(0,1),(1,1),(1,2),(1,3)})]
    for r in range(1, 4):
        for combo in itertools.combinations(range(len(comps)), r):
            blocks = [comps[i] for i in combo]
            N, M, E = disjoint_union(blocks)
            nv, a, b, mt = check(N, M, E)
            pb = math.prod(own_models(*c) for c in blocks)
            pm = math.prod(own_matchings(*c) for c in blocks)
            assert b == pb and mt == pm
            print(f"blocks={combo} vars={nv} bf={a} own={b} prod={pb} match={mt} prodmatch={pm}")

def sec_c():
    print("== (2) complete K_{n,m}: formula vs brute force / own / DP / n!S(m+1,n+1) ==")
    for n in range(1, 7):
        for m in range(n, 13):
            f = complete_models_formula(n, m)
            dp = complete_models_dp(n, m)
            st = math.factorial(n) * stirling2(m + 1, n + 1)
            assert f == dp == st
            if n * m <= BF_MAX:
                nv, a, b, mt = check(n, m, Knm(n, m))
                assert f == b == a, (n, m)
                assert mt == math.perm(m, n)
                print(f"K_{n},{m}: vars={nv} bf={a} own={b} formula={f} match={mt}=m!/(m-n)! ratio={float(f/mt):.6g}")
            elif f <= 5_000_000:
                b = own_models(n, m, Knm(n, m)); mt = own_matchings(n, m, Knm(n, m))
                assert f == b and mt == math.perm(m, n)
                print(f"K_{n},{m}: own={b} formula={f} match={mt} ratio={float(f/mt):.6g} (no bf, vars={n*m})")
    print("formula == DP == n!S(m+1,n+1) for all 1<=n<=6, n<=m<=12: OK")
    for n in range(1, 60):
        for m in range(n, 80):
            assert complete_models_formula(n, m) == complete_models_dp(n, m) == math.factorial(n) * stirling2(m + 1, n + 1)
    print("formula == DP == n!S(m+1,n+1) for all 1<=n<60, n<=m<80: OK")

    print("== (b) K_{n,n+1}: conjecture ratio = (n+2)/2 ==")
    for n in range(1, 41):
        f = complete_models_formula(n, n + 1); mt = math.perm(n + 1, n)
        assert Fraction(f, mt) == Fraction(n + 2, 2)
        assert f == math.factorial(n) * math.comb(n + 2, 2)
        if n <= 6 or n % 10 == 0:
            print(f"n={n} models={f} match={mt} ratio={Fraction(f, mt)}")
    print("K_{n,n+1}: models = n!*C(n+2,2), ratio = (n+2)/2 exactly for n=1..40 (formula); bf-verified for n<=4 above")

    print("== (c) K_{n,2n}: ratio, lower bound ((n+1)/4)^n, and log(ratio)/(n ln n) ==")
    for n in list(range(1, 13)) + [20, 40, 80, 160, 320]:
        f = complete_models_formula(n, 2 * n); mt = math.perm(2 * n, n)
        r = Fraction(f, mt)
        lb = math.factorial(n) * (n + 1) ** n
        assert f >= lb
        lr = math.log(f) - math.log(mt)
        assert Fraction(f, mt) >= Fraction((n + 1) ** n, 4 ** n)
        print(f"n={n:3d} log(ratio)={lr:.4f} ratio^(1/n)={math.exp(lr/n):.4f} ((n+1)/4)={((n+1)/4):.4f} "
              f"log(ratio)/(n ln n)={(lr/(n*math.log(n)) if n>1 else float('nan')):.4f}")

    print("== (2) fixed n, m->inf: ratio^(1/m) -> n+1 ? ==")
    for n in (1, 2, 3):
        for m in (10, 50, 200, 800):
            f = complete_models_formula(n, m); mt = math.perm(m, n)
            print(f"n={n} m={m} ratio^(1/m)={math.exp((math.log(f)-math.log(mt))/m):.5f}")

if __name__ == "__main__":
    main()
