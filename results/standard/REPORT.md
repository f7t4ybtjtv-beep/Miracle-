# Rapport de campagne satlab — `standard`

- Commit satlab : `06c33ad329f0c070ac9c552d9555a7227db8f19d`
- Python 3.13.16 — Linux-6.18.44-fc-v139-x86_64-with-glibc2.39
- Budget : 300000 conflits par instance (au-delà : UNKNOWN, censuré)
- Durée totale : 349.5 s

Reproduire : `python3 -m satlab bench --campaign standard`. Les compteurs sont déterministes ; seuls les temps varient.

## Contrôles de validité

| Expérience | Runs | UNKNOWN | Certificats vérifiés | Rejetés | Statut attendu vérifié | Violations | Contre-tests | Désaccords |
|---|---|---|---|---|---|---|---|---|
| random3sat_threshold | 120 | 0 | 120 | 0 | 0 | 0 | 60 | 0 |
| random3sat_phase_n50 | 220 | 0 | 220 | 0 | 0 | 0 | 220 | 0 |
| planted3sat_threshold | 30 | 0 | 30 | 0 | 30 | 0 | 6 | 0 |
| pigeonhole | 18 | 0 | 18 | 0 | 18 | 0 | 15 | 0 |
| tseitin_3regular | 55 | 0 | 55 | 0 | 55 | 0 | 30 | 0 |
| coloring3_threshold | 30 | 0 | 30 | 0 | 0 | 0 | 6 | 0 |

## random3sat_threshold (`random_ksat`, axe `n`)

| n | vars | runs | SAT | UNSAT | conflits méd. | conflits max | décisions méd. | temps méd. (s) | taille cert. méd. | vérif. méd. (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 20.0 | 12 | 11 | 1 | 3.5 | 23 | 9.5 | 0.00017 | 20.0 | 3e-05 |
| 30 | 30.0 | 12 | 8 | 4 | 11.0 | 29 | 17.5 | 0.00045 | 30.0 | 4e-05 |
| 40 | 40.0 | 12 | 6 | 6 | 28.0 | 115 | 36.5 | 0.00139 | 40.0 | 0.00067 |
| 50 | 50.0 | 12 | 8 | 4 | 31.0 | 70 | 39.5 | 0.00161 | 50.0 | 7e-05 |
| 60 | 60.0 | 12 | 8 | 4 | 67.0 | 129 | 84.5 | 0.00412 | 60.0 | 0.00012 |
| 70 | 70.0 | 12 | 6 | 6 | 103.0 | 249 | 121.5 | 0.00523 | 81.5 | 0.00221 |
| 80 | 80.0 | 12 | 6 | 6 | 154.0 | 284 | 184.5 | 0.01082 | 121.5 | 0.00472 |
| 100 | 100.0 | 12 | 7 | 5 | 279.0 | 592 | 344.5 | 0.02499 | 100.0 | 0.00016 |
| 120 | 120.0 | 12 | 4 | 8 | 1101.5 | 1610 | 1338.0 | 0.12643 | 1079.5 | 0.12355 |
| 150 | 150.0 | 12 | 7 | 5 | 2122.5 | 4654 | 2584.5 | 0.28269 | 150.0 | 0.00022 |

Ajustement des conflits médians sur 10 points : exponentiel base 1.0483 par unité de `n` (R² = 0.9644) ; polynomial degré 3.106 (R² = 0.9730). Verdict (écart de R² minimal 0.02) : **inconclusive**.

## random3sat_phase_n50 (`random_ksat`, axe `ratio`)

| ratio | vars | runs | SAT | UNSAT | conflits méd. | conflits max | décisions méd. | temps méd. (s) | taille cert. méd. | vérif. méd. (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| 3.0 | 50.0 | 20 | 20 | 0 | 1.0 | 15 | 19.0 | 0.00018 | 50.0 | 5e-05 |
| 3.4 | 50.0 | 20 | 20 | 0 | 3.0 | 18 | 21.0 | 0.0003 | 50.0 | 6e-05 |
| 3.8 | 50.0 | 20 | 20 | 0 | 10.0 | 92 | 23.0 | 0.00064 | 50.0 | 6e-05 |
| 4.0 | 50.0 | 20 | 17 | 3 | 16.0 | 109 | 26.0 | 0.00091 | 50.0 | 7e-05 |
| 4.2 | 50.0 | 20 | 14 | 6 | 38.0 | 118 | 52.5 | 0.00219 | 50.0 | 7e-05 |
| 4.3 | 50.0 | 20 | 12 | 8 | 38.0 | 113 | 46.0 | 0.00241 | 50.0 | 9e-05 |
| 4.4 | 50.0 | 20 | 11 | 9 | 41.0 | 107 | 47.5 | 0.00198 | 50.0 | 9e-05 |
| 4.6 | 50.0 | 20 | 6 | 14 | 46.5 | 93 | 52.0 | 0.00194 | 50.0 | 0.002 |
| 5.0 | 50.0 | 20 | 1 | 19 | 52.5 | 106 | 59.5 | 0.00289 | 52.5 | 0.00299 |
| 5.6 | 50.0 | 20 | 0 | 20 | 37.5 | 57 | 42.0 | 0.00188 | 37.5 | 0.002 |
| 6.4 | 50.0 | 20 | 0 | 20 | 30.5 | 47 | 35.0 | 0.00131 | 30.5 | 0.00147 |

## planted3sat_threshold (`planted_ksat`, axe `n`)

| n | vars | runs | SAT | UNSAT | conflits méd. | conflits max | décisions méd. | temps méd. (s) | taille cert. méd. | vérif. méd. (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| 50 | 50.0 | 6 | 6 | 0 | 8.0 | 51 | 26.5 | 0.0004 | 50.0 | 6e-05 |
| 100 | 100.0 | 6 | 6 | 0 | 59.0 | 108 | 107.5 | 0.0039 | 100.0 | 0.00011 |
| 150 | 150.0 | 6 | 6 | 0 | 198.5 | 520 | 281.0 | 0.02784 | 150.0 | 0.0002 |
| 200 | 200.0 | 6 | 6 | 0 | 483.0 | 14137 | 668.5 | 0.06317 | 200.0 | 0.00025 |
| 300 | 300.0 | 6 | 6 | 0 | 1175.5 | 4039 | 1672.5 | 0.22097 | 300.0 | 0.0004 |

Ajustement des conflits médians sur 5 points : exponentiel base 1.0194 par unité de `n` (R² = 0.9026) ; polynomial degré 2.833 (R² = 0.9974). Verdict (écart de R² minimal 0.02) : **polynomial**.

## pigeonhole (`pigeonhole`, axe `holes`)

| holes | vars | runs | SAT | UNSAT | conflits méd. | conflits max | décisions méd. | temps méd. (s) | taille cert. méd. | vérif. méd. (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 12 | 3 | 0 | 3 | 7 | 7 | 6 | 0.00015 | 7 | 0.00015 |
| 4 | 20 | 3 | 0 | 3 | 28 | 30 | 32 | 0.00083 | 28 | 0.00073 |
| 5 | 30 | 3 | 0 | 3 | 148 | 157 | 176 | 0.00669 | 148 | 0.00739 |
| 6 | 42 | 3 | 0 | 3 | 823 | 852 | 1012 | 0.08923 | 823 | 0.11927 |
| 7 | 56 | 3 | 0 | 3 | 6155 | 7629 | 7507 | 1.63397 | 10796 | 2.35255 |
| 8 | 72 | 3 | 0 | 3 | 37564 | 50520 | 45589 | 17.92162 | 69284 | 29.99053 |

Ajustement des conflits médians sur 6 points : exponentiel base 5.6866 par unité de `holes` (R² = 0.9968) ; polynomial degré 8.742 (R² = 0.9616). Verdict (écart de R² minimal 0.02) : **exponential**.

## tseitin_3regular (`tseitin`, axe `n`)

| n | vars | runs | SAT | UNSAT | conflits méd. | conflits max | décisions méd. | temps méd. (s) | taille cert. méd. | vérif. méd. (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| 10 | 15 | 5 | 0 | 5 | 41 | 52 | 44 | 0.00116 | 41 | 0.00096 |
| 14 | 21 | 5 | 0 | 5 | 97 | 111 | 107 | 0.00229 | 97 | 0.00233 |
| 18 | 27 | 5 | 0 | 5 | 306 | 340 | 346 | 0.01396 | 306 | 0.0141 |
| 22 | 33 | 5 | 0 | 5 | 562 | 864 | 846 | 0.02453 | 562 | 0.03171 |
| 26 | 39 | 5 | 0 | 5 | 469 | 614 | 692 | 0.0235 | 469 | 0.02623 |
| 30 | 45 | 5 | 0 | 5 | 754 | 939 | 973 | 0.04829 | 754 | 0.05021 |
| 34 | 51 | 5 | 0 | 5 | 1809 | 2873 | 2541 | 0.11583 | 1809 | 0.13901 |
| 40 | 60 | 5 | 0 | 5 | 2224 | 6607 | 3026 | 0.18211 | 3225 | 0.24706 |
| 46 | 69 | 5 | 0 | 5 | 11475 | 23510 | 16572 | 1.38313 | 20958 | 1.92118 |
| 50 | 75 | 5 | 0 | 5 | 6379 | 16818 | 9277 | 0.60294 | 11019 | 0.87408 |
| 56 | 84 | 5 | 0 | 5 | 32997 | 63472 | 44664 | 4.29349 | 60921 | 8.09142 |

Ajustement des conflits médians sur 11 points : exponentiel base 1.1386 par unité de `n` (R² = 0.9574) ; polynomial degré 3.537 (R² = 0.9346). Verdict (écart de R² minimal 0.02) : **exponential**.

## coloring3_threshold (`coloring`, axe `n`)

| n | vars | runs | SAT | UNSAT | conflits méd. | conflits max | décisions méd. | temps méd. (s) | taille cert. méd. | vérif. méd. (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 60.0 | 6 | 2 | 4 | 8.0 | 14 | 13.0 | 0.00036 | 11.5 | 0.00051 |
| 40 | 120.0 | 6 | 2 | 4 | 17.0 | 24 | 26.0 | 0.00105 | 22.0 | 0.00109 |
| 60 | 180.0 | 6 | 2 | 4 | 15.5 | 131 | 29.0 | 0.00125 | 77.0 | 0.00186 |
| 80 | 240.0 | 6 | 1 | 5 | 79.5 | 102 | 104.0 | 0.01013 | 88.5 | 0.00937 |
| 100 | 300.0 | 6 | 3 | 3 | 39.5 | 57 | 79.0 | 0.00662 | 178.5 | 0.00201 |

Ajustement des conflits médians sur 5 points : exponentiel base 1.0240 par unité de `n` (R² = 0.7026) ; polynomial degré 1.188 (R² = 0.7145). Verdict (écart de R² minimal 0.02) : **inconclusive**.

## Portée

Ces mesures décrivent un solveur CDCL précis sur des tailles finies. Une croissance exponentielle observée n'est pas une borne inférieure, et une croissance polynomiale observée n'est pas un algorithme polynomial : aucun de ces résultats ne tranche P vs NP. Leur valeur est de vérifier, avec certificats contrôlés, des comportements attendus par la théorie de la complexité des preuves et de fournir des points de comparaison reproductibles.

Repères théoriques (taille des réfutations en résolution, que le CDCL sans prétraitement ne peut battre) : pigeonnier 2^Ω(h) (Haken 1985) ; Tseitin sur expanseurs 2^Ω(n) (Urquhart 1987, Ben-Sasson & Wigderson 2001) ; k-CNF aléatoire UNSAT à densité constante 2^Ω(n) avec forte probabilité (Chvátal & Szemerédi 1988). Un verdict « polynomial » ou « inconclusive » sur ces familles traduit donc des tailles trop petites pour l'asymptotique, pas une contradiction.
