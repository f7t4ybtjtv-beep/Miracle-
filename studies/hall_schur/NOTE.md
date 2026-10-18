# Couplages, témoins de Hall et Schur(N,3) — note de vérification

Cette note examine (1) une proposition sur l'encodage pigeonnier dans les
graphes bipartis équilibrés, (2) les trois questions de suite qui
l'accompagnaient, et (3) le fichier `pnp_schur_extension_results_20261019.json`
(sha256 `e74f4438…d0f4d7`). Chaque affirmation porte un statut :

- **prouvé** : preuve écrite et relue étape par étape (par au moins deux
  lectures indépendantes) ;
- **vérifié** : recalculé par du code exécuté, avec au moins deux méthodes
  indépendantes quand c'est possible ;
- **réfuté** : contre-exemple certifié ;
- **non vérifiable** : données ou définitions manquantes.

Toutes les réfutations UNSAT citées ont un certificat DRUP accepté par
`satlab/checker.py`, et par drat-trim quand c'est indiqué. `reproduce.py`
recalcule les résultats principaux en ~6 s ; `evidence/` contient les scripts et
sorties des enquêtes plus lourdes (voir `evidence/README.md`).

**Portée.** Rien ici ne touche à P vs NP. Ce sont des faits combinatoires
élémentaires ou des mesures sur de petites tailles ; les bornes de complexité
de preuve citées sont des résultats connus, non re-démontrés.

Encodage utilisé partout (« encodage faible ») : pour un graphe biparti
G = (X, Y, E), une variable par arête ; pour chaque x ∈ X la clause
∨_{y ∈ N(x)} e(x,y) ; pour chaque y ∈ Y et chaque paire x1 < x2 de voisins
de y, la clause ¬e(x1,y) ∨ ¬e(x2,y). Aucune clause « au plus un trou par
pigeon ». Implémentation : `satlab.generators.graph_php_cnf`.

---

## 1. Proposition (cas équilibré) — **prouvée et vérifiée**

*Énoncé.* Si |X| = |Y| = n, les modèles de l'encodage faible sont exactement
les couplages parfaits ; leur nombre est le permanent de la matrice
d'adjacence.

*La preuve proposée est correcte, à une étape près.* Le double comptage
Σ_x deg(x) = |E_A| = Σ_y deg(y) ≤ n et |E_A| ≥ n donne bien deg(x) = 1 pour
tout x. Pour conclure à un couplage **parfait**, il faut aussi deg(y) = 1
pour tout y : cela découle du même argument (n entiers ≤ 1 de somme n). La
réciproque est correcte.

*Vérification.* Tous les graphes étiquetés pour n = 1, 2, 3, 4 (2, 16, 512 et
65 536 graphes). On compare trois comptes indépendants : le nombre de
modèles par inclusion-exclusion, la force brute (n ≤ 3) et le nombre de
couplages parfaits par programmation dynamique. Résultat : 0 désaccord, et
Σ modèles = n!·2^{n²−n}. Les agents ont aussi testé 600 graphes aléatoires
pour n = 5 et 6 avec la formule de Ryser, et certifié par CDCL les 65 536
graphes n = 4 (37 823 SAT, 27 713 UNSAT, 0 échec).

*Cas déséquilibrés* (prouvés et vérifiés). Si |X| > |Y|, l'encodage est
toujours UNSAT : c'est le principe des tiroirs. Plus généralement, pour
|X| ≥ |Y|, modèles = couplages saturant X. Si |X| < |Y|, les modèles
forment un sur-ensemble strict en général ; le plus petit exemple est
X = {x}, Y = {y1, y2}, avec 3 modèles pour 2 couplages (voir §4).

*Nouveauté.* À notre avis, c'est un fait élémentaire de double comptage
(folklore). Aucune recherche bibliographique n'a été faite. Rappel :
compter les couplages parfaits est #P-complet (Valiant 1979), donc compter
les modèles de cette famille de CNF l'est aussi.

*Non vérifiable.* La « famille réparée ou non » (r+2 pigeons, r+2 trous ;
comptes « 0 puis r! ») n'est définie nulle part dans le dépôt. La
proposition garantit seulement que, pour toute famille équilibrée,
l'énumération exhaustive des modèles et une énumération des couplages
parfaits donnent les mêmes nombres. Les valeurs 0 et r! elles-mêmes ne
peuvent pas être vérifiées sans la définition du graphe.

## 2. Q1 — Un témoin de Hall de taille k donne-t-il une réfutation courte ?

Notations : S est un témoin de Hall (|N(S)| < |S|), k = |S|, m = |N(S)| ≤ k−1.

**Oui, en 2^{O(k)} — prouvé et vérifié.** La CNF F_S du témoin (clauses
de pigeon de S, clauses de trou sur N(S) entre pigeons de S) est une
sous-CNF de la CNF complète. Une réfutation de F_S réfute donc la CNF
complète : en résolution c'est immédiat, et en DRUP la propagation unitaire
est monotone. La construction explicite suivante est implémentée dans
`satlab/hallproof.py` :

> pour H ⊆ N(S), |H| = j−1 : D(j,H) = ∨_{i≤j} ∨_{h ∈ N(p_i)\H} e(p_i,h)
> (« les pigeons 1..j ne logent pas tous dans H ») ; on dérive D(j+1,H)
> à partir des D(j, H\{h}), et D(m+1, N(S)) est la clause vide.

- Taille exacte sur K_{m+1,m} : **2^{m−1}(m+2) − 1 lemmes**, au plus cela
  sur un témoin quelconque. Vérifié par trois générateurs indépendants :
  deux agents (m = 2..12, formule close ; preuves acceptées par
  `checker.py` et drat-trim pour m = 2..10) et `satlab.hallproof` (m = 1..8
  avec `checker.py`, m = 2..9 avec drat-trim).
- En résolution pure : m(m+3)·2^{m−2} étapes, vérifiées comme résolvantes
  exactes pour m = 2..10.
- Cela fait environ k·2^k lignes, et non O(2^k) ; savoir si O(2^k) est
  atteignable reste **ouvert**.
- Sur des graphes à témoin implanté (25 et 30 instances côté agents, jusqu'à
  30 pigeons et 423 variables, avec `checker.py` et drat-trim ; côté
  `satlab.hallproof` : 30 dans `reproduce.py` et 20 dans les tests unitaires
  avec `checker.py`, plus 10 contrôlées ponctuellement par drat-trim), la
  preuve du seul témoin est acceptée sur la **formule complète**.

**Polynomiale ? Non en général — prouvé, avec une borne inférieure citée.**
Si S ∪ N(S) induit K_{k,k−1}, alors F_S = PHP(k, k−1), qui exige des
réfutations par résolution de taille 2^{Ω(k)} (Haken 1985 ; cité de
mémoire, confiance élevée). Le transfert à la CNF complète n'est pas
automatique :

- *transfert prouvé* si X \ S se couple dans Y \ N(S) : la restriction
  correspondante transforme exactement la CNF complète en F_S (vérifié
  100/100) ;
- *contre-exemple au transfert sans condition* : K_{9,8} ⊔ K_{2,1} contient
  PHP(9,8), mais la clause vide y est déjà RUP (réfutation en une ligne).

Si k = O(log n), la borne 2^{k−2}(k+1) est polynomiale en n.

*Comportement du CDCL* (vérifié, 3 graines par cellule). Sur un K_{k,k−1}
implanté dans des graphes à n = 20..60 pigeons, le nombre de conflits est
multiplié par environ 5 à chaque incrément de k (médianes du cœur seul,
k = 3..9 : 2, 7, 28, 146, 767, 5 953, 32 001) et ne dépend presque pas de n.
Le CDCL dépasse le nombre de lemmes de la preuve explicite dès k = 6
(32 001 conflits contre 1 279 lemmes à k = 9). Plus de 99,7 % des littéraux
appris portent sur des variables du cœur, mais **pas 100 %** (96 sur
39 295 hors du cœur dans une cellule k = 7).

## 3. Q2 — La CNF d'un témoin minimal est-elle un MUS ?

**Non en général — réfuté par contre-exemple certifié.**

- *Clauses de pigeon : toujours nécessaires* (prouvé). Par minimalité,
  S \ {x} vérifie la condition de Hall, donc se couple. Corollaire :
  |N(S)| = |S| − 1.
- *Clauses de trou : critère exact* (prouvé ; 0 désaccord sur 294 214
  clauses). ¬e(x1,y) ∨ ¬e(x2,y) est nécessaire si et seulement si
  S \ {x1,x2} se couple dans N(S) \ {y}.
- *Plus petit contre-exemple* : 3 pigeons et 2 trous, N(a) = {y1},
  N(b) = N(c) = {y1,y2}. La clause ¬e(b,y1) ∨ ¬e(c,y1) est redondante.
  Il est unique à isomorphisme près.
- *L'exemple de la discussion* (N(a) = N(b) = {y1,y3}, N(c) = N(d) = {y1,y2})
  est aussi un contre-exemple : deux clauses de trou sur y1 sont
  redondantes.
- *K_{k,k−1}* : la CNF induite (PHP classique) **est** un MUS pour tout k ≥ 2.

Proportion exhaustive de témoins minimaux dont la CNF induite est un MUS,
graphes étiquetés comptés avec multiplicité (recalculée par `reproduce.py`
et par deux agents) :

| \|X\|×\|Y\| | 3×2 | 3×3 | 4×2 | 4×3 | 4×4 | 5×3 |
|---|---|---|---|---|---|---|
| MUS / témoins | 79/85 | 285/303 | 560/656 | 4113/5457 | 26180/31556 | 58920/101160 |

La proportion baisse quand |X| augmente à |Y| fixé. Elle **ne baisse pas**
quand |Y| augmente à |X| fixé (correction apportée par le vérificateur).

**Structure des MUS de la CNF complète — prouvée et vérifiée.** On note
d(T) = |T| − |N(T)| la déficience. Pour tout MUS d'ensemble de pigeons P :

1. chaque clause de trou du MUS relie deux pigeons de P ;
2. d(T) < d(P) pour toute partie stricte T ⊂ P, et d(P) ≥ 1 ;
3. P est un témoin de Hall minimal **si et seulement si** d(P) = 1. Le MUS
   est alors formé des clauses de pigeon de P et d'un sous-ensemble minimal
   des clauses de trou induites.

Il existe des MUS de déficience 2 et 3 : pour |X| ≤ 5, |Y| ≤ 3, en
énumérant les MUS d'un représentant par classe d'isomorphisme de graphes, on
en compte 1 196 de déficience 1, 2 204 de déficience 2 et 744 de
déficience 3. Le plus petit est N(a) = N(b) = {y1},
N(c) = N(d) = {y1,y2}, avec le MUS {P(a), P(b), P(c), P(d),
¬e(a,y1)∨¬e(c,y1), ¬e(b,y1)∨¬e(d,y1), ¬e(c,y2)∨¬e(d,y2)}. Son ensemble de
pigeons {a,b,c,d} n'est pas un témoin minimal (le témoin minimal {a,b} y est
inclus). La condition 2 est nécessaire mais **pas suffisante** pour qu'un
ensemble P porte un MUS : 3 pigeons sur un seul trou forment un
contre-exemple.

*Ouvert.* Une condition nécessaire et suffisante simple pour qu'un P donné
porte un MUS. Autre point ouvert : dans tous les cas énumérés, chaque témoin
minimal porte exactement un MUS (l'ensemble H des clauses de trou serait
unique). C'est observé, non prouvé.

## 4. Q3 — Familles à grand écart quand |X| < |Y|

*Reformulation nécessaire.* Pour |X| < |Y|, il n'existe aucun couplage
parfait au sens strict. Le dénominateur pertinent est le nombre de couplages
**saturant X**. Les modèles de l'encodage faible correspondent aux familles
d'ensembles S_x ⊆ N(x) non vides et deux à deux disjoints ; les couplages
saturants sont les modèles où tous les |S_x| valent 1.

**Théorème (prouvé ; vérifié exactement sur environ 2,9 millions de
graphes).** Soit k = |N(X)| − |X| le nombre de trous excédentaires non
isolés. S'il existe un couplage saturant X :

  (3/2)^k ≤ modèles / couplages saturants ≤ (|X|+1)^k,

avec un rapport égal à 1 si et seulement si k = 0. La borne inférieure est
atteinte exactement quand, pour tout couplage saturant M, les trous de N(X)
libres pour M sont de degré 1 et ont des voisins distincts. L'écart est donc
exponentiel **exactement** quand l'excès k croît linéairement.

| Famille | Modèles | Couplages saturants | Rapport |
|---|---|---|---|
| n étoiles K_{1,2} disjointes | 3^n | 2^n | (3/2)^n (borne atteinte) |
| n pigeons à d trous privés | (2^d−1)^n | d^n | ((2^d−1)/d)^n |
| K_{n,m} | n!·S(m+1, n+1) | m!/(m−n)! | Θ((n+1)^m / m^n) à n fixé |
| K_{n,n+1} | n!·C(n+2, 2) | (n+1)! | (n+2)/2 (seulement linéaire) |
| K_{n,2n} | | | ((n+1)/4)^n ≤ r ≤ (n+1)^n, donc log r = n ln n + O(n) |

S(·,·) désigne les nombres de Stirling de seconde espèce.

## 5. Audit du JSON Schur(N,3)

L'encodage reconstitué reproduit exactement tous les nombres de variables et
de clauses : var(i,c) = 3(i−1)+c+1 ; pour chaque i, une clause « au moins
une couleur » (ALO) et trois clauses « au plus une couleur » (AMO) ; pour
x ≤ y avec x+y = z ≤ N, une clause ¬(x,c) ∨ ¬(y,c) ∨ ¬(z,c) par couleur. Il
est implémenté dans `satlab.generators.schur`.

| Affirmation du fichier | Verdict |
|---|---|
| Comptes (42/203, …, 150/2075) | **vérifié** : \|F_N\| = 4N + 3⌊N²/4⌋, 3N variables |
| Schur(14,3) UNSAT | **vérifié** et certifié (DRUP, deux vérificateurs) ; Schur(13,3) est SAT, avec 18 colorations soit 3 à permutation des couleurs près, par exemple {1,4,7,10,13}, {2,3,11,12}, {5,6,8,9} ; cohérent avec S(3) = 13 |
| « pour tout N ≥ 14, Schur(14,3) est une sous-CNF de Schur(N,3) et la même réfutation sert » | **prouvé** (la numérotation ne dépend pas de N ; monotonie de RUP) et **vérifié** : une même preuve DRUP de N = 14 est acceptée pour N = 14, 15, 20, 30, 40, 50 par `checker.py` et drat-trim ; témoin négatif : rejetée sur N = 13 |
| scope « NOT A P!=NP LOWER BOUND » | **correct** : c'est la monotonie triviale des nombres de Schur ; une preuve de taille constante en N est le contraire d'une dureté |
| `original_core_clauses: 203` | **trompeur** : 203 est la CNF entière. Les 42 clauses AMO ne figurent dans **aucun** MUS (prouvé : garder une couleur par entier). Les cœurs minimaux trouvés ont 133 à 137 clauses (14 ALO, 0 AMO). Tout MUS en contient au moins 101 ; la taille minimale reste ouverte dans [101, 133] |
| 2102 nœuds / 147 conflits | **non vérifiable** : source (sha `7fa57b61…`) non fournie. Pour comparaison, le DPLL de satlab donne 751 nœuds et le CDCL de 176 à 246 conflits selon la graine et l'ordre des clauses. 147 est aussi exactement le nombre de clauses de somme à N = 14 (3 × 49) : coïncidence ou champ mal étiqueté, indécidable |
| `verified: true` pour N > 14 | justifiable uniquement par l'argument d'inclusion (aucun artefact de preuve fourni) ; cet argument est correct |

*Réserve.* Que les comptes coïncident ne prouve pas que l'encodage d'origine
soit identique à la reconstruction. Avec une autre numérotation des
variables, l'inclusion pourrait ne plus être littérale.

## 6. Erreurs détectées en cours de route (boucle de rétroaction)

La vérification adverse a réfuté plusieurs affirmations formulées pendant
l'étude, dont une des miennes :

| Affirmation initiale | Correction |
|---|---|
| (moi) « l'ensemble de pigeons de tout MUS est un témoin de Hall minimal » | faux ; vrai seulement à déficience 1 (§3) |
| « 100 % des littéraux appris par le CDCL sont dans le cœur » | > 99,7 % ; une moyenne arrondie à `%5.1f` masquait 96 littéraux hors cœur |
| « le témoin minimal vaut k sauf 2 instances » | 3 exceptions, d'après le propre fichier de sortie |
| « la proportion de MUS baisse avec la taille » | seulement avec \|X\| ; elle ne baisse pas avec \|Y\| |
| « log r = n ln n + Θ(n) » pour K_{n,2n} | les bornes établies donnent seulement + O(n) |

Ces erreurs ont une cause commune : **une affirmation universelle (« tous »,
« toujours », « baisse ») tirée d'un résumé** (pourcentage arrondi, tendance
sur une seule direction, extrapolation d'un cas observé), au lieu d'un
compteur exact ou d'une preuve. C'est une faiblesse du principe de
vérification lui-même, pas de chaque cas : toute affirmation universelle
doit désormais reposer sur un compteur exact (« 0 sur N ») ou sur une preuve.
Les tendances doivent préciser la direction et la plage testées.

## 7. Reproduire

```bash
python3 studies/hall_schur/reproduce.py          # ~6 s, toutes assertions, écrit results.json
python3 -m unittest discover -s satlab/tests -t . # inclut les nouveaux modules
```

Modules ajoutés à `satlab` : `matching` (couplage maximum, témoin de Hall
minimal, comptes de couplages), `core` (MUS par suppression, redondance),
`hallproof` (preuve DRUP explicite depuis un témoin), et dans `generators` :
`graph_php_cnf`, `bipartite_php` (statut attendu calculé par Hall, sans
solveur) et `schur`.
