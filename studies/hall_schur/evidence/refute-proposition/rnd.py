import sys, time, random
from multiprocessing import Pool
sys.path.insert(0, '/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/refute-proposition')
from rcommon import *
from satlab.reference import brute_force

def job(a):
    n, rows = a
    nv, cls, E = cnf(n, n, rows)
    p = perm_naive(n, rows); mc = models_choice(n, n, rows)
    bf = brute_force(nv, cls, count=True)[2] if nv <= 20 else None
    ok = (p == mc) and (bf is None or bf == p)
    return nv, p, bf is not None, ok

if __name__ == '__main__':
    R = random.Random(777)
    for n in (5, 6):
        tasks = []
        for i in range(400):
            q = R.choice([0.25, 0.35, 0.5]) if i < 200 else R.uniform(0.3, 1.0)
            tasks.append((n, [sum(1 << y for y in range(n) if R.random() < q) for _ in range(n)]))
        tasks.append((n, [(1 << n) - 1] * n))
        t = time.time()
        with Pool(4) as pl: res = pl.map(job, tasks, chunksize=4)
        print('n=%d graphs=%d bad=%d bf_checked=%d E=%d..%d perm_max=%d nonzero_perm=%d t=%.1fs' % (
            n, len(res), sum(not r[3] for r in res), sum(r[2] for r in res),
            min(r[0] for r in res), max(r[0] for r in res), max(r[1] for r in res),
            sum(r[1] > 0 for r in res), time.time() - t), flush=True)
