import sys
sys.path.insert(0, '.')
from mylib import *
from satlab.cdcl import CDCLSolver
adj = {x: set(range(8)) for x in range(9)}
adj[9] = {100}; adj[10] = {100}
nv, cls, var = encode(adj)
proof = [[]]  # empty clause directly
print("nv", nv, "ncl", len(cls))
print("empty clause alone RUP: satlab", satlab_check(nv, cls, proof), "drat", drat_check(nv, cls, proof, "ctr"))
r = CDCLSolver(nv, cls, seed=0).solve(); print("CDCL", r.status, r.stats['conflicts'])
# also check that PHP^9_8 alone has no such tiny proof: empty clause not RUP
nv2, cls2, _ = encode({x: set(range(8)) for x in range(9)})
print("PHP9_8 alone: empty RUP?", satlab_check(nv2, cls2, [[]]))
