# Contrôles indépendants de la campagne `standard`

Ce fichier consigne les contrôles faits **en dehors** de la chaîne
`satlab bench` (qui vérifie déjà chaque certificat avec `satlab/checker.py`
et compare les statuts aux oracles ; voir `REPORT.md`).

## 1. Second vérificateur tiers : drat-trim

Instances et preuves exportées par
`python3 -m satlab bench --campaign standard --artifacts results/artifacts`
(commit `1d32c97`), puis passées une à une à
[drat-trim](https://github.com/marijnheule/drat-trim) (compilé depuis les
sources, `gcc -O2`) avec `drat-trim inst.cnf inst.drup -t 600` :

- **241 preuves UNSAT sur 241 : `s VERIFIED`**, 0 échec ;
- les 232 instances SAT ont un modèle vérifié par `checker.py` (la
  vérification d'un modèle est une simple évaluation clause par clause).

Contrôles négatifs (le vérificateur doit dire non) :

- une preuve PHP(8,7) tronquée à 200 lignes : `s NOT VERIFIED` (drat-trim)
  et `REJECTED` (`checker.py`) ;
- la preuve valide de PHP(7,6) appliquée à la formule privée de sa première
  clause (devenue SAT, confirmé par le solveur) : `s NOT VERIFIED`
  (drat-trim) et `REJECTED … non RUP` (`checker.py`).

Les artefacts (≈ 47 Mo) ne sont pas versionnés ; la commande ci-dessus les
régénère à l'identique.

## 2. Déterminisme

Deux exécutions complètes de la campagne (commits `1d32c97` puis `06c33ad`,
ce dernier ne modifiant que les métadonnées et le verdict d'ajustement) :
473 runs, **mêmes instances (SHA-256) et compteurs identiques** sur
`status`, `decisions`, `propagations`, `conflicts`, `restarts`, `learned`,
`deleted`, `max_level`, `units_learned`, `avg_lbd`, `cert_size`, `cert_ok`,
`ref_status`. Seuls les temps diffèrent.

## 3. Contre-tests aléatoires du solveur et du vérificateur

```
python3 -m satlab crosscheck --count 20000 --max-vars 30 --seed 1
```

20 000 formules k-SAT (k ∈ {2, 3, 4}) tirées autour du seuil de chaque k,
4 à 30 variables, oracle force brute (≤ 12 variables) ou DPLL :

| instances | SAT | UNSAT | désaccords | certificats rejetés | avec suppressions DRUP | certificats falsifiés | falsifiés acceptés |
|---|---|---|---|---|---|---|---|
| 20 000 | 13 338 | 6 662 | **0** | **0** | 4 928 | 11 260 | **0** |

## Limites connues

- Le solveur est en Python pur : les tailles atteignables sont modestes
  (PHP jusqu'à 8 trous, Tseitin jusqu'à 56 sommets). Les verdicts de
  croissance portent sur ces plages seulement.
- L'ajustement exponentiel/polynomial compare deux R² sur des médianes ; un
  écart < 0,02 est déclaré « inconclusive ». Sur le 3-SAT aléatoire au seuil,
  le verdict est « inconclusive » alors que la théorie (Chvátal & Szemerédi
  1988) impose une croissance exponentielle pour les réfutations : la plage
  n ≤ 150 est trop étroite pour la distinguer, et les médianes mélangent
  instances SAT et UNSAT.
- Les familles `coloring3_threshold` aux tailles testées sont faciles
  (≤ 131 conflits) : elles ne constituent pas un témoin de dureté.
