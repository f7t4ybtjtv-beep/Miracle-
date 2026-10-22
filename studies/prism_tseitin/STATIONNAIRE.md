# Démonstration : la réfutation de Tseitin sur le prisme T_k a 32k − 33 résolvantes

Objet : compléter la vérification par calcul de `verify.py` (k = 3..60 et 100) par une
démonstration pour tout k ≥ 3, pour l'ordre d'élimination périodique décrit ci-dessous.
Ce n'est qu'une majoration : la longueur minimale de T_k n'est pas traitée.

## 1. Cadre

**Graphe.** Le prisme a des sommets t_i et u_i, pour i ∈ ℤ/kℤ, et trois types d'arêtes :
rail haut T_i = t_i t_{i+1}, rail bas B_i = u_i u_{i+1}, barreau R_i = t_i u_i.
Chaque sommet est de degré 3. Les variables sont les arêtes, donc 3k variables.

**Charges.** c(t_0) = 1, c(v) = 0 pour les autres sommets. Chaque arête compte deux fois dans
la somme des parités, donc Σ_v c(v) ≡ 1 contredit la somme des parités : T_k est insatisfiable.

**Contraintes.** Pour un ensemble X de variables et p ∈ {0,1}, on note P(X,p) l'ensemble
des clauses C_α, une par affectation α : X → {0,1} de parité |α| := Σ_{x∈X} α(x) ≢ p. La
clause C_α est falsifiée par α et seulement par α : elle contient x si α(x) = 0 et ¬x si
α(x) = 1. Il y a 2^{|X|−1} clauses dans P(X,p). Le CNF de Tseitin est la réunion, sur les
sommets v, de P(∂v, c(v)), où ∂v est l'ensemble des trois arêtes incidentes à v.

Une clause de P(X,p) a un nombre de littéraux négatifs ≡ p+1 (mod 2) : c'est la parité de
l'affectation qu'elle interdit.

**Ordre d'élimination.** On élimine dans l'ordre des clés ((i+OFFS[t])·3 + PERM.index(t)),
avec OFFS = (1,1,0) et PERM = (2,0,1). Concrètement, la suite est :

  R_0 ; puis pour j = 1, …, k−1 : R_j, T_{j−1}, B_{j−1} ; puis T_{k−1}, B_{k−1}.

Il y a 1 + 3(k−1) + 2 = 3k éliminations. On s'arrête dès que la clause vide apparaît.

**Dédoublonnage.** Une résolvante déjà présente n'est pas comptée. Le compte est le nombre
de résolvantes distinctes produites, ce qui est aussi le nombre de lignes de la preuve.

## 2. Trois lemmes de résolution

**Lemme 1 (variables disjointes).** Soient X et Y disjoints, x ∉ X ∪ Y, p, q ∈ {0,1}.
La résolution de P(X∪{x},p) avec P(Y∪{x},q) sur x donne exactement les 2^{|X|+|Y|−1}
clauses de P(X∪Y, p+q), toutes distinctes et non tautologiques.

*Démonstration.* Une résolvante de C_α et C_β sur x exige que l'un contienne x et l'autre
¬x, donc α(x) ≠ β(x). Posons a = α|X, b = β|Y et γ = a ∪ b, affectation sur X∪Y. Comme X et
Y sont disjoints, la résolvante est non tautologique et falsifiée exactement par γ.
- Si α(x) = 0, β(x) = 1 : C_α interdit (a,0), donc |a| ≡ p+1 ; C_β interdit (b,1), donc
  |b| + 1 ≡ q+1, donc |b| ≡ q. Alors |γ| ≡ p+q+1.
- Si α(x) = 1, β(x) = 0 : par symétrie, |a| ≡ p et |b| ≡ q+1, donc |γ| ≡ p+q+1.
Les deux cas donnent les γ de parité p+q+1, et chacun n'apparaît qu'une fois, car la
parité de a décide du cas. Les résolvantes sont donc les clauses qui interdisent les γ de
parité p+q+1, c'est-à-dire P(X∪Y, p+q). ∎

**Lemme 2 (une variable commune).** Soient X et Y tels que X ∩ Y = {b}, et x ∉ X ∪ Y.
La résolution de P(X∪{x},p) avec P(Y∪{x},q) sur x donne exactement les clauses C_γ pour
les γ sur X∪Y tels que |γ| + γ(b) ≡ p+q+1 ; il y en a 2^{|X|+|Y|−2}, toutes distinctes.

*Démonstration.* Une résolvante non tautologique exige que α et β aient le même signe sur b,
donc γ est bien défini sur X∪Y. Avec a = α|X et b' = β|Y, on a |a| + |b'| = |γ| + γ(b),
car b est compté deux fois. Le reste du calcul est celui du lemme 1. ∎

**Lemme 3 (variables complètes).** Si S est un ensemble de m variables et si toutes les
clauses sur S sont présentes, la résolution sur une variable de S donne les 2^{m−1} clauses
complètes sur S∖{x}, toutes distinctes.

*Démonstration.* Pour chaque affectation s de S∖{x}, la clause qui interdit (s, x=0) et celle
qui interdit (s, x=1) donnent la clause qui interdit s. ∎

## 3. Déroulement et récurrence

Soit Σ_j l'ensemble des clauses après l'élimination de R_0, …, R_j, T_0, …, T_{j−1},
B_0, …, B_{j−1}. Posons W_j = {T_j, B_j, T_{k−1}, B_{k−1}}.

**Invariant.** Pour 0 ≤ j ≤ k−2,

  Σ_j = Orig_{≥j+1} ∪ P(W_j, 1),

où Orig_{≥j+1} est l'ensemble des clauses de Tseitin des sommets t_i et u_i pour i ≥ j+1, et
P(W_j,1) a 8 clauses. Cette parité 1 est la charge de la région {colonnes 0..j} : les arêtes
frontières de cette région sont exactement W_j.

**Cas de base j = 0.** On élimine R_0, qui appartient à ∂t_0 = {T_{k−1},T_0,R_0} (charge 1) et
à ∂u_0 = {B_{k−1},B_0,R_0} (charge 0). Par le lemme 1 avec X = {T_{k−1},T_0},
Y = {B_{k−1},B_0}, p = 1, q = 0 : on obtient P(W_0, 1), soit 8 résolvantes. Donc Σ_0 =
Orig_{≥1} ∪ P(W_0,1).

**Pas d'induction, pour 0 ≤ j ≤ k−3.** On suppose Σ_j = Orig_{≥j+1} ∪ P(W_j,1). Le bloc j+1
élimine R_{j+1}, T_j, B_j. Comme j+1 ≤ k−2, les variables T_{j+1}, B_{j+1} sont distinctes de
T_{k−1}, B_{k−1}, et T_j, B_j ne sont pas dans {T_{j+1}, B_{j+1}} : les hypothèses des lemmes
sont satisfaites. Les seules clauses contenant R_{j+1}, T_j ou B_j sont celles énumérées ci-dessous.

*Étape R_{j+1}.* Les clauses contenant R_{j+1} sont P(∂t_{j+1}, 0) et P(∂u_{j+1}, 0), avec
∂t_{j+1} = {T_j, T_{j+1}, R_{j+1}} et ∂u_{j+1} = {B_j, B_{j+1}, R_{j+1}}. Ces deux ensembles
sont disjoints une fois R_{j+1} retiré. Lemme 1, avec X = {T_j,T_{j+1}}, Y = {B_j,B_{j+1}},
p = q = 0 : on obtient P({T_j,T_{j+1},B_j,B_{j+1}}, 0), soit **8** résolvantes.

*Étape T_j.* Les clauses contenant T_j sont P(W_j, 1) (avec T_j, B_j, T_{k−1}, B_{k−1}) et
P({T_j, T_{j+1}, B_j, B_{j+1}}, 0) (la seconde vient de l'étape R_{j+1}). Retirons T_j : les
ensembles restants sont X = {B_j, T_{k−1}, B_{k−1}} et Y = {B_j, T_{j+1}, B_{j+1}}, qui se
recoupent exactement sur b = B_j. Lemme 2 avec p = 1, q = 0 : les résolvantes sont les C_γ
pour γ sur les cinq variables {B_j, T_{k−1}, B_{k−1}, T_{j+1}, B_{j+1}} avec
|γ| + γ(B_j) ≡ p+q+1 ≡ 0.
Posons w = (T_{k−1}, B_{k−1}) et s = (T_{j+1}, B_{j+1}). Comme |γ| = γ(B_j) + |w| + |s|, on a
|γ| + γ(B_j) ≡ |w| + |s|. La condition est donc |w| + |s| ≡ 0, indépendante de γ(B_j). Il y a
donc **16** résolvantes : pour chacune des 8 valeurs (w,s) de parité 0, les deux valeurs de B_j.

*Étape B_j.* Les clauses contenant B_j sont les 16 résolvantes précédentes. Pour chaque
(w,s) de parité ≡ 0 (ici la restriction de γ aux quatre autres variables), les deux clauses
« γ(B_j)=0 » et « γ(B_j)=1 » sont présentes. Leur résolution sur B_j donne la clause qui
interdit (w,s) : c'est l'ensemble P({T_{k−1},B_{k−1},T_{j+1},B_{j+1}}, 1), car interdire les
(w,s) de parité 0 revient à imposer parité 1. Il y a **8** résolvantes distinctes.

Le bloc j+1 donne donc 8 + 16 + 8 = **32** résolvantes, et Σ_{j+1} = Orig_{≥j+2} ∪
P(W_{j+1}, 1), ce qui est l'invariant au rang j+1.

## 4. La queue : j = k−2 et les dernières éliminations

Au rang j = k−2, on a Σ_{k−2} = Orig_{≥k−1} ∪ P(W_{k−2}, 1), avec W_{k−2} = {T_{k−2},
B_{k−2}, T_{k−1}, B_{k−1}}.

- **R_{k−1}** : les clauses contenant R_{k−1} sont P(∂t_{k−1}, 0) et P(∂u_{k−1}, 0), avec
  ∂t_{k−1} = {T_{k−2}, T_{k−1}, R_{k−1}} et ∂u_{k−1} = {B_{k−2}, B_{k−1}, R_{k−1}}. Lemme 1 :
  P(W_{k−2}, 0), soit **8** résolvantes. L'état contient alors P(W_{k−2},1) et
  P(W_{k−2},0) : deux contraintes contradictoires sur les mêmes quatre variables.
- **T_{k−2}** : les clauses contenant T_{k−2} sont P(W_{k−2},1) et P(W_{k−2},0), qui portent
  sur les mêmes quatre variables. Après retrait de T_{k−2}, les deux ensembles sont sur
  S := {B_{k−2}, T_{k−1}, B_{k−1}} et se recoupent sur les trois variables de S. Une résolvante
  n'est non tautologique que si les deux affectations α et β coïncident sur S ; notons γ leur
  valeur commune. Avec p = 1 pour le premier ensemble et q = 0 pour le second :
  - si α(T_{k−2}) = 0 et β(T_{k−2}) = 1, la clause de P(W,1) exige |γ| ≡ p+1 = 0, et celle de
    P(W,0) exige |γ| ≡ q = 0 : on obtient les γ de parité 0 ;
  - si α(T_{k−2}) = 1 et β(T_{k−2}) = 0, on obtient |γ| ≡ p = 1 et |γ| ≡ q+1 = 1 : les γ de
    parité 1.
  Toutes les affectations de S sont donc obtenues une fois chacune : ce sont les **8** clauses
  complètes sur S.
- **B_{k−2}** : les clauses contenant B_{k−2} sont les 8 clauses complètes sur S. Lemme 3 :
  **4** résolvantes (les clauses complètes sur {T_{k−1}, B_{k−1}}).
- **T_{k−1}** : lemme 3 sur les 4 clauses complètes sur {T_{k−1}, B_{k−1}} : **2** résolvantes.
- **B_{k−1}** : lemme 3 sur les 2 clauses complètes sur {B_{k−1}} : **1** résolvante, la clause
  vide. On s'arrête.

La queue compte donc 8 + 8 + 4 + 2 + 1 = **23** résolvantes, R_{k−1} inclus.

## 5. Total

- R_0 : 8.
- Blocs j+1 = 1, …, k−2 : 32 chacun, soit 32(k−2).
- Queue (R_{k−1}, T_{k−2}, B_{k−2}, T_{k−1}, B_{k−1}) : 23.

Total : 8 + 32(k−2) + 23 = 32k − 33, pour tout k ≥ 3.

La largeur maximale est 5 : elle est atteinte aux étapes T_j, où les clauses ont cinq
variables. Les autres étapes ont des clauses de largeur au plus 4.

**Remarque sur k = 3.** Les blocs stationnaires sont j+1 ∈ {1}, et la queue est le bloc 2. Le
total est 8 + 32 + 23 = 63, ce que `verify.py` a bien vérifié.

## 6. Ce que cette démonstration établit, et ce qu'elle n'établit pas

**Établi.** Pour tout k ≥ 3, l'ordre périodique donne une réfutation de résolution de T_k avec
exactement 32k − 33 résolvantes distinctes, de largeur au plus 5. Donc L(T_k) ≤ 32k − 33.

**Non établi.**
- La longueur minimale L(T_k) : on n'a que cette majoration.
- Une borne inférieure de la forme 32k − c : non cherchée.
- La forme exacte du document : ses étapes intermédiaires (« 15 résolutions », etc.) ne
  sont pas reconstituées ici.
- Cette démonstration n'a pas été relue par un vérificateur indépendant. Les formules
  des lemmes ont été contrôlées par calcul : `verify.py` vérifie les comptes par étape
  (motif 8 ; 8, 16, 8 ; queue 8, 8, 4, 2, 1) pour k = 3..60 et 100. L'invariant de bord
  (parité 1 sur W_j après chaque bloc) a été contrôlé pour k = 4, 7, 12, 30. Les lemmes 1 et 2
  sont des calculs élémentaires sur la parité.
