import os
import random
import subprocess
import sys
import tempfile
import unittest

from satlab import bench, cdcl, checker, generators, reference
from satlab.dimacs import format_model, parse_dimacs

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def certify(cnf, res):
    if res.status == "SAT":
        return checker.check_model(cnf.num_vars, cnf.clauses, res.model)
    return checker.check_proof(cnf.num_vars, cnf.clauses,
                               checker._parse_proof("\n".join(res.proof)))


class TestDimacs(unittest.TestCase):
    def test_roundtrip_and_hash(self):
        cnf, _ = generators.random_ksat(10, 30, seed=3)
        back = parse_dimacs(cnf.to_dimacs())
        self.assertEqual(back.clauses, cnf.clauses)
        self.assertEqual(back.sha256(), cnf.sha256())

    def test_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            parse_dimacs("p cnf 2 1\n1 3 0\n")


class TestGenerators(unittest.TestCase):
    def test_deterministic(self):
        for fam, kw in [("random_ksat", dict(n=20, m=80)), ("tseitin", dict(n=10)),
                        ("coloring", dict(n=12, k=3, avg_degree=4)),
                        ("planted_ksat", dict(n=20, m=80)), ("pigeonhole", dict(holes=4))]:
            a, _ = generators.generate(fam, seed=7, **kw)
            b, _ = generators.generate(fam, seed=7, **kw)
            self.assertEqual(a.sha256(), b.sha256(), fam)

    def test_meta_params_match_call_params(self):
        # l'axe d'une campagne est lu dans méta["params"] : les noms doivent
        # être ceux des arguments, jamais écrasés par une grandeur dérivée
        cases = [("tseitin", dict(n=10, d=3)), ("pigeonhole", dict(holes=4)),
                 ("coloring", dict(n=12, k=3, avg_degree=4)),
                 ("random_ksat", dict(n=20, m=80, k=3))]
        for fam, kw in cases:
            _, meta = generators.generate(fam, seed=1, **kw)
            for k, v in kw.items():
                self.assertEqual(meta["params"][k], v, (fam, k))

    def test_planted_hidden_model_satisfies(self):
        cnf, meta = generators.planted_ksat(40, 200, seed=1)
        self.assertTrue(checker.check_model(cnf.num_vars, cnf.clauses, meta["hidden"])[0])

    def test_small_expected_status_by_brute_force(self):
        cases = [generators.pigeonhole(3), generators.tseitin(6, seed=2)]
        for cnf, meta in cases:
            sat, _, _ = reference.brute_force(cnf.num_vars, cnf.clauses)
            self.assertEqual("SAT" if sat else "UNSAT", meta["expected"])


class TestSolverAgainstOracles(unittest.TestCase):
    def test_random_formulas_vs_brute_force(self):
        rng = random.Random(0)
        for i in range(300):
            n = rng.randint(1, 10)
            k = rng.randint(1, min(4, n))
            cnf, _ = generators.random_ksat(n, rng.randint(0, 6 * n), k, seed=i)
            # petites bases apprises et redémarrages fréquents : exerce les
            # suppressions DRUP et le retour au niveau 0
            res = cdcl.solve(cnf, seed=i, max_learnts=rng.choice([3, 10, None]),
                             restart_unit=rng.choice([1, 5, 100]))
            sat, _, _ = reference.brute_force(n, cnf.clauses)
            self.assertEqual(res.status == "SAT", sat, i)
            ok, msg = certify(cnf, res)
            self.assertTrue(ok, msg)

    def test_dpll_agrees(self):
        for s in range(30):
            cnf, _ = generators.random_ksat(30, 128, seed=s)
            res = cdcl.solve(cnf, seed=s)
            st, model, _ = reference.dpll(cnf.num_vars, cnf.clauses)
            self.assertEqual(res.status == "SAT", st)
            if st:
                self.assertTrue(checker.check_model(cnf.num_vars, cnf.clauses, model)[0])

    def test_unsat_families_certified(self):
        for cnf, _ in [generators.pigeonhole(5), generators.tseitin(16, seed=1),
                       generators.pigeonhole(4, seed=3)]:
            res = cdcl.solve(cnf, seed=0, max_learnts=50)
            self.assertEqual(res.status, "UNSAT")
            self.assertTrue(certify(cnf, res)[0])

    def test_edge_cases(self):
        self.assertEqual(cdcl.CDCLSolver(1, [[]]).solve().status, "UNSAT")
        self.assertEqual(cdcl.CDCLSolver(1, [[1], [-1]]).solve().status, "UNSAT")
        r = cdcl.CDCLSolver(3, []).solve()
        self.assertEqual(r.status, "SAT")
        self.assertEqual(len(r.model), 3)
        self.assertEqual(cdcl.CDCLSolver(2, [[1, -1], [2, 2]]).solve().status, "SAT")

    def test_budget_gives_unknown(self):
        cnf, _ = generators.pigeonhole(7)
        self.assertEqual(cdcl.solve(cnf, max_conflicts=10).status, "UNKNOWN")

    def test_luby(self):
        self.assertEqual([cdcl.luby(i) for i in range(1, 16)],
                         [1, 1, 2, 1, 1, 2, 4, 1, 1, 2, 1, 1, 2, 4, 8])


class TestCheckerSoundness(unittest.TestCase):
    """Le vérificateur doit REJETER les faux certificats."""

    def test_rejects_wrong_model(self):
        self.assertFalse(checker.check_model(2, [[1, 2], [-1]], [1, 2])[0])
        self.assertFalse(checker.check_model(2, [[1, 2]], [1, -1])[0])  # incohérent

    def test_rejects_non_rup_lemma(self):
        # formule SAT ; le "lemme" 1 n'est pas conséquence par RUP
        steps = checker._parse_proof("1 0\n-1 0\n0\n")
        self.assertFalse(checker.check_proof(2, [[1, 2], [-1, 2]], steps)[0])

    def test_rejects_proof_without_empty_clause(self):
        steps = checker._parse_proof("2 0\n")
        self.assertFalse(checker.check_proof(2, [[1, 2], [-1, 2]], steps)[0])

    def test_deletion_is_honoured(self):
        # {x}, {-x} : RUP de la clause vide ; après suppression de {x}, plus possible
        self.assertTrue(checker.check_proof(1, [[1], [-1]], checker._parse_proof("0\n"))[0])
        self.assertFalse(checker.check_proof(1, [[1], [-1]], checker._parse_proof("d 1 0\n0\n"))[0])

    def test_proof_reused_on_weakened_formula_is_rejected(self):
        cnf, _ = generators.pigeonhole(4)
        res = cdcl.solve(cnf)
        steps = checker._parse_proof("\n".join(res.proof))
        self.assertTrue(checker.check_proof(cnf.num_vars, cnf.clauses, steps)[0])
        weakened = cnf.clauses[1:]          # retire la clause du pigeon 0 : PHP(4,4) SAT
        self.assertFalse(checker.check_proof(cnf.num_vars, weakened, steps)[0])


class TestBench(unittest.TestCase):
    def test_growth_fit_detects_shapes(self):
        xs = list(range(5, 30, 3))
        self.assertEqual(bench.growth_fit(xs, [2 ** x for x in xs])["better"], "exponential")
        self.assertEqual(bench.growth_fit(xs, [x ** 3 for x in xs])["better"], "polynomial")
        # deux points quasi alignés pour les deux modèles : pas de verdict
        near = bench.growth_fit([10, 11, 12], [100, 110, 121])
        self.assertEqual(near["better"], "inconclusive")

    def test_run_instance_row(self):
        row = bench.run_instance("pigeonhole", dict(holes=4), 0)
        self.assertEqual(row["status"], "UNSAT")
        self.assertTrue(row["cert_ok"])
        self.assertTrue(row["expected_ok"])
        self.assertTrue(row["ref_agree"])


class TestCLI(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "satlab"] + list(args), cwd=ROOT,
                              capture_output=True, text=True)

    def test_gen_solve_verify_pipeline(self):
        with tempfile.TemporaryDirectory() as d:
            cnf = os.path.join(d, "php.cnf")
            proof = os.path.join(d, "php.drup")
            self.assertEqual(self.run_cli("gen", "pigeonhole", "--param", "holes=4",
                                          "-o", cnf).returncode, 0)
            self.assertEqual(self.run_cli("solve", cnf, "--proof", proof).returncode, 20)
            # vérificateur exécuté comme script isolé, hors paquet
            r = subprocess.run([sys.executable, os.path.join(ROOT, "satlab", "checker.py"),
                                cnf, "--proof", proof], capture_output=True, text=True, cwd=d)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("VERIFIED", r.stdout)

            cnf2 = os.path.join(d, "pl.cnf")
            model = os.path.join(d, "pl.model")
            self.run_cli("gen", "planted_ksat", "--param", "n=30", "--param", "m=120", "-o", cnf2)
            self.assertEqual(self.run_cli("solve", cnf2, "--model", model).returncode, 10)
            self.assertEqual(self.run_cli("verify", cnf2, "--model", model).returncode, 0)
            # modèle qui falsifie la première clause : doit être rejeté
            first = parse_dimacs(open(cnf2).read()).clauses[0]
            bad = {abs(l): -l for l in first}
            with open(model, "w") as f:
                f.write(format_model([bad.get(v, v) for v in range(1, 31)]))
            r = self.run_cli("verify", cnf2, "--model", model)
            self.assertEqual(r.returncode, 1)
            self.assertIn("REJECTED", r.stdout)


if __name__ == "__main__":
    unittest.main()
