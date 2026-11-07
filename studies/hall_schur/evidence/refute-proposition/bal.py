import sys, time
from multiprocessing import Pool
sys.path.insert(0, '/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/refute-proposition')
from rcommon import *
from satlab.reference import brute_force


def job(a):
    n, g = a
    rows = [(g >> (n * x)) & ((1 << n) - 1) for x in range(n)]
    nv, cls, E = cnf(n, n, rows)
    sat, mdl, bf = brute_force(nv, cls, count=True)
    p = perm_naive(n, rows)
    mc = models_choice(n, n, rows)
    mb = models_bits(nv, cls) if n <= 3 else mc  # bitmask brute force only n<=3 (time)
    ok = (bf == p == mc == mb) and (sat == (p > 0))
    # check SAT model returned is a perfect matching
    if sat:
        F = [E[l - 1] for l in mdl if l > 0]
        if sorted(x for x, _ in F) != list(range(n)) or sorted(y for _, y in F) != list(range(n)):
            ok = False
    return p, ok


if __name__ == '__main__':
    for n in (1, 2, 3, 4):
        t = time.time()
        with Pool(4) as pl:
            res = pl.map(job, [(n, g) for g in range(1 << (n * n))], chunksize=512)
        hist = {}
        for p, _ in res:
            hist[p] = hist.get(p, 0) + 1
        print('n=%d graphs=%d bad=%d total=%d hist=%s t=%.1fs' % (
            n, len(res), sum(1 for _, o in res if not o), sum(p for p, _ in res),
            dict(sorted(hist.items())), time.time() - t), flush=True)
