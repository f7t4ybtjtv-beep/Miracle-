"""Lecture/écriture DIMACS CNF et empreinte canonique des instances."""

import hashlib


class CNF:
    __slots__ = ("num_vars", "clauses", "comments")

    def __init__(self, num_vars, clauses, comments=None):
        self.num_vars = num_vars
        self.clauses = [list(c) for c in clauses]
        self.comments = list(comments or [])

    @property
    def num_clauses(self):
        return len(self.clauses)

    def to_dimacs(self):
        lines = ["c " + c for c in self.comments]
        lines.append("p cnf %d %d" % (self.num_vars, len(self.clauses)))
        lines.extend(" ".join(map(str, c)) + " 0" for c in self.clauses)
        return "\n".join(lines) + "\n"

    def sha256(self):
        """Empreinte indépendante des commentaires et de l'ordre des littéraux."""
        body = "p cnf %d %d\n" % (self.num_vars, len(self.clauses))
        body += "".join(
            " ".join(map(str, sorted(c, key=lambda l: (abs(l), l)))) + " 0\n"
            for c in self.clauses
        )
        return hashlib.sha256(body.encode()).hexdigest()


def parse_dimacs(text):
    num_vars = None
    declared = None
    clauses, comments, cur = [], [], []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("c"):
            comments.append(line[1:].strip())
            continue
        if line.startswith("p"):
            parts = line.split()
            if len(parts) != 4 or parts[1] != "cnf":
                raise ValueError("en-tête DIMACS invalide : %r" % line)
            num_vars, declared = int(parts[2]), int(parts[3])
            continue
        if line.startswith("%"):  # terminateur SATLIB
            break
        for tok in line.split():
            lit = int(tok)
            if lit == 0:
                clauses.append(cur)
                cur = []
            else:
                cur.append(lit)
    if cur:
        clauses.append(cur)
    if num_vars is None:
        raise ValueError("en-tête 'p cnf' manquant")
    if declared is not None and declared != len(clauses):
        raise ValueError("%d clauses déclarées, %d lues" % (declared, len(clauses)))
    for c in clauses:
        for lit in c:
            if abs(lit) > num_vars:
                raise ValueError("littéral %d hors de [1, %d]" % (lit, num_vars))
    return CNF(num_vars, clauses, comments)


def read_dimacs(path):
    with open(path) as f:
        return parse_dimacs(f.read())


def write_dimacs(cnf, path):
    with open(path, "w") as f:
        f.write(cnf.to_dimacs())


def format_model(model):
    """model : liste de littéraux (signe = valeur). Format SAT-competition."""
    return "s SATISFIABLE\nv " + " ".join(map(str, model)) + " 0\n"
