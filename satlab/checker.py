#!/usr/bin/env python3
"""Vérificateur de certificats SAT/UNSAT AUTONOME.

Ce fichier n'importe volontairement aucun autre module de satlab : il peut
être copié seul et exécuté pour contrôler un résultat sans faire confiance
au solveur (ni au générateur, ni au parseur du paquet).

  python3 checker.py instance.cnf --model model.txt   # certificat SAT
  python3 checker.py instance.cnf --proof proof.drup  # certificat UNSAT

Certificat SAT : chaque clause contient un littéral vrai du modèle, et le
modèle est cohérent (jamais x et -x).

Certificat UNSAT : preuve DRUP (Reverse Unit Propagation avec suppressions).
Chaque lemme L doit être RUP vis-à-vis de la base courante : propager
unitairement la négation de L doit produire un conflit. La preuve doit
dériver la clause vide. RUP implique la conséquence logique, donc une preuve
acceptée établit l'insatisfiabilité de la formule d'origine.
"""

import sys


def _parse_cnf(text):
    nv, clauses, cur = None, [], []
    for line in text.splitlines():
        line = line.strip()
        if not line or line[0] == "c":
            continue
        if line[0] == "p":
            nv = int(line.split()[2])
            continue
        if line[0] == "%":
            break
        for tok in line.split():
            v = int(tok)
            if v == 0:
                clauses.append(cur)
                cur = []
            else:
                cur.append(v)
    if cur:
        clauses.append(cur)
    if nv is None:
        raise ValueError("en-tête 'p cnf' manquant")
    return nv, clauses


def _parse_model(text):
    lits = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line[0] in "cs":
            continue
        if line[0] == "v":
            line = line[1:]
        lits.extend(int(t) for t in line.split() if t != "0")
    return lits


def _parse_proof(text):
    """Renvoie une liste de (is_delete, clause)."""
    steps = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line[0] == "c":
            continue
        delete = line[0] == "d"
        if delete:
            line = line[1:]
        lits = [int(t) for t in line.split()]
        if not lits or lits[-1] != 0:
            raise ValueError("ligne de preuve non terminée par 0 : %r" % line)
        steps.append((delete, lits[:-1]))
    return steps


def check_model(num_vars, clauses, model):
    """Renvoie (ok, message)."""
    val = {}
    for lit in model:
        if lit == 0 or abs(lit) > num_vars:
            return False, "littéral %d hors domaine" % lit
        if val.get(abs(lit), lit > 0) != (lit > 0):
            return False, "modèle incohérent sur la variable %d" % abs(lit)
        val[abs(lit)] = lit > 0
    for i, c in enumerate(clauses):
        if not any(val.get(abs(l)) == (l > 0) for l in c):
            return False, "clause %d non satisfaite : %s" % (i + 1, c)
    return True, "modèle valide (%d clauses satisfaites)" % len(clauses)


class _RupDB:
    """Base de clauses à deux littéraux surveillés, robuste au retour arrière."""

    def __init__(self):
        self.clauses = []   # id -> liste de littéraux, None si supprimée
        self.watches = {}   # littéral -> ids de clauses
        self.units = {}     # id -> littéral, pour les clauses unitaires
        self.index = {}     # clé triée -> ids vivants (multiensemble)
        self.has_empty = 0

    def add(self, clause):
        c = sorted(set(clause), key=lambda l: (abs(l), l))
        cid = len(self.clauses)
        self.clauses.append(c)
        self.index.setdefault(tuple(c), []).append(cid)
        if not c:
            self.has_empty += 1
        elif len(c) == 1:
            self.units[cid] = c[0]
        else:
            self.watches.setdefault(c[0], []).append(cid)
            self.watches.setdefault(c[1], []).append(cid)

    def delete(self, clause):
        key = tuple(sorted(set(clause), key=lambda l: (abs(l), l)))
        ids = self.index.get(key)
        if not ids:
            return False
        cid = ids.pop()
        if not self.clauses[cid]:
            self.has_empty -= 1
        self.clauses[cid] = None
        self.units.pop(cid, None)
        return True

    def rup(self, lemma):
        """Vrai si la propagation unitaire de ¬lemma atteint un conflit."""
        if self.has_empty:
            return True
        assign = {}
        trail = []

        def enqueue(lit):
            v = assign.get(abs(lit))
            if v is None:
                assign[abs(lit)] = lit > 0
                trail.append(lit)
                return True
            return v == (lit > 0)

        for lit in lemma:
            if not enqueue(-lit):
                return True  # lemme tautologique
        for lit in self.units.values():
            if not enqueue(lit):
                return True

        def value(lit):
            v = assign.get(abs(lit))
            return None if v is None else v == (lit > 0)

        q = 0
        while q < len(trail):
            false_lit = -trail[q]
            q += 1
            ws = self.watches.get(false_lit)
            if not ws:
                continue
            keep = []
            conflict = False
            for i, cid in enumerate(ws):
                c = self.clauses[cid]
                if c is None:
                    continue  # suppression paresseuse
                if conflict:
                    keep.append(cid)
                    continue
                if c[0] == false_lit:
                    c[0], c[1] = c[1], c[0]
                if value(c[0]) is True:
                    keep.append(cid)
                    continue
                moved = False
                for k in range(2, len(c)):
                    if value(c[k]) is not False:
                        c[1], c[k] = c[k], c[1]
                        self.watches.setdefault(c[1], []).append(cid)
                        moved = True
                        break
                if moved:
                    continue
                keep.append(cid)
                if value(c[0]) is False:
                    conflict = True
                else:
                    enqueue(c[0])
            self.watches[false_lit] = keep
            if conflict:
                return True
        return False


def check_proof(num_vars, clauses, steps):
    """Vérifie une preuve DRUP. Renvoie (ok, message)."""
    db = _RupDB()
    for c in clauses:
        db.add(c)
    lemmas = deletions = 0
    for n, (delete, lits) in enumerate(steps, 1):
        if any(lit == 0 or abs(lit) > num_vars for lit in lits):
            return False, "étape %d : littéral hors domaine" % n
        if delete:
            db.delete(lits)  # supprimer une clause absente est inoffensif
            deletions += 1
            continue
        if not db.rup(lits):
            return False, "étape %d : lemme %s non RUP" % (n, lits)
        lemmas += 1
        db.add(lits)
        if not lits:
            return True, "preuve valide (%d lemmes, %d suppressions)" % (lemmas, deletions)
    if db.rup([]):
        return True, "preuve valide (%d lemmes, %d suppressions ; clause vide par RUP)" % (
            lemmas, deletions)
    return False, "la preuve ne dérive pas la clause vide"


def main(argv=None):
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cnf")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--model")
    g.add_argument("--proof")
    args = ap.parse_args(argv)
    with open(args.cnf) as f:
        nv, clauses = _parse_cnf(f.read())
    if args.model:
        with open(args.model) as f:
            ok, msg = check_model(nv, clauses, _parse_model(f.read()))
    else:
        with open(args.proof) as f:
            ok, msg = check_proof(nv, clauses, _parse_proof(f.read()))
    print(("VERIFIED " if ok else "REJECTED ") + msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
