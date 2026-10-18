"""Cœurs insatisfiables : extraction d'un MUS et test de minimalité.

Un MUS (minimal unsatisfiable subset) est un ensemble de clauses UNSAT dont
chaque sous-ensemble strict est SAT. Il suffit de vérifier que retirer
n'importe quelle clause seule rend la formule SAT (la satisfiabilité est
monotone pour l'inclusion). Les appels SAT passent par le CDCL ; chaque
verdict SAT est accompagné d'un modèle vérifié, et le verdict UNSAT final du
MUS peut être certifié par une preuve DRUP (`certify=True`).
"""

from . import cdcl, checker


def _sat(num_vars, clauses):
    res = cdcl.CDCLSolver(num_vars, clauses, emit_proof=False).solve()
    if res.status == "SAT":
        ok, msg = checker.check_model(num_vars, clauses, res.model)
        if not ok:
            raise AssertionError("modèle invalide renvoyé par le CDCL : " + msg)
        return True
    if res.status == "UNSAT":
        return False
    raise RuntimeError("budget épuisé")


def shrink_to_mus(num_vars, clauses, order=None):
    """Extraction par suppression : renvoie les indices d'un MUS de `clauses`.

    `order` fixe l'ordre dans lequel on tente de retirer les clauses (par
    défaut l'ordre d'origine) ; des ordres différents peuvent donner des MUS
    différents.
    """
    if _sat(num_vars, clauses):
        raise ValueError("la formule est satisfiable : pas de cœur")
    keep = set(range(len(clauses)))
    for i in (order if order is not None else range(len(clauses))):
        trial = keep - {i}
        if not _sat(num_vars, [clauses[j] for j in sorted(trial)]):
            keep = trial
    return sorted(keep)


def redundant_clauses(num_vars, clauses):
    """Indices des clauses dont le retrait (seul) laisse la formule UNSAT."""
    return [i for i in range(len(clauses))
            if not _sat(num_vars, clauses[:i] + clauses[i + 1:])]


def is_mus(num_vars, clauses):
    return not _sat(num_vars, clauses) and not redundant_clauses(num_vars, clauses)


def certify_unsat(num_vars, clauses):
    """Preuve DRUP de l'insatisfiabilité, vérifiée par le vérificateur autonome."""
    res = cdcl.CDCLSolver(num_vars, clauses).solve()
    if res.status != "UNSAT":
        raise ValueError("formule non réfutée : %s" % res.status)
    ok, msg = checker.check_proof(num_vars, clauses, checker._parse_proof("\n".join(res.proof)))
    if not ok:
        raise AssertionError(msg)
    return res.proof
