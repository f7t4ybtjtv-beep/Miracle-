import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from witness_exh import run
tot, smallest = run(eval(sys.argv[1]))
for k, v in tot.items():
    print(k, "frac %d/%d = %.4f" % (v['mus'], v['w'], v['mus'] / v['w']))
print("failure counters:", {k: sum(v[k] for v in tot.values()) for k in ['unsat_fail', 'pig_unnec', 'crit_mis', 'hole_tested']})
