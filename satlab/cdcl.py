"""Solveur exact CDCL instrumenté.

Composants : deux littéraux surveillés, apprentissage 1-UIP, heuristique
VSIDS (tas paresseux), sauvegarde de phase, redémarrages de Luby, réduction
de la base apprise par LBD. Chaque clause apprise / supprimée est écrite dans
une preuve DRUP vérifiable par satlab.checker, sans faire confiance au
solveur.

Toutes les décisions sont déterministes à graine fixée (ordre initial des
variables mélangé par random.Random(seed)).
"""

import heapq
import random
import time

SAT, UNSAT, UNKNOWN = "SAT", "UNSAT", "UNKNOWN"


def luby(i):
    """i-ème terme (1-indexé) de la suite de Luby : 1 1 2 1 1 2 4 ..."""
    k = 1
    while (1 << k) - 1 < i:
        k += 1
    while True:
        if i == (1 << k) - 1:
            return 1 << (k - 1)
        i -= (1 << (k - 1)) - 1
        k = 1
        while (1 << k) - 1 < i:
            k += 1


class Result:
    __slots__ = ("status", "model", "stats", "proof")

    def __init__(self, status, model, stats, proof):
        self.status = status
        self.model = model      # liste de littéraux si SAT
        self.stats = stats      # dict de mesures
        self.proof = proof      # liste de lignes DRUP (ou None)


class CDCLSolver:
    def __init__(self, num_vars, clauses, seed=0, emit_proof=True,
                 max_conflicts=None, restart_unit=100, var_decay=0.95,
                 max_learnts=None):
        self.n = num_vars
        self.rng = random.Random(seed)
        self.emit_proof = emit_proof
        self.proof = [] if emit_proof else None
        self.max_conflicts = max_conflicts
        self.restart_unit = restart_unit
        self.var_decay = var_decay
        self.max_learnts = max_learnts

        self.assign = [0] * (num_vars + 1)     # 0 / +1 / -1
        self.level = [0] * (num_vars + 1)
        self.reason = [None] * (num_vars + 1)
        self.phase = [-1] * (num_vars + 1)
        self.activity = [0.0] * (num_vars + 1)
        self.var_inc = 1.0
        self.trail, self.trail_lim = [], []
        self.qhead = 0

        self.clauses = []          # id -> liste de littéraux, None si supprimée
        self.learnt_ids = []
        self.lbd = {}
        self.watches = {}
        for v in range(1, num_vars + 1):
            self.watches[v] = []
            self.watches[-v] = []

        order = list(range(1, num_vars + 1))
        self.rng.shuffle(order)
        # Petites activités initiales aléatoires : départage déterministe.
        for rank, v in enumerate(order):
            self.activity[v] = 1e-6 * (num_vars - rank)
        self.heap = [(-self.activity[v], v) for v in order]
        heapq.heapify(self.heap)

        self.stats = dict(decisions=0, propagations=0, conflicts=0,
                          restarts=0, learned=0, learned_lits=0, lbd_sum=0,
                          deleted=0, max_level=0, units_learned=0)
        self.ok = True
        for c in clauses:
            if not self._add_input(c):
                self.ok = False
                break

    # -- utilitaires ----------------------------------------------------
    def _val(self, lit):
        a = self.assign[lit if lit > 0 else -lit]
        return a if lit > 0 else -a

    def _decision_level(self):
        return len(self.trail_lim)

    def _enqueue(self, lit, reason):
        v = abs(lit)
        self.assign[v] = 1 if lit > 0 else -1
        self.level[v] = len(self.trail_lim)
        self.reason[v] = reason
        self.trail.append(lit)

    def _log(self, lits, delete=False):
        if self.emit_proof:
            self.proof.append(("d " if delete else "") + " ".join(map(str, lits)) +
                              (" 0" if lits else "0"))

    def _add_input(self, clause):
        lits = []
        seen = set()
        for lit in clause:
            if -lit in seen:
                return True          # tautologie : ignorée
            if lit not in seen:
                seen.add(lit)
                lits.append(lit)
        if not lits:
            return False
        if len(lits) == 1:
            val = self._val(lits[0])
            if val == -1:
                return False
            if val == 0:
                self._enqueue(lits[0], None)
            return True
        cid = len(self.clauses)
        self.clauses.append(lits)
        self.watches[lits[0]].append(cid)
        self.watches[lits[1]].append(cid)
        return True

    # -- propagation ----------------------------------------------------
    def _propagate(self):
        clauses, watches, assign = self.clauses, self.watches, self.assign
        props = 0
        conflict = None
        while self.qhead < len(self.trail):
            p = self.trail[self.qhead]
            self.qhead += 1
            props += 1
            false_lit = -p
            ws = watches[false_lit]
            i = j = 0
            n = len(ws)
            while i < n:
                cid = ws[i]
                i += 1
                c = clauses[cid]
                if c is None:
                    continue
                if c[0] == false_lit:
                    c[0], c[1] = c[1], c[0]
                first = c[0]
                fv = assign[first] if first > 0 else -assign[-first]
                if fv == 1:
                    ws[j] = cid
                    j += 1
                    continue
                for k in range(2, len(c)):
                    lk = c[k]
                    if (assign[lk] if lk > 0 else -assign[-lk]) != -1:
                        c[1], c[k] = lk, c[1]
                        watches[lk].append(cid)
                        break
                else:
                    ws[j] = cid
                    j += 1
                    if fv == -1:
                        conflict = cid
                        while i < n:
                            ws[j] = ws[i]
                            j += 1
                            i += 1
                    else:
                        self._enqueue(first, cid)
            del ws[j:]
            if conflict is not None:
                break
        self.stats["propagations"] += props
        return conflict

    # -- analyse de conflit ---------------------------------------------
    def _bump(self, v):
        self.activity[v] += self.var_inc
        if self.activity[v] > 1e100:
            for u in range(1, self.n + 1):
                self.activity[u] *= 1e-100
            self.var_inc *= 1e-100
            self.heap = [(-self.activity[u], u) for u in range(1, self.n + 1)
                         if self.assign[u] == 0]
            heapq.heapify(self.heap)
        elif self.assign[v] == 0:
            heapq.heappush(self.heap, (-self.activity[v], v))

    def _analyze(self, confl):
        dl = self._decision_level()
        seen = [False] * (self.n + 1)
        learnt = [0]
        counter = 0
        p = None
        idx = len(self.trail) - 1
        clause = self.clauses[confl]
        while True:
            for q in clause:
                if q == p:
                    continue
                v = abs(q)
                if not seen[v] and self.level[v] > 0:
                    seen[v] = True
                    self._bump(v)
                    if self.level[v] == dl:
                        counter += 1
                    else:
                        learnt.append(q)
            while not seen[abs(self.trail[idx])]:
                idx -= 1
            p = self.trail[idx]
            idx -= 1
            seen[abs(p)] = False
            counter -= 1
            if counter == 0:
                break
            clause = self.clauses[self.reason[abs(p)]]
        learnt[0] = -p
        if len(learnt) == 1:
            bt = 0
        else:
            best = max(range(1, len(learnt)), key=lambda k: self.level[abs(learnt[k])])
            learnt[1], learnt[best] = learnt[best], learnt[1]
            bt = self.level[abs(learnt[1])]
        lbd = len({self.level[abs(l)] for l in learnt})
        self.var_inc /= self.var_decay
        return learnt, bt, lbd

    def _backtrack(self, lvl):
        if self._decision_level() <= lvl:
            return
        lim = self.trail_lim[lvl]
        for k in range(len(self.trail) - 1, lim - 1, -1):
            lit = self.trail[k]
            v = abs(lit)
            self.phase[v] = 1 if lit > 0 else -1
            self.assign[v] = 0
            self.reason[v] = None
            heapq.heappush(self.heap, (-self.activity[v], v))
        del self.trail[lim:]
        del self.trail_lim[lvl:]
        self.qhead = lim

    def _pick(self):
        heap = self.heap
        while heap:
            negact, v = heapq.heappop(heap)
            if self.assign[v] == 0 and -negact == self.activity[v]:
                return v
        for v in range(1, self.n + 1):   # filet de sécurité (tas vidé)
            if self.assign[v] == 0:
                return v
        return 0

    # -- réduction de la base apprise -----------------------------------
    def _locked(self, cid):
        c = self.clauses[cid]
        v = abs(c[0])
        return self.reason[v] == cid and self._val(c[0]) == 1

    def _reduce_db(self):
        live = [cid for cid in self.learnt_ids if self.clauses[cid] is not None]
        live.sort(key=lambda cid: (self.lbd[cid], len(self.clauses[cid])))
        keep_n = len(live) // 2
        kept = live[:keep_n]
        for cid in live[keep_n:]:
            if self.lbd[cid] <= 2 or self._locked(cid):
                kept.append(cid)
                continue
            self._log(self.clauses[cid], delete=True)
            self.clauses[cid] = None
            del self.lbd[cid]
            self.stats["deleted"] += 1
        self.learnt_ids = kept

    # -- boucle principale ----------------------------------------------
    def solve(self):
        t0 = time.perf_counter()
        status = self._search() if self.ok else UNSAT
        if status == UNSAT and self.emit_proof:
            self._log([])
        self.stats["time_s"] = time.perf_counter() - t0
        st = self.stats
        st["avg_learned_len"] = st["learned_lits"] / st["learned"] if st["learned"] else 0.0
        st["avg_lbd"] = st["lbd_sum"] / st["learned"] if st["learned"] else 0.0
        model = None
        if status == SAT:
            model = [v if self.assign[v] == 1 else -v for v in range(1, self.n + 1)]
        return Result(status, model, dict(st), self.proof)

    def _search(self):
        if self._propagate() is not None:
            return UNSAT
        restart_idx = 1
        budget = luby(restart_idx) * self.restart_unit
        conflicts_since_restart = 0
        max_learnts = self.max_learnts or max(len(self.clauses) // 3, 2000)
        while True:
            confl = self._propagate()
            if confl is not None:
                self.stats["conflicts"] += 1
                conflicts_since_restart += 1
                if self._decision_level() == 0:
                    return UNSAT
                learnt, bt, lbd = self._analyze(confl)
                self._backtrack(bt)
                self._log(learnt)
                self.stats["learned"] += 1
                self.stats["learned_lits"] += len(learnt)
                self.stats["lbd_sum"] += lbd
                if len(learnt) == 1:
                    self.stats["units_learned"] += 1
                    self._enqueue(learnt[0], None)
                else:
                    cid = len(self.clauses)
                    self.clauses.append(learnt)
                    self.watches[learnt[0]].append(cid)
                    self.watches[learnt[1]].append(cid)
                    self.learnt_ids.append(cid)
                    self.lbd[cid] = lbd
                    self._enqueue(learnt[0], cid)
                if self.max_conflicts is not None and self.stats["conflicts"] >= self.max_conflicts:
                    return UNKNOWN
                continue
            if conflicts_since_restart >= budget:
                self.stats["restarts"] += 1
                restart_idx += 1
                budget = luby(restart_idx) * self.restart_unit
                conflicts_since_restart = 0
                self._backtrack(0)
            if len(self.learnt_ids) >= max_learnts:
                self._reduce_db()
                max_learnts = int(max_learnts * 1.1)
            v = self._pick()
            if v == 0:
                return SAT
            self.stats["decisions"] += 1
            self.trail_lim.append(len(self.trail))
            if self._decision_level() > self.stats["max_level"]:
                self.stats["max_level"] = self._decision_level()
            self._enqueue(v if self.phase[v] > 0 else -v, None)


def solve(cnf, **kw):
    return CDCLSolver(cnf.num_vars, cnf.clauses, **kw).solve()
