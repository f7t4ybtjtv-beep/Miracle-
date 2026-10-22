"""Part (4): satlab CDCL on planted complete witnesses K_{k,k-1} inside random dense graphs.

Graph (hallcore.planted_graph, p_in=1, p_rest=0.5, p_cross=0.5, extra_holes=2):
  pigeons n, holes n+1; S={0..k-1} complete to T (|T|=k-1), no S->Y\\T edges;
  X\\S has a planted perfect matching into Y\\T, plus random edges (p=0.5) to Y\\T and to T.
Checked per instance: X\\S matchable into Y\\T (so lower bound transfers), and minimal witness found
by matching equals S.  Baseline: the isolated PHP^k_{k-1} (graph = witness only).
Usage: exp_cdcl.py KMAX NS SEEDS CAP
"""
import random
import sys
import time

sys.path.insert(0, "/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/hall_witness")
from hallcore import *  # noqa
from satlab.cdcl import CDCLSolver
from satlab import checker

import os
KS = list(range(int(os.environ.get("KMIN", "3")), int(sys.argv[1]) + 1))
NS = [int(a) for a in sys.argv[2].split(",")]
SEEDS = int(sys.argv[3])
CAP = int(sys.argv[4])
VERIFY = len(sys.argv) > 5

rng = random.Random(777)
print("k  n   nv    ncl   conflicts(per seed)              median  core_lits_in_learnts%  t_s")
for k in KS:
    for n in [0] + NS:
        confs, tt, frac = [], 0.0, []
        for s in range(SEEDS):
            if n == 0:
                adj = {x: set(range(k - 1)) for x in range(k)}
                nX, nY = k, k - 1
            else:
                nY, adj, S, T, R = planted_graph(n, k, rng)
                nX = n
                rest = [x for x in range(k, n)]
                radj = {x: adj[x] & set(R) for x in rest}
                assert len(max_matching(rest, radj)) == len(rest)
                assert minimal_witness(n, adj) == S
            nv, cl, var = encode(nX, nY, adj)
            core = {var[(x, y)] for x in range(k) for y in range(k - 1) if (x, y) in var}
            t0 = time.time()
            r = CDCLSolver(nv, cl, seed=s, max_conflicts=CAP).solve()
            tt += time.time() - t0
            assert r.status in ("UNSAT", "UNKNOWN")
            if VERIFY and r.status == "UNSAT":
                ok, msg = checker.check_proof(nv, cl, checker._parse_proof("\n".join(
                    l if isinstance(l, str) else " ".join(map(str, l)) + " 0" for l in r.proof)))
                assert ok, msg
            confs.append(r.stats["conflicts"] if r.status == "UNSAT" else ">%d" % CAP)
            # fraction of literals in learned clauses (proof additions) that are core vars
            tot = cin = 0
            for line in r.proof:
                txt = line if isinstance(line, str) else " ".join(map(str, line))
                if txt.startswith("d"):
                    continue
                lits = [int(t) for t in txt.split() if t != "0"]
                tot += len(lits)
                cin += sum(1 for l in lits if abs(l) in core)
            frac.append(100.0 * cin / tot if tot else 100.0)
        num = sorted(c for c in confs if isinstance(c, int))
        med = num[len(num) // 2] if len(num) == len(confs) else "cap"
        print("%d %3s %5d %6d  %-34s %6s  %5.1f  %.1f" % (
            k, n if n else "iso", nv, len(cl), confs, med, sum(frac) / len(frac), tt), flush=True)
