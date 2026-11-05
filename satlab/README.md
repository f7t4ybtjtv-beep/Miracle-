# satlab — outil de recherche SAT reproductible

Outil expérimental pour l'étude empirique de SAT dans le cadre de P vs NP :
génération d'instances, résolution exacte instrumentée, mesures de
complexité, contre-tests et certificats vérifiables **séparément** du
solveur. Python 3 standard uniquement (aucune dépendance).

> **Portée.** Des mesures sur un solveur et des tailles finies ne prouvent
> ni ne réfutent P ≠ NP. Une croissance exponentielle observée n'est pas une
> borne inférieure ; une croissance polynomiale observée n'est pas un
> algorithme polynomial. L'outil sert à produire des résultats *vérifiés et
> reproductibles*, et à les confronter aux résultats connus de complexité des
> preuves.

## Principe de confiance

Aucun résultat n'est cru sur parole :

| Résultat | Certificat | Contrôle |
|---|---|---|
| SAT | modèle (affectation complète) | chaque clause a un littéral vrai |
| UNSAT | preuve DRUP (lemmes + suppressions) | chaque lemme est RUP ; la clause vide est dérivée |
| statut attendu | construction mathématique (pigeonnier, Tseitin, planted) | comparé au statut du solveur |
| statut | oracle indépendant (force brute ≤ 16 vars, DPLL ≤ 60 vars) | comparé au statut du solveur |

`satlab/checker.py` **n'importe rien du paquet** : on peut le copier seul et
l'exécuter (`python3 -I checker.py …`). Le vérificateur est lui-même testé
contre des certificats falsifiés (modèles mutés, preuves réutilisées sur une
formule affaiblie devenue SAT, lemmes non RUP, suppressions) qui doivent être
rejetés.

## Utilisation

```bash
# générer
python3 -m satlab gen pigeonhole --param holes=6 -o php6.cnf
python3 -m satlab gen random_ksat --seed 3 --param n=100 --param m=426 -o r.cnf

# résoudre (code retour 10 = SAT, 20 = UNSAT, 0 = budget épuisé)
python3 -m satlab solve php6.cnf --proof php6.drup --json
python3 -m satlab solve r.cnf --model r.model

# vérifier indépendamment
python3 -m satlab verify php6.cnf --proof php6.drup
python3 satlab/checker.py r.cnf --model r.model

# contre-tests aléatoires (CDCL vs oracles + mutations de certificats)
python3 -m satlab crosscheck --count 2000 --max-vars 24

# campagnes (résultats dans --out : runs.csv, summary.json, REPORT.md)
python3 -m satlab bench --campaign quick --out /tmp/q
python3 -m satlab bench --campaign standard --out results/standard \
        --artifacts results/artifacts      # écrit aussi .cnf / .model / .drup

# tests
python3 -m unittest discover -s satlab/tests -t .
```

Les preuves DRUP produites sont aussi au format accepté par `drat-trim`,
ce qui permet un second contrôle par un outil tiers.

## Familles d'instances

| Famille | Paramètres | Statut attendu | Intérêt |
|---|---|---|---|
| `random_ksat` | `n`, `m`, `k` | — | seuil de satisfiabilité (≈ 4,27 pour k = 3), dureté maximale au seuil |
| `planted_ksat` | `n`, `m`, `k` | SAT (solution cachée) | instances SAT garanties, modèle caché fourni |
| `pigeonhole` | `holes` | UNSAT | résolution en 2^Ω(h) (Haken 1985) |
| `tseitin` | `n` sommets, `d` | UNSAT | sur expanseurs, résolution en 2^Ω(n) (Urquhart 1987 ; Ben-Sasson–Wigderson 2001) |
| `coloring` | `n`, `k`, `avg_degree` | — | k-coloration de G(n, p) |

Le CDCL (sans prétraitement ni extensions) produit des réfutations qui se
traduisent en résolution : sur pigeonnier et Tseitin, une croissance
exponentielle est donc **attendue** par la théorie, quelle que soit
l'heuristique. Ces familles servent de témoins pour valider la chaîne de
mesure.

## Mesures

Par instance (`runs.csv`) : empreinte SHA-256 canonique, nombre de variables
et de clauses, statut, décisions, propagations, conflits, redémarrages,
clauses apprises / supprimées, longueur et LBD moyens des clauses apprises,
niveau de décision max, taille du certificat, temps de résolution et de
vérification, statut attendu, verdict de l'oracle.

Par expérience (`summary.json`, `REPORT.md`) : médianes par taille, et
ajustement des conflits médians par `log y = a + b·x` (exponentiel) contre
`log y = a + c·log x` (polynomial), avec R². Les tailles où une instance a
épuisé le budget sont exclues de l'ajustement (médiane censurée).

## Reproductibilité

Toutes les sources d'aléa passent par `random.Random(seed)`. À graine fixée,
les instances (vérifiables par leur SHA-256) et tous les compteurs du solveur
sont identiques d'une exécution à l'autre ; seuls les temps dépendent de la
machine. Le rapport consigne le commit (`-dirty` si l'arbre est modifié) et
la version de Python.

## Architecture du solveur (`cdcl.py`)

Deux littéraux surveillés, analyse 1-UIP, VSIDS (tas paresseux), sauvegarde
de phase, redémarrages de Luby, réduction de la base apprise par LBD
(clauses de LBD ≤ 2 et clauses « verrouillées » conservées). Chaque clause
apprise et chaque suppression est journalisée en DRUP.
