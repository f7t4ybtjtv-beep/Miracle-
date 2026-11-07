"""(5) AMO redundancy and deletion-based MUS extraction for Schur(14,3), CDCL oracle.
Every UNSAT answer for the final MUS is certified (DRUP, satlab.checker + drat-trim);
every SAT answer in the minimality check is certified by check_model."""
import sys, os, random, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from schur_common import schur_cnf, write_dimacs
from satlab.cdcl import CDCLSolver
from satlab import checker

DRAT = "/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/ext/drat-trim/drat-trim"
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

nv, alo, amo, tri = schur_cnf(14)
kind = {}
for c in alo: kind[tuple(c)] = "ALO"
for c in amo: kind[tuple(c)] = "AMO"
for c in tri: kind[tuple(c)] = "TRI3" if len(c) == 3 else "TRI2"
F = alo + amo + tri


def certify_unsat(cl, tag):
    r = CDCLSolver(nv, cl, seed=0).solve()
    assert r.status == "UNSAT", r.status
    ptxt = "\n".join(r.proof) + "\n"
    ok, msg = checker.check_proof(nv, cl, checker._parse_proof(ptxt))
    cnf = os.path.join(OUT, tag + ".cnf"); prf = os.path.join(OUT, tag + ".drup")
    write_dimacs(cnf, nv, cl); open(prf, "w").write(ptxt)
    p = subprocess.run([DRAT, cnf, prf], capture_output=True, text=True, timeout=120)
    return ok and ("s VERIFIED" in p.stdout), msg


def is_sat(cl):
    r = CDCLSolver(nv, cl, seed=0, emit_proof=False).solve()
    if r.status == "SAT":
        ok, _ = checker.check_model(nv, cl, r.model)
        assert ok
        return True
    assert r.status == "UNSAT"
    return False


def comp(cl):
    d = {"ALO": 0, "AMO": 0, "TRI3": 0, "TRI2": 0}
    for c in cl: d[kind[tuple(c)]] += 1
    return d


print("F14 = %d clauses: %s" % (len(F), comp(F)))
noamo = alo + tri
print("F14 minus all 42 AMO clauses: %d clauses, UNSAT certified (satlab.checker + drat-trim): %s"
      % (len(noamo), certify_unsat(noamo, "noamo")))


def deletion_mus(order):
    cur = list(order)
    i = 0
    while i < len(cur):
        trial = cur[:i] + cur[i + 1:]
        if is_sat(trial):
            i += 1           # clause necessary
        else:
            cur = trial      # clause redundant, drop it
    return cur


def verify_mus(mus, tag):
    unsat = certify_unsat(mus, tag)
    minimal = all(is_sat(mus[:i] + mus[i + 1:]) for i in range(len(mus)))
    return unsat, minimal


orders = [("natural ALO,AMO,TRI", F),
          ("AMO first, then TRI, then ALO", amo + tri + alo),
          ("TRI first, then AMO, then ALO", tri + amo + alo)]
rng = random.Random(12345)
for k in range(5):
    o = F[:]; rng.shuffle(o)
    orders.append(("random shuffle #%d (Random(12345))" % k, o))

results = []
for idx, (name, o) in enumerate(orders):
    mus = deletion_mus(o)
    unsat, minimal = verify_mus(mus, "mus%d" % idx)
    results.append(len(mus))
    print("[%s] MUS size=%d composition=%s certified_UNSAT=%s every-single-deletion-SAT=%s"
          % (name, len(mus), comp(mus), unsat[0], minimal))
    if idx == 1:
        with open(os.path.join(OUT, "mus_amo_first.txt"), "w") as f:
            for c in mus: f.write(" ".join(map(str, c)) + " 0\n")
print("MUS sizes found:", results)

# Which ALO clauses are individually necessary (in AMO-free formula)?
nec = [i + 1 for i in range(14) if is_sat([c for c in noamo if c != alo[i]])]
print("numbers i whose ALO clause is necessary in F14\\AMO:", nec)
# Which triple clauses are individually necessary in F14 (transition clauses)?
nec_t = [c for c in tri if is_sat([d for d in F if d != c])]
print("triple clauses individually necessary in full F14: %d" % len(nec_t))
