import sys, os, subprocess, hashlib, glob, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r1 import gen
from satlab.cdcl import CDCLSolver
from satlab import checker, reference
D=os.path.dirname(os.path.abspath(__file__)); O=D+'/out'
A='/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/schur-audit/out'
DT='/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/ext/drat-trim/drat-trim'
def wcnf(path,nv,cls):
    with open(path,'w') as f:
        f.write('p cnf %d %d\n'%(nv,len(cls)))
        for c in cls: f.write(' '.join(map(str,c))+' 0\n')
def drat(cnf,prf):
    r=subprocess.run([DT,cnf,prf],capture_output=True,text=True,timeout=120)
    out=r.stdout
    core=[l.strip() for l in out.replace('\r','\n').split('\n') if 'in core' in l]
    return ('s VERIFIED' in out), core
def sat_eval(cls,model):  # model: set of true vars
    return all(any((l>0 and l in model) or (l<0 and -l not in model) for l in c) for c in cls)
# own proof with seed 3
F14=[c for _,c in gen(14)]
r=CDCLSolver(42,[list(c) for c in F14],seed=3).solve()
print('own CDCL seed3:',r.status,r.stats.get('conflicts'))
open(O+'/mine14.drup','w').write('\n'.join(r.proof)+'\n')
theirs=A+'/schur14.drup'
print('their proof sha256',hashlib.sha256(open(theirs,'rb').read()).hexdigest())
pl=[l for l in open(theirs).read().split('\n') if l.strip()]
print('their proof lines',len(pl),'deletions',sum(l.startswith('d ') for l in pl),'maxvar',max(abs(int(t)) for l in pl for t in l.replace('d ','').split() if t!='0'))
for N in (14,15,20,30,40,50):
    cl=[c for _,c in gen(N)]; nv=3*N
    p=O+'/my%d.cnf'%N; wcnf(p,nv,cl)
    for name,prf in (('theirs',theirs),('mine',O+'/mine14.drup')):
        ok,core=drat(p,prf)
        sc=checker.check_proof(nv,[list(c) for c in cl],checker._parse_proof(open(prf).read()))
        print(N,nv,len(cl),name,'drat VERIFIED' if ok else 'drat FAIL',core[:1],'| satlab',sc)
# negative control: proof against F13 must fail
cl13=[c for _,c in gen(13)]; wcnf(O+'/my13.cnf',39,cl13)
print('control F13 with their proof:',drat(O+'/my13.cnf',theirs)[0], checker.check_proof(39,[list(c) for c in cl13],checker._parse_proof(open(theirs).read())))
# dpll nodes
for n in (13,14):
    cl=[list(c) for _,c in gen(n)]
    print('dpll',n,reference.dpll(3*n,cl)[0::2])
for s in range(5):
    rr=CDCLSolver(42,[list(c) for c in F14],seed=s).solve(); print('cdcl seed',s,rr.status,rr.stats['conflicts'])
