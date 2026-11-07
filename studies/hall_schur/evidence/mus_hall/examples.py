"""Verify the three explicit examples with satlab brute_force, the CDCL solver
(model / DRUP proof checked by satlab.checker) and drat-trim."""
import os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from satlab.reference import brute_force
from satlab.cdcl import CDCLSolver
from satlab import checker

DRAT = "/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/ext/drat-trim/drat-trim"
OUT = os.path.dirname(os.path.abspath(__file__)) + "/out_examples"
os.makedirs(OUT, exist_ok=True)


def certify(nv, cls, tag):
    """Return 'SAT'/'UNSAT' with all certificates verified; asserts agreement."""
    bf, _, nmod = brute_force(nv, cls, count=True)
    r = CDCLSolver(nv, cls, seed=0).solve()
    if r.status == 'SAT':
        ok, msg = checker.check_model(nv, cls, r.model)
        assert ok and bf, (tag, msg)
        return 'SAT', nmod, 'model ok'
    assert r.status == 'UNSAT' and not bf, tag
    ptxt = "\n".join(r.proof) + "\n"
    ok, msg = checker.check_proof(nv, cls, checker._parse_proof(ptxt))
    assert ok, (tag, msg)
    cnf = os.path.join(OUT, tag + ".cnf")
    prf = os.path.join(OUT, tag + ".drup")
    with open(cnf, "w") as f:
        f.write("p cnf %d %d\n" % (nv, len(cls)))
        for c in cls:
            f.write(" ".join(map(str, c)) + " 0\n")
    with open(prf, "w") as f:
        f.write(ptxt)
    out = subprocess.run([DRAT, cnf, prf], capture_output=True, text=True, timeout=60).stdout
    assert "s VERIFIED" in out, (tag, out)
    return 'UNSAT', nmod, 'satlab proof ok + drat-trim VERIFIED'


def analyse(name, nX, nY, adj, sub_mask=None, names="abcdefg"):
    nv, cls, meta, var = encode(nX, nY, adj)
    print("=" * 70)
    print(name, "adj:", {names[x]: ["y%d" % (y + 1) for y in bits(adj[x])] for x in range(nX)})
    mw = minimal_hall_witnesses(nX, adj)
    print("minimal Hall witnesses:", [sorted(names[x] for x in S) for S in mw])
    if sub_mask is None:
        S = frozenset(range(nX))
        assert S in mw, "S=X not a minimal witness"
        sub_mask = induced_mask(meta, S)
    idx = bits(sub_mask)
    sub = [cls[i] for i in idx]
    st, nmod, how = certify(nv, sub, name.replace(" ", "_") + "_F")
    print("formula (%d clauses): %s [%s]" % (len(sub), st, how))
    assert st == 'UNSAT'
    for i in idx:
        md = meta[i]
        rest = [cls[j] for j in idx if j != i]
        st2, nmod2, how2 = certify(nv, rest, name.replace(" ", "_") + "_minus%d" % i)
        lab = ("P(%s)" % names[md[1]]) if md[0] == 'P' else \
              "H(y%d:%s,%s)" % (md[1] + 1, names[md[2]], names[md[3]])
        crit = ''
        if md[0] == 'H':
            crit = ' criterion(matching of S-{x1,x2} into N(S)-{y}) => %s' % (
                'necessary' if hole_clause_necessary_criterion(adj, set(range(nX)), md[1], md[2], md[3]) else 'redundant')
        print("  remove %-14s -> %s (#models=%s; %s)%s" % (lab, st2, nmod2, how2, crit))
    return nv, cls, meta


# Example A: task candidate
analyse("ExA task candidate", 4, 3, (0b101, 0b101, 0b011, 0b011))
# Example B: 3 pigeons / 2 holes, 5 edges
analyse("ExB 3x2", 3, 2, (0b01, 0b11, 0b11))
# Example C: K_{4,2}, MUS with all 4 pigeons; y1 conflict graph = C4 a-b-d-c-a,
# y2 conflict graph = {ad, bc}
nv, cls, meta, var = encode(4, 2, (0b11,) * 4)
want = {('H', 0, 0, 1), ('H', 0, 1, 3), ('H', 0, 2, 3), ('H', 0, 0, 2),
        ('H', 1, 0, 3), ('H', 1, 1, 2)}
mask = 0
for i, md in enumerate(meta):
    if md[0] == 'P' or md in want:
        mask |= 1 << i
analyse("ExC K42 MUS", 4, 2, (0b11,) * 4, sub_mask=mask)
print("ExC: N(S)=2 holes, |S|=4; minimal Hall witnesses are the 3-subsets, so the MUS pigeon set {a,b,c,d} is NOT a minimal witness")

# Example D: smallest MUS (found by exhaustive.py) whose pigeon set is not a
# minimal witness: a,b -> {y1}; c,d -> {y1,y2}; MUS = P(a..d) + H(y1:a,c) + H(y1:b,d) + H(y2:c,d)
nv, cls, meta, var = encode(4, 2, (0b01, 0b01, 0b11, 0b11))
want = {('H', 0, 0, 2), ('H', 0, 1, 3), ('H', 1, 2, 3)}
mask = sum(1 << i for i, md in enumerate(meta) if md[0] == 'P' or md in want)
analyse("ExD smallest nonminimal MUS", 4, 2, (0b01, 0b01, 0b11, 0b11), sub_mask=mask)
print("ExD: pigeon set {a,b,c,d}, |N|=2, deficiency 2; minimal witness is only {a,b}")

# K_{k,k-1}: induced CNF of S=X (= PHP(k,k-1)) is an MUS
for k in range(2, 7):
    adj = tuple([(1 << (k - 1)) - 1] * k)
    nv, cls, meta, var = encode(k, k - 1, adj)
    assert minimal_hall_witnesses(k, adj) == [frozenset(range(k))]
    st, _, how = certify(nv, cls, "PHP%d" % k) if nv <= 20 else (None, None, None)
    if nv > 20:
        r = CDCLSolver(nv, cls, seed=0).solve()
        ok, _ = checker.check_proof(nv, cls, checker._parse_proof("\n".join(r.proof) + "\n"))
        st = 'UNSAT' if (r.status == 'UNSAT' and ok) else 'FAIL'
    nec = 0
    for i in range(len(cls)):
        rest = cls[:i] + cls[i + 1:]
        r = CDCLSolver(nv, rest, seed=0).solve()
        assert r.status == 'SAT' and checker.check_model(nv, rest, r.model)[0]
        nec += 1
    print("K_{%d,%d}: induced CNF %s, %d/%d clauses necessary (models checked); criterion says MUS=%s"
          % (k, k - 1, st, nec, len(cls), criterion_induced_is_mus(adj, frozenset(range(k)))))
