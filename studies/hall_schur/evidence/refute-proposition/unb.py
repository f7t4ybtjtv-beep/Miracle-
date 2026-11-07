import sys, itertools, math
sys.path.insert(0, '/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/refute-proposition')
from rcommon import *
from satlab.reference import brute_force

def ie(nx, ny, rows):
    t = 0
    for S in range(1 << nx):
        p = 1
        for y in range(ny):
            p *= 1 + sum(1 for x in range(nx) if (rows[x] >> y) & 1 and not (S >> x) & 1)
        t += (-1) ** bin(S).count('1') * p
    return t

def cond(nx, ny, rows):
    # exists X-saturating matching M and edge (x,y) with y uncovered by M
    for p in itertools.permutations(range(ny), nx):
        if all((rows[i] >> p[i]) & 1 for i in range(nx)):
            cov = set(p)
            if any((rows[x] >> y) & 1 and y not in cov for x in range(nx) for y in range(ny)):
                return True
    return False

smallest = None
for nx, ny in [(2,1),(3,1),(3,2),(4,1),(4,2),(4,3),(5,1),(5,2),(1,2),(1,3),(1,4),(2,3),(2,4),(3,4),(1,5),(2,5),(0,2),(2,0)]:
    tot = sat = strict = bad = 0
    for g in range(1 << (nx * ny)):
        rows = [(g >> (ny * x)) & ((1 << ny) - 1) for x in range(nx)]
        nv, cls, E = cnf(nx, ny, rows)
        bf = brute_force(nv, cls, count=True)[2]
        mc = models_choice(nx, ny, rows); xm = xsat_matchings(nx, ny, rows)
        if not (bf == mc == ie(nx, ny, rows)): bad += 1
        if bf < xm: bad += 1
        if (bf > 0) != (xm > 0): bad += 1
        if (bf > xm) != cond(nx, ny, rows): bad += 1
        if nx > ny and bf != 0: bad += 1
        tot += 1; sat += bf > 0; strict += bf > xm
        if bf > xm:
            key = (nx + ny, len(E))
            if smallest is None or key < smallest[0]: smallest = (key, nx, ny, E, bf, xm)
    print((nx, ny), 'graphs', tot, 'sat', sat, 'strict', strict, 'bad', bad, flush=True)
print('smallest', smallest)
for n in range(1, 6):
    rows = [(1 << (n + 1)) - 1] * n
    m = models_choice(n, n + 1, rows); x = xsat_matchings(n, n + 1, rows)
    print('K_{%d,%d}' % (n, n + 1), m, x, math.factorial(n + 1) * (n + 2) // 2, m == math.factorial(n+1)*(n+2)//2, x == math.factorial(n+1))
