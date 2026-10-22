import sys, os, glob, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1 import gen
from satlab.cdcl import CDCLSolver
from satlab import reference, checker
A='/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/schur-audit/out'
def v(i,c): return 3*(i-1)+c+1
def recon(N):  # literally the task's reconstruction order
    cl=[]
    for i in range(1,N+1):
        cl.append([v(i,0),v(i,1),v(i,2)])
        for a in range(3):
            for b in range(a+1,3): cl.append([-v(i,a),-v(i,b)])
    for z in range(2,N+1):
        for x in range(1,z//2+1):
            y=z-x
            for c in range(3):
                cl.append(sorted(set([-v(x,c),-v(y,c),-v(z,c)])))
    return cl
def rd(p):
    cls=[];
    for l in open(p):
        if l.startswith(('p','c')) or not l.strip(): continue
        cls.append(tuple(sorted(int(t) for t in l.split() if t!='0')))
    return cls
R=recon(14); print('recon == my set:', set(map(tuple,map(sorted,R)))==set(tuple(sorted(c)) for _,c in gen(14)))
print('their schur14.cnf == recon order:', rd(A+'/schur14.cnf')==[tuple(sorted(c)) for c in R])
for s in range(5):
    r=CDCLSolver(42,[list(c) for c in R],seed=s).solve(); print('cdcl recon-order seed',s,r.status,r.stats['conflicts'])
kind={tuple(sorted(c)):k for k,c in gen(14)}
F=set(kind)
def evalm(cls,model):
    T=set(l for l in model if l>0) if model and isinstance(model,(list,tuple)) else None
    return T
def dsat(cls):
    s,m,_=reference.dpll(42,[list(c) for c in cls]); return s,m
def model_ok(cls,m):
    # m from dpll: inspect format
    ok,msg=checker.check_model(42,[list(c) for c in cls],m); return ok
for p in sorted(glob.glob(A+'/mus*.cnf')):
    M=rd(p)
    assert set(M)<=F and len(set(M))==len(M)
    from collections import Counter
    comp=Counter(kind[c] for c in M)
    s,_=dsat(M)
    allsat=True
    for i in range(len(M)):
        sub=M[:i]+M[i+1:]
        s2,m2=dsat(sub)
        if not s2 or not model_ok(sub,m2): allsat=False
    print(os.path.basename(p),len(M),dict(comp),'dpll UNSAT' if s is False else 'NOT UNSAT','minimal' if allsat else 'NOT MINIMAL')
# necessity in full F14 via dpll
FL=[tuple(sorted(c)) for c in R]
nec=[]
for i,c in enumerate(FL):
    sub=FL[:i]+FL[i+1:]; s,m=dsat(sub)
    if s:
        assert model_ok(sub,m); nec.append(kind[c])
from collections import Counter
print('individually necessary clauses in F14:',len(nec),dict(Counter(nec)))
# F14 minus AMO unsat via dpll
noamo=[c for c in FL if kind[c]!='AMO']; print('F14\\AMO dpll:',dsat(noamo)[0], len(noamo))
