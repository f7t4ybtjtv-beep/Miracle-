"""(2) Random balanced graphs n=5,6.
Set A (brute force): 300 per n, edge prob p=0.5 (n=5) / 0.4 (n=6), rejection-sampled to |E|<=18
so satlab.reference.brute_force (2^|E| assignments) is feasible.
Set B (dense, no brute force possible >24 vars): 300 per n with p uniform in [0.3,0.95], generic
#DPLL counter vs permanent (DP + Ryser). Seed fixed."""
import sys, time, random
from multiprocessing import Pool
sys.path.insert(0, '/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/pm-balanced')
from common import *
from satlab.reference import brute_force

def jobA(args):
    n, adj = args
    nv, cl, _ = encode(n, n, adj)
    _, _, cnt = brute_force(nv, cl, count=True)
    pdp, pr, dc = perm_dp(n, adj), perm_ryser(n, adj), dpll_count(nv, cl)
    return nv, pdp, (cnt == pdp == pr == dc)

def jobB(args):
    n, adj = args
    nv, cl, _ = encode(n, n, adj)
    pdp, pr, dc = perm_dp(n, adj), perm_ryser(n, adj), dpll_count(nv, cl)
    return nv, pdp, (pdp == pr == dc)

if __name__ == '__main__':
    rng = random.Random(20261018)
    for n, p in ((5, 0.5), (6, 0.4)):
        t = time.time()
        A = []
        while len(A) < 300:
            adj = {(x, y) for x in range(n) for y in range(n) if rng.random() < p}
            if len(adj) <= 18:
                A.append((n, adj))
        with Pool(4) as pool:
            ra = pool.map(jobA, A, chunksize=4)
        B = []
        for _ in range(300):
            q = rng.uniform(0.3, 0.95)
            B.append((n, {(x, y) for x in range(n) for y in range(n) if rng.random() < q}))
        with Pool(4) as pool:
            rb = pool.map(jobB, B, chunksize=4)
        for name, r in (('A brute', ra), ('B dpll', rb)):
            es = [e for e, _, _ in r]; ps = [q for _, q, _ in r]
            print(f"n={n} set {name}: graphs={len(r)} mismatches={sum(not ok for *_, ok in r)} "
                  f"|E| range={min(es)}..{max(es)} perm>0: {sum(q>0 for q in ps)} max perm={max(ps)} "
                  f"time={time.time()-t:.1f}s", flush=True)
