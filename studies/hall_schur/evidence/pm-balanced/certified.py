"""Certified solver cross-check (supplementary).
(a) ALL 65536 balanced n=4 graphs: CDCL status == (perm>0); SAT model passes checker.check_model and
    is a perfect matching; UNSAT proof passes checker.check_proof.
(b) ALL unbalanced (3,2) and (4,3) graphs: CDCL UNSAT + checker.check_proof OK.
(c) Complete K_{m+1,m} (= pigeonhole PHP^{m+1}_m without 'one hole per pigeon' clauses), m=1..6:
    CDCL UNSAT, proof checked by satlab checker AND external drat-trim.
Graphs with an isolated left vertex contain an empty clause; handled as trivially UNSAT
(proof = '0') and checked the same way."""
import sys, os, subprocess, time
from multiprocessing import Pool
W = '/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/pm-balanced'
sys.path.insert(0, W)
from common import *
from satlab.cdcl import CDCLSolver
from satlab import checker
DRAT = '/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/ext/drat-trim/drat-trim'

def solve(nv, cl):
    if any(len(c) == 0 for c in cl):
        return 'UNSAT', None, ['0']
    r = CDCLSolver(nv, cl, seed=0).solve()
    return r.status, r.model, r.proof

def job(args):
    nx, ny, mask = args
    adj = adj_from_mask(nx, ny, mask)
    nv, cl, var = encode(nx, ny, adj)
    st, model, proof = solve(nv, cl)
    expect_sat = nx == ny and perm_dp(nx, adj) > 0
    if st == 'SAT':
        ok, _ = checker.check_model(nv, cl, model)
        inv = {v: e for e, v in var.items()}
        E = [inv[l] for l in model if l > 0]
        pm = sorted(e[0] for e in E) == list(range(nx)) and sorted(e[1] for e in E) == list(range(ny))
        return (expect_sat and ok and pm), st
    if st == 'UNSAT':
        ok, _ = checker.check_proof(nv, cl, checker._parse_proof("\n".join(proof)))
        return ((not expect_sat) and ok), st
    return False, st

if __name__ == '__main__':
    for nx, ny in ((4, 4), (3, 2), (4, 3)):
        t = time.time()
        with Pool(4) as p:
            res = p.map(job, [(nx, ny, m) for m in range(1 << (nx * ny))], chunksize=256)
        print(f"({nx},{ny}) graphs={len(res)} SAT={sum(s=='SAT' for _,s in res)} "
              f"UNSAT={sum(s=='UNSAT' for _,s in res)} failures={sum(not ok for ok,_ in res)} "
              f"time={time.time()-t:.1f}s", flush=True)
    os.makedirs(W + '/php', exist_ok=True)
    for m in range(1, 7):
        adj = {(x, y) for x in range(m + 1) for y in range(m)}
        nv, cl, _ = encode(m + 1, m, adj)
        t = time.time()
        r = CDCLSolver(nv, cl, seed=0).solve()
        ok, msg = checker.check_proof(nv, cl, checker._parse_proof("\n".join(r.proof)))
        f = f"{W}/php/k{m+1}_{m}.cnf"; pf = f"{W}/php/k{m+1}_{m}.drup"
        open(f, 'w').write(f"p cnf {nv} {len(cl)}\n" + "".join(" ".join(map(str, c)) + " 0\n" for c in cl))
        open(pf, 'w').write("\n".join(r.proof) + "\n")
        out = subprocess.run([DRAT, f, pf], capture_output=True, text=True, timeout=120).stdout
        print(f"K_{{{m+1},{m}}}: vars={nv} clauses={len(cl)} status={r.status} proof_lines={len(r.proof)} "
              f"satlab_checker={ok} drat_trim_verified={'s VERIFIED' in out} t={time.time()-t:.1f}s", flush=True)
