# Passation : site « Fatiha, maman d'Amine »

Ce document est fait pour qu'une autre IA (ou un développeur) reprenne le travail. Il dit ce qui marche et ce qui a été
vérifié, et surtout ce qui n'est **pas** fini.

## 1. Le projet en bref
- **Site statique, sans serveur, sans compilation.** Tout le site Fatiha tient dans **un seul fichier** :
  `fatiha/index.html` (HTML, puis `<style>`, puis `<script>`).
  - Moteur 3D : **CesiumJS 1.145.0**, chargé depuis jsDelivr.
  - Bibliothèques chargées seulement quand on en a besoin : hls.js 1.5.13, satellite.js 6.0.2, world-atlas 2.0.2.
- **Ce que fait le site** : survol de la Terre en 3D vers dix lieux de rencontre des cultures, avec :
  - une vue de nuit depuis l'orbite ;
  - une plongée depuis l'espace ;
  - une « Veille » de données publiques ;
  - un mur de télés et de radios en direct, « The Light · Stream » ;
  - une qualité « Ultra · HDR 5K » ;
  - une image 5K à télécharger ;
  - Google 3D, facultatif (avec une clé Google).
- **Dépôt et adresses** :
  - Dépôt : https://github.com/f7t4ybtjtv-beep/Miracle-
  - Site en ligne (GitHub Pages, publié à chaque push sur `main`) : https://f7t4ybtjtv-beep.github.io/Miracle-/fatiha/
  - L'ancienne adresse `nour/index.html` redirige vers `fatiha/`.
- **Lire avant de coder** : `CLAUDE.md` à la racine. Il liste les pièges de Cesium 1.145 déjà rencontrés : alpha
  numérique seulement, mot réservé GLSL `cast`, plan lointain infini, plantage iPhone sans OIT, etc.
- **Lancer le site en local** : `python3 -m http.server 8000`, puis ouvrir http://localhost:8000/fatiha/

## 2. Branches
| Branche | Contenu | État |
|---|---|---|
| `main` | Version publiée en ligne, avant la refonte | en ligne |
| `claude/fatiha-cinema` (PR #30, brouillon) | **Version complète et testée** : refonte « cinéma spatial », The Light · Stream, satellites militaires, Ultra · HDR 5K et corrections, plus ce dossier `handoff/` | **à jour, fonctionne** |
| `claude/wip-plongee` | Plongée nette et fluide | **NON TERMINÉ, NON TESTÉ** |
| `claude/wip-donnees` | Événements naturels, aurores, météo, feux | **NON TERMINÉ, NON TESTÉ** |
| `claude/wip-cameras-musique` | Caméras de ville, musique, bande-son | **NON TERMINÉ, NON TESTÉ** |
| `claude/wip-spectacle` | Visite cinéma, curseur du temps, partage, photo EPIC | **NON TERMINÉ, NON TESTÉ** |

- **Les quatre branches `wip-*`** partent d'un commit un peu plus ancien (`0cd1d9e`).
- **Les mêmes travaux existent en patchs** dans ce dossier (`wip-*.patch`), refaits pour s'appliquer sur
  `claude/fatiha-cinema` :
  ```bash
  git checkout claude/fatiha-cinema
  git apply --3way handoff/wip-plongee.patch   # etc., un par un, puis tester
  ```
- **Vérifié** : les quatre patchs s'appliquent ensemble sans conflit, et le JavaScript obtenu est valide
  (`node --check`).
- **Pas vérifié** : aucun n'a été testé dans un navigateur après la fin de son écriture.

## 3. Ce qui marche (branche `claude/fatiha-cinema`)
- **Design « cinéma spatial »** :
  - couleurs : noir bleuté `#04060B`, texte `#F4F6FA`, un seul accent bleu glacier `#9FD3FF` ;
  - polices : Inter fine et JetBrains Mono.
- **Mise en page** :
  - en haut à gauche, le nom et une ligne d'état ;
  - en haut à droite, les boutons ronds « Orbite » et « Menu » ;
  - en bas, la bande des lieux ;
  - la fiche du lieu est sans cadre, avec « Lire la suite » et les pastilles Plonger, Nuit et Google Earth ;
  - les panneaux (Menu, Veille, The Light · Stream) sont un tiroir à droite sur ordinateur et une feuille en bas sur
    téléphone. Échap et ✕ les ferment.
- **The Light · Stream** :
  - les télés (iptv-org) et les radios (radio-browser) du pays choisi s'affichent en petits carrés ;
  - un aperçu vidéo muet tourne seulement dans les carrés visibles, au plus 4 sur téléphone et 6 sur ordinateur ;
  - toucher un carré l'ouvre en grand, avec le son ;
  - « Hors ligne » s'affiche au bout de 10 s si le flux ne répond pas ;
  - on choisit le pays en touchant le globe ;
  - autres onglets : caméras (liens) et titres sur les conflits (GDELT).
- **Veille** : séismes (USGS), station spatiale, satellites militaires, nuages réels, lumières de nuit (NASA),
  précipitations, jour et nuit réels, salle de situation.
  - Les satellites militaires viennent du catalogue public CelesTrak, groupe `military`. Leurs positions sont calculées
    avec satellite.js et gardées 2 h en cache.
- **Qualité « Ultra · HDR 5K »** : rendu HDR, image calculée jusqu'à 5120 px (4096 px sur téléphone), puis réduite à
  l'écran.
- **Tests faits** : Playwright avec SwiftShader, sur téléphone (393×852) et ordinateur.
  - Interface, menu, Direct, choix du pays sur le globe et image 5K (5120×3258) sont testés avec des réponses simulées.
  - Les vraies images Esri et NASA s'affichent bien depuis l'orbite.
  - Aucune erreur de page.

## 4. Travaux inachevés : ce qui est écrit, ce qui manque
Pour tous les quatre, il manque au minimum : les tests dans un navigateur, la relecture, les crédits
(`$('credits').innerHTML = [...]`), la version (`NOUR_BUILD`), le README et `CLAUDE.md`.

### A. Plongée nette et fluide (`wip-plongee`)
**Problème signalé par la propriétaire** : la plongée est « floue, pas nette, pas assez fluide ». Causes trouvées dans le
code d'origine :
- le flou de vitesse `nour_rush` est trop fort jusqu'à la fin ;
- le voile gris des nuages dure trop longtemps ;
- rien ne précharge les tuiles et rien ne les attend ;
- il y a une pause morte de 4 s en haut ;
- la qualité peut baisser d'elle-même en pleine plongée ;
- `diving` reste vrai après une plongée interrompue.

**Ce qui est écrit** :
- une loi de descente tabulée (`DIVE_F`) sur la hauteur au-dessus du sol, qui ralentit fortement à la fin ;
- une montée sans pause ;
- un virage réduit (40°) ;
- un flou léger, nul dans le dernier kilomètre, avec un échantillonnage linéaire ;
- un voile bref vers 3 km au-dessus du sol ;
- un « palier » de fin (`startSettle`) qui attend que les tuiles soient chargées, 2,5 s au plus ;
- un **préchargement** des tuiles Esri sous le lieu, gardées dans une `Map` et servies par une enveloppe de
  `requestImage` (au plus 120 tuiles) ;
- pas de baisse de qualité pendant la plongée (`diveSeq`).

**Ce qui manque** : les mesures avant et après avec la vraie imagerie Esri, et une vérification à l'œil sur téléphone.

### B. Données publiques (`wip-donnees`)
**Ce qui est écrit** :
- **Événements naturels** NASA EONET : points sur le globe, liste, toucher un point fait voler la caméra
  (`#eonet-box`, `#eonet-list`).
- **Aurores** NOAA OVATION : un voile vert dessiné à partir de la grille de 65 160 points (`#aurora-box`).
- **Feux actifs** (`#fires-box`), déjà branchés sur le WMS de GIBS (`WebMapServiceImageryProvider`,
  `VIIRS_NOAA20_Thermal_Anomalies_375m_All`), comme il le faut (voir §5).
- **Météo du lieu** sur la fiche, Open-Meteo (`#card-weather`).
- **Précipitations** : la couche passe par le mécanisme d'arrêt automatique.

**Ce qui manque** : les tests. La météo ne peut pas être testée en vrai depuis le cloud (limite d'Open-Meteo, voir §5).

### C. Caméras, musique, bande-son (`wip-cameras-musique`)
**Ce qui est écrit** :
- un onglet Caméras (`#cam-*`) avec les caméras de ville, un grand lecteur et des points sur le globe. Les lecteurs
  YouTube utilisent déjà `referrerpolicy="strict-origin"`, ce qui est correct (voir §5) ;
- Windy en option, seulement avec `?wkey=` : aucune clé dans le code ;
- un onglet Musique par genre, avec des radios radio-browser (`#music-*`) ;
- une bande-son générée par WebAudio (`#btn-soundtrack`, fonction `setSoundtrack(on)`) qui suit l'altitude et la
  plongée.

**Ce qui manque** :
- mettre dans `CITY_CAMS` la liste vérifiée de `handoff/citycams.json` et les 9 caméras du §6 ;
- les tests.

### D. Spectacle (`wip-spectacle`)
**Ce qui est écrit**, dans le nouveau groupe de menu « Spectacle » :
- **Visite cinéma** (`#btn-tour`, `#cine-*`) : les dix lieux enchaînés, bandes noires au format cinéma, titres comme un
  générique ; un toucher arrête la visite.
- **Curseur du temps** (`#btn-time`) : jour et nuit sur 24 h.
- **Partager cette vue** (`#btn-share`) : un lien `#vue=lat,lon,h,cap,inclinaison`.
- **Photo EPIC de la Terre entière** (`#btn-epic`, `#epic-*`).

**Ce qui manque** : les tests, en particulier la remise en place de la vue partagée au démarrage et la photo EPIC
réelle.

## 5. Faits vérifiés EN VRAI (9 nov. 2026, depuis le cloud)
- **Ces services répondent, et acceptent les appels depuis une page web** (`Access-Control-Allow-Origin: *`) :

  | Service | Adresse |
  |---|---|
  | NASA EONET | `https://eonet.gsfc.nasa.gov/api/v3/events?status=open&days=30` |
  | NOAA aurores | `https://services.swpc.noaa.gov/json/ovation_aurora_latest.json` |
  | NASA EPIC | `https://epic.gsfc.nasa.gov/api/natural` |
  | radio-browser | — |
  | iptv-org | — |
  | jsDelivr | — |
  | Esri World Imagery | — |
  | NASA GIBS | — |
  | USGS | — |
  | wheretheiss.at | — |

  - Champs EONET : `id`, `title`, `categories[]`, `sources[]`, `geometry[]`.
  - Champs OVATION : `"Observation Time"`, `"Forecast Time"`, `"Data Format"`, `coordinates` = `[lon 0..359, lat -90..90, valeur]`.
  - Image EPIC : `https://epic.gsfc.nasa.gov/archive/natural/AAAA/MM/JJ/jpg/<image>.jpg` (vérifiée, 200).
- **Feux actifs NASA** : les couches `*_Thermal_Anomalies_*` de GIBS n'existent **qu'en tuiles vectorielles (MVT)** dans le
  service WMTS, aussi bien en 3857 qu'en 4326. Une couche image WMTS échouera.
  - **Le service WMS les rend en PNG transparent, avec CORS** (vérifié) :
    `https://gibs.earthdata.nasa.gov/wms/epsg3857/best/wms.cgi`, couche
    `VIIRS_NOAA20_Thermal_Anomalies_375m_All`, `format=image/png`, `transparent=true`, `time=<veille>`.
  - Dans Cesium, on la branche avec `WebMapServiceImageryProvider`.
- **Couches GIBS déjà utilisées, confirmées** :
  - `VIIRS_SNPP_CorrectedReflectance_TrueColor` (jpeg, GoogleMapsCompatible_Level9) ;
  - `VIIRS_Black_Marble` (png, Level8, 2016-01-01) ;
  - `IMERG_Precipitation_Rate` (png, Level6).
- **Limites venant des serveurs eux-mêmes** (ce ne sont pas des bugs ; elles concernent l'adresse partagée du cloud, pas
  un visiteur chez lui) :
  - **CelesTrak** coupe la connexion chiffrée venant des adresses de centres de données. Garder le message d'erreur
    clair.
  - **Open-Meteo** répond HTTP 429 `{"reason":"Daily API request limit exceeded..."}` à l'adresse du cloud. La limite
    pour un visiteur est d'environ 10 000 appels par jour.
  - **GDELT** répond 429 si on l'appelle plus d'une fois toutes les 5 s. Le code respecte déjà ce délai.
- **Windy Webcams** : il n'y a pas de clé valide (la propriétaire ne peut pas en créer). La fonction reste endormie ; ne
  jamais la rendre obligatoire.
- **YouTube intégré** : sans l'information « site d'origine », le lecteur affiche « Video player configuration error »
  (erreur 153).
  - Ne pas mettre `referrerpolicy="no-referrer"` sur ces lecteurs.
  - Utiliser la politique par défaut ou `strict-origin-when-cross-origin`.
  - Forme d'intégration : `https://www.youtube-nocookie.com/embed/<id>?autoplay=1&mute=1&playsinline=1`.
- **SkylineWebcams** : leurs conditions interdisent d'intégrer leurs vidéos ailleurs ; seule une image mise à jour
  toutes les 5 minutes est permise. Ne pas les intégrer.

## 6. Caméras de ville vérifiées (sans clé)
**Les 3 contrôles réussis par chacune** :
1. elle est intégrable (oEmbed 200) ;
2. elle est en direct (`isLive` plus des spectateurs) ;
3. le lecteur intégré la joue (`playableInEmbed: true`, avec un bloc `liveStreamability`).

Le propriétaire de chaque chaîne est identifié. Les chaînes anonymes sont exclues.

**Dans `handoff/citycams.json` (9)** :
- Ajaccio, Le Havre, Toulouse : Vision-Environnement, exploitant de webcams touristiques.
- Londres, Abbey Road : EarthCam.
- New York : Times Square, statue de la Liberté, pont de Brooklyn, World Trade Center (EarthCam).
- Washington, Maison-Blanche : earthTV.

**Également vérifiées le 9 nov. vers 18:30 UTC, à ajouter** (identifiant de vidéo YouTube) :

| Ville | Vue | Identifiant | Diffuseur |
|---|---|---|---|
| Paris | Sacré-Cœur | `-xzg3wujOVM` | PARIS TV, paris-tv.com |
| Jérusalem | Mur occidental | `77akujLn4k8` | EarthCam |
| Jérusalem | Grande place du Kotel | `LMHUcDktP-w` | Western Wall Heritage Foundation, thekotel.org |
| Tokyo | Shibuya | `5B4LmH4JbnY` | ANNnewsCH (TV Asahi) |
| Tokyo | Shibuya | `dfVK7ld38Ys` | FNN (Fuji TV) |
| Vatican | — | `03pYP2Nmreo` | Vatican Media Live |
| Venise | Bassin de Saint-Marc | `7-XBRpKSv4Q` | I Love You Venice |
| Venise | Rialto | `nviU2HYj-Jc` | I Love You Venice |
| Rome | Vue vers Saint-Pierre | `89d3tEaqImM` | RAMSAT, ramsat.it |

**Pas encore trouvé de direct officiel intégrable** : Marseille, Nice, Lyon, Bordeaux, Tolède, Cordoue, Grenade, Madrid,
Barcelone, Istanbul, Maroc, Égypte, La Mecque.
- Pour La Mecque, il n'y a que des rediffusions non officielles : exclues.
- La tour Eiffel (CESE) interdit l'intégration.

**Pistes non encore contrôlées** :

| Lieu | Identifiant |
|---|---|
| Tokyo Tower | `nu6NE55_X7A` |
| Kyodo, Shiodome | `VM18f-IIUTw` |
| Vannes Tourisme | `dXckWr5B8f8` |
| Saint-Malo | `p6nAlz4_bdI`, `VNOV8KgGR0c` |
| Brest | `SZmbvyfbPbg` |
| Cannes | `z6BNMoj9Pyo` |
| Les Arcs | `B0vZX9GnpxI` |
| Saint-Gervais | `elGbyX0KCMg` |

Les directs YouTube changent parfois d'adresse : vérifier de nouveau avant d'ajouter, et marquer « Hors ligne » quand une
caméra ne joue plus.

## 7. Règles à respecter
- **Caméras** : jamais de caméra privée ou mal protégée (listes de type Insecam). Seulement des caméras publiées par leur
  propriétaire, montrant des lieux publics.
- **Personnes** : rien qui suive ou identifie des personnes. Les satellites viennent uniquement du catalogue public.
- **Clés** : jamais de clé dans le code. Une clé facultative vient du visiteur par `?gkey=` ou `?wkey=`, et reste
  seulement dans son navigateur.
- **Google 3D** : pas d'export d'image au-dessus des tuiles Google ; c'est une condition de Google.
- **Textes venant de l'extérieur** : toujours par `textContent`, jamais par `innerHTML`.
- **Adresses** : https seulement.
- **Caméra de la scène** : la faire bouger uniquement par le moteur de vol `startFlight` (jamais `camera.flyTo`).
- **Mouvement réduit** : respecter `prefers-reduced-motion`.
- **Honnêteté** : ne jamais annoncer comme vérifié ce qui n'a pas été vu marcher. Une source en panne affiche un message
  et se coupe.

## 8. Ordre conseillé pour finir
1. Appliquer `wip-plongee` et tester la plongée sur un vrai téléphone et un vrai ordinateur (vraie imagerie).
2. Appliquer `wip-donnees` ; vérifier les feux (WMS), puis EONET, les aurores et la météo.
3. Appliquer `wip-cameras-musique` ; remplir `CITY_CAMS` (§6) et garder `strict-origin` sur les lecteurs YouTube.
4. Appliquer `wip-spectacle` ; tester la visite, le curseur du temps, le partage et EPIC.
5. Ajouter les crédits et la version, et mettre à jour le README et `CLAUDE.md`.
6. Fusionner la PR #30 dans `main` : le site en ligne se met à jour tout seul (GitHub Pages).
