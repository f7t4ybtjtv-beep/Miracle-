"""(2) Exhaustive check, balanced n=1..4: for ALL 2^(n^2) biadjacency matrices,
brute-force model count (satlab.reference.brute_force, count=True) == permanent (DP over subsets),
and also == Ryser, == generic #DPLL, == inclusion-exclusion formula. Also checks that every model
found is a perfect matching (enumerated separately for n<=3)."""
import sys, time, itertools
from multiprocessing import Pool
sys.path.insert(0, '/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/pm-balanced')
from common import *
from satlab.reference import brute_force

def models_all(nv, clauses):
    out = []
    for bits in itertools.product((False, True), repeat=nv):
        if all(any(bits[abs(l) - 1] == (l > 0) for l in c) for c in clauses):
            out.append(bits)
    return out

def job(args):
    n, mask, full_models = args
    adj = adj_from_mask(n, n, mask)
    nv, cl, var = encode(n, n, adj)
    sat, model, cnt = brute_force(nv, cl, count=True)
    pdp = perm_dp(n, adj)
    pr = perm_ryser(n, adj)
    ie = ie_model_count(n, n, adj)
    dc = dpll_count(nv, cl)
    bad = []
    if not (cnt == pdp == pr == ie == dc) or sat != (pdp > 0):
        bad.append(('count', n, mask, cnt, pdp, pr, ie, dc, sat))
    if full_models:
        inv = {v: e for e, v in var.items()}
        for bits in models_all(nv, cl):
            E = [inv[i + 1] for i, b in enumerate(bits) if b]
            xs = sorted(e[0] for e in E); ys = sorted(e[1] for e in E)
            if not (xs == list(range(n)) and ys == list(range(n))):
                bad.append(('notPM', n, mask, E))
    return pdp, bad

if __name__ == '__main__':
    for n in (1, 2, 3, 4):
        t = time.time()
        tasks = [(n, m, n <= 3) for m in range(1 << (n * n))]
        with Pool(4) as p:
            res = p.map(job, tasks, chunksize=256)
        bads = [b for _, bl in res for b in bl]
        hist = {}
        for pdp, _ in res:
            hist[pdp] = hist.get(pdp, 0) + 1
        print(f"n={n}: graphs={len(tasks)} mismatches={len(bads)} "
              f"total_models={sum(r[0] for r in res)} perm_hist={dict(sorted(hist.items()))} "
              f"time={time.time()-t:.1f}s", flush=True)
        for b in bads[:5]:
            print("  BAD", b)
