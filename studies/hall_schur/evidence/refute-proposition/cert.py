import sys, os, subprocess, random, time
from multiprocessing import Pool
sys.path.insert(0, '/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/refute-proposition')
from rcommon import *
from satlab.cdcl import CDCLSolver
from satlab import checker
D = '/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/refute-proposition/drup'
DT = '/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/ext/drat-trim/drat-trim'
os.makedirs(D, exist_ok=True)

def solve(nx, ny, rows, seed=0):
    nv, cls, E = cnf(nx, ny, rows)
    if any(len(c) == 0 for c in cls):
        return 'UNSAT_TRIVIAL', nv, cls, E, None
    r = CDCLSolver(nv, cls, seed=seed).solve()
    return r.status, nv, cls, E, r

def job(g):
    n = 4
    rows = [(g >> (n * x)) & 15 for x in range(n)]
    st, nv, cls, E, r = solve(n, n, rows, seed=g)
    p = perm_naive(n, rows)
    if st == 'UNSAT_TRIVIAL':
        return ('U', p == 0)
    if st == 'SAT':
        ok, _ = checker.check_model(nv, cls, r.model)
        F = [E[l - 1] for l in r.model if l > 0]
        pm = sorted(x for x, _ in F) == [0,1,2,3] and sorted(y for _, y in F) == [0,1,2,3]
        return ('S', ok and pm and p > 0)
    if st == 'UNSAT':
        ok, _ = checker.check_proof(nv, cls, checker._parse_proof('\n'.join(r.proof)))
        return ('U', ok and p == 0)
    return ('?', False)

def drat(nv, cls, proof, tag):
    f = os.path.join(D, tag + '.cnf'); pf = os.path.join(D, tag + '.drup')
    with open(f, 'w') as h:
        h.write('p cnf %d %d\n' % (nv, len(cls)))
        for c in cls: h.write(' '.join(map(str, c)) + ' 0\n')
    with open(pf, 'w') as h: h.write('\n'.join(proof) + '\n')
    out = subprocess.run([DT, f, pf], capture_output=True, text=True, timeout=120).stdout
    return 's VERIFIED' in out and 'NOT VERIFIED' not in out

if __name__ == '__main__':
    t = time.time()
    with Pool(4) as pl: res = pl.map(job, range(1 << 16), chunksize=256)
    print('n=4 SAT=%d UNSAT=%d fail=%d t=%.1fs' % (sum(r[0]=='S' for r in res), sum(r[0]=='U' for r in res),
          sum(not r[1] for r in res), time.time() - t), flush=True)
    for m in range(1, 7):
        rows = [(1 << m) - 1] * (m + 1)
        st, nv, cls, E, r = solve(m + 1, m, rows)
        sl = checker.check_proof(nv, cls, checker._parse_proof('\n'.join(r.proof)))[0]
        print('K_{%d,%d}' % (m+1, m), st, 'vars', nv, 'prooflines', len(r.proof), 'satlab', sl, 'drat-trim', drat(nv, cls, r.proof, 'K%d' % m), flush=True)
    rows = [7] * 4; st, nv, cls, E, r = solve(4, 3, rows)
    print('negative control fake proof on K_{4,3}: drat-trim verified =', drat(nv, cls, ['0'], 'fake'))
    # drat-trim on random sample of nontrivial UNSAT n=4 graphs
    R = random.Random(5); cnt = okc = 0
    for g in R.sample(range(1 << 16), 3000):
        rows = [(g >> (4 * x)) & 15 for x in range(4)]
        st, nv, cls, E, r = solve(4, 4, rows, seed=g)
        if st == 'UNSAT':
            cnt += 1; okc += drat(nv, cls, r.proof, 'g')
            if cnt >= 300: break
    print('drat-trim on n=4 nontrivial UNSAT sample:', okc, '/', cnt)
