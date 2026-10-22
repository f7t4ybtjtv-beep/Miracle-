"""Random larger graphs (beyond exhaustive range), oracle = satlab CDCL with
every answer certified by satlab.checker (SAT: model; UNSAT: DRUP proof).

Part A: for each minimal Hall witness S, decide clause-by-clause necessity in
the induced CNF and compare with the matching criterion.
Part B: extract MUSes of the FULL encoding by deletion (random clause orders)
and check: hole clauses only between pigeons of P; d(T) < d(P) for every
proper subset T of P (strict deficiency maximality); whether P is a minimal
Hall witness.
"""
import os, sys, random, itertools, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
from satlab.cdcl import CDCLSolver
from satlab import checker

stats = dict(oracle_calls=0, sat=0, unsat=0)


def solve(nv, cls):
    stats['oracle_calls'] += 1
    if any(len(c) == 0 for c in cls):
        stats['unsat'] += 1
        return False
    r = CDCLSolver(nv, cls, seed=0).solve()
    if r.status == 'SAT':
        ok, msg = checker.check_model(nv, cls, r.model)
        assert ok, msg
        stats['sat'] += 1
        return True
    assert r.status == 'UNSAT'
    ok, msg = checker.check_proof(nv, cls, checker._parse_proof("\n".join(r.proof) + "\n"))
    assert ok, msg
    stats['unsat'] += 1
    return False


def dfc(adj, T):
    return len(T) - popcount(nbhd(adj, T))


def strict_defmax(adj, S):
    dS = dfc(adj, S)
    return all(dfc(adj, T) < dS for r in range(len(S)) for T in itertools.combinations(sorted(S), r))


def random_graph(rng, nX, nY, p):
    return tuple(sum(1 << y for y in range(nY) if rng.random() < p) for _ in range(nX))


rng = random.Random(20261018)
t0 = time.time()
A = dict(graphs=0, witnesses=0, max_witness_size=0, induced_unsat=0, induced_mus=0,
         pigeon_nec_fail=0, hole_criterion_mismatch=0, hole_clauses_tested=0)
B = dict(muses=0, bad_hole=0, not_strict_defmax=0, pset_minimal_witness=0, pset_nonminimal=0,
         max_def=0, max_pset=0)
while time.time() - t0 < 150:
    nX = rng.randint(5, 8)
    nY = rng.randint(max(1, nX - 3), nX - 1)
    adj = random_graph(rng, nX, nY, rng.choice([0.3, 0.45, 0.6]))
    nv, cls, meta, var = encode(nX, nY, adj)
    mws = minimal_hall_witnesses(nX, adj)
    A['graphs'] += 1
    for S in mws:
        A['witnesses'] += 1
        A['max_witness_size'] = max(A['max_witness_size'], len(S))
        F = bits(induced_mask(meta, S))
        Fc = [cls[i] for i in F]
        assert not solve(nv, Fc)
        A['induced_unsat'] += 1
        allnec = True
        for i in F:
            nec = solve(nv, [cls[j] for j in F if j != i])
            if meta[i][0] == 'P':
                A['pigeon_nec_fail'] += (not nec)
            else:
                A['hole_clauses_tested'] += 1
                _, y, x1, x2 = meta[i]
                A['hole_criterion_mismatch'] += (nec != hole_clause_necessary_criterion(adj, S, y, x1, x2))
            allnec &= nec
        A['induced_mus'] += allnec
    # Part B: deletion-based MUS extraction from the full encoding
    if mws and len(cls) <= 80:
        for _ in range(2):
            order = list(range(len(cls)))
            rng.shuffle(order)
            cur = set(order)
            for i in order:
                trial = cur - {i}
                if not solve(nv, [cls[j] for j in sorted(trial)]):
                    cur = trial
            M = sorted(cur)
            # re-verify MUS
            assert not solve(nv, [cls[j] for j in M])
            assert all(solve(nv, [cls[j] for j in M if j != i]) for i in M)
            B['muses'] += 1
            P = frozenset(meta[i][1] for i in M if meta[i][0] == 'P')
            B['bad_hole'] += any(meta[i][0] == 'H' and not (meta[i][2] in P and meta[i][3] in P) for i in M)
            B['not_strict_defmax'] += (not strict_defmax(adj, P))
            if P in set(mws):
                B['pset_minimal_witness'] += 1
            else:
                B['pset_nonminimal'] += 1
            B['max_def'] = max(B['max_def'], dfc(adj, P))
            B['max_pset'] = max(B['max_pset'], len(P))
print("seed 20261018, time %.1fs" % (time.time() - t0))
print("Part A:", A)
print("Part B:", B)
print("oracle:", stats)
