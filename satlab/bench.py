"""Campagnes d'expériences reproductibles.

Pour chaque instance : génération (graine fixée) -> empreinte SHA-256 ->
résolution CDCL instrumentée -> vérification INDÉPENDANTE du certificat
(satlab.checker) -> contrôle du statut attendu par construction ->
contre-test par solveurs de référence quand la taille le permet.

Les ajustements de croissance (exponentielle vs polynomiale) sont purement
descriptifs : ils caractérisent CE solveur sur CES tailles, et ne disent rien
en eux-mêmes de P vs NP.
"""

import csv
import json
import math
import os
import platform
import statistics
import subprocess
import time

from . import cdcl, checker, generators, reference
from .dimacs import format_model

# Chaque expérience : famille, axe de croissance (clé de params qui sert de
# "taille"), liste de jeux de paramètres, graines, budget de conflits.
CAMPAIGNS = {
    "quick": [
        dict(name="random3sat_threshold", family="random_ksat", axis="n",
             params=[dict(n=n, m=round(4.26 * n), k=3) for n in (20, 30, 40)],
             seeds=range(5)),
        dict(name="pigeonhole", family="pigeonhole", axis="holes",
             params=[dict(holes=h) for h in (3, 4, 5, 6)], seeds=range(2)),
        dict(name="tseitin_3regular", family="tseitin", axis="n",
             params=[dict(n=v, d=3) for v in (8, 12, 16)], seeds=range(3)),
    ],
    "standard": [
        dict(name="random3sat_threshold", family="random_ksat", axis="n",
             params=[dict(n=n, m=round(4.26 * n), k=3)
                     for n in (20, 30, 40, 50, 60, 70, 80, 100, 120, 150)],
             seeds=range(12)),
        dict(name="random3sat_phase_n50", family="random_ksat", axis="ratio",
             params=[dict(n=50, m=round(r * 50), k=3)
                     for r in (3.0, 3.4, 3.8, 4.0, 4.2, 4.3, 4.4, 4.6, 5.0, 5.6, 6.4)],
             seeds=range(20)),
        dict(name="planted3sat_threshold", family="planted_ksat", axis="n",
             params=[dict(n=n, m=round(4.26 * n), k=3) for n in (50, 100, 150, 200, 300)],
             seeds=range(6)),
        dict(name="pigeonhole", family="pigeonhole", axis="holes",
             params=[dict(holes=h) for h in (3, 4, 5, 6, 7, 8)], seeds=range(3)),
        dict(name="tseitin_3regular", family="tseitin", axis="n",
             params=[dict(n=v, d=3) for v in (10, 14, 18, 22, 26, 30, 34, 40, 46, 50, 56)],
             seeds=range(5)),
        dict(name="coloring3_threshold", family="coloring", axis="n",
             params=[dict(n=v, k=3, avg_degree=4.69) for v in (20, 40, 60, 80, 100)],
             seeds=range(6)),
    ],
}

BRUTE_FORCE_MAX_VARS = 16
DPLL_MAX_VARS = 60
DPLL_NODE_LIMIT = 200000
DEFAULT_MAX_CONFLICTS = 300000


def _git_commit():
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL,
                                       cwd=here).decode().strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain", "--", "."],
                                        stderr=subprocess.DEVNULL, cwd=here).decode().strip()
        return head + ("-dirty" if dirty else "")
    except Exception:
        return None


def run_instance(family, params, seed, max_conflicts=DEFAULT_MAX_CONFLICTS,
                 crosscheck=True, artifact_dir=None):
    cnf, meta = generators.generate(family, seed=seed, **params)
    sizes = [len(c) for c in cnf.clauses]
    row = dict(family=family, seed=seed, **{"p_" + k: v for k, v in meta["params"].items()})
    row.update(num_vars=cnf.num_vars, num_clauses=cnf.num_clauses,
               clause_len_mean=round(statistics.mean(sizes), 3) if sizes else 0,
               sha256=cnf.sha256(), expected=meta["expected"])

    res = cdcl.solve(cnf, seed=seed, max_conflicts=max_conflicts)
    row["status"] = res.status
    for k in ("decisions", "propagations", "conflicts", "restarts", "learned",
              "deleted", "max_level", "units_learned"):
        row[k] = res.stats[k]
    row["avg_learned_len"] = round(res.stats["avg_learned_len"], 3)
    row["avg_lbd"] = round(res.stats["avg_lbd"], 3)
    row["solve_s"] = round(res.stats["time_s"], 5)

    # Vérification indépendante : on repasse par le texte (comme un tiers).
    t0 = time.perf_counter()
    if res.status == "SAT":
        ok, msg = checker.check_model(cnf.num_vars, cnf.clauses, res.model)
        row["cert_kind"], row["cert_size"] = "model", len(res.model)
    elif res.status == "UNSAT":
        proof_text = "\n".join(res.proof) + "\n"
        ok, msg = checker.check_proof(cnf.num_vars, cnf.clauses,
                                      checker._parse_proof(proof_text))
        row["cert_kind"], row["cert_size"] = "drup", len(res.proof)
    else:
        ok, msg = None, "budget épuisé (résultat censuré)"
        row["cert_kind"], row["cert_size"] = None, 0
    row["cert_ok"] = ok
    row["cert_msg"] = msg
    row["check_s"] = round(time.perf_counter() - t0, 5)
    row["expected_ok"] = (None if meta["expected"] is None or res.status == "UNKNOWN"
                          else meta["expected"] == res.status)

    row["ref_solver"], row["ref_status"], row["ref_agree"] = None, None, None
    if crosscheck and res.status != "UNKNOWN":
        if cnf.num_vars <= BRUTE_FORCE_MAX_VARS:
            sat, _, _ = reference.brute_force(cnf.num_vars, cnf.clauses)
            row["ref_solver"], row["ref_status"] = "brute_force", "SAT" if sat else "UNSAT"
        elif cnf.num_vars <= DPLL_MAX_VARS:
            sat, _, nodes = reference.dpll(cnf.num_vars, cnf.clauses, DPLL_NODE_LIMIT)
            if sat is not None:
                row["ref_solver"], row["ref_status"] = "dpll", "SAT" if sat else "UNSAT"
                row["dpll_nodes"] = nodes
        if row["ref_status"] is not None:
            row["ref_agree"] = row["ref_status"] == res.status

    if artifact_dir:
        os.makedirs(artifact_dir, exist_ok=True)
        stem = os.path.join(artifact_dir, "%s_%s_s%d" % (
            family, "_".join("%s%s" % kv for kv in sorted(params.items())), seed))
        with open(stem + ".cnf", "w") as f:
            f.write(cnf.to_dimacs())
        if res.status == "SAT":
            with open(stem + ".model", "w") as f:
                f.write(format_model(res.model))
        elif res.status == "UNSAT":
            with open(stem + ".drup", "w") as f:
                f.write("\n".join(res.proof) + "\n")
    return row


# -- ajustements -----------------------------------------------------------
def _linfit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - a - b * x) ** 2 for x, y in zip(xs, ys))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return a, b, r2


# Écart minimal de R² pour départager les deux modèles. En deçà, sur des
# tailles finies et étroites, les deux formes sont indiscernables : le
# verdict est "inconclusive" plutôt qu'un choix arbitraire.
FIT_R2_MARGIN = 0.02


def growth_fit(sizes, values):
    """Compare log y ~ b·x (exponentielle) et log y ~ c·log x (polynôme)."""
    pts = [(x, y) for x, y in zip(sizes, values) if x > 0 and y > 0]
    if len(pts) < 3:
        return None
    xs = [p[0] for p in pts]
    ly = [math.log(p[1]) for p in pts]
    e = _linfit(xs, ly)
    p = _linfit([math.log(x) for x in xs], ly)
    if not e or not p:
        return None
    return dict(points=len(pts),
                exp_rate=round(e[1], 5), exp_base=round(math.exp(e[1]), 5), exp_r2=round(e[2], 4),
                poly_degree=round(p[1], 4), poly_r2=round(p[2], 4),
                better=("inconclusive" if abs(e[2] - p[2]) < FIT_R2_MARGIN
                        else "exponential" if e[2] > p[2] else "polynomial"))


def summarize(rows, exp):
    axis = exp["axis"]
    key = "p_" + axis
    groups = {}
    for r in rows:
        groups.setdefault(r[key], []).append(r)
    table = []
    for x in sorted(groups):
        g = groups[x]
        solved = [r for r in g if r["status"] != "UNKNOWN"]
        conf = [r["conflicts"] for r in g]
        table.append(dict(
            axis_value=x, runs=len(g), solved=len(solved),
            sat=sum(r["status"] == "SAT" for r in g),
            unsat=sum(r["status"] == "UNSAT" for r in g),
            num_vars=statistics.median(r["num_vars"] for r in g),
            median_conflicts=statistics.median(conf),
            max_conflicts=max(conf),
            median_decisions=statistics.median(r["decisions"] for r in g),
            median_solve_s=round(statistics.median(r["solve_s"] for r in g), 5),
            median_cert_size=statistics.median(r["cert_size"] for r in g),
            median_check_s=round(statistics.median(r["check_s"] for r in g), 5),
        ))
    fit = None
    if axis != "ratio":
        # Une médiane censurée (budget atteint) sous-estime : on l'exclut.
        usable = [t for t in table if t["solved"] == t["runs"]]
        fit = growth_fit([t["axis_value"] for t in usable],
                         [t["median_conflicts"] for t in usable])
    checks = dict(
        runs=len(rows),
        unknown=sum(r["status"] == "UNKNOWN" for r in rows),
        cert_verified=sum(r["cert_ok"] is True for r in rows),
        cert_rejected=sum(r["cert_ok"] is False for r in rows),
        expected_checked=sum(r["expected_ok"] is not None for r in rows),
        expected_violations=sum(r["expected_ok"] is False for r in rows),
        crosschecked=sum(r["ref_agree"] is not None for r in rows),
        crosscheck_disagreements=sum(r["ref_agree"] is False for r in rows),
    )
    return dict(name=exp["name"], family=exp["family"], axis=axis,
                table=table, conflicts_growth=fit, checks=checks)


def run_campaign(name="standard", out_dir="results", seeds=None, max_conflicts=DEFAULT_MAX_CONFLICTS,
                 artifact_dir=None, only=None, log=print):
    exps = CAMPAIGNS[name]
    if only:
        exps = [e for e in exps if e["name"] in only]
    os.makedirs(out_dir, exist_ok=True)
    all_rows, summaries = [], []
    t_start = time.perf_counter()
    for exp in exps:
        ss = list(seeds if seeds is not None else exp["seeds"])
        rows = []
        for params in exp["params"]:
            for s in ss:
                row = run_instance(exp["family"], params, s, max_conflicts=max_conflicts,
                                   artifact_dir=artifact_dir and os.path.join(artifact_dir, exp["name"]))
                row["experiment"] = exp["name"]
                rows.append(row)
            last = rows[-len(ss):]
            log("[%s] %s : %s conflits médians, statuts %s" % (
                exp["name"], params,
                statistics.median(r["conflicts"] for r in last),
                {s: sum(r["status"] == s for r in last) for s in ("SAT", "UNSAT", "UNKNOWN")}))
        summaries.append(summarize(rows, exp))
        all_rows.extend(rows)

    fields = []
    for r in all_rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with open(os.path.join(out_dir, "runs.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(all_rows)
    env = dict(campaign=name, satlab_commit=_git_commit(), python=platform.python_version(),
               platform=platform.platform(), max_conflicts=max_conflicts,
               wall_time_s=round(time.perf_counter() - t_start, 2),
               note="Les temps dépendent de la machine ; les compteurs (conflits, décisions, "
                    "propagations, tailles de preuve) sont déterministes à graine fixée.")
    with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump(dict(environment=env, experiments=summaries), f, indent=2, ensure_ascii=False)
    with open(os.path.join(out_dir, "REPORT.md"), "w") as f:
        f.write(render_report(env, summaries))
    return env, summaries


def render_report(env, summaries):
    L = ["# Rapport de campagne satlab — `%s`" % env["campaign"], "",
         "- Commit satlab : `%s`" % env["satlab_commit"],
         "- Python %s — %s" % (env["python"], env["platform"]),
         "- Budget : %d conflits par instance (au-delà : UNKNOWN, censuré)" % env["max_conflicts"],
         "- Durée totale : %.1f s" % env["wall_time_s"], "",
         "Reproduire : `python3 -m satlab bench --campaign %s`. Les compteurs sont "
         "déterministes ; seuls les temps varient." % env["campaign"], "",
         "## Contrôles de validité", "",
         "| Expérience | Runs | UNKNOWN | Certificats vérifiés | Rejetés | Statut attendu vérifié | "
         "Violations | Contre-tests | Désaccords |",
         "|---|---|---|---|---|---|---|---|---|"]
    for s in summaries:
        c = s["checks"]
        L.append("| %s | %d | %d | %d | %d | %d | %d | %d | %d |" % (
            s["name"], c["runs"], c["unknown"], c["cert_verified"], c["cert_rejected"],
            c["expected_checked"], c["expected_violations"], c["crosschecked"],
            c["crosscheck_disagreements"]))
    for s in summaries:
        L += ["", "## %s (`%s`, axe `%s`)" % (s["name"], s["family"], s["axis"]), "",
              "| %s | vars | runs | SAT | UNSAT | conflits méd. | conflits max | décisions méd. | "
              "temps méd. (s) | taille cert. méd. | vérif. méd. (s) |" % s["axis"],
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for t in s["table"]:
            L.append("| %s | %s | %d | %d | %d | %s | %s | %s | %s | %s | %s |" % (
                t["axis_value"], t["num_vars"], t["runs"], t["sat"], t["unsat"],
                t["median_conflicts"], t["max_conflicts"], t["median_decisions"],
                t["median_solve_s"], t["median_cert_size"], t["median_check_s"]))
        g = s["conflicts_growth"]
        if g:
            L += ["", "Ajustement des conflits médians sur %d points : exponentiel "
                  "base %.4f par unité de `%s` (R² = %.4f) ; polynomial degré %.3f (R² = %.4f). "
                  "Verdict (écart de R² minimal %.2f) : **%s**." % (
                      g["points"], g["exp_base"], s["axis"], g["exp_r2"],
                      g["poly_degree"], g["poly_r2"], FIT_R2_MARGIN, g["better"])]
    L += ["", "## Portée", "",
          "Ces mesures décrivent un solveur CDCL précis sur des tailles finies. Une croissance "
          "exponentielle observée n'est pas une borne inférieure, et une croissance polynomiale "
          "observée n'est pas un algorithme polynomial : aucun de ces résultats ne tranche "
          "P vs NP. Leur valeur est de vérifier, avec certificats contrôlés, des comportements "
          "attendus par la théorie de la complexité des preuves et de fournir des points de "
          "comparaison reproductibles.", "",
          "Repères théoriques (taille des réfutations en résolution, que le CDCL sans "
          "prétraitement ne peut battre) : pigeonnier 2^Ω(h) (Haken 1985) ; Tseitin sur "
          "expanseurs 2^Ω(n) (Urquhart 1987, Ben-Sasson & Wigderson 2001) ; k-CNF aléatoire "
          "UNSAT à densité constante 2^Ω(n) avec forte probabilité (Chvátal & Szemerédi "
          "1988). Un verdict « polynomial » ou « inconclusive » sur ces familles traduit "
          "donc des tailles trop petites pour l'asymptotique, pas une contradiction.", ""]
    return "\n".join(L)
