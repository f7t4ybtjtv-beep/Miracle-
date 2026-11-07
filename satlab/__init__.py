"""satlab — outil de recherche SAT reproductible (stdlib uniquement).

Modules :
- dimacs      : lecture/écriture CNF DIMACS, hachage canonique d'instance
- generators  : familles d'instances (k-SAT aléatoire, planted, pigeonnier,
                Tseitin, coloration) à graine déterministe
- cdcl        : solveur exact CDCL instrumenté, émet des preuves DRUP
- reference   : solveurs de référence indépendants (force brute, DPLL)
                pour les contre-tests
- checker     : vérificateur de certificats AUTONOME (modèles et preuves
                DRUP) ; n'importe aucun autre module de satlab
- bench       : campagnes d'expériences, ajustements de croissance, rapport
"""

__version__ = "0.1.0"
