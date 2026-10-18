"""Composition of the drat-trim core (-c) of the SAME Schur(14,3) proof checked against FN."""
import sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schur_common import schur_cnf
DRAT = "/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/ext/drat-trim/drat-trim"
OUT = os.path.join(HERE, "out")
for N in (14, 15, 20, 30, 40, 50):
    nv, alo, amo, tri = schur_cnf(N)
    kind = {}
    for c in alo: kind[tuple(sorted(c))] = "ALO"
    for c in amo: kind[tuple(sorted(c))] = "AMO"
    for c in tri: kind[tuple(sorted(c))] = "TRI"
    core = os.path.join(OUT, "core%d.cnf" % N)
    p = subprocess.run([DRAT, os.path.join(OUT, "schur%d.cnf" % N), os.path.join(OUT, "schur14.drup"),
                        "-c", core], capture_output=True, text=True, timeout=120)
    cl = []
    for line in open(core):
        if line.startswith("p") or line.startswith("c") or not line.strip():
            continue
        cl.append(tuple(sorted(int(t) for t in line.split()[:-1])))
    d = {}
    for c in cl: d[kind[c]] = d.get(kind[c], 0) + 1
    outside = sum(1 for c in cl if max(abs(l) for l in c) > 42)
    print("N=%d VERIFIED=%s core=%d %s clauses_using_vars>42=%d"
          % (N, "s VERIFIED" in p.stdout, len(cl), d, outside))
