# Independent generator + counts + exhaustive colorings (pure product enumeration)
import itertools, sys, time
def v(i,c): return 3*(i-1)+c+1
def gen(N):
    cl=[]
    for i in range(1,N+1):
        cl.append(('ALO',tuple(v(i,c) for c in range(3))))
        for a,b in itertools.combinations(range(3),2): cl.append(('AMO',(-v(i,a),-v(i,b))))
    # different enumeration: iterate over all x<=y with x+y<=N
    for x in range(1,N+1):
        for y in range(x,N+1):
            z=x+y
            if z>N: break
            for c in range(3):
                lits=sorted(set([-v(x,c),-v(y,c),-v(z,c)]))
                cl.append(('SUM2' if x==y else 'SUM3',tuple(lits)))
    return cl
if __name__=='__main__':
    exp={14:(42,203),15:(45,228),20:(60,380),30:(90,795),40:(120,1360),50:(150,2075)}
    for N,(ev,ec) in exp.items():
        cl=gen(N); nv=max(abs(l) for _,c in cl for l in c)
        dup=len(cl)-len(set(c for _,c in cl))
        cf=4*N+3*(N*N//4)
        from collections import Counter
        print(N,nv,len(cl),cf,dup,dict(Counter(k for k,_ in cl)),'OK' if (nv,len(cl))==(ev,ec)==(nv,cf) else 'MISMATCH')
    bad=[N for N in range(1,401) if len(gen(N))!=4*N+3*(N*N//4)] if False else None
    # closed form vs sum formula
    print('closed form mismatches 1..2000:',[N for N in range(1,2001) if N+3*N+3*sum(z//2 for z in range(2,N+1))!=4*N+3*(N*N//4)])
    # exhaustive product enumeration of colorings
    for n in (12,13,14):
        t=time.time()
        triples=[(x,y,x+y) for x in range(1,n+1) for y in range(x,n+1) if x+y<=n]
        cnt=0; ex=None
        # fix color of 1 to 0 to cut by 3, multiply back (symmetry under color permutation is exact)
        for col in itertools.product(range(3),repeat=n-1):
            c=(0,)+col
            ok=True
            for x,y,z in triples:
                if c[x-1]==c[y-1]==c[z-1]: ok=False;break
            if ok:
                cnt+=1; ex=ex or c
        print('n',n,'colorings',3*cnt,'example',ex,'time %.1f'%(time.time()-t))
