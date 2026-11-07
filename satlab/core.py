"""Cœurs insatisfiables : extraction d'un MUS et test de minimalité.

Un MUS (minimal unsatisfiable subset) est un ensemble de clauses UNSAT dont
chaque sous-ensemble strict est SAT. Il suffit de vérifier que retirer
n'importe quelle clause seule rend la formule SAT (la satisfiabilité est
monotone pour l'inclusion). Les appels SAT passent par le CDCL. Chaque
verdict SAT est validé par le modèle renvoyé ; avec certify=True (défaut),
chaque verdict UNSAT est validé par une preuve DRUP passée au vérificateur
autonome, conformément à la règle « tout résultat est certifié ».
"""

from . import cdcl, checker


def _sat(num_vars, clauses, certify=True):
    res = cdcl.CDCLSolver(num_vars, clauses, emit_proof=certify).solve()
    if res.status == "SAT":
        ok, msg = checker.check_model(num_vars, clauses, res.model)
        if not ok:
            raise AssertionError("modèle invalide renvoyé par le CDCL : " + msg)
        return True
    if res.status == "UNSAT":
        if certify:
            ok, msg = checker.check_proof(num_vars, clauses,
                                          checker._parse_proof("\n".join(res.proof)))
            if not ok:
                raise AssertionError("preuve UNSAT rejetée : " + msg)
        return False
    raise RuntimeError("budget épuisé")


def shrink_to_mus(num_vars, clauses, order=None, certify=True):
    """Extraction par suppression : renvoie les indices d'un MUS de `clauses`.

    `order` fixe l'ordre dans lequel on tente de retirer les clauses (par
    défaut l'ordre d'origine) ; des ordres différents peuvent donner des MUS
    différents.
    """
    if order is not None and sorted(order) != list(range(len(clauses))):
        raise ValueError("order doit être une permutation des indices de clauses")
    if _sat(num_vars, clauses, certify):
        raise ValueError("la formule est satisfiable : pas de cœur")
    keep = set(range(len(clauses)))
    for i in (order if order is not None else range(len(clauses))):
        trial = keep - {i}
        if not _sat(num_vars, [clauses[j] for j in sorted(trial)], certify):
            keep = trial
    return sorted(keep)


def redundant_clauses(num_vars, clauses, certify=True):
    """Indices des clauses dont le retrait (seul) laisse la formule UNSAT."""
    return [i for i in range(len(clauses))
            if not _sat(num_vars, clauses[:i] + clauses[i + 1:], certify)]


def is_mus(num_vars, clauses, certify=True):
    return (not _sat(num_vars, clauses, certify)
            and not redundant_clauses(num_vars, clauses, certify))


def certify_unsat(num_vars, clauses):
    """Preuve DRUP de l'insatisfiabilité, vérifiée par le vérificateur autonome."""
    res = cdcl.CDCLSolver(num_vars, clauses).solve()
    if res.status != "UNSAT":
        raise ValueError("formule non réfutée : %s" % res.status)
    ok, msg = checker.check_proof(num_vars, clauses, checker._parse_proof("\n".join(res.proof)))
    if not ok:
        raise AssertionError(msg)
    return res.proof
