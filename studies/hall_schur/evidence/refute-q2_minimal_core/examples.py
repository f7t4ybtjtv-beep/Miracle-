import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import *
from satlab.reference import brute_force
from satlab.cdcl import CDCLSolver
from satlab import checker

HERE = os.path.dirname(os.path.abspath(__file__))
DT = "/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/ext/drat-trim/drat-trim"

def triple(adj, cl, tag):
    """three oracles: choice, own DPLL, satlab brute_force; plus drat-trim on UNSAT."""
    a = sat_choice(adj, cl); b = sat_generic(adj, cl)
    nv, cnf = to_cnf(adj, cl)
    c = None
    if nv <= 22:
        c = brute_force(nv, cnf)[0]
    dt = None
    if not a:
        r = CDCLSolver(nv, cnf, seed=0).solve()
        assert r.status == 'UNSAT'
        p = os.path.join(HERE, "tmp_%s" % tag)
        with open(p + ".cnf", "w") as f:
            f.write("p cnf %d %d\n" % (nv, len(cnf)))
            for cc in cnf: f.write(" ".join(map(str, cc)) + " 0\n")
        with open(p + ".drup", "w") as f:
            f.write("\n".join(r.proof) + "\n")
        o = subprocess.run([DT, p + ".cnf", p + ".drup"], capture_output=True, text=True, timeout=60).stdout
        dt = "s VERIFIED" in o
        ok, msg = checker.check_proof(nv, cnf, checker._parse_proof("\n".join(r.proof) + "\n"))
        dt = (dt, ok)
    assert a == b and (c is None or c == a), (a, b, c)
    return a, dt

def name(c, L, Yn):
    return "P(%s)" % L[c[1]] if c[0] == 'P' else "H(%s:%s,%s)" % (Yn[c[1]], L[c[2]], L[c[3]])

def report(title, adj, nY, S=None, cl=None):
    L = "abcdefgh"; Yn = ["y%d" % (i + 1) for i in range(nY)]
    print("==", title, "adj", adj)
    print(" minimal witnesses:", [[L[x] for x in w] for w in minimal_witnesses(adj)])
    if cl is None:
        cl = induced_clauses(adj, S)
    a, dt = triple(adj, cl, title)
    print(" #clauses", len(cl), "SAT" if a else "UNSAT", "drat-trim/satlab-checker", dt)
    for i, c in enumerate(cl):
        rest = cl[:i] + cl[i + 1:]
        s, dt = triple(adj, rest, title + "_m%d" % i)
        if not s:
            print("  removing", name(c, L, Yn), "-> still UNSAT; drat-trim,checker:", dt)
    print(" redundant count:", len(redundant_clauses(adj, cl)), "MUS:", is_mus(adj, cl))

# a,b ~ {y1,y3}; c,d ~ {y1,y2}   (y1=bit0,y2=bit1,y3=bit2)
report("ExA", (0b101, 0b101, 0b011, 0b011), 3, S=[0, 1, 2, 3])
report("ExB", (0b01, 0b11, 0b11), 2, S=[0, 1, 2])
adjD = (0b01, 0b01, 0b11, 0b11)
musD = [('P', 0), ('P', 1), ('P', 2), ('P', 3), ('H', 0, 0, 2), ('H', 0, 1, 3), ('H', 1, 2, 3)]
report("ExD", adjD, 2, cl=musD)
adjC = (0b11,) * 4
musC = [('P', x) for x in range(4)] + [('H', 0, 0, 1), ('H', 0, 1, 3), ('H', 0, 2, 3), ('H', 0, 0, 2), ('H', 1, 0, 3), ('H', 1, 1, 2)]
report("ExC", adjC, 2, cl=musC)
# K_{k,k-1}
for k in range(2, 7):
    adj = tuple([(1 << (k - 1)) - 1] * k)
    cl = induced_clauses(adj, range(k))
    mw = minimal_witnesses(adj)
    print("K_{%d,%d}" % (k, k - 1), "minwit", mw == [list(range(k))], "#cl", len(cl),
          "MUS(choice)", is_mus(adj, cl), "MUS(dpll)", is_mus(adj, cl, sat_generic) if k <= 5 else "skip")
