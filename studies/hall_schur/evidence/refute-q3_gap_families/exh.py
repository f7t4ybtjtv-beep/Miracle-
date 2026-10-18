# Independent exhaustive check: models via DP over holes (hole -> 0 or a neighbour, all pigeons hit),
# matchings via DP over holes (hole unused or matched to an unmatched neighbour pigeon).
import sys, itertools
from fractions import Fraction as F
from math import comb

def counts(n, m, adj):  # adj[y] = bitmask of pigeons adjacent to hole y
    full = (1<<n)-1
    dm = {0:1}; dt = {0:1}
    for y in range(m):
        a = adj[y]
        nm_ = {}; nt = {}
        bits = [1<<i for i in range(n) if a>>i & 1]
        for mask, c in dm.items():
            nm_[mask] = nm_.get(mask,0)+c
            for b in bits:
                k = mask|b; nm_[k] = nm_.get(k,0)+c
        for mask, c in dt.items():
            nt[mask] = nt.get(mask,0)+c
            for b in bits:
                if not mask & b:
                    k = mask|b; nt[k] = nt.get(k,0)+c
        dm, dt = nm_, nt
    return dm.get(full,0), dt.get(full,0)

def matchings_list(n, m, adj):
    out = []
    def rec(x, used, cur):
        if x == n: out.append(tuple(cur)); return
        for y in range(m):
            if adj[y]>>x & 1 and not used>>y & 1:
                cur.append(y); rec(x+1, used|1<<y, cur); cur.pop()
    rec(0,0,[]); return out

shapes = [tuple(map(int,s.split('x'))) for s in sys.argv[1:]]
tot = dict(graphs=0, withM=0, eq=0, ratio1=0, viol=0)
mink = {}
for n,m in shapes:
    E = n*m
    for g in range(1<<E):
        adj = [(g >> (y*n)) & ((1<<n)-1) for y in range(m)]
        tot['graphs'] += 1
        mo, ma = counts(n,m,adj)
        if (mo==0) != (ma==0): tot['viol']+=1; print('VIOL zero', n,m,g)
        if ma == 0: continue
        tot['withM'] += 1
        NX = sum(1 for y in range(m) if adj[y])
        k = NX - n
        r = F(mo, ma)
        if not (F(3,2)**k <= r <= (n+1)**k): tot['viol']+=1; print('VIOL bound',n,m,g,k,r)
        if (r==1) != (k==0): tot['viol']+=1; print('VIOL ratio1',n,m,g)
        if r==1: tot['ratio1']+=1
        mink[k] = min(mink.get(k, r/F(3,2)**k), r/F(3,2)**k)
        eq = (r == F(3,2)**k)
        # condition: for every saturating matching, free holes in N(X) have deg 1 and distinct neighbours
        cond = True
        for M in matchings_list(n,m,adj):
            used = set(M); nb = []
            for y in range(m):
                if adj[y] and y not in used:
                    if bin(adj[y]).count('1') != 1: cond=False; break
                    nb.append(adj[y])
            if not cond or len(set(nb)) != len(nb): cond=False; break
        if eq: tot['eq']+=1
        if eq != cond: tot['viol']+=1; print('VIOL eqcond',n,m,g,eq,cond)
print(shapes, tot, {k:str(v) for k,v in sorted(mink.items())})
