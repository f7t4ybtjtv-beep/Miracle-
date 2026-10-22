# Pièces justificatives

Scripts et sorties texte des enquêtes menées pour `../NOTE.md` : cinq
enquêtes indépendantes, chacune suivie d'une contre-vérification adverse
écrite avec un code distinct. Ils sont conservés **tels qu'exécutés** :

| Dossier | Sujet | Contre-vérification |
|---|---|---|
| `pm-balanced/` | proposition (cas équilibré, déséquilibré) | `refute-proposition/` |
| `hall_witness/` | Q1 : preuve explicite, transfert, CDCL | `refute-q1_hall_refutation/` |
| `mus_hall/` | Q2 : MUS, critère, déficience | `refute-q2_minimal_core/` |
| `q3-weak-ratio/` | Q3 : écarts modèles / couplages | `refute-q3_gap_families/` |
| `schur-audit/` | audit du JSON Schur(N,3) | `refute-schur_json/` |
| `review/` | comptes exacts des littéraux hors cœur (`exact.out`), journal drat-trim des preuves de `satlab.hallproof` | — |

Les sorties `pm-balanced/*.out` et `refute-proposition/*.out` ont été
régénérées après la première revue, avec les mêmes scripts et les mêmes
graines, parce qu'elles n'avaient pas été conservées la première fois.

Limites de ces archives :

- Elles contiennent des chemins absolus vers l'espace de travail de la session
  d'origine : binaire drat-trim compilé depuis
  https://github.com/marijnheule/drat-trim, et dossiers de sortie. Il faut les
  adapter pour relancer.
- Les gros fichiers produits (`.cnf`, `.drup`) ne sont pas versionnés.
- Elles s'exécutent avec `PYTHONPATH` pointant sur la racine du dépôt.
- Les sorties `*.txt` / `*.out` sont celles réellement obtenues.

Le script `../reproduce.py` recalcule de façon autonome les résultats
principaux avec `satlab` seul, en quelques secondes. C'est lui qui fait
référence.
