"""Exhaustive study over ALL bipartite graphs with 1<=|X|<=XMAX, 0<=|Y|<=YMAX
(isomorphism classes under permutations of X and of Y; labelled counts kept
as weights).

For every graph:
  * MSSes of the full encoding computed exhaustively over all 2^|E|
    assignments; all MUSes by hitting-set duality; each MUS re-verified
    directly (UNSAT, every one-clause removal SAT); for graphs with <= EXH_M
    clauses, MUS list cross-checked against an independent exhaustive scan of
    all 2^m clause subsets.
  * every minimal Hall witness S: induced CNF UNSAT? every pigeon clause
    necessary? every hole clause necessary? MUS? and agreement with the
    matching criterion.
  * every MUS: properties of its pigeon set.
"""
import os, sys, time, itertools, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

XMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 4
YMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 3
EXH_M = int(sys.argv[3]) if len(sys.argv) > 3 else 20

t0 = time.time()
C = dict(graphs_iso=0, graphs_lab=0, exhaustive_crosschecked_iso=0,
         mw_iso=0, mw_lab=0, mw_mus_iso=0, mw_mus_lab=0,
         induced_unsat_fail=0, pigeon_unnecessary=0, criterion_mismatch=0,
         hole_clause_criterion_mismatch=0,
         mus_total_iso=0, mus_total_lab=0, mus_bad_hole_clause=0,
         mus_no_violator=0, mus_pigeonset_not_violator=0,
         mus_pigeonset_minimal_witness=0, mus_pigeonset_not_minimal=0,
         mus_minwit_not_subset_of_induced=0,
         minwit_without_mus=0, mus_verify_fail=0,
         mus_not_strict_defmax=0, strict_defmax_sets=0,
         strict_defmax_sets_with_mus=0, strict_defmax_connected=0,
         strict_defmax_connected_with_mus=0, mus_deficiency_hist={})

def dfc(adj, T):
    return len(T) - popcount(nbhd(adj, T))

def strict_defmax(adj, S):
    dS = dfc(adj, S)
    return all(dfc(adj, T) < dS for r in range(len(S)) for T in itertools.combinations(sorted(S), r))

def connected(adj, S):
    S = list(S)
    seen = {S[0]}; stack = [S[0]]
    while stack:
        x = stack.pop()
        for z in S:
            if z not in seen and adj[z] & adj[x]:
                seen.add(z); stack.append(z)
    return len(seen) == len(S)
smallest_nonmus = None      # (|X|+|Y|, |E|, nX, nY, adj, S)
smallest_nonmin_mus = None
by_size = {}

for nX in range(1, XMAX + 1):
    for nY in range(0, YMAX + 1):
        classes = all_graph_classes(nX, nY)
        for adj, w in classes.items():
            C['graphs_iso'] += 1
            C['graphs_lab'] += w
            nv, cls, meta, var = encode(nX, nY, adj)
            m = len(cls)
            mss = sat_masks(nv, cls)
            muses = all_muses_duality(m, mss)
            for M in muses:
                if not is_mus(M, mss):
                    C['mus_verify_fail'] += 1
            if m <= EXH_M:
                ex = all_muses_exhaustive(m, mss)
                assert ex == muses, ("MUS enumeration mismatch", nX, nY, adj)
                C['exhaustive_crosschecked_iso'] += 1
            # ---- minimal witnesses / induced CNF
            mws = minimal_hall_witnesses(nX, adj)
            key = (nX, nY)
            bs = by_size.setdefault(key, dict(iso=0, lab=0, mw_lab=0, mw_mus_lab=0,
                                              mus_lab=0, mus_nonmin_lab=0))
            bs['iso'] += 1; bs['lab'] += w
            for S in mws:
                C['mw_iso'] += 1; C['mw_lab'] += w; bs['mw_lab'] += w
                F = induced_mask(meta, S)
                if is_sat(F, mss):
                    C['induced_unsat_fail'] += 1
                    continue
                mus = True
                for i in bits(F):
                    nec = is_sat(F & ~(1 << i), mss)
                    if meta[i][0] == 'P' and not nec:
                        C['pigeon_unnecessary'] += 1
                    if meta[i][0] == 'H':
                        _, y, x1, x2 = meta[i]
                        if nec != hole_clause_necessary_criterion(adj, S, y, x1, x2):
                            C['hole_clause_criterion_mismatch'] += 1
                    mus &= nec
                if mus != criterion_induced_is_mus(adj, S):
                    C['criterion_mismatch'] += 1
                if mus:
                    C['mw_mus_iso'] += 1; C['mw_mus_lab'] += w; bs['mw_mus_lab'] += w
                else:
                    E = sum(popcount(r) for r in adj)
                    cand = (nX + nY, E, nX, nY, adj, sorted(S))
                    if smallest_nonmus is None or cand < smallest_nonmus:
                        smallest_nonmus = cand
                if not any(M & ~F == 0 and
                           frozenset(meta[i][1] for i in bits(M) if meta[i][0] == 'P') == S
                           for M in muses):
                    C['minwit_without_mus'] += 1
            # ---- MUS structure
            mwset = set(mws)
            viol = hall_violators(nX, adj)
            for M in muses:
                C['mus_total_iso'] += 1; C['mus_total_lab'] += w; bs['mus_lab'] += w
                P = frozenset(meta[i][1] for i in bits(M) if meta[i][0] == 'P')
                for i in bits(M):
                    if meta[i][0] == 'H' and not (meta[i][2] in P and meta[i][3] in P):
                        C['mus_bad_hole_clause'] += 1
                if not any(T <= P for T in viol):
                    C['mus_no_violator'] += 1
                if popcount(nbhd(adj, P)) >= len(P):
                    C['mus_pigeonset_not_violator'] += 1
                if not strict_defmax(adj, P):
                    C['mus_not_strict_defmax'] += 1
                dd = str(dfc(adj, P))
                C['mus_deficiency_hist'][dd] = C['mus_deficiency_hist'].get(dd, 0) + 1
                if P in mwset:
                    C['mus_pigeonset_minimal_witness'] += 1
                    if M & ~induced_mask(meta, P):
                        C['mus_minwit_not_subset_of_induced'] += 1
                else:
                    C['mus_pigeonset_not_minimal'] += 1
                    bs['mus_nonmin_lab'] += w
                    E = sum(popcount(r) for r in adj)
                    cand = (nX + nY, E, nX, nY, adj, sorted(P), len(bits(M)))
                    if smallest_nonmin_mus is None or cand < smallest_nonmin_mus:
                        smallest_nonmin_mus = cand
            mus_psets = set(frozenset(meta[i][1] for i in bits(M) if meta[i][0] == 'P') for M in muses)
            for r in range(1, nX + 1):
                for S in itertools.combinations(range(nX), r):
                    S = frozenset(S)
                    if dfc(adj, S) >= 1 and strict_defmax(adj, S):
                        C['strict_defmax_sets'] += 1
                        has = S in mus_psets
                        C['strict_defmax_sets_with_mus'] += has
                        if connected(adj, S):
                            C['strict_defmax_connected'] += 1
                            C['strict_defmax_connected_with_mus'] += has
                            if not has:
                                print("  strict-defmax connected S without MUS:", nX, nY, adj, sorted(S))
        print("done |X|=%d |Y|=%d  iso classes=%d  t=%.1fs" % (nX, nY, len(classes), time.time() - t0), flush=True)

print(json.dumps(C, indent=1))
print("fraction of minimal witnesses (labelled, with multiplicity) whose induced CNF is MUS: %d/%d = %.4f"
      % (C['mw_mus_lab'], C['mw_lab'], C['mw_mus_lab'] / C['mw_lab']))
print("same over iso classes: %d/%d = %.4f" % (C['mw_mus_iso'], C['mw_iso'], C['mw_mus_iso'] / C['mw_iso']))
print("smallest non-MUS induced CNF (|X|+|Y|, |E|, nX, nY, adj, S):", smallest_nonmus)
print("smallest MUS with non-minimal pigeon set (|X|+|Y|, |E|, nX, nY, adj, P, |MUS|):", smallest_nonmin_mus)
print("per (|X|,|Y|): iso, labelled graphs, minimal witnesses(lab), induced=MUS(lab), MUSes(lab), MUSes with non-minimal pigeon set(lab)")
for k in sorted(by_size):
    b = by_size[k]
    print(k, b['iso'], b['lab'], b['mw_lab'], b['mw_mus_lab'], b['mus_lab'], b['mus_nonmin_lab'])
print("time %.1fs" % (time.time() - t0))
