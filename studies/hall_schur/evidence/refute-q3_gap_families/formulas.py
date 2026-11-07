import sys, random, math
from math import comb, factorial, log
from fractions import Fraction as F
sys.path.insert(0, '.')
from exh import counts
from satlab.reference import brute_force

def cnf(n, m, adj):
    var = {}
    for x in range(n):
        for y in range(m):
            if adj[y]>>x & 1: var[(x,y)] = len(var)+1
    cl = []
    for x in range(n):
        cl.append([var[(x,y)] for y in range(m) if (x,y) in var])
    for y in range(m):
        nb = [x for x in range(n) if (x,y) in var]
        for i in range(len(nb)):
            for j in range(i+1, len(nb)):
                cl.append([-var[(nb[i],y)], -var[(nb[j],y)]])
    return len(var), cl

# 1) brute_force vs DP on all graphs of shapes with nm<=9, and random graphs up to 20 vars
cnt = 0
for n,m in [(1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),(2,2),(2,3),(2,4),(3,3),(3,2),(4,2)]:
    for g in range(1<<(n*m)):
        adj = [(g >> (y*n)) & ((1<<n)-1) for y in range(m)]
        nv, cl = cnf(n,m,adj)
        mo,_ = counts(n,m,adj)
        if nv == 0:
            continue
        bf = brute_force(nv, cl, count=True)[2]
        assert bf == mo, (n,m,g,bf,mo); cnt += 1
rng = random.Random(7)
for _ in range(150):
    n = rng.randint(2,5); m = rng.randint(n, 8)
    while True:
        adj = [rng.getrandbits(n) for _ in range(m)]
        if sum(bin(a).count('1') for a in adj) <= 18: break
    nv, cl = cnf(n,m,adj); mo,_ = counts(n,m,adj)
    assert brute_force(nv, cl, count=True)[2] == mo; cnt += 1
print('brute_force==DP on', cnt, 'graphs')

def Kmodels(n,m): return sum((-1)**j*comb(n,j)*(n+1-j)**m for j in range(n+1))
S = {}
def stir(N,K):
    if (N,K) in S: return S[(N,K)]
    if N==K: r=1
    elif K==0 or K>N: r=0
    else: r = K*stir(N-1,K)+stir(N-1,K-1)
    S[(N,K)] = r; return r
sys.setrecursionlimit(100000)
# K_{n,m}: DP vs formula vs Stirling; matchings vs perm
for n in range(1,9):
    for m in range(n, 15):
        full = (1<<n)-1
        mo, ma = counts(n,m,[full]*m)
        assert mo == Kmodels(n,m) == factorial(n)*stir(m+1,n+1), (n,m)
        assert ma == math.perm(m,n)
# brute force on complete graphs <=20 vars
for n,m in [(2,10),(4,5),(3,6),(2,8),(4,4),(1,20)]:
    nv, cl = cnf(n,m,[(1<<n)-1]*m)
    print('K',n,m,'bf',brute_force(nv,cl,count=True)[2],'formula',Kmodels(n,m),'match',math.perm(m,n))
# K_{n,n+1}
for n in range(1,61):
    assert F(Kmodels(n,n+1), math.perm(n+1,n)) == F(n+2,2)
    assert Kmodels(n,n+1) == factorial(n)*comb(n+2,2)
print('K_{n,n+1} ratio (n+2)/2 OK n=1..60')
# disjoint stars K_{1,d}: DP of disjoint union
def stars(n,d):
    adj = []
    for x in range(n): adj += [1<<x]*d
    return counts(n, n*d, adj)
for d in range(1,5):
    for n in range(1,6):
        if n*d>20: continue
        mo,ma = stars(n,d)
        assert mo == (2**d-1)**n and ma == d**n, (n,d,mo,ma)
mo,ma = stars(12,2); print('12 stars K12:',mo,ma, mo==3**12, ma==2**12)
# disjoint stars brute force at 20 vars
adj=[]; 
for x in range(10): adj += [1<<x]*2
nv,cl = cnf(10,20,adj); print('bf 10 K_{1,2}:', brute_force(nv,cl,count=True)[2], 3**10)
# K_{n,2n}: exact ratio, check bounds and the Theta(n) term
for n in [1,2,5,10,20,40,80,160,320,640]:
    mo = Kmodels(n,2*n); ma = math.perm(2*n,n)
    lr = log(mo) - log(ma)
    assert F(mo,ma) >= F(n+1,4)**n and F(mo,ma) <= (n+1)**n
    # sharper upper bound via ratio <= (n+1)^{2n} * n!/(2n)!
    ub = 2*n*log(n+1) - (math.lgamma(2*n+1)-math.lgamma(n+1))
    print(f'K_n,2n n={n}: lnratio={lr:.4f} (lnratio - n ln n)/n={(lr-n*log(n))/n:.5f} sharperUB/n={(ub-n*log(n))/n:.5f} lnratio/(n ln n)={lr/(n*log(n)) if n>1 else float("nan"):.4f} ratio^(1/n)={math.exp(lr/n):.3f}')
