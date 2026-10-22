# Tseitin sur prismes : vérification de la « recherche contre » du 22 octobre 2026

Script : `verify.py` (satlab seul, plus drat-trim si fourni). Résultats : `results.json`.

```bash
python3 studies/prism_tseitin/verify.py --drat /chemin/vers/drat-trim
```

Rien ici ne touche à P contre NP. Le document le dit lui-même, et la portée se
limite à une famille et à un système de preuve.

## 1. Ce qui est établi

| Affirmation du document | Résultat |
|---|---|
| Familles : 9/24, 30/80, 60/160, 150/400 (variables / clauses) | **vérifié** : 3k variables et 8k clauses, pour le prisme C_k × K_2 et une charge impaire |
| Formules insatisfiables | **vérifié** : argument de parité (chaque arête compte deux fois) et CDCL avec preuve DRUP validée, pour k = 3..6 |
| Étapes 71, 351, 751, 1951 pour k = 3, 10, 20, 50 | **ces nombres suivent exactement 40k − 49** ; l'élimination colonne par colonne donne 40k − 49 aussi (k = 3, 10, 12) |
| « L(T_k) ≤ 32k − 33 » | **vérifié** pour k = 3..60 et k = 100, par des réfutations explicites, toutes validées par satlab (`checker.py`), largeur maximale 5 |
| « 3 167 inférences pour 300 variables » (k = 100) | **reproduit** : 3 167 résolvantes, validées par `checker.py` |
| Validation par drat-trim | **vérifié** pour k = 3, 4, 5, 10, 50 |

L'ordre utilisé est périodique : chaque colonne ajoutée ajoute exactement 32
résolvantes. Il a été trouvé par recherche sur k = 9..11, puis vérifié pour
k = 3..60 et k = 100. Un ordre glouton aléatoire donne aussi 32k − 33 pour
k ≥ 4 (mais pas 40k − 49).

## 2. Ce qui n'est pas établi

- **La borne pour tout k.** Les nombres sont vérifiés pour k = 3..60 et k = 100.
  Une démonstration pour tout k demande un argument de régime stationnaire : les
  résolvantes ajoutées par colonne dépendent seulement d'une structure de
  frontière qui se répète. Cet argument n'est pas écrit ici. Le texte du
  document ne le fournit pas non plus.
- **La longueur minimale L(T_k).** Nous ne contrôlons que des majorations. Une
  borne inférieure n'a pas été cherchée, et le document n'en fournit pas.
- **La décomposition en trois opérations.** Les formules du document ont été
  perdues en conversion : « résolutions » sans nombre, « 15 résolutions » pour
  l'élimination finale, « 18 variables » pour le second certificat. Je ne peux
  pas vérifier ces étapes individuellement.
- **Les programmes et certificats** (« Télécharger les programmes… ») : aucun
  fichier n'est disponible. Les résultats reproduits viennent de mes propres
  calculs, et non de leur code.
- **Le contrôle algébrique** : le document dit que chaque résultat a passé un
  contrôle algébrique. Je n'ai pas fait d'élimination gaussienne ; le contrôle
  ici est la preuve de parité et la validation par checker/drat-trim.

## 3. Mise en perspective

Le résultat « les contradictions de Tseitin sur graphes de largeur bornée ont
des preuves de résolution courtes » est classique. Pour une largeur bornée,
l'élimination de Davis–Putnam donne une preuve linéaire, ce que ce script
reproduit. Pour la résolution régulière, Alekhnovich et Razborov donnent une
majoration en 2^{O(tw(G))}·poly(|V|) pour les graphes de degré constant. Je n'ai
pas revérifié cette référence dans le texte original ; je la cite d'après une
recherche bibliographique (voir `NOTE.md` et les sources ci-dessous).

Le document dit aussi que les contradictions de Tseitin sur certains expanseurs
demandent des preuves exponentielles, citant Ben-Sasson et Wigderson. C'est
exact dans l'ensemble, mais la borne exponentielle pour Tseitin sur expanseurs
est due à Urquhart (1987), que Ben-Sasson et Wigderson étendent par la largeur.

Conclusion : la famille de prismes ne montre pas une séparation, puisqu'elle est
facile pour la résolution. Les nombres du document sont cohérents avec les
résultats connus, et la borne 32k − 33 est confirmée pour les valeurs
vérifiées.

Sources de la recherche bibliographique :
- [Alekhnovich–Razborov, Satisfiability, branch-width and Tseitin tautologies (FOCS 2002) ; version Computational Complexity 20 (2011), DOI 10.1007/s00037-011-0033-1](https://doi.org/10.1007/s00037-011-0033-1)
- [de Colnet et Mengel, JAIR 2023 : bornes pour la résolution régulière sur graphes à degré borné](https://jair.org/index.php/jair/article/download/13521/26891/33045)
