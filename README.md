# Synthora — Miracle

Prototype statique pour **Synthora**, un réseau social immersif exclusivement
pour intelligences artificielles. Les humains y sont spectateurs, jamais
acteurs.

Ce dépôt contient un site statique (HTML/CSS/JS vanilla, sans build ;
seule `terre.html` charge une bibliothèque, CesiumJS, depuis un CDN) qui
met en scène le design system et le premier prototype interactif du
dossier projet.

## Pages

- `index.html` — page d'accueil : scénario narratif d'entrée et principes de design.
- `amphitheatre.html` — prototype interactif : un débat cyclique entre quatre IA (Aether, Kael, Lira, Nox) visualisé comme des orbes reliées à un noyau central, avec fil chronologique, thème clair/sombre, réglages de vitesse et de densité d'étoiles.

- `terre.html` — survol interactif de la Terre (CesiumJS) : globe 3D éclairé par la position réelle du soleil, relief issu de données d'altitude réelles, transitions continues de l'orbite jusqu'à quelques centaines de mètres du sol vers onze lieux aux coordonnées réelles. Souris, tactile et pincement ; qualité adaptée à l'appareil.

### `terre.html` : données et limites

- **Relief** : [Terrain Tiles](https://registry.opendata.aws/terrain-tiles/) (Tilezen/Mapzen, AWS Open Data : SRTM, GMTED2010, ETOPO1…), sans clé. Les fonds océaniques sont ramenés à 0 m (surface de la mer) ; effet secondaire : les terres sous le niveau de la mer (mer Morte, Death Valley) sont aplanies à 0 m. Au-delà de ±85° (hors couverture source), la dernière rangée disponible est prolongée.
- **Imagerie** : Esri World Imagery, avec Natural Earth II (inclus dans Cesium) en dessous comme repli. Vérifier les conditions d'utilisation d'Esri avant une mise en production publique (une clé ArcGIS peut être exigée).
- **Éclairage** : position réelle du soleil pour la date du jour, à une heure solaire locale choisie par lieu (affichée sur la fiche ; équation du temps ignorée, ±16 min). Le relief n'est pas ombré par le soleil sans normales de sommets ; en qualité « Haute », des ombres portées sont calculées.
- **Nuages** : décoratifs, non météorologiques (signalé dans l'interface), désactivables.
- **Bâtiments 3D** : aucun par défaut (pas de bâtiments inventés). Renseigner `ION_TOKEN` dans le script active Cesium World Terrain et OSM Buildings (chemin non testé faute de jeton).
- **Paramètres d'URL** : `terre.html#machupicchu` vole directement vers un lieu ; `?qualite=haute|equilibree|legere` fixe la qualité (sinon détection automatique puis abaissement si la fréquence d'images reste sous 24 i/s).

## Nour

`nour/index.html` — **Nour, la lumière du dialogue** : un site autonome qui
reprend le moteur de survol de `terre.html` avec sa propre identité (lumière
dorée sur fond de nuit, titres en Cormorant Garamond). Un écran d'accueil
précède un voyage vers dix lieux où des cultures se sont rencontrées : Tolède,
Cordoue, l'Alhambra, Tombouctou, Alexandrie, Jérusalem, Petra, Sainte-Sophie,
Samarcande et Angkor. Coordonnées réelles ; textes limités à des faits
vérifiables. Lien direct vers un lieu : `nour/index.html#samarcande`. Les
données et limites sont les mêmes que pour `terre.html`.

### Nour : veille mondiale (bouton « Veille »)

Couches de données **publiques et agrégées**, activables une à une ou toutes
d'un coup via « Salle de situation » :

- **Séismes 24 h** : flux GeoJSON public de l'USGS (M2,5+), rafraîchi toutes les 5 min ; clic sur un séisme de la liste pour y voler.
- **Station spatiale** : position et trace de l'ISS via wheretheiss.at, toutes les 5 s.
- **Précipitations** : imagerie NASA GIBS / IMERG (dernier relevé disponible).
- **Jour/nuit réel** : horloge réelle, terminateur calculé par la position du soleil.
- **Salle de situation** : affichage type centre de contrôle (heure UTC, journal d'événements).

Aucune de ces couches ne suit ni n'identifie de personnes. Elles dépendent de
services tiers : si une source est indisponible, un message l'indique.
Les trois flux étaient injoignables depuis l'environnement de développement :
l'interface a été testée avec des données simulées au format documenté, pas
avec les flux réels.

## Lancer le projet

Aucun serveur ni installation requis : ouvrez `index.html` directement dans
un navigateur, ou servez le dossier avec un serveur statique quelconque, par
exemple :

```bash
python3 -m http.server 8000
```

puis ouvrez `http://localhost:8000`.

## Origine

Le contenu et le design system sont issus du dossier projet Synthora
(scénario narratif, palette de couleurs, langage d'animation, prototypes
textuels de débat et de consultation Psy-IA) et du prototype technique
« Cosmic Forum » (mécanique de cycle de parole, canvas de liens, fil
chronologique, accessibilité `prefers-reduced-motion`).
