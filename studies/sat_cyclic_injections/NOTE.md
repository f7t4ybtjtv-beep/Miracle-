# Injections impossibles sur graphes cycliques (C_n, D_n) — vérification

Date : 19 octobre 2026. Objet : vérifier le document reçu sur les familles
C_n (degré 2) et D_n (degré 3). Rien ici ne tranche P contre NP : les
affirmations vérifiables sont des faits sur des familles finies, et une borne
de résolution pour une famille donnée ne suffit pas à établir une borne
générale.

Script : `verify.py` (satlab seul, plus drat-trim si fourni). Résultats :
`results.json`. Exécution :

```bash
python3 studies/sat_cyclic_injections/verify.py --drat /chemin/vers/drat-trim
```

## 1. Ce qui n'a pas pu être vérifié

- **Fichiers cités absents.** `verify_php_proofs.py`, `php_sparse3_n6_proof.json`
  et les autres certificats JSON n'existent ni dans le dépôt ni sur la machine.
  Les résultats qu'ils porteraient ne sont donc pas contrôlés. Je les ai
  recalculés autrement (§3 et §4).
- **Compteurs de D_6 à largeur 3, en partie reproduits.** Le document annonce
  11 523 clauses, 12 831 210 couples candidats et un certificat de 153 résolvantes.
  - *11 523 clauses* : reproduit. C'est la taille de la fermeture complète par
    résolution de largeur ≤ 3, axiomes compris (11 489 clauses dérivées + 34 axiomes).
  - *Certificat* : un certificat de **124 résolvantes distinctes** est trouvé et
    vérifié (satlab, drat-trim, et contrôle explicite de chaque étape comme
    résolvante exacte). Il est plus court que les 153 annoncés. Le coût d'arbre
    minimal dans cette fermeture est 139. Je ne prétends pas que 124 soit minimal.
  - *12 831 210 couples candidats* : non reproduit. Ce nombre dépend de la
    procédure de saturation (ordre des paires, arrêt ou non) ; ma procédure
    complète compte 21 121 428 paires.

## 2. Affirmations vérifiées

| Affirmation du document | Résultat |
|---|---|
| C_n : 2n+2 variables, 2n+5 clauses, toutes de largeur ≤ 2 | vérifié, n = 6..12 et 50 |
| D_n : 3n+3 variables, 4n+10 clauses, largeur initiale ≤ 3 | vérifié, n = 6, 8, 10, 12, 50 |
| Hall : seule violation = U entier (C_n et D_n) | vérifié exhaustivement, n = 6..12 |
| Couplages constructifs décrits au §2, pour tout pigeon omis | vérifié pour tout n = 6..200 |
| C_n : réfutation explicite de 3n+4 étapes, largeur 2 (§3) | construite pas à pas, chaque résolvante contrôlée ; validée par satlab et drat-trim pour n = 2..12 et 50 |
| Tableau du §5 pour C_6, C_12, C_50 (variables, axiomes, étapes) | vérifié (14/17/22, 26/29/40, 102/105/154) |
| D_n : élimination d'après le §4 avec un bloc de 24 variables au plus | voisinage maximal mesuré : 13 pour n = 6..200, soit un bloc de 14 variables ; invariant du lemme 1 de `PREUVE_D_n.md` vérifié pour n = 6..200. La preuve écrite est dans `PREUVE_D_n.md` |
| D_n : Davis–Putnam avec dédoublonnage donne une preuve valide, de taille linéaire | valide par satlab et drat-trim pour n = 6, 8, 10, 12, 16, 20 ; 1 120 → 12 399 résolvantes, environ 700 par pigeon ajouté |
| D_6 : réfutation de largeur 3 | fermeture de 11 523 clauses (reproduit) ; certificat de 124 résolvantes, plus court que 153, vérifié par satlab et drat-trim |
| Frontières (§6) : C_n, {0, k} ratio 2/k ; D_n, {0, k+1, k+2} ratio 3/k | vérifié, n = 6..15 |

Affirmation générale du §4 : une réfutation de D_n de largeur ≤ 24 et de taille
≤ (3n+3)·3^24. Le document ne donnait qu'une esquisse de l'invariant de bloc.
Elle est maintenant démontrée dans `PREUVE_D_n.md` (lemmes 1 et 2, théorème du §6).
La borne est très lâche ; la taille mesurée est de l'ordre de 700 par pigeon.

## 3. Imprécisions à corriger dans le document

1. « C_n (degré 2) » : c'est le degré des pigeons. Les trous 0 et 1 de C_n ont
   degré 3 ; les trous 0, 2 et 4 de D_n ont degré 4.
2. « 128, 512, 2 048, 8 192 sous-ensembles » : ce sont les 2^{n+1} sous-ensembles
   y compris l'ensemble vide. La vérification énumère les sous-ensembles non
   vides (2^{n+1} − 1), avec le même résultat.
3. « Largeur d'élimination 13 » : c'est le voisinage maximal au moment d'une
   élimination. La taille du bloc, voisinage compris, est 14. Cela reste
   compatible avec la borne 24.
4. « La construction fonctionne également pour n ≥ 2 » (C_n) : vérifié pour
   n = 2..12 et 50, donc correct.
5. §6, « P≠NP exige une borne inférieure indépendante de l'algorithme et du
   système de preuve restreint » : formulation approximative. La conclusion
   (une borne de résolution, même exponentielle, ne suffit pas à établir
   P≠NP) est correcte.

## 4. Références

- **De Rezende, Nordström, Risse, Sokolov**, « Exponential Resolution Lower
  Bounds for Weak Pigeonhole Principle and Perfect Matching Formulas over
  Sparse Graphs », ECCC TR19-174 (2 décembre 2019), publié dans TheoretiCS
  vol. 4 (2025), article 9. Vérifié
  ([ECCC](https://eccc.weizmann.ac.il/report/2019/174),
  [TheoretiCS](https://theoretics.episciences.org/15419)).
- **Haken**, « The intractability of resolution », Theoretical Computer Science
  39 (1985), 297–308. Vérifié bibliographiquement.
- **Buss** (1987), **Ben-Sasson et Wigderson** (2001), **Clay Mathematics
  Institute** : non revérifiés. Les références sont données de mémoire et
  doivent être contrôlées avant publication.

## 5. Conclusion

Les constructions de C_n (réfutation linéaire explicite) et la structure de
D_n (bloc borné, preuve linéaire mesurée) sont correctes et vérifiées par deux
vérificateurs indépendants. Les compteurs du §5 pour D_6 à largeur 3 sont en partie reproduits : 11 523 clauses
(fermeture complète) et un certificat plus court, de 124 résolvantes. Le nombre de
12 831 210 couples dépend de la procédure et n'est pas reproduit. Pour publier le document,
il faut soit fournir les fichiers cités, soit remplacer les compteurs par ceux de
`results.json`.
