#!/usr/bin/env python3
"""Régénère hallproof_drat_trim.txt : preuves de satlab.hallproof contrôlées par drat-trim.

    python3 studies/hall_schur/evidence/review/hallproof_drat.py --drat /chemin/drat-trim

K_{m+1,m} pour m = 2..9 (k2..k9 : m = 2..9) et 10 graphes à témoin implanté (p0..p9).
Chaque ligne donne le nombre de lignes de preuve et le verdict de drat-trim.
"""
import argparse
import os
import random
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, ROOT)

from satlab import generators, hallproof  # noqa: E402
from satlab.dimacs import CNF  # noqa: E402


def verdict(drat, cnf_path, proof_path):
    out = subprocess.run([drat, cnf_path, proof_path], capture_output=True, text=True).stdout
    for line in out.replace("\r", "\n").splitlines():
        if line.startswith("s "):
            return line.strip()
    return "pas de verdict"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--drat", required=True)
    args = ap.parse_args()
    rows = []
    with tempfile.TemporaryDirectory() as d:
        for m in range(2, 10):
            adj = [list(range(m)) for _ in range(m + 1)]
            nv, clauses, _ = generators.graph_php_cnf(adj, m)
            _, lines = hallproof.hall_witness_proof(adj, m)
            rows.append(("k%d" % m, CNF(nv, clauses), lines))
        for s in range(10):
            rng = random.Random(s)
            n = rng.randint(10, 30)
            c, meta = generators.bipartite_php(n, n + 2, 0.5, witness=rng.randint(3, 7), seed=s)
            _, lines = hallproof.hall_witness_proof(meta["adj"], n + 2)
            rows.append(("p%d" % s, c, lines))
        for name, cnf, lines in rows:
            cp = os.path.join(d, name + ".cnf")
            pp = os.path.join(d, name + ".drup")
            with open(cp, "w") as f:
                f.write(cnf.to_dimacs())
            with open(pp, "w") as f:
                f.write("\n".join(lines) + "\n")
            print("%s.cnf %d lignes : %s" % (name, len(lines), verdict(args.drat, cp, pp)))


if __name__ == "__main__":
    main()
