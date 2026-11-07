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

## Fatiha

`fatiha/index.html` — **Fatiha, maman d’Amine** (anciennement « Nour, la lumière du dialogue ») : un site autonome qui
reprend le moteur de survol de `terre.html` avec sa propre identité (lumière
dorée sur fond de nuit, titres en Cormorant Garamond). Un écran d'accueil
précède un voyage vers dix lieux où des cultures se sont rencontrées : Tolède,
Cordoue, l'Alhambra, Tombouctou, Alexandrie, Jérusalem, Petra, Sainte-Sophie,
Samarcande et Angkor. Coordonnées réelles ; textes limités à des faits
vérifiables. L'ancienne adresse `nour/` redirige vers `fatiha/`. Lien direct vers un lieu : `fatiha/index.html#samarcande`. Les
données et limites sont les mêmes que pour `terre.html`.

### Fatiha : qualité d'image

Le panneau « Sources et qualité » propose **Auto**, **Haute**, **Équilibrée** et **Légère** (choix mémorisé dans le navigateur ; `?qualite=haute|equilibree|legere` l'impose aussi). En Auto, la qualité part de l'appareil (les téléphones démarrent en « Équilibrée », rendu à 2× la résolution CSS) et ne baisse que si la fréquence d'images reste sous 24 i/s de façon prolongée, après un temps de chauffe. La version du site est affichée dans ce même panneau. L'effet d'eau de Cesium est volontairement désactivé : il donnait des côtes en escaliers et des taches de reflet sur les terres sous le niveau de la mer.

### Fatiha : veille mondiale (bouton « Veille »)

Couches de données **publiques et agrégées**, activables une à une ou toutes
d'un coup via « Salle de situation » :

- **Nuages réels** (activé par défaut) : mosaïque quotidienne NASA GIBS / VIIRS, datée de deux jours (le dernier jour toujours complet), visible depuis l'orbite et fondue vers l'imagerie Esri entre 800 et 150 km d'altitude. Le noir (absence de donnée) est rendu transparent.
- **Lumières de nuit** (activé par défaut) : NASA Black Marble 2016, dessiné uniquement du côté nuit du globe et estompé sous 80 km d'altitude.
- **Séismes 24 h** : flux GeoJSON public de l'USGS (M2,5+), rafraîchi toutes les 5 min ; clic sur un séisme de la liste pour y voler.
- **Station spatiale** : position et trace de l'ISS via wheretheiss.at, toutes les 5 s.
- **Précipitations** : imagerie NASA GIBS / IMERG (dernier relevé disponible).
- **Jour/nuit réel** : horloge réelle, terminateur calculé par la position du soleil.
- **Salle de situation** : affichage type centre de contrôle (heure UTC, journal d'événements).

L'éclairage du globe suit la vraie position du soleil à toute altitude : la face nocturne est assombrie (30 % de sa luminosité de jour) et le terminateur est visible. Les arrivées aux lieux se font en plein jour (soleil à ~32°). Aucune de ces couches ne suit ni n'identifie de personnes. Elles dépendent de
services tiers : si une source est indisponible, un message l'indique.
Les flux (USGS, ISS, NASA GIBS) étaient injoignables depuis l'environnement de
développement : l'interface a été testée avec des données simulées au format
documenté, pas avec les flux réels. Une couche NASA se désactive d'elle-même
après une douzaine d'erreurs de tuiles.

### Fatiha : vue de nuit depuis l'orbite

Chaque fiche de lieu propose **« Voir la nuit depuis l'orbite »** : un vol vers
une vue oblique à environ 600 km d'altitude (la Station spatiale
internationale évolue vers 400 km), inclinée de 33°, avec l'horloge réglée sur
23 h, heure solaire locale, et un cap choisi pour chaque lieu. **« Revenir au
lieu, de jour »** ramène à l'arrivée habituelle.

- Les lumières sont celles du composite NASA Black Marble (2016) : elles montrent l'éclairage d'une année passée, pas celui d'aujourd'hui. La couche est activée à l'ouverture de cette vue.
- Cesium garde 30 % des couleurs de jour sur la face nocturne, ce qui ressemble au crépuscule plus qu'à la nuit : à moins de 1 500 km d'altitude, l'imagerie de jour est assombrie de 45 % en douceur quand le soleil est sous l'horizon au point regardé (progressif de −3° à −20°).
- Les étoiles sont celles du ciel Tycho-2 fourni avec Cesium (positions réelles), avec des niveaux relevés pour qu'elles ressortent. Si ce ciel ne se charge pas, celui de Cesium reste en place.
- Le limbe est une **approximation** de l'aspect des photos de l'ISS : un limbe bleu fin avec son halo et une fine bande verte (là où l'on voit la luminescence nocturne de l'atmosphère), selon l'altitude rasée par chaque rayon, côté nuit seulement. Ce n'est pas un modèle physique. Le relief au limbe le masque.
- Les zones sombres prennent une teinte bleu nuit froide, sans toucher aux lumières chaudes. Les lumières les plus vives ont un léger halo (flou à demi-résolution, seulement la nuit, absent en qualité Légère) ; `?bloom=0` à `?bloom=3` règle son intensité (1 par défaut, 0 le supprime).
- De loin, au-dessus d'un globe éclairé (vue d'ensemble, ouverture), les étoiles s'estompent : une photo de la Terre éclairée est exposée pour elle et montre un ciel noir. C'est un choix d'exposition, pas une règle physique. Elles reviennent en volant bas ou de nuit.
- La brume de profondeur de Cesium est désactivée : elle assombrissait les tuiles lointaines une à une et laissait des zigzags dans les vues obliques de nuit.

Limites : cette vue n'a été vue qu'avec de fausses tuiles de lumières (de petits
points regroupés en villes) et une imagerie unie (NASA et Esri sont injoignables
depuis l'environnement de développement). Le halo et la teinte ont été réglés
sur ces simulations : leur intensité avec le vrai Black Marble n'est pas
vérifiée, d'où le réglage `?bloom=`.

### Fatiha : Direct (bouton « Direct »)

Un panneau pour écouter, regarder et s'informer sur le pays d'un lieu, d'un pays
touché sur le globe ou choisi dans la liste. Rien n'est chargé avant l'ouverture
d'une rubrique.

- **Radios** : annuaire communautaire radio-browser.info, radios les plus écoutées du pays, flux https seulement. La radio continue pendant le survol, avec un bouton d'arrêt dans la barre d'état.
- **Télé** : playlists communautaires iptv-org (chaînes gratuites en accès libre), lues par hls.js (chargé à la demande) ou nativement sous Safari. Beaucoup de flux sont géobloqués, hors ligne ou refusés par le navigateur : le panneau le dit. Les chaînes d'un pays peuvent dépendre de l'État.
- **Caméras** : uniquement des liens vers des annuaires de webcams publiques (carte Windy, directs YouTube filtrés). Le site n'ouvre, n'explore ni ne répertorie aucune caméra privée ou mal protégée.
- **Conflits** : titres de presse repérés par mots-clés dans GDELT (environ 15 minutes de latence, dernières 24 h, filtre FR/EN), sans images ni positions de troupes, avec des liens vers des sources de référence (ONU Info, CICR, ReliefWeb, UCDP, ACLED). Ce sont des titres automatiques, non vérifiés ; en temps de guerre les faits sont contestés.
- Jérusalem n'est rattachée à aucun pays (son statut est disputé) : le panneau demande d'en choisir un.

Vie privée : ouvrir une rubrique contacte radio-browser.info, GitHub (iptv-org),
GDELT, jsDelivr et les serveurs des radios et des chaînes, qui voient l'adresse IP
du visiteur.

Limites : aucun de ces services n'est joignable depuis l'environnement de
développement. Le code a été testé avec des réponses simulées au format
documenté, jamais avec les vrais services ; leurs en-têtes CORS (surtout ceux de
GDELT) et leurs formats actuels ne sont pas vérifiés. Si un service refuse,
l'interface l'indique.

### Fatiha : image jusqu'à 5K

« Enregistrer en 5K » (panneau « Sources et qualité ») rend la vue courante dans
un tampon de jusqu'à 5120 px sur le grand côté (moins si l'appareil ne le permet
pas), ajoute les crédits en bas et télécharge un PNG. L'image est calculée sur
l'appareil du visiteur, avec les vraies données. Elle demande beaucoup de
mémoire graphique. Le bouton est désactivé avec Google 3D : les conditions de
Google n'autorisent pas l'export de ses images.

### Fatiha : Google Earth 3D (optionnel, clé Google requise)

Un bouton **Google 3D** apparaît dans Fatiha uniquement si une clé Google Maps
Platform est présente. Il remplace la carte (satellite Esri, relief ombré)
par les *Photorealistic 3D Tiles* de Google (Map Tiles API), avec le logo et
les mentions de sources exigés par Google. Sans clé, rien ne change et aucune
requête n'est envoyée à Google.

1. Google Cloud : créer un projet, activer la facturation, activer **Map Tiles API**.
2. Créer une clé API, la **restreindre** : sites web autorisés `https://f7t4ybtjtv-beep.github.io/*`, et API autorisée **Map Tiles API** seulement. Ajouter une alerte de budget et un plafond de quota.
3. Essai privé : ouvrir `fatiha/index.html?gkey=VOTRE_CLE`. La clé est mémorisée dans ce navigateur uniquement et retirée de l'adresse ; `?gkey=off` l'oublie.
4. Pour tous les visiteurs : renseigner la constante `GOOGLE_MAPS_KEY` dans `fatiha/index.html`. Une clé côté navigateur est visible de tous : seules ses restrictions la protègent, et l'usage est facturé au projet Google Cloud de la clé.

Limites : testé uniquement avec une fausse tuile et de fausses réponses de Google
(le service est injoignable depuis l'environnement de développement), jamais avec
les vraies données. En mode Google 3D, la lumière du soleil réelle, les
précipitations et le relief ombré ne s'appliquent plus (la lumière est celle des
tuiles), et la vue de nuit n'est pas proposée.

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
