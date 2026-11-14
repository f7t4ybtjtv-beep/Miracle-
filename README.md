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
reprend le moteur de survol de `terre.html` avec sa propre identité, « cinéma spatial » (noir bleuté `#04060B`,
texte blanc froid, un seul accent bleu glacier `#9FD3FF`, Inter fine et JetBrains Mono). Un écran d'accueil
précède un voyage vers treize lieux où des cultures se sont rencontrées : Tolède,
Cordoue, l'Alhambra, Al Quaraouiyine à Fès, Tombouctou, la chapelle Palatine de Palerme,
Alexandrie, Jérusalem, Petra, Sainte-Sophie, Samarcande, Nalanda et Angkor. Coordonnées réelles ; textes limités à des faits
vérifiables. L'ancienne adresse `nour/` redirige vers `fatiha/`. Lien direct vers un lieu : `fatiha/index.html#samarcande`,
vers sa vue de nuit ou sa plongée : `#samarcande/nuit`, `#samarcande/plongee` ; `#visite` lance la visite cinéma ;
`#vue=lat,lon,altitude,cap,inclinaison,heure` rouvre un point de vue exact. Le bouton « Partager » de la fiche copie le
lien du lieu (ou ouvre le partage du téléphone) ; « Partager cette vue » (menu) copie le point de vue exact.
« Trajet » (menu, Affichage) trace depuis l'espace un arc entre les lieux visités. La fiche d'un lieu donne aussi la
météo du moment (Open-Meteo). Les données et limites sont les mêmes que pour `terre.html`.

**Aucun lien vers un autre site** : les sources sont nommées en texte (crédits, titres de presse, source d'un événement naturel), les vidéos, radios et caméras jouent dans la page.

En haut à gauche, le nom et une ligne d'état ; en haut à droite, « Orbite » et « Menu » ; en bas, la bande des lieux.
Les panneaux (Menu, Veille, The Light · Stream) sont un tiroir à droite sur ordinateur et une feuille en bas sur
téléphone ; Échap et ✕ les ferment.

### Fatiha : voyage d'ouverture

À la place d'une barre de chargement, la page s'ouvre sur un vol en cockpit, de Neptune vers la Terre : Neptune,
Uranus, Saturne (Titan à côté), Jupiter (les quatre lunes galiléennes en points), Mars, la Lune, puis la Terre,
où le vrai globe prend le relais. Chaque disque est une **photo** de sonde ou de télescope (Voyager 2, Cassini,
Juno, Rosetta, Galileo, Apollo 17), créditée dans le coin et dans « Sources et crédits ». Tailles et vitesse ne
sont pas à l'échelle ; les distances affichées sont réelles (fiches planétaires de la NASA, arrondies) et l'écart
entre les rencontres suit ces distances, comprimé dans le temps. « Passer » (ou Échap) coupe le voyage tout de suite : le dessin est libéré et le globe prend le relais.
Avec « mouvement réduit », les photos défilent en fondu, sans trajectoire. Un lien direct (`#tolede`, `#vue=…`)
ou `?intro=0` (les tests) saute le voyage : la fiche-titre simple le remplace.

### Fatiha : qualité d'image

Le menu (« Qualité d'image ») propose **Ultra · HDR 5K** (rendu HDR, image calculée jusqu'à 5120 px puis réduite à l'écran, pour un ordinateur puissant), **Auto**, **Haute**, **Équilibrée** et **Légère** (choix mémorisé dans le navigateur ; `?qualite=haute|equilibree|legere` l'impose aussi). En Auto, un ordinateur part de l'appareil. Un téléphone (écran tactile étroit, ou iOS) part en « Légère » : le voyage est dessiné à 1,5× et le globe à 2× au plus, pour ne pas faire tomber l'onglet. Si l'image reste fluide, Auto peut remonter d'un cran à la fois ; ce plafond de pixels reste. Sur un ordinateur, Auto ne fait que descendre, après un temps de chauffe, si la fréquence reste basse. La version du site (`2026-11-14.2`) est affichée dans « Sources et crédits », en bas du menu. L'effet d'eau de Cesium est volontairement désactivé : il donnait des côtes en escaliers et des taches de reflet sur les terres sous le niveau de la mer.

Le mode automatique ne descend en « Légère » que si l'image reste sous 15 images par seconde (24 pour passer de « Haute » à « Équilibrée ») : ce dernier palier coûte de la netteté. Sur un téléphone parti en « Légère », il peut au contraire remonter si la fréquence reste au-dessus de 48 images par seconde. À l'arrivée sur un lieu, la caméra attend (« Mise au point », 7 s au plus) que les images du sol visibles soient chargées avant d'afficher la fiche.

### Fatiha : boussole, carnet de voyage, raccourcis

- **Boussole** : la ligne d'état affiche le cap de la caméra (« Cap 336° NO »).
- **Fiche** : distance géodésique (WGS84) depuis le lieu précédent, « à 229 km de Tolède ».
- **Menu** : « Lieu au hasard » (un lieu pas encore vu), « Plein écran » (seulement si le navigateur le permet : pas Safari sur iPhone), « Carnet de voyage » (lieux vus et kilomètres parcourus, gardés dans ce navigateur sous `nour.carnet`, bouton « Effacer »).
- **Clavier** (ordinateur) : ← → lieu précédent ou suivant, P plonger, N nuit, O orbite, H lieu au hasard, M menu. Inactif pendant la saisie, la visite cinéma ou quand un panneau est ouvert.
- **Enquête** : un encadré « Une personne a disparu : que faire » donne les numéros officiels (17, 112, 116 000) en texte simple. Le site ne fait ni reconnaissance de visages ni recherche de personnes.

### Fatiha : veille mondiale (bouton « Veille »)

Couches de données **publiques et agrégées**, activables une à une ou toutes
d'un coup via « Salle de situation » :

- **Nuages réels** (activé par défaut) : mosaïque quotidienne NASA GIBS / VIIRS. Une tuile test est sondée d'abord : NOAA-20, puis NOAA-21, puis SNPP, du jour le plus récent (J-1) au plus ancien (J-30) ; sans réponse, la couche est désactivée. Visible depuis l'orbite et fondue vers l'imagerie Esri entre 800 et 150 km d'altitude. Le noir (absence de donnée) est rendu transparent.
- **Lumières de nuit** (activé par défaut) : NASA Black Marble 2016, dessiné uniquement du côté nuit du globe et estompé sous 80 km d'altitude.
- **Séismes 24 h** : flux GeoJSON public de l'USGS (M2,5+), rafraîchi toutes les 5 min ; clic sur un séisme de la liste pour y voler.
- **Station spatiale** : position et trace de l'ISS via wheretheiss.at, toutes les 5 s.
- **Précipitations** : imagerie NASA GIBS / IMERG (dernier relevé disponible).
- **Jour/nuit réel** : horloge réelle, terminateur calculé par la position du soleil.
- **Satellites militaires** : catalogue public CelesTrak (groupe `military`), positions calculées avec satellite.js et gardées 2 h en cache. CelesTrak coupe les connexions venant de centres de données : la couche le dit et se coupe.
- **Événements naturels** : NASA EONET (feux, tempêtes, volcans… des 30 derniers jours), un point par événement et une liste ; toucher l'un ou l'autre y fait voler la caméra.
- **Feux actifs** : points chauds VIIRS (NOAA-20, 375 m) de la veille, rendus en PNG par le service WMS de NASA GIBS (ces couches n'existent qu'en tuiles vectorielles dans le WMTS).
- **Aurores** : prévision à 30 min du modèle OVATION (NOAA SWPC), dessinée en voile vert.
- **Salle de situation** : affichage type centre de contrôle (heure UTC, journal d'événements).

L'éclairage du globe suit la vraie position du soleil à toute altitude : la face nocturne est assombrie (30 % de sa luminosité de jour) et le terminateur est visible. Les arrivées aux lieux se font en plein jour (soleil à ~32°). Aucune de ces couches ne suit ni n'identifie de personnes. Elles dépendent de
services tiers : si une source est indisponible, un message l'indique.
Les flux sont injoignables depuis le navigateur de test : l'interface a été testée
avec des réponses simulées au format vérifié le 9 nov. 2026 (EONET, OVATION, GIBS WMS,
Open-Meteo répondent bien avec CORS), pas avec les flux réels dans le navigateur. Une
couche NASA se désactive d'elle-même après une douzaine d'erreurs de tuiles.

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

### Fatiha : plongée depuis l'espace

Chaque fiche propose aussi **« Plonger depuis l'espace »** : un vol vers une vue
d'ensemble où la Terre remplit l'écran, enchaînée sans pause avec une chute de 13 s caméra à la
verticale jusqu'à environ 300 m au-dessus du lieu, avec un virage de 40°. Elle
reprend l'idée d'une plongée filmée de l'espace jusqu'à la rue :

- la descente suit une loi tabulée sur la hauteur au-dessus du sol, qui ralentit fortement à la fin : les niveaux de tuiles changent lentement près du sol ;
- pendant la montée, les tuiles Esri dont la descente aura besoin (au plus 120) sont préchargées ; à la fin, un court palier (2,5 s au plus) attend les dernières tuiles avant la fiche ;
- un **flou de vitesse** léger, calculé d'après la vitesse de descente réelle, entre quelques milliers et ~20 km au-dessus du sol, nul ensuite ;
- un **voile** bref vers 3 km au-dessus du sol (il suit le bouton « Nuages »). C'est un effet décoratif, pas la météo réelle ;
- la qualité ne baisse pas d'elle-même pendant la plongée ;
- « Retour de jour » ramène à l'arrivée habituelle. Avec « réduire les animations » activé, le vol est raccourci et le flou supprimé.

Limite : la netteté de la dernière image est celle de l'imagerie satellite (Esri)
à cet endroit. Elle ne montre ni les passants ni les détails d'une vidéo tournée
au drone. Testé avec une imagerie unie simulée (trajectoire, flou, brume et
retour vérifiés) ; l'aspect avec la vraie imagerie n'est pas vérifié.

### Fatiha : Enquête (menu) — outils de sources ouvertes

Un panneau d'outils pour enquêter sur des **lieux et des données publiques** (jamais sur des personnes), sans lien vers
un autre site :

- **Point** : toucher le globe donne les coordonnées en décimal, DMS, UTM et MGRS, l'altitude du relief et l'heure
  solaire ; copier, épingler. « Aller à » accepte des coordonnées en décimal, DMS (N/S/E/O) ou MGRS ; pas de
  recherche par nom, faute de pouvoir la vérifier.
- **Mesure** : distance géodésique avec caps, surface d'un polygone, profil du relief entre deux points avec ligne de
  vue (courbure de la Terre et réfraction, coefficient 0,13).
- **Soleil** : azimut et hauteur du soleil, direction et longueur des ombres, lever, coucher, heure dorée ; les heures
  où une ombre prend une direction donnée (dater une photo) ; régler le globe sur cette heure.
- **Images** : deux dates côte à côte avec un rideau (NASA GIBS : VIIRS et MODIS ~250 m, Landsat et Sentinel-2 HLS
  30 m, lumières de la nuit du jour, inondations) ; la dernière date disponible est cherchée automatiquement.
- **Journal** : épingles gardées dans le navigateur, export GeoJSON et KML, import GeoJSON.

Vérification : les calculs (UTM, MGRS, géodésiques, surfaces, soleil, ligne de vue) sont comparés à des bibliothèques
indépendantes sur des centaines de cas — UTM à 10⁻⁵ mm de pyproj, MGRS identique au paquet `mgrs`, géodésiques à
0,08 mm de geographiclib, surfaces à 3·10⁻⁹ près, soleil à 0,05° de l'algorithme SPA du NREL, lever et coucher à 5 s.
Les huit couches d'images ont été vérifiées sur le vrai service de la NASA. Le relief réel (AWS) n'est pas joignable
depuis l'environnement de test : profil et ligne de vue y sont testés sur un relief simulé dont la réponse est connue.
Bâtiments et arbres ne sont pas dans le modèle de relief.

### Fatiha : Spectacle (menu)

- **Visite cinéma** : les treize lieux enchaînés, bandes noires au format 2,39:1 et titres comme un générique. Elle part du lieu affiché et trace son propre trajet. Toucher l'image la met en pause et rend le globe (on peut regarder autour), « Reprendre » continue ; Échap ou « Quitter » l'arrête, comme tout autre vol (un lieu, la nuit, la plongée, Orbite, un lien). Un onglet caché la met en pause.
- **Curseur du temps** : l'heure solaire locale sur 24 h, au lieu affiché ou au centre de l'écran.
- **Partager cette vue** : un lien `#vue=…` vers le point de vue exact, heure comprise.
- **La Terre entière, aujourd'hui** : les photos du jour de NASA EPIC (satellite DSCOVR, à 1,5 million de km), puis un vol vers le côté photographié.

### Fatiha : The Light · Stream (menu, « En direct »)

Un panneau pour écouter, regarder et s'informer sur le pays d'un lieu, d'un pays
touché sur le globe ou choisi dans la liste. Rien n'est chargé avant l'ouverture
d'une rubrique.

- **Radios** : annuaire communautaire radio-browser.info, radios les plus écoutées du pays, flux https seulement. La radio continue pendant le survol, avec un bouton d'arrêt dans la barre d'état.
- **Télé** : playlists communautaires iptv-org (chaînes gratuites en accès libre), lues par hls.js (chargé à la demande) ou nativement sous Safari. Beaucoup de flux sont géobloqués, hors ligne ou refusés par le navigateur : le panneau le dit. Les chaînes d'un pays peuvent dépendre de l'État.
- **Musique** : radios radio-browser classées par genre.
- **Caméras** : 17 caméras de lieux publics (Paris, Jérusalem, Tokyo, Vatican, Venise, New York, Londres, Ajaccio…), directs YouTube publiés par leurs propriétaires (offices de tourisme, chaînes, réseaux de webcams), contrôlés le 9 nov. 2026, un point bleu chacune sur le globe. Sous cette liste, et seulement tant que l'onglet est ouvert sur un point connu, les widgets officiels de Windy.com : les webcams publiques les plus proches (`webcams.windy.com/webcams/public/embed/nearby`) et la carte (`embed.windy.com/embed.html`). Un pays choisi dans la liste est centré sur sa capitale (l'Allemagne sur Berlin) ; un lieu du parcours ou un point touché recentre les widgets. Aucune iframe vers `www.windy.com`, aucun appel à `api.windy.com`. Le site n'ouvre, n'explore ni ne répertorie aucune caméra privée ou mal protégée. Un direct peut s'arrêter ou changer d'adresse.
- **Bande-son** (menu, Affichage) : une musique calme générée dans le navigateur (WebAudio), qui suit l'altitude et la plongée.
- **Conflits** : titres de presse repérés par mots-clés dans GDELT (environ 15 minutes de latence, dernières 24 h, filtre FR/EN), sans images ni positions de troupes, avec le nom de sources de référence (ONU Info, CICR, ReliefWeb, UCDP, ACLED). Ce sont des titres automatiques, non vérifiés ; en temps de guerre les faits sont contestés.
- Jérusalem n'est rattachée à aucun pays (son statut est disputé) : le panneau demande d'en choisir un.

Vie privée : ouvrir une rubrique contacte radio-browser.info, GitHub (iptv-org),
GDELT, jsDelivr, Windy.com (onglet Caméras, seulement sur un point connu) et les
serveurs des radios et des chaînes, qui voient l'adresse IP du visiteur.

Limites : aucun de ces services n'est joignable depuis l'environnement de
développement. Le code a été testé avec des réponses simulées au format
documenté, jamais avec les vrais services ; leurs en-têtes CORS (surtout ceux de
GDELT) et leurs formats actuels ne sont pas vérifiés. Si un service refuse,
l'interface l'indique.

### Fatiha : image jusqu'à 5K

« Enregistrer une image 5K » (menu, Qualité d'image) rend la vue courante dans
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

## Outil de recherche SAT (`satlab/`)

Indépendamment du site, `satlab/` est un outil Python (bibliothèque standard
uniquement) pour l'étude empirique de SAT : générateurs d'instances,
solveur CDCL instrumenté émettant des preuves DRUP, vérificateur de
certificats autonome, contre-tests et campagnes reproductibles. Voir
[`satlab/README.md`](satlab/README.md) et les résultats dans
[`results/standard/REPORT.md`](results/standard/REPORT.md).

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
