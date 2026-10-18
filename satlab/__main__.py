"""CLI satlab.

  python3 -m satlab gen FAMILLE --seed S --param k=v ... -o inst.cnf
  python3 -m satlab solve inst.cnf [--model m.txt] [--proof p.drup] [--json]
  python3 -m satlab verify inst.cnf (--model m.txt | --proof p.drup)
  python3 -m satlab crosscheck --count 500 --max-vars 24
  python3 -m satlab bench --campaign standard --out results
"""

import argparse
import json
import random
import sys

from . import bench, cdcl, checker, generators, reference
from .dimacs import format_model, read_dimacs


def _parse_params(items):
    out = {}
    for it in items or []:
        k, v = it.split("=", 1)
        try:
            out[k] = int(v)
        except ValueError:
            out[k] = float(v)
    return out


def cmd_gen(a):
    cnf, meta = generators.generate(a.family, seed=a.seed, **_parse_params(a.param))
    text = cnf.to_dimacs()
    if a.output:
        with open(a.output, "w") as f:
            f.write(text)
        print(json.dumps(dict(meta, sha256=cnf.sha256(), num_vars=cnf.num_vars,
                              num_clauses=cnf.num_clauses), ensure_ascii=False))
    else:
        sys.stdout.write(text)
    return 0


def cmd_solve(a):
    cnf = read_dimacs(a.cnf)
    res = cdcl.solve(cnf, seed=a.seed, max_conflicts=a.max_conflicts, emit_proof=bool(a.proof))
    if res.status == "SAT" and a.model:
        with open(a.model, "w") as f:
            f.write(format_model(res.model))
    if res.status == "UNSAT" and a.proof:
        with open(a.proof, "w") as f:
            f.write("\n".join(res.proof) + "\n")
    if a.json:
        print(json.dumps(dict(status=res.status, sha256=cnf.sha256(), stats=res.stats)))
    else:
        print("s " + {"SAT": "SATISFIABLE", "UNSAT": "UNSATISFIABLE"}.get(res.status, "UNKNOWN"))
        for k, v in res.stats.items():
            print("c %s = %s" % (k, v))
        if res.status == "SAT" and not a.model:
            print("v " + " ".join(map(str, res.model)) + " 0")
    return {"SAT": 10, "UNSAT": 20}.get(res.status, 0)


SAT_THRESHOLD_BAND = {2: (0.6, 1.6), 3: (3.0, 6.0), 4: (7.0, 13.0)}


def cmd_crosscheck(a):
    """Contre-tests : CDCL vs oracle (force brute <= 12 vars, DPLL au-delà)
    + vérification de chaque certificat,
    puis mutations de certificats qui DOIVENT être rejetées."""
    rng = random.Random(a.seed)
    disagreements = cert_failures = mutants_accepted = mutants = 0
    stats = dict(sat=0, unsat=0, conflicts=0, with_deletions=0, oracle_dpll=0)
    for i in range(a.count):
        n = rng.randint(4, max(4, a.max_vars))
        k = rng.choice([2, 3, 3, 3, 4])
        # densités autour du seuil de chaque k : là où les instances sont dures
        lo, hi = SAT_THRESHOLD_BAND[k]
        m = round(rng.uniform(lo, hi) * n)
        cnf, _ = generators.random_ksat(n, m, k, seed=rng.randrange(1 << 30))
        res = cdcl.solve(cnf, seed=i, max_learnts=rng.choice([2, 8, None]),
                         restart_unit=rng.choice([1, 4, 100]))
        if n <= 12:
            sat, _, _ = reference.brute_force(n, cnf.clauses)
        else:
            sat, _, _ = reference.dpll(n, cnf.clauses)
            stats["oracle_dpll"] += 1
        stats["sat" if res.status == "SAT" else "unsat"] += 1
        stats["conflicts"] += res.stats["conflicts"]
        stats["with_deletions"] += res.stats["deleted"] > 0
        if (res.status == "SAT") != sat:
            disagreements += 1
            print("DÉSACCORD instance %d (sha %s)" % (i, cnf.sha256()))
        if res.status == "SAT":
            ok, _ = checker.check_model(n, cnf.clauses, res.model)
            # mutation : inverser un littéral ; rejet attendu si plus aucun modèle
            # ne passe -> on ne compte que les mutants réellement invalides.
            j = rng.randrange(n)
            mut = list(res.model)
            mut[j] = -mut[j]
            truly_bad = not all(any(l in mut for l in c) for c in cnf.clauses)
            if truly_bad:
                mutants += 1
                mutants_accepted += checker.check_model(n, cnf.clauses, mut)[0]
        else:
            steps = checker._parse_proof("\n".join(res.proof))
            ok, _ = checker.check_proof(n, cnf.clauses, steps)
            # mutation : retirer une clause d'origine qui sert ; la même preuve
            # ne doit plus être acceptée si la formule réduite est SAT.
            if cnf.clauses:
                drop = rng.randrange(len(cnf.clauses))
                rest = cnf.clauses[:drop] + cnf.clauses[drop + 1:]
                if reference.dpll(n, rest)[0]:
                    mutants += 1
                    mutants_accepted += checker.check_proof(n, rest, steps)[0]
        cert_failures += not ok
    print(json.dumps(dict(instances=a.count, disagreements=disagreements,
                          certificate_failures=cert_failures, mutants=mutants,
                          mutants_wrongly_accepted=mutants_accepted, **stats)))
    return 0 if disagreements == cert_failures == mutants_accepted == 0 else 1


def cmd_bench(a):
    seeds = range(a.seeds) if a.seeds else None
    bench.run_campaign(a.campaign, out_dir=a.out, seeds=seeds, max_conflicts=a.max_conflicts,
                       artifact_dir=a.artifacts, only=a.only)
    print("Résultats écrits dans %s/ (runs.csv, summary.json, REPORT.md)" % a.out)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="satlab")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("gen", help="générer une instance")
    g.add_argument("family", choices=sorted(generators.FAMILIES))
    g.add_argument("--seed", type=int, default=0)
    g.add_argument("--param", action="append", metavar="K=V")
    g.add_argument("-o", "--output")
    g.set_defaults(fn=cmd_gen)

    s = sub.add_parser("solve", help="résoudre une instance DIMACS")
    s.add_argument("cnf")
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--max-conflicts", type=int)
    s.add_argument("--model")
    s.add_argument("--proof")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_solve)

    v = sub.add_parser("verify", help="vérifier un certificat (vérificateur autonome)")
    v.add_argument("cnf")
    grp = v.add_mutually_exclusive_group(required=True)
    grp.add_argument("--model")
    grp.add_argument("--proof")
    v.set_defaults(fn=lambda a: checker.main(
        [a.cnf] + (["--model", a.model] if a.model else ["--proof", a.proof])))

    c = sub.add_parser("crosscheck", help="contre-tests contre des solveurs de référence")
    c.add_argument("--count", type=int, default=500)
    c.add_argument("--max-vars", type=int, default=24)
    c.add_argument("--seed", type=int, default=0)
    c.set_defaults(fn=cmd_crosscheck)

    b = sub.add_parser("bench", help="lancer une campagne")
    b.add_argument("--campaign", default="standard", choices=sorted(bench.CAMPAIGNS))
    b.add_argument("--out", default="results")
    b.add_argument("--seeds", type=int, help="remplace le nombre de graines")
    b.add_argument("--max-conflicts", type=int, default=bench.DEFAULT_MAX_CONFLICTS)
    b.add_argument("--artifacts", help="dossier où écrire instances et certificats")
    b.add_argument("--only", nargs="*", help="sous-ensemble d'expériences")
    b.set_defaults(fn=cmd_bench)

    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
