"""(3) Unbalanced graphs, exhaustive over ALL biadjacency matrices for each (nx,ny), nx!=ny,
1<=nx,ny<=4 with nx*ny<=12, plus (1,5),(5,1),(2,5),(5,2).
- nx>ny: brute-force says UNSAT for every graph.
- nx<ny: brute-force model count == inclusion-exclusion formula == generic #DPLL;
  count >= #X-saturating matchings; strict '>' iff exists X-saturating matching M and an edge (x,y)
  with y not covered by M (characterization proved in report). Smallest strict example reported."""
import sys, itertools
from multiprocessing import Pool
sys.path.insert(0, '/tmp/claude-0/-home-user-Miracle-/70522c83-6675-5d19-92f6-406e51f45a69/scratchpad/wf/pm-balanced')
from common import *
from satlab.reference import brute_force

def xsat_matchings(nx, ny, adj):
    out = []
    def rec(x, M, used):
        if x == nx:
            out.append(list(M)); return
        for y in range(ny):
            if (x, y) in adj and y not in used:
                rec(x + 1, M + [(x, y)], used | {y})
    rec(0, [], frozenset())
    return out

def job(args):
    nx, ny, mask = args
    adj = adj_from_mask(nx, ny, mask)
    nv, cl, _ = encode(nx, ny, adj)
    sat, _, cnt = brute_force(nv, cl, count=True)
    Ms = xsat_matchings(nx, ny, adj)
    pred = any(any((x, y) in adj for x in range(nx) for y in range(ny) if y not in {e[1] for e in M})
               for M in Ms)
    ie = ie_model_count(nx, ny, adj)
    dc = dpll_count(nv, cl)
    return dict(nx=nx, ny=ny, mask=mask, E=len(adj), sat=sat, cnt=cnt, nm=len(Ms), pred=pred,
                ok_count=(cnt == ie == dc), ok_ge=(cnt >= len(Ms)), ok_char=((cnt > len(Ms)) == pred),
                ok_satiff=(sat == (len(Ms) > 0)))

if __name__ == '__main__':
    shapes = [(a, b) for a in range(1, 5) for b in range(1, 5) if a != b and a * b <= 12]
    shapes += [(1, 5), (5, 1), (2, 5), (5, 2)]
    smallest = None
    for nx, ny in shapes:
        with Pool(4) as p:
            res = p.map(job, [(nx, ny, m) for m in range(1 << (nx * ny))], chunksize=128)
        if nx > ny:
            print(f"({nx},{ny}) graphs={len(res)} SAT_count={sum(r['sat'] for r in res)} "
                  f"countmismatch={sum(not r['ok_count'] for r in res)}")
        else:
            strict = [r for r in res if r['cnt'] > r['nm']]
            print(f"({nx},{ny}) graphs={len(res)} sat={sum(r['sat'] for r in res)} "
                  f"strict(models>xsat)={len(strict)} countmismatch={sum(not r['ok_count'] for r in res)} "
                  f"ge_fail={sum(not r['ok_ge'] for r in res)} charfail={sum(not r['ok_char'] for r in res)} "
                  f"satiff_fail={sum(not r['ok_satiff'] for r in res)} "
                  f"strict_among_sat={len(strict)}/{sum(r['sat'] for r in res)}")
            for r in strict:
                key = (nx + ny, r['E'])
                if smallest is None or key < smallest[0]:
                    smallest = (key, r)
    print("smallest strict example:", smallest)
    # explicit listing for the smallest example X={x0}, Y={y0,y1}, both edges
    adj = {(0, 0), (0, 1)}
    nv, cl, var = encode(1, 2, adj)
    print("example clauses", cl, "var", var)
    print("models:", [bits for bits in itertools.product((0, 1), repeat=nv)
                      if all(any(bits[abs(l)-1] == (l > 0) for l in c) for c in cl)],
          "xsat matchings:", xsat_matchings(1, 2, adj))
    # balanced-plus-one illustrating 'in general': nx=n, ny=n+1 complete graph
    for n in range(1, 5):
        adj = {(x, y) for x in range(n) for y in range(n + 1)}
        nv, cl, _ = encode(n, n + 1, adj)
        print(f"K_{{{n},{n+1}}}: models={brute_force(nv, cl, count=True)[2]} xsat={count_xsat_matchings(n, n+1, adj)}")
