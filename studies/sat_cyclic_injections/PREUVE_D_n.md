# Preuve : D_n admet une réfutation de résolution de taille linéaire et de largeur ≤ 23

Objet : compléter le §4 du document, qui ne faisait qu'esquisser l'invariant
de largeur. Ici, chaque étape est démontrée. Le lemme 3 est aussi vérifié par
calcul pour tout n = 6..200 (`verify.py`, fonction `check_d_invariant`).

## 1. Définitions

Soit n ≥ 6. Les pigeons ordinaires sont les éléments de ℤ/nℤ ; le pigeon
supplémentaire est noté ∞. Pour un pigeon p, N(p) désigne ses trous voisins :

- N(p) = {p, p+1, p+3} pour p ordinaire ;
- N(∞) = {0, 2, 4}.

Une variable x_{p,h} existe pour chaque arête (p,h). La CNF D_n contient :

- la clause de pigeon P(p) = ∨_{h∈N(p)} x_{p,h} pour chaque pigeon p ;
- la clause de trou ¬x_{p,h} ∨ ¬x_{q,h} pour chaque trou h et chaque paire de
  pigeons distincts p, q ∈ N⁻¹(h).

Pour un trou ordinaire h, N⁻¹(h) = {h, h−1, h−3}, et ∞ s'y ajoute si
h ∈ {0, 2, 4}.

On dit qu'une variable est « du pigeon p » si elle s'écrit x_{p,h}.

## 2. Faits sur le graphe d'interaction

**Fait 1.** Deux pigeons ordinaires p ≠ q partagent un trou seulement si
q − p ∈ {±1, ±2, ±3} mod n. En effet, les trois pigeons de N⁻¹(h) sont h, h−1
et h−3, dont les écarts deux à deux valent 1, 2 et 3.

**Fait 2.** Le pigeon ∞ partage un trou avec un pigeon ordinaire seulement si
ce pigeon appartient à A = {n−3, n−1, 0, 1, 2, 3, 4}. En effet,
N⁻¹(0) = {0, n−1, n−3}, N⁻¹(2) = {2, 1, n−1} et N⁻¹(4) = {4, 3, 1}, auxquels
s'ajoute ∞.

**Fait 3 (graphe primal).** Deux variables sont liées dans le graphe primal
si elles apparaissent dans une même clause. Une variable du pigeon p n'est
liée qu'à des variables de pigeons q tels que p = q ou p et q partagent un
trou. Les variables de P(p) sont liées entre elles, et les clauses de trou
lient deux variables de pigeons qui partagent le trou.

## 3. Ordre d'élimination et ensembles de pigeons

Soit σ l'ordre suivant : d'abord les pigeons 3, 4, …, n−1 (les trois variables
de chaque pigeon consécutivement, dans un ordre quelconque) ; ensuite les
pigeons 0, 1, 2 ; enfin ∞.

Pour 3 ≤ k ≤ n−1, on pose

  B_k = {0, 1, 2, ∞} ∪ {k, k+1, k+2, k+3} (mod n).

Ces ensembles ont au plus 8 pigeons, donc au plus 24 variables. Pour k+j ≥ n,
l'indice k+j est remplacé par k+j−n ∈ {0,1,2}, déjà présent dans
{0,1,2,∞}. Pour k ≤ n−4, les quatre indices k, …, k+3 sont distincts et
ordinaires.

Soit F_k = B_k \ {k} = {0,1,2,∞} ∪ {k+1, k+2, k+3}.

## 4. Élimination de Davis–Putnam et graphe de remplissage

L'élimination de Davis–Putnam d'une variable v remplace les clauses qui
contiennent v par leurs résolvantes sur v, en retirant les clauses qui
contiennent v. Elle préserve la satisfiabilité : une formule est
insatisfiable si et seulement si la formule obtenue après élimination de
toutes les variables contient la clause vide.

Le graphe primal de la formule courante évolue de la façon suivante : éliminer
v rend le voisinage N(v) = {u : u liée à v} clique (les résolvantes contiennent
toutes des variables de N(v)), puis retire v. Une clause contenant v au moment
de son élimination n'a pas de variable hors de N[v], et ses résolvantes n'ont
de variable que dans N(v).

**Lemme 0.** Le nombre de résolvantes distinctes produites en éliminant v est
au plus 3^{|N(v)|+1} : ce sont des clauses non tautologiques sur N[v], et il y a
3^{|N[v]|} telles clauses (chaque variable positive, négative ou absente).

## 5. Lemme d'invariant

**Lemme 1 (invariant).** Pour tout k ∈ {3, …, n−1}, au moment où l'on élimine
l'une des variables du pigeon k (quel que soit l'état des autres éliminations
du pigeon k), le voisinage courant N(v) de la variable v est inclus dans
l'ensemble des variables des pigeons de B_k.

*Démonstration.* Par récurrence sur k, avec une sous-récurrence sur les
éliminations à l'intérieur du pigeon k.

**Étape (a) : ce que laissent les étapes précédentes.** Soit k ≥ 3. Après
l'élimination complète des pigeons 3, …, k−1, les arêtes restantes du graphe
primal sont de deux sortes :

- des arêtes originales entre variables restantes ;
- des arêtes de remplissage, créées pendant une élimination d'un pigeon k' avec
  3 ≤ k' ≤ k−1.

*Arêtes de remplissage.* Pendant l'élimination du pigeon k', tout voisinage
courant d'une variable de ce pigeon est inclus dans B_{k'} (par hypothèse de
récurrence, lemme 1 pour k'). Les arêtes créées sont donc des paires de
variables de B_{k'}. Une fois le pigeon k' entièrement éliminé, les arêtes
qui touchent encore un de ses variables disparaissent. Il reste donc des arêtes
de remplissage contenues dans B_{k'} \ {k'} = F_{k'}.

Une arête de remplissage survivante à l'étape k, créée à l'étape k' ≤ k−1,
relie deux variables de pigeons dans F_{k'} = {0,1,2,∞} ∪ {k'+1, k'+2, k'+3}.
Comme les pigeons 3, …, k−1 sont éliminés, seules comptent les extrémités de
pigeons ≥ k, et elles appartiennent à {k'+1, k'+2, k'+3} ∩ [k, n−1]. Puisque
k' ≤ k−1, on a k'+3 ≤ k+2, donc ces extrémités sont dans {k, k+1, k+2}.

*Arêtes originales.* Une variable du pigeon k est liée à des variables de
pigeons q tels que q ∈ {k−3, …, k+3} (mod n), par le fait 1, et à ∞ si
k ∈ A, par le fait 2. Les pigeons q ∈ {k−3, k−2, k−1} avec q ≥ 3 sont déjà
éliminés ; ceux avec q ∈ {0, 1, 2} appartiennent à B_k. Il reste donc
q ∈ {k, …, k+3} ∪ {0, 1, 2, ∞}, c'est-à-dire des pigeons de B_k.

Conclusion de (a) : au début de l'élimination du pigeon k, tout voisin d'une
variable du pigeon k appartient à un pigeon de B_k.

**Étape (b) : préservation au cours de l'élimination du pigeon k.** Supposons
l'hypothèse vraie pour l'état courant : chaque variable restante du pigeon k a
son voisinage dans B_k. Soit v une variable du pigeon k éliminée à cet instant.
Son voisinage N(v) est dans B_k. Après élimination, pour toute variable
restante u, le nouveau voisinage est (N(u) \ {v}) ∪ (N(v) \ {u}). Il reste donc
dans B_k. Par récurrence sur les éliminations de ce pigeon, l'hypothèse reste
vraie pour toutes les variables restantes du pigeon k, et tous les voisinages
au moment d'une élimination sont dans B_k.

Cela prouve le lemme 1. ∎

**Lemme 2 (taille des résolvantes).** Pour k ∈ {3, …, n−1}, chaque résolvante
produite pendant l'élimination du pigeon k est une clause sur des variables de
B_k, donc sur au plus 24 variables, et sa largeur est au plus 23 (une
résolvante n'a pas la variable pivot).

*Démonstration.* Les clauses qui contiennent v sont sur N[v] ⊆ B_k (lemme 1),
donc leurs résolvantes sont sur N(v) ⊆ B_k \ {v}. ∎

## 6. Conclusion : borne de taille

**Théorème.** Pour tout n ≥ 6, D_n admet une réfutation de résolution de largeur
au plus 23 et de taille au plus (3n+3)·3^24, c'est-à-dire linéaire en n.

*Démonstration.* On élimine les variables selon σ. Pour les pigeons 3, …, n−1,
le lemme 2 et le lemme 0 donnent au plus 3^24 nouvelles résolvantes par
variable éliminée. Il reste à éliminer les 12 variables des pigeons 0, 1, 2 et ∞,
qui ne produisent qu'un nombre constant de résolvantes (au plus 3^12 par
variable). Le nombre de variables est 3n+3. D'où un total d'au plus
(3n+3)·3^24 résolvantes. Par la correction de Davis–Putnam, la formule
insatisfiable aboutit à la clause vide, qui est donc dérivée. La suite des
résolvantes, dans l'ordre de leur production, est une réfutation de résolution
valide : chaque résolvante est dérivée de deux clauses déjà présentes. ∎

**Remarque.** La borne 3^24 est très lâche. Les mesures de `verify.py` donnent
1 120 résolvantes pour n = 6, 12 399 pour n = 20, et une croissance d'environ
700 résolvantes par pigeon ajouté. La largeur mesurée des clauses produites est
au plus 10 pour n ≤ 20. Le voisinage maximal mesuré pour n ≤ 200 est 13, donc
un bloc de 14 variables, ce qui est compatible avec le lemme 2.

## 7. Ce que cette preuve ne montre pas

- Elle ne dit rien sur la taille minimale d'une réfutation de D_n, ni sur la
  question de savoir si O(2^k) est atteignable pour les témoins de Hall
  (question du document d'origine, §2).
- Elle n'utilise que la structure de D_n. Pour un autre graphe de degré 3 avec
  une largeur de bande bornée, le même argument s'applique, mais la constante
  change.
- Elle ne contredit pas les bornes inférieures de résolution pour les familles
  expanseurs (Haken 1985 ; Ben-Sasson–Wigderson 2001 ; de Rezende et al. 2025),
  car D_n a une largeur de bande bornée, donc n'est pas un expanseur.
