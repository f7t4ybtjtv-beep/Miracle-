import sys, random, time, statistics
sys.path.insert(0, '.')
from mylib import *
from satlab.cdcl import CDCLSolver
from satlab import checker
ks = [int(a) for a in sys.argv[1].split(',')]
ns = sys.argv[2].split(',')
seeds = 3
print("k n nv ncl conflicts median core%% t_s proofOK(first seed)")
for k in ks:
    for ntok in ns:
        confs = []; tot = core = 0; t0 = time.time(); pok = None
        for s in range(seeds):
            rng = random.Random(1000 * k + 7 * s + (0 if ntok == 'iso' else int(ntok)))
            if ntok == 'iso':
                adj = {x: set(range(k - 1)) for x in range(k)}; S = list(range(k)); T = list(range(k - 1))
            else:
                adj, S, T = planted(int(ntok), k, 1.0, 0.5, rng)
            nv, cls, var = encode(adj, rng)
            corev = {var[(x, y)] for x in S for y in adj[x]}
            r = CDCLSolver(nv, cls, seed=s).solve()
            assert r.status == 'UNSAT'
            confs.append(r.stats['conflicts'])
            for line in r.proof:
                if line.startswith('d'): continue
                lits = [int(t) for t in line.split()][:-1]
                tot += len(lits); core += sum(abs(l) in corev for l in lits)
            if s == 0 and nv <= 2000 and k <= 7:
                text = "\n".join(r.proof)
                pok = checker.check_proof(nv, cls, checker._parse_proof(text))[0]
        print(k, ntok, nv, len(cls), confs, statistics.median(confs), "%.1f" % (100.0 * core / max(tot, 1)), "%.1f" % (time.time() - t0), pok, flush=True)
