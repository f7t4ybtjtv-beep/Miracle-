"""(4) one DRUP refutation of Schur(14,3), checked against Schur(N,3) for several N
with satlab.checker and drat-trim; (6) plain DPLL / CDCL statistics."""
import sys, os, subprocess, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schur_common import all_clauses, write_dimacs
from satlab.cdcl import CDCLSolver
from satlab import checker
from satlab.reference import dpll

DRAT = "/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/ext/drat-trim/drat-trim"
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

nv14, c14 = all_clauses(14)
r = CDCLSolver(nv14, c14, seed=0).solve()
print("CDCL Schur(14,3) seed=0:", r.status, {k: r.stats[k] for k in
      ("conflicts", "decisions", "propagations", "learned", "deleted", "restarts")
      if k in r.stats})
proof_path = os.path.join(OUT, "schur14.drup")
with open(proof_path, "w") as f:
    f.write("\n".join(r.proof) + "\n")
ptext = open(proof_path).read()
print("proof lines=%d lemmas=%d deletions=%d sha256=%s" % (
    len(r.proof), sum(1 for l in r.proof if not l.startswith("d")),
    sum(1 for l in r.proof if l.startswith("d")),
    hashlib.sha256(ptext.encode()).hexdigest()))
maxvar = max(abs(int(t)) for l in r.proof for t in l.replace("d", "").split())
print("max variable in proof:", maxvar)

steps = checker._parse_proof(ptext)
for N in (14, 15, 20, 30, 40, 50):
    nv, cl = all_clauses(N)
    cnf = os.path.join(OUT, "schur%d.cnf" % N)
    write_dimacs(cnf, nv, cl)
    ok, msg = checker.check_proof(nv, cl, steps)
    p = subprocess.run([DRAT, cnf, proof_path], capture_output=True, text=True, timeout=120)
    ver = "s VERIFIED" in p.stdout
    core = [l for l in p.stdout.splitlines() if "core" in l.lower()]
    print("N=%d vars=%d clauses=%d | satlab.checker: %s %s | drat-trim VERIFIED=%s | %s"
          % (N, nv, len(cl), ok, msg, ver, "; ".join(x.strip() for x in core[:2])))

# CDCL statistics across seeds
for s in range(5):
    rr = CDCLSolver(nv14, c14, seed=s).solve()
    print("CDCL seed=%d status=%s conflicts=%d decisions=%d" % (
        s, rr.status, rr.stats["conflicts"], rr.stats["decisions"]))

# plain DPLL
for N in (13, 14):
    nv, cl = all_clauses(N)
    t = time.time()
    st, model, nodes = dpll(nv, cl)
    print("satlab.reference.dpll Schur(%d,3): status=%s nodes=%d time=%.1fs" % (N, st, nodes, time.time() - t))
    if st:
        print("  model check:", checker.check_model(nv, cl, model))
