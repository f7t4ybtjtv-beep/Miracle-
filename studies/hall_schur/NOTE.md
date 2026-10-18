# Couplages, témoins de Hall et Schur(N,3) — note de vérification

Cette note examine (1) une proposition sur l'encodage pigeonnier dans les
graphes bipartis équilibrés, (2) les trois questions de suite qui
l'accompagnaient, et (3) le fichier `pnp_schur_extension_results_20261019.json`
(sha256 `e74f4438…d0f4d7`). Chaque affirmation porte un statut :

- **prouvé** : preuve écrite dans cette note (dans le texte ou en annexe) et
  relue indépendamment ;
- **vérifié** : recalculé par du code exécuté, avec au moins deux méthodes
  indépendantes quand c'est possible ; le domaine testé est précisé ;
- **réfuté** : contre-exemple certifié ;
- **non vérifiable** : données ou définitions manquantes.

Toute insatisfiabilité citée est certifiée par une preuve DRUP. Dans
`reproduce.py`, `satlab.core` fait vérifier chaque verdict UNSAT par
`satlab/checker.py`. Dans `evidence/`, les preuves sont contrôlées par
`checker.py` et souvent aussi par drat-trim. `reproduce.py` recalcule les
résultats principaux et les vérifie par assertion en ~10 s. `evidence/`
contient les scripts et les sorties brutes des enquêtes plus lourdes (voir
`evidence/README.md`).

**Portée.** Rien ici ne touche à P vs NP. Ce sont des faits combinatoires
élémentaires ou des mesures sur de petites tailles ; les bornes inférieures
de complexité de preuve citées sont des résultats connus, non re-démontrés.

Encodage utilisé partout (« encodage faible ») : pour un graphe biparti
G = (X, Y, E), une variable par arête ; pour chaque x ∈ X la clause
P(x) = ∨_{y ∈ N(x)} e(x,y) ; pour chaque y ∈ Y et chaque paire x1 < x2 de
voisins de y, la clause H(y: x1,x2) = ¬e(x1,y) ∨ ¬e(x2,y). Aucune clause
« au plus un trou par pigeon ». Implémentation :
`satlab.generators.graph_php_cnf`.

---

## 1. Proposition (cas équilibré) — **prouvée et vérifiée**

*Énoncé.* Si |X| = |Y| = n, les modèles de l'encodage faible sont exactement
les couplages parfaits ; leur nombre est le permanent de la matrice
d'adjacence.

*La preuve proposée est correcte.* Le double comptage
Σ_x deg(x) = |E_A| = Σ_y deg(y) ≤ n et |E_A| ≥ n donne deg(x) = 1 pour tout
x. Il reste une ligne, implicite dans la proposition : comme deg(y) ≤ 1,
les n arêtes ont des trous distincts et couvrent donc les n trous. Le
couplage est bien parfait. La réciproque est correcte.

*Vérification.* Tous les graphes étiquetés pour n = 1, 2, 3, 4 (2, 16, 512 et
65 536 graphes). Trois comptes indépendants sont comparés : le nombre de
modèles par inclusion-exclusion, la force brute (n ≤ 3) et le nombre de
couplages parfaits par programmation dynamique. Résultat : 0 désaccord, et
Σ modèles = n!·2^{n²−n} (`reproduce.py`). Côté archives :
- 600 graphes aléatoires par valeur de n pour n = 5 et 6 (1 200 au total),
  comptés par force brute ou #DPLL, et comparés aux couplages calculés par
  Ryser et par DP : 0 désaccord ;
- les 65 536 graphes n = 4 certifiés par CDCL : 37 823 SAT, 27 713 UNSAT,
  0 échec (`evidence/pm-balanced/*.out`, contre-vérification dans
  `evidence/refute-proposition/*.out`).

*Cas déséquilibrés* (prouvés et vérifiés). Si |X| > |Y|, l'encodage est
toujours UNSAT : c'est le principe des tiroirs. Plus généralement, pour
|X| ≥ |Y|, modèles = couplages saturant X. Si |X| < |Y|, les modèles
forment un sur-ensemble, strict en général. Le plus petit exemple strict
est X = {x}, Y = {y1, y2} : 3 modèles pour 2 couplages (voir §4).

*Nouveauté.* À notre avis, c'est un fait élémentaire de double comptage
(folklore). Aucune recherche bibliographique n'a été faite. Rappel :
compter les couplages parfaits est #P-complet (Valiant 1979), donc compter
les modèles de cette famille de CNF l'est aussi.

*Non vérifiable.* La « famille réparée ou non » (r+2 pigeons, r+2 trous ;
comptes « 0 puis r! ») n'est définie nulle part dans le dépôt. La
proposition garantit seulement que, pour toute famille équilibrée,
l'énumération des modèles et celle des couplages parfaits donnent les mêmes
nombres. Les valeurs 0 et r! elles-mêmes ne peuvent pas être vérifiées sans
la définition du graphe.

## 2. Q1 — Un témoin de Hall de taille k donne-t-il une réfutation courte ?

Notations : S est un témoin de Hall (|N(S)| < |S|), k = |S|, m = |N(S)| ≤ k−1.

**Oui, en 2^{O(k)} — prouvé et vérifié.** La CNF F_S du témoin (clauses
P(x) pour x ∈ S, clauses de trou sur N(S) entre pigeons de S) est une
sous-CNF de la CNF complète. Une réfutation de F_S réfute donc la CNF
complète : en résolution c'est immédiat, et en DRUP la propagation unitaire
est monotone. La construction explicite est implémentée dans
`satlab/hallproof.py` ; preuve en annexe C.

> pour H ⊆ N(S), |H| = j−1 : D(j,H) = ∨_{i≤j} ∨_{h ∈ N(p_i)\H} e(p_i,h)
> (« les pigeons 1..j ne logent pas tous dans H ») ; on dérive D(j+1,H)
> à partir des D(j, H\{h}), et D(m+1, N(S)) est la clause vide.

- Taille : **2^{m−1}(m+2) − 1 lemmes** exactement sur K_{m+1,m}, et au plus
  autant sur tout témoin. Avec m ≤ k−1, cela fait au plus
  (k+1)·2^{k−2} − 1 lignes, soit Θ(k·2^k) et non O(2^k). Savoir si O(2^k)
  est atteignable reste **ouvert**.
- La forme close a été vérifiée par trois générateurs indépendants. Les
  deux agents l'ont vérifiée pour m = 2..12, avec des preuves acceptées par
  `checker.py` et drat-trim pour m = 2..9 et m = 2..10 respectivement.
  `satlab.hallproof` l'a vérifiée pour m = 1..8 avec `checker.py` et pour
  m = 2..9 avec drat-trim (`evidence/review/hallproof_drat_trim.txt`).
- En résolution pure : m(m+3)·2^{m−2} étapes, vérifiées comme résolvantes
  exactes pour m = 2..10.
- Sur des graphes à témoin implanté, la preuve du seul témoin est acceptée
  sur la **formule complète** :
  - côté agents : 25 et 30 instances, jusqu'à 30 pigeons et 423 variables,
    avec `checker.py` et drat-trim ;
  - côté `satlab.hallproof` : 30 instances dans `reproduce.py`, avec
    `checker.py`, et 10 avec drat-trim ;
  - témoins arbitraires (non minimaux, non complets, ordre mélangé, pigeons
    sans voisin) : tous ceux de 150 petits graphes aléatoires, dans les
    tests unitaires. Les relecteurs en ont testé 52 253 de plus, sans aucun
    échec.

**Polynomiale ? Non en général — prouvé, avec une borne inférieure citée.**
Si S ∪ N(S) induit K_{k,k−1}, alors F_S = PHP(k, k−1), qui exige des
réfutations par résolution de taille 2^{Ω(k)} (Haken 1985 ; cité, confiance
élevée). Le transfert à la CNF complète n'est pas automatique :

- *transfert prouvé* si X \ S se couple dans Y \ N(S) : la restriction
  « arêtes de ce couplage vraies, autres arêtes de X \ S fausses »
  transforme exactement la CNF complète en F_S (vérifié 100/100), et
  restreindre une réfutation ne l'allonge pas ;
- *contre-exemple au transfert sans condition* : K_{9,8} ⊔ K_{2,1} contient
  PHP(9,8), mais la clause vide y est déjà RUP (réfutation en une ligne).

Si k = O(log n), la borne (k+1)·2^{k−2} est polynomiale en n.

*Comportement du CDCL* (vérifié). K_{k,k−1} est implanté dans des graphes de
n = 20, 30, 40, 50, 60 pigeons, avec 3 graines par cellule. Exception :
pour k = 9, n = 40 et 60 n'ont qu'une graine, et n = 30 et 50 ne sont pas
mesurés.
- Le nombre de conflits est multiplié en moyenne par environ 5 à chaque
  incrément de k (facteur entre 3,5 et 7,8). Médianes du cœur seul, pour
  k = 3..9 : 2, 7, 28, 146, 767, 5 953, 32 001.
- Il ne dépend presque pas de n.
- Le CDCL dépasse le nombre de lemmes de la preuve explicite dès k = 6
  (32 001 conflits contre 1 279 lemmes à k = 9).
- Les clauses apprises portent presque toutes sur des variables du cœur,
  mais **pas toutes**. Comptes exacts (`evidence/review/exact.out`) : 0
  littéral hors cœur pour k ≤ 7 ; 62 sur 137 496 à k = 8, n = 20 (une
  graine). Sur les instances de la contre-vérification : 96 sur 39 295 à
  k = 7.

## 3. Q2 — La CNF d'un témoin minimal est-elle un MUS ?

**Non en général — réfuté par contre-exemple certifié.** Preuves en annexe A.

- *Clauses de pigeon : toujours nécessaires* (prouvé). Corollaire :
  |N(S)| = |S| − 1.
- *Clauses de trou : critère exact* (prouvé ; 0 désaccord avec le test
  direct sur 294 214 clauses). H(y: x1,x2) est nécessaire si et seulement si
  S \ {x1,x2} se couple dans N(S) \ {y}.
- *Plus petit contre-exemple* : 3 pigeons et 2 trous, N(a) = {y1},
  N(b) = N(c) = {y1,y2}. H(y1: b,c) est redondante. L'exemple est unique à
  isomorphisme près, et minimal à la fois en sommets et en arêtes.
- *L'exemple de la discussion* (N(a) = N(b) = {y1,y3}, N(c) = N(d) = {y1,y2})
  est aussi un contre-exemple : H(y1: a,b) et H(y1: c,d) sont redondantes.
- *K_{k,k−1}* : la CNF induite (PHP classique) **est** un MUS pour tout k ≥ 2.
  Par le critère, le graphe restant K_{k−2,k−2} a toujours un couplage
  parfait.

Proportion exhaustive de témoins minimaux dont la CNF induite est un MUS,
sur les graphes étiquetés comptés avec multiplicité. Elle est recalculée par
`reproduce.py` à l'aide du critère. Le critère y est comparé au test MUS
direct, certifié, sur 2 467 témoins, et il a été recalculé indépendamment
par deux agents.

| \|X\|×\|Y\| | 3×2 | 3×3 | 4×2 | 4×3 | 4×4 | 5×3 |
|---|---|---|---|---|---|---|
| MUS / témoins | 79/85 | 285/303 | 560/656 | 4113/5457 | 26180/31556 | 58920/101160 |
| proportion | 0,929 | 0,941 | 0,854 | 0,754 | 0,830 | 0,582 |

Tendances, sur les seules plages testées :
- à |Y| fixé, la proportion **baisse** quand |X| augmente (|Y| = 2 et 3,
  |X| ≤ 6 ; |Y| = 4, |X| ≤ 5) ;
- à |X| fixé, elle **n'est pas monotone** en |Y|. Elle croît pour |X| = 3
  (|Y| = 2..5 : 0,929 → 0,984). Elle décroît pour |X| = 5 (|Y| = 2..4 :
  0,793 → 0,539). Elle baisse puis remonte pour |X| = 4 (0,854 → 0,754 →
  0,830).

Les valeurs hors tableau viennent de
`evidence/refute-q2_minimal_core/out_witness_ext.txt`.

**Structure des MUS de la CNF complète — prouvée (annexe A) et vérifiée**
(exhaustivement pour |X| ≤ 5, |Y| ≤ 3 et |X| ≤ 4, |Y| ≤ 4 ; 997 MUS extraits
dans `reproduce.py`). On note d(T) = |T| − |N(T)| la déficience. Pour tout
MUS d'ensemble de pigeons P :

1. chaque clause de trou du MUS relie deux pigeons de P ;
2. d(T) < d(P) pour toute partie stricte T ⊊ P (T = ∅ compris), donc
   d(P) ≥ 1 ;
3. P est un témoin de Hall minimal **si et seulement si** d(P) = 1. Le MUS
   est alors formé des clauses de pigeon de P et d'un sous-ensemble minimal
   des clauses de trou induites. Réciproquement, toute telle union est un
   MUS.

Il existe des MUS de déficience 2 et 3. Pour |X| ≤ 5, |Y| ≤ 3, en
énumérant les MUS d'un représentant par classe d'isomorphisme de graphes, on
en compte 1 196 de déficience 1, 2 204 de déficience 2 et 744 de
déficience 3. Le plus petit est N(a) = N(b) = {y1}, N(c) = N(d) = {y1,y2},
avec le MUS {P(a), P(b), P(c), P(d), H(y1: a,c), H(y1: b,d), H(y2: c,d)}.
Son ensemble de pigeons {a,b,c,d} n'est pas un témoin minimal : il contient
le témoin minimal {a,b}. La condition 2 est nécessaire mais **pas
suffisante** pour qu'un ensemble P porte un MUS : avec 3 pigeons sur un
seul trou, tout MUS n'utilise que 2 des 3 clauses de pigeon.

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

**Théorème (prouvé en annexe B ; vérifié exactement, en fractions, sur
environ 2,9 millions de graphes avec n·m ≤ 16 et formats 3×6, 2×9, 2×10,
4×5).** Soit k = |N(X)| − |X| le nombre de trous excédentaires non isolés.
S'il existe un couplage saturant X :

  (3/2)^k ≤ r = modèles / couplages saturants ≤ (|X|+1)^k.

- Le rapport vaut 1 si et seulement si k = 0.
- La borne inférieure est atteinte exactement quand, pour tout couplage
  saturant M, les trous de N(X) libres pour M sont de degré 1 et ont des
  voisins distincts.

*Conséquences, et limite.* L'écart est exponentiel en |X| dès que
k = Ω(|X|). Il est sous-exponentiel si k = o(|X|/log|X|), d'après la borne
supérieure. Entre les deux, les bornes ne tranchent pas, et un excès
sous-linéaire peut suffire. Avec G = K_{a,2a} ⊔ (n−a)·K_{1,1} et
a ≈ n/ln n, on a k = a = o(n) mais ln r ≥ a·ln((a+1)/4) = n(1 − o(1)).
Valeurs exactes (`reproduce.py`), pour n = 50, 100, 200, 400 et 800 :
k/n = 0,26 → 0,15 et ln r / n = 0,549 → 0,635. L'écart n'est donc **pas**
exponentiel « exactement quand k est linéaire ».

| Famille | Modèles | Couplages saturants | Rapport |
|---|---|---|---|
| n étoiles K_{1,2} disjointes | 3^n | 2^n | (3/2)^n (borne atteinte) |
| n pigeons à d trous privés | (2^d−1)^n | d^n | ((2^d−1)/d)^n |
| K_{n,m} | n!·S(m+1, n+1) | m!/(m−n)! | Θ((n+1)^m / m^n) à n fixé |
| K_{n,n+1} | n!·C(n+2, 2) | (n+1)! | (n+2)/2 (seulement linéaire) |
| K_{n,2n} | ≥ n!·(n+1)^n | (2n)!/n! | ((n+1)/4)^n ≤ r ≤ (n+1)^n, donc ln r = n ln n + O(n) |

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
| « pour tout N ≥ 14, Schur(14,3) est une sous-CNF de Schur(N,3) et la même réfutation sert » | **prouvé** (la numérotation ne dépend pas de N ; monotonie de RUP) et **vérifié** : une même preuve DRUP de N = 14 est acceptée pour N = 14, 15, 20, 30, 40, 50 par `checker.py` et drat-trim. Contrôles négatifs : rejet *syntaxique* sur N = 13 (variables hors domaine) ; rejet *logique* sur F₁₄ privée de la clause ALO de 1, formule devenue SAT (`reproduce.py`) |
| scope « NOT A P!=NP LOWER BOUND » | **correct** : c'est la monotonie triviale des nombres de Schur ; une preuve de taille constante en N est le contraire d'une dureté |
| `original_core_clauses: 203` | **trompeur** : 203 est la CNF entière. Les 42 clauses AMO ne figurent dans **aucun** MUS (prouvé : garder une seule couleur par entier préserve tous les modèles). Les cœurs minimaux trouvés ont 133 à 137 clauses (14 ALO, 0 AMO). Tout MUS en contient au moins 101 (14 ALO et 87 clauses de somme individuellement nécessaires) ; la taille minimale reste ouverte dans [101, 133] |
| 2102 nœuds / 147 conflits | **non vérifiable** : source (sha `7fa57b61…`) non fournie. Pour comparaison, le DPLL de satlab donne 751 nœuds et le CDCL de 176 à 246 conflits selon la graine et l'ordre des clauses. 147 est aussi exactement le nombre de clauses de somme à N = 14 (3 × 49) : coïncidence ou champ mal étiqueté, indécidable |
| `verified: true` pour N > 14 | justifiable uniquement par l'argument d'inclusion (aucun artefact de preuve fourni) ; cet argument est correct |

*Réserve.* Que les comptes coïncident ne prouve pas que l'encodage d'origine
soit identique à la reconstruction. Avec une autre numérotation des
variables, l'inclusion pourrait ne plus être littérale.

## 6. Erreurs détectées (boucle de rétroaction)

Deux passes de vérification adverse ont réfuté plusieurs affirmations. Les
premières venaient des enquêtes ; les suivantes venaient de **la première
version de cette note**, y compris des corrections que j'y avais apportées
aux premières :

| Affirmation | Correction |
|---|---|
| (moi) « l'ensemble de pigeons de tout MUS est un témoin de Hall minimal » | faux ; vrai seulement à déficience 1 (§3) |
| « 100 % des littéraux appris sont dans le cœur, dans tous les runs » | faux : la colonne était arrondie à `%5.1f` ; comptes exacts : 62 / 137 496 hors cœur à k = 8 (§2) |
| (moi, 1re version) « l'arrondi masquait 96 littéraux » | ces 96 viennent d'autres instances, où l'affichage indiquait 99,8 ; l'arrondi masquait 62 littéraux ailleurs |
| « le témoin minimal vaut k sauf 2 instances » | 3 exceptions, d'après le propre fichier de sortie |
| « la proportion de MUS baisse avec la taille » | seulement avec \|X\| à \|Y\| fixé |
| (moi, 1re version) « elle ne baisse pas avec \|Y\| » | faux : non monotone en \|Y\| (§3) |
| (moi, 1re version) « l'écart est exponentiel exactement quand k croît linéairement » | réciproque fausse (§4) |
| « log r = n ln n + Θ(n) » pour K_{n,2n} | les bornes établies donnent seulement + O(n) |
| (moi, 1re version) statut « prouvé » sans preuve écrite (§3, §4) | preuves ajoutées en annexes A et B |
| (moi, 1re version) « toutes les réfutations citées sont certifiées » | `satlab.core` acceptait des UNSAT sans preuve ; il certifie désormais chaque verdict UNSAT |

Ces erreurs ont deux causes communes, qui sont des faiblesses du principe de
vérification lui-même plutôt que de chaque cas :

1. **Affirmation universelle tirée d'un résumé** (pourcentage arrondi,
   tendance observée dans une seule direction, extrapolation, « donc » non
   démontré). Règle : toute affirmation universelle repose sur un compteur
   exact (« 0 sur N ») ou sur une preuve écrite ; toute tendance précise sa
   direction et sa plage.
2. **Vérification appliquée aux résultats mais pas aux corrections ni à la
   synthèse.** Plusieurs erreurs de la première version étaient des
   corrections, ou des reformulations de résultats corrects. Règle : une
   correction ou une synthèse est une nouvelle affirmation et repasse par la
   même vérification adverse avant publication.

## 7. Reproduire

```bash
python3 studies/hall_schur/reproduce.py           # ~10 s, assertions, écrit results.json (déterministe)
python3 -m unittest discover -s satlab/tests -t . # inclut les nouveaux modules
```

Modules ajoutés à `satlab` :
- `matching` : couplage maximum itératif, témoin de Hall minimal, comptes
  de couplages ;
- `core` : MUS par suppression, redondance, verdicts UNSAT certifiés ;
- `hallproof` : preuve DRUP explicite à partir d'un témoin ;
- dans `generators` : `graph_php_cnf`, `bipartite_php` (statut attendu
  calculé par Hall, sans solveur) et `schur`.

---

## Annexe A — Preuves (Q2, structure des MUS)

Notation : F désigne l'encodage faible du graphe. Pour S ⊆ X, F_S est la CNF
induite (clauses P(x), x ∈ S, et H(y: x1,x2) avec x1, x2 ∈ S). Une
affectation qui choisit une arête vraie par pigeon d'un ensemble, avec des
trous distincts, satisfait toutes les clauses de trou ; on dira qu'elle
*réalise un couplage*.

**A1. Clauses de pigeon nécessaires.** Soit S un témoin minimal et x ∈ S.
Par minimalité, toute partie T ⊆ S \ {x} vérifie |N(T)| ≥ |T|. Par le
théorème de Hall, S \ {x} se couple dans N(S). Réaliser ce couplage
satisfait F_S \ {P(x)}. Corollaire :
|N(S)| ≥ |N(S \ {x})| ≥ |S| − 1, donc |N(S)| = |S| − 1.

**A2. Critère des clauses de trou.** Soit C = H(y: x1,x2) ∈ F_S.
- (⇐) Si S \ {x1,x2} se couple dans N(S) \ {y} par M, on met
  e(x1,y) = e(x2,y) = 1 et on réalise M. Seule C est violée, donc
  F_S \ {C} est SAT.
- (⇒) Soit σ un modèle de F_S \ {C}. F_S est UNSAT, donc σ viole C :
  e(x1,y) = e(x2,y) = 1. Les clauses H(y: x1,x3) restent présentes et
  imposent e(x3,y) = 0 pour tout autre x3 ∈ S. Chaque x ∈ S \ {x1,x2}
  choisit donc une arête vraie vers un trou y' ≠ y. Les clauses de trou
  sur y' sont intactes, donc ces choix sont deux à deux distincts : c'est
  le couplage cherché.

**A3. Structure des MUS.** Soit F' un MUS de F, P son ensemble de pigeons
(x ∈ P ⟺ P(x) ∈ F'), H ses clauses de trou.

1. *Toute clause de H relie deux pigeons de P.* Supposons que
   C = H(y: x1,x2) ∈ H avec x1 ∉ P. Par minimalité, F' \ {C} a un modèle σ.
   On met à 0 toutes les variables de x1 : seule la clause P(x1) contient
   ces variables positivement, et elle n'est pas dans F'. Le résultat
   satisfait donc F' \ {C} et aussi C, si bien que F' serait SAT :
   contradiction.

2. *d(T) < d(P) pour toute partie stricte T ⊊ P.* Supposons le contraire et
   prenons T maximal pour l'inclusion parmi les parties strictes de P
   vérifiant d(T) ≥ d(P). Le cas T = ∅, où d(∅) = 0, couvre l'hypothèse
   d(P) ≤ 0.

   *Hall pour P \ T dans Y \ N(T).* Soit U ⊆ P \ T non vide.
   - Si T ∪ U = P : d(P) ≤ d(T) donne |U| ≤ |N(P)| − |N(T)| = |N(U) \ N(T)|.
   - Sinon, par maximalité, d(T ∪ U) < d(P) ≤ d(T), ce qui donne
     |U| < |N(U) \ N(T)|.

   Il existe donc un couplage μ de P \ T dans Y \ N(T).

   *Contradiction.* Soit F'_T l'ensemble des clauses de F' n'impliquant que
   des pigeons de T ; c'est une partie stricte de F', donc elle est SAT. On
   choisit dans un modèle une arête vraie f(x) ∈ N(x) pour chaque x ∈ T, et
   l'on réalise {x → f(x)} ∪ μ. Les clauses de pigeon de P sont satisfaites.
   Considérons une clause H(y: x1,x2) ∈ F' :
   - si x1, x2 ∈ T, elle appartient à F'_T, et f(x1) = f(x2) = y la
     violerait déjà dans ce modèle ;
   - si un seul des deux est dans T, son trou f(·) est dans N(T) et l'autre,
     μ(·), est hors de N(T) ;
   - si aucun n'est dans T, μ est injectif.

   Aucune clause n'est violée, donc F' est SAT : contradiction. Avec T = ∅,
   on obtient en particulier d(P) ≥ 1.

3. *d(P) = 1 ⟺ P témoin minimal.*
   - (⇒) d(P) ≥ 1 et d(T) ≤ 0 pour toute partie stricte T : P viole la
     condition de Hall, et toutes ses parties strictes la vérifient.
   - (⇐) Par le corollaire de A1.

   F' est alors formé des clauses P(x), x ∈ P, et d'un H ⊆ F_P (par 1)
   minimal rendant l'ensemble UNSAT.

   *Réciproque.* Pour S témoin minimal et H ⊆ F_S minimal tel que
   P(S) ∪ H soit UNSAT, l'union P(S) ∪ H est un MUS :
   - retirer une clause de H la rend SAT, par minimalité de H ;
   - retirer P(x) donne un sous-ensemble de F_S \ {P(x)}, qui est SAT
     par A1.

**A4. La condition 2 n'est pas suffisante.** Trois pigeons a, b, c ont pour
seul voisin y. Alors d = 2 et toute partie stricte a une déficience ≤ 1.
Supposons qu'un MUS contienne P(a), P(b) et P(c). Il contient aussi au moins
une clause H(y: u,v), sans quoi il serait SAT. Mais {P(u), P(v), H(y: u,v)}
est UNSAT et en serait une partie stricte, ce qui contredit la minimalité.
Aucun MUS ne contient donc les trois clauses de pigeon.

## Annexe B — Preuves (Q3)

Soit n = |X|, et soit M un couplage saturant X. Ses trous libres dans N(X)
sont au nombre de k = |N(X)| − n, quel que soit M.

**B1. Décomposition.** Un modèle (S_x) contient exactement Π_x |S_x|
couplages saturants M (choisir M(x) ∈ S_x). Inversement, les modèles
contenant un M donné correspondent exactement aux applications h des k
trous libres vers X ∪ {⊥} telles que h(y) ∈ N(y) ∪ {⊥}. On pose alors
S_x = {M(x)} ∪ h⁻¹(x) ; les ensembles sont disjoints. En notant
a_x = |h⁻¹(x)| :

  modèles = Σ_M Σ_h Π_x 1/(1 + a_x).

**B2. Borne supérieure.** Chaque terme vaut au plus 1, et il y a
Π_{y libre} (1 + deg y) ≤ (n+1)^k applications h. D'où
modèles ≤ (n+1)^k · couplages.

**B3. Borne inférieure.** Pour M fixé, on choisit un voisin x(y) de chaque
trou libre et l'on ne garde que les h avec h(y) ∈ {⊥, x(y)}. Soit
c_x = |{y : x(y) = x}|, de sorte que Σ c_x = k. La somme restreinte vaut

  Π_x f(c_x), avec f(c) = Σ_a C(c,a)/(1+a) = (2^{c+1} − 1)/(c+1).

On a f(0) = 1 et f(c+1)/f(c) = (2^{c+2}−1)(c+1) / ((2^{c+1}−1)(c+2)). Ce
rapport vaut 3/2 pour c = 0 et 14/9 pour c = 1. Pour c ≥ 2, il dépasse
2 · 3/4 = 3/2 : le premier facteur est > 2 et (c+1)/(c+2) ≥ 3/4. Donc
f(c) ≥ (3/2)^c, et chaque M contribue au moins (3/2)^k. En sommant sur M :
modèles ≥ (3/2)^k · couplages.

**B4. Cas d'égalité et rapport 1.** Il y a égalité si et seulement si, pour
tout M, deux conditions sont remplies :
- aucun h n'a été écarté, c'est-à-dire que tout trou libre est de degré 1 ;
- f(c_x) = (3/2)^{c_x} pour tout x, c'est-à-dire c_x ≤ 1, car le rapport
  est > 3/2 dès c ≥ 1.

Si k = 0, B2 donne r ≤ 1 ; si k ≥ 1, B3 donne r ≥ 3/2. Donc r = 1 ⟺ k = 0.

**B5. Familles.**
- *K_{n,m}.* Un modèle est une application des m trous vers {⊥, 1..n} qui
  atteint chaque pigeon. L'inclusion-exclusion donne
  Σ_j (−1)^j C(n,j)(n+1−j)^m. On obtient aussi n!·S(m+1, n+1) en ajoutant
  un trou fictif dont le bloc représente ⊥.
- *K_{n,n+1}.* S(n+2, n+1) = C(n+2, 2), d'où r = (n+2)/2.
- *K_{n,2n}.* Pour la borne inférieure, on envoie les trous 1..n
  bijectivement sur les pigeons (n! façons), puis chacun des trous n+1..2n
  vers l'une quelconque des n+1 étiquettes. Les modèles obtenus sont
  distincts, d'où modèles ≥ n!(n+1)^n et
  r ≥ (n+1)^n / C(2n,n) ≥ ((n+1)/4)^n. Pour la borne supérieure,
  modèles ≤ (n+1)^{2n} et couplages = (2n)!/n! ≥ (n+1)^n.
- *Excès sous-linéaire.* Pour une union disjointe, modèles et couplages se
  multiplient, et K_{1,1} contribue un facteur 1. Donc
  r(K_{a,2a} ⊔ (n−a)K_{1,1}) = r(K_{a,2a}) ≥ ((a+1)/4)^a. Avec a ~ n/ln n,
  ln r ≥ a(ln a − ln 4) = n(1 − o(1)).

## Annexe C — Preuve de la construction de Q1

Fixons des pigeons p_1..p_{m+1} de S, et posons T = N(S), |T| = m.
- Le lemme E(j+1,H,h) = D(j+1,H) ∨ ¬e(p_{j+1},h) est RUP. On nie le lemme :
  e(p_{j+1},h) est vrai et tous les littéraux de D(j+1,H) sont faux. Les
  clauses de trou sur h imposent ¬e(p_i,h) pour i ≤ j. D(j, H\{h}) est déjà
  dans la base, et tous ses littéraux sont alors faux : ils pointent hors de
  H, ou vers h. C'est un conflit.
- D(j+1,H) est RUP : les lemmes E donnent ¬e(p_{j+1},h) pour tout h ∈ H
  voisin de p_{j+1}, et la clause P(p_{j+1}) est alors fausse.
- Ordre de génération : niveau par niveau, j = 1..m, donc chaque
  D(j, H\{h}) précède son usage. D(1,∅) = P(p_1) est une clause d'entrée.
  D(m+1, T) est vide, car tous les voisins sont dans T.
- Compte : Σ_{j=1}^{m} C(m,j)(j+1) = m·2^{m−1} + 2^m − 1 = 2^{m−1}(m+2) − 1,
  avec égalité quand chaque p_{j+1} est voisin de tout H.
