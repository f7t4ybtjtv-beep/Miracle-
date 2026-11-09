(() => {
  'use strict';
  const C = Cesium;
  // Same as original: empty Ion token — no new account/secret.
  const ION_TOKEN = '';

  const PLACES = [
  {
    "id": "tolede",
    "name": "Tolède",
    "country": "Espagne",
    "lat": 39.857,
    "lon": -4.0237,
    "text": "Aux XIIe et XIIIe siècles, des traducteurs y firent passer en latin puis en castillan des œuvres scientifiques et philosophiques écrites en arabe : c'est ce qu'on appelle l'« école des traducteurs de Tolède ». La ville est bâtie sur un méandre du Tage.",
    "meta": "UNESCO 1986 · Ville historique de Tolède",
    "view": {
      "heading": 330,
      "pitch": -20,
      "range": 3200
    }
  },
  {
    "id": "cordoue",
    "name": "Mosquée-cathédrale de Cordoue",
    "country": "Espagne",
    "lat": 37.8789,
    "lon": -4.7794,
    "text": "Commencée en 785 sous l'émir omeyyade Abd al-Rahman Ier, la grande mosquée fut transformée en cathédrale après la prise de la ville par Ferdinand III de Castille en 1236. Ses arcs bicolores et la cathédrale insérée en son centre portent ces deux histoires.",
    "meta": "UNESCO 1984 · Centre historique de Cordoue",
    "view": {
      "heading": 200,
      "pitch": -22,
      "range": 1800
    }
  },
  {
    "id": "alhambra",
    "name": "Alhambra",
    "country": "Espagne",
    "lat": 37.1761,
    "lon": -3.5881,
    "text": "Palais et forteresse des souverains nasrides, élevés pour l'essentiel aux XIIIe–XIVe siècles sur la colline de la Sabika, dernier contrefort de la Sierra Nevada, à Grenade. Après 1492, Charles Quint y fit élever un palais Renaissance accolé aux palais nasrides.",
    "meta": "UNESCO 1984",
    "view": {
      "heading": 160,
      "pitch": -22,
      "range": 2400
    }
  },
  {
    "id": "tombouctou",
    "name": "Tombouctou",
    "country": "Mali",
    "lat": 16.7711,
    "lon": -3.0105,
    "text": "Aux portes du Sahara, près du fleuve Niger, la ville fut un foyer de savoir dont témoignent des milliers de manuscrits. La mosquée Djingareyber, en terre crue, fut élevée au XIVe siècle, au retour de pèlerinage du souverain du Mali Kankou Moussa.",
    "meta": "UNESCO 1988",
    "view": {
      "heading": 20,
      "pitch": -20,
      "range": 2600
    }
  },
  {
    "id": "alexandrie",
    "name": "Bibliotheca Alexandrina",
    "country": "Égypte",
    "lat": 31.2089,
    "lon": 29.9092,
    "text": "Inaugurée en 2002 sur le front de mer d'Alexandrie, près de l'emplacement présumé de la bibliothèque antique fondée sous les Ptolémées. Son mur de granit porte des caractères de nombreux systèmes d'écriture.",
    "meta": "Inaugurée en 2002",
    "view": {
      "heading": 170,
      "pitch": -18,
      "range": 2000
    }
  },
  {
    "id": "jerusalem",
    "name": "Vieille ville de Jérusalem",
    "country": "Proche-Orient",
    "lat": 31.7767,
    "lon": 35.2345,
    "text": "Sur moins d'un kilomètre carré, la vieille ville réunit des lieux saints du judaïsme, du christianisme et de l'islam, dont le mur des Lamentations, l'église du Saint-Sépulcre et le Dôme du Rocher.",
    "meta": "UNESCO 1981",
    "view": {
      "heading": 250,
      "pitch": -24,
      "range": 2400
    }
  },
  {
    "id": "petra",
    "name": "Petra",
    "country": "Jordanie",
    "lat": 30.3222,
    "lon": 35.4515,
    "text": "Capitale des Nabatéens, mi-bâtie, mi-taillée dans le grès d'un bassin montagneux près de Wadi Musa. Grand centre caravanier de l'encens d'Arabie, au carrefour de l'Arabie, de l'Égypte et de la Syrie-Phénicie, la cité mêle traditions nabatéennes, architecture hellénistique et apports romains.",
    "meta": "UNESCO 1985",
    "view": {
      "heading": 200,
      "pitch": -32,
      "range": 1800
    }
  },
  {
    "id": "istanbul",
    "name": "Sainte-Sophie",
    "country": "Turquie",
    "lat": 41.0086,
    "lon": 28.9802,
    "text": "Construite de 532 à 537 sous l'empereur Justinien, la basilique devint mosquée en 1453, musée en 1934, puis de nouveau mosquée en 2020. Elle domine la péninsule historique, bordée par la Corne d'Or, le Bosphore et la mer de Marmara.",
    "meta": "UNESCO 1985 · Zones historiques d'Istanbul",
    "view": {
      "heading": 300,
      "pitch": -20,
      "range": 2600
    }
  },
  {
    "id": "samarcande",
    "name": "Le Registan, Samarcande",
    "country": "Ouzbékistan",
    "lat": 39.6547,
    "lon": 66.9758,
    "text": "Place bordée de trois madrasas, dont celle d'Ouloug Beg (1417–1420), prince astronome. Samarcande fut une étape majeure des routes de la soie, entre la Chine, l'Inde, la Perse et la Méditerranée.",
    "meta": "UNESCO 2001 · Samarkand – carrefour de cultures",
    "view": {
      "heading": 180,
      "pitch": -24,
      "range": 1600
    }
  },
  {
    "id": "angkor",
    "name": "Angkor Vat",
    "country": "Cambodge",
    "lat": 13.4125,
    "lon": 103.867,
    "text": "Temple construit au début du XIIe siècle sous Suryavarman II et dédié à Vishnou, puis devenu un lieu de culte bouddhiste. Il est entouré de douves d'environ 190 m de large, au nord de Siem Reap.",
    "meta": "UNESCO 1992 · Angkor",
    "view": {
      "heading": 90,
      "pitch": -32,
      "range": 4200
    }
  }
];

  const PHOTOS_MANIFEST_URL = 'photos/photos.json';
  const PHOTOS_BASE = 'photos/';

  const $ = (id) => document.getElementById(id);
  const loader = $('loader');
  const fill = $('loader-fill');
  const btnStart = $('btn-start');
  let viewer, labelsEntity = [], mode = 'tour'; // 'tour' | 'explore'
  let index = 0;
  let flying = false;
  let cinematicState = 'idle', cinematicResult = null;
  const INTRO_SESSION_KEY = 'fatiha.intro.seen.v1';
  const introSeen = () => { try { return sessionStorage.getItem(INTRO_SESSION_KEY) === '1'; } catch (_) { return false; } };
  const rememberIntro = () => { try { sessionStorage.setItem(INTRO_SESSION_KEY, '1'); } catch (_) {} };

  function setProgress(p) {
    fill.style.width = Math.max(8, Math.min(100, p)) + '%';
  }

  function fmtCoord(lat, lon) {
    const ns = lat >= 0 ? 'N' : 'S';
    const ew = lon >= 0 ? 'E' : 'O';
    return Math.abs(lat).toFixed(4) + '° ' + ns + ' · ' + Math.abs(lon).toFixed(4) + '° ' + ew;
  }

  function buildPlaceList() {
    const root = $('place-list');
    root.innerHTML = '';
    PLACES.forEach((p, i) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'fatiha-place';
      b.dataset.i = i;
      b.innerHTML = '<span class="fatiha-place__number">' + String(i+1).padStart(2,'0') + '</span><span>' + p.name + '</span><span class="fatiha-place__country">' + p.country + '</span>';
      b.addEventListener('click', () => { setMode('tour'); goTo(i, true); });
      root.appendChild(b);
    });
  }

  const escapeHTML = (value) => String(value || '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

  function buildCredits(manifestPlaces) {
    const ul = $('credits-list');
    ul.innerHTML = '';
    (manifestPlaces || []).forEach((place) => {
      (place.photos || []).forEach((ph, j) => {
        const li = document.createElement('li');
        const title = (ph.commonsTitle || ph.file || '').replace(/^File:/, '');
        li.innerHTML = '<div class="t">' + place.name + (place.photos.length > 1 ? ' — photo ' + (j + 1) : '') + '</div>'
          + '<div>' + (ph.caption || title) + '</div>'
          + '<div>Titre : <a class="commons-title" href="' + ph.page + '" target="_blank" rel="noopener noreferrer">' + escapeHTML(title) + '</a></div>'
          + '<div>Auteur : ' + (ph.author || '—') + ' · Licence : '
          + (ph.licenseUrl ? ('<a href="' + ph.licenseUrl + '" target="_blank" rel="noopener noreferrer">' + (ph.license || '—') + '</a>') : (ph.license || '—'))
          + '</div>'
          + '<div><a href="' + (ph.page || '#') + '" target="_blank" rel="noopener noreferrer">Page Wikimedia Commons ↗</a></div>';
        ul.appendChild(li);
      });
    });
  }

  function mergePhotos(manifest) {
    const byId = {};
    (manifest.places || []).forEach((p) => { byId[p.id] = p; });
    PLACES.forEach((p) => {
      const src = byId[p.id];
      p.photos = ((src && src.photos) || []).map((ph) => ({
        src: PHOTOS_BASE + ph.file,
        artist: ph.author,
        license: ph.license,
        licenseUrl: ph.licenseUrl,
        pageurl: ph.page,
        title: ph.commonsTitle || ph.file,
        caption: ph.caption || '',
      }));
    });
    buildCredits(manifest.places || []);
    if (!loader.classList.contains('hide')) return;
    updateCard(index);
  }

  function updateCard(i) {
    const p = PLACES[i];
    $('card-kicker').textContent = (i + 1) + ' / ' + PLACES.length + ' · ' + p.country;
    $('card-title').textContent = p.name;
    $('card-coords').textContent = fmtCoord(p.lat, p.lon);
    $('card-text').textContent = p.text;
    $('card-meta').textContent = p.meta;
    $('place-counter').textContent = (i + 1) + ' / ' + PLACES.length;

    const shots = $('card-shots');
    shots.innerHTML = '';
    const cap = $('card-photo-cap');
    if (p.photos && p.photos.length) {
      p.photos.forEach((ph, j) => {
        const figure = document.createElement('figure'); figure.className = 'fatiha-photo';
        figure.innerHTML = '<img class="fatiha-photo__image" src="'+ph.src+'" alt="'+p.name+' — photo '+(j+1)+'" width="1920" height="1280">'
          + '<figcaption class="fatiha-photo__credit">'+ph.caption+'<br>Photo : '+ph.artist+' · <a href="'+ph.licenseUrl+'" target="_blank" rel="noopener noreferrer">'+ph.license+'</a> · <a href="'+ph.pageurl+'" target="_blank" rel="noopener noreferrer">'+escapeHTML(ph.title.replace(/^File:/,''))+'</a> · affichage recadré, fichier inchangé</figcaption>';
        shots.appendChild(figure);
      });
      cap.hidden = false;
      cap.innerHTML = '<button type="button" class="gallery-choice" data-photo="0" aria-label="Afficher la première photo">01</button><span> / </span><button type="button" class="gallery-choice" data-photo="1" aria-label="Afficher la seconde photo">02</button><span class="gallery-hint"> · deux regards sur le lieu · faites glisser</span>';
      cap.querySelectorAll('button').forEach(b => b.onclick = () => shots.scrollTo({left: shots.clientWidth * Number(b.dataset.photo), behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'}));
      shots.scrollLeft = 0;

    } else {
      cap.hidden = true;
    }

    [...$('place-list').children].forEach((el, j) => { el.classList.toggle('on', j === i); el.setAttribute('aria-current', String(j === i)); });
    $('card').scrollTop = 0;
  }

  function unlockCamera() {
    const ctl = viewer.scene.screenSpaceCameraController;
    ctl.enableRotate = true;
    ctl.enableTranslate = true;
    ctl.enableZoom = true;
    ctl.enableTilt = true;
    ctl.enableLook = true;
    ctl.minimumZoomDistance = 1;
    ctl.maximumZoomDistance = Number.POSITIVE_INFINITY;
    ctl.enableCollisionDetection = false;
  }

  function tourCameraLimits() {
    const ctl = viewer.scene.screenSpaceCameraController;
    ctl.enableRotate = true;
    ctl.enableTranslate = true;
    ctl.enableZoom = true;
    ctl.enableTilt = true;
    ctl.enableLook = true;
    // Soft limits for comfort during tour, still fully steerable
    ctl.minimumZoomDistance = 80;
    ctl.maximumZoomDistance = 5.0e7;
    ctl.enableCollisionDetection = true;
  }

  function setMode(m) {
    viewer.camera.cancelFlight();
    mode = m;
    const exploring = m === 'explore';
    $('btn-explore').classList.toggle('on', exploring);
    $('btn-tour').classList.toggle('on', !exploring);
    $('mode-label').textContent = exploring ? 'Exploration libre' : 'Parcours';
    $('explore-banner').classList.toggle('show', exploring);
    $('card').classList.toggle('hidden', exploring);
    $('place-nav').classList.toggle('hidden', exploring);
    $('btn-explore').setAttribute('aria-pressed', String(exploring));
    $('btn-tour').setAttribute('aria-pressed', String(!exploring));
    if (exploring) {
      unlockCamera();
      viewer.camera.flyTo({
        destination: C.Cartesian3.fromDegrees(20, 15, 2.2e7),
        duration: 1.6,
      });
    } else {
      tourCameraLimits();
      goTo(index, true);
    }
  }

  function goTo(i, animate) {
    if (!viewer) return;
    index = (i + PLACES.length) % PLACES.length;
    updateCard(index);
    const p = PLACES[index];
    const v = p.view || { heading: 0, pitch: -25, range: 2500 };
    const center = C.Cartesian3.fromDegrees(p.lon, p.lat, 0);
    const heading = C.Math.toRadians(v.heading || 0);
    const pitch = C.Math.toRadians(v.pitch || -25);
    const range = v.range || 2500;
    flying = true;
    viewer.camera.flyToBoundingSphere(
      new C.BoundingSphere(center, range * 0.15),
      {
        offset: new C.HeadingPitchRange(heading, pitch, range),
        duration: animate ? 2.4 : 0,
        complete: () => { flying = false; },
        cancel: () => { flying = false; },
      }
    );
  }

  function addMarkers() {
    PLACES.forEach((p, i) => {
      const ent = viewer.entities.add({
        id: 'place-' + p.id,
        position: C.Cartesian3.fromDegrees(p.lon, p.lat),
        point: {
          pixelSize: 10,
          color: C.Color.fromCssColorString('#E3B062'),
          outlineColor: C.Color.fromCssColorString('#0B0E14'),
          outlineWidth: 2,
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
        },
        label: {
          text: p.name,
          font: '600 14px Inter, sans-serif',
          fillColor: C.Color.fromCssColorString('#F4ECDF'),
          outlineColor: C.Color.fromCssColorString('#0B0E14'),
          outlineWidth: 3,
          style: C.LabelStyle.FILL_AND_OUTLINE,
          verticalOrigin: C.VerticalOrigin.BOTTOM,
          pixelOffset: new C.Cartesian2(0, -18),
          // Masquer les noms au dézoom ; garder les dix repères ponctuels.
          distanceDisplayCondition: new C.DistanceDisplayCondition(0, 75000),
          disableDepthTestDistance: Number.POSITIVE_INFINITY,
          show: true,
        },
      });
      labelsEntity.push(ent);
      // click handler via picked entity
    });

    const handler = new C.ScreenSpaceEventHandler(viewer.scene.canvas);
    handler.setInputAction((click) => {
      const picked = viewer.scene.pick(click.position);
      if (C.defined(picked) && picked.id && picked.id.id && String(picked.id.id).startsWith('place-')) {
        const id = String(picked.id.id).slice(6);
        const i = PLACES.findIndex((p) => p.id === id);
        if (i >= 0) { setMode('tour'); goTo(i, true); }
      }
    }, C.ScreenSpaceEventType.LEFT_CLICK);
  }

  
  // Terrain Terrarium (AWS Open Data) — same source as the original page.
  const TERRAIN_URL = 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png';
  const TERRAIN_MAX_LEVEL = 15;
  const GRID = 65;
  const MERC_MAX_LAT = 85.0511287798 * Math.PI / 180;
  const mercY = (lat) => (1 - Math.log(Math.tan(Math.PI / 4 + lat / 2)) / Math.PI) / 2;

  class TerrariumTerrainProvider {
    constructor() {
      this.tilingScheme = new C.GeographicTilingScheme();
      this.errorEvent = new C.Event();
      this.credit = new C.Credit('Relief : Tilezen/Mapzen Terrain Tiles (AWS Open Data) — SRTM, GMTED2010, ETOPO1');
      this.hasWaterMask = false;
      this.hasVertexNormals = false;
      this.availability = undefined;
      this._levelZeroError = C.TerrainProvider.getEstimatedLevelZeroGeometricErrorForAHeightmap(
        this.tilingScheme.ellipsoid, GRID, this.tilingScheme.getNumberOfXTilesAtLevel(0));
      this._canvas = document.createElement('canvas');
      this._canvas.width = this._canvas.height = 256;
      this._ctx = this._canvas.getContext('2d', { willReadFrequently: true });
      this._cache = new Map();
    }
    getLevelMaximumGeometricError(level) { return this._levelZeroError / (1 << level); }
    getTileDataAvailable(x, y, level) { return level <= TERRAIN_MAX_LEVEL ? undefined : false; }
    loadTileDataAvailability() { return undefined; }
    _source(z, x, y, request) {
      const key = z + '/' + x + '/' + y;
      const hit = this._cache.get(key);
      if (hit) { this._cache.delete(key); this._cache.set(key, hit); return hit; }
      const url = TERRAIN_URL.replace('{z}', z).replace('{x}', x).replace('{y}', y);
      const img = new C.Resource({ url, request }).fetchImage({ preferImageBitmap: true });
      if (!img) return undefined;
      const p = img.then((im) => {
        this._ctx.drawImage(im, 0, 0, 256, 256);
        if (im.close) im.close();
        const px = this._ctx.getImageData(0, 0, 256, 256).data;
        const h = new Float32Array(256 * 256);
        for (let i = 0, j = 0; i < h.length; i++, j += 4) {
          const v = px[j] * 256 + px[j + 1] + px[j + 2] / 256 - 32768;
          h[i] = v > 0 ? v : 0;
        }
        return h;
      });
      p.catch(() => this._cache.delete(key));
      this._cache.set(key, p);
      if (this._cache.size > 48) this._cache.delete(this._cache.keys().next().value);
      return p;
    }
    requestTileGeometry(x, y, level, request) {
      const rect = this.tilingScheme.tileXYToRectangle(x, y, level);
      const z = Math.min(level, TERRAIN_MAX_LEVEL), n = 1 << z, size = n * 256;
      const toPx = (lon, lat) => [
        (lon + Math.PI) / (2 * Math.PI) * size - 0.5,
        mercY(C.Math.clamp(lat, -MERC_MAX_LAT, MERC_MAX_LAT)) * size - 0.5,
      ];
      const [x0] = toPx(rect.west, rect.north), [x1] = toPx(rect.east, rect.south);
      const ya = toPx(0, rect.north)[1], yb = toPx(0, rect.south)[1];
      const tx0 = Math.floor(Math.max(x0 - 1, 0) / 256), tx1 = Math.floor(Math.min(x1 + 1, size - 1) / 256);
      const ty0 = Math.floor(Math.max(ya - 1, 0) / 256), ty1 = Math.floor(Math.min(yb + 1, size - 1) / 256);
      const keys = [];
      for (let ty = ty0; ty <= ty1; ty++) for (let tx = tx0; tx <= tx1; tx++) keys.push([tx, ty]);
      const first = this._source(z, keys[0][0], keys[0][1], request);
      if (!first) return undefined;
      const rest = keys.slice(1).map(([tx, ty]) => this._source(z, tx, ty));
      if (rest.some((p) => !p)) return undefined;
      return Promise.all([first, ...rest]).then((tiles) => {
        const lookup = new Map(keys.map(([tx, ty], i) => [ty * n + tx, tiles[i]]));
        const pixel = (X, Y) => {
          X = C.Math.clamp(X, 0, size - 1); Y = C.Math.clamp(Y, 0, size - 1);
          const t = lookup.get((Y >> 8) * n + (X >> 8));
          return t ? t[(Y & 255) * 256 + (X & 255)] : 0;
        };
        const sample = (lon, lat) => {
          const [fx, fy] = toPx(lon, lat);
          const X = Math.floor(fx), Y = Math.floor(fy), u = fx - X, v = fy - Y;
          return (pixel(X, Y) * (1 - u) + pixel(X + 1, Y) * u) * (1 - v)
               + (pixel(X, Y + 1) * (1 - u) + pixel(X + 1, Y + 1) * u) * v;
        };
        const dLon = rect.east - rect.west, dLat = rect.north - rect.south;
        const out = new Float32Array(GRID * GRID);
        for (let r = 0; r < GRID; r++) {
          const lat = rect.north - r / (GRID - 1) * dLat;
          for (let c = 0; c < GRID; c++) out[r * GRID + c] = sample(rect.west + c / (GRID - 1) * dLon, lat);
        }
        return new C.HeightmapTerrainData({
          buffer: out, width: GRID, height: GRID,
          childTileMask: level < TERRAIN_MAX_LEVEL ? 15 : 0,
        });
      });
    }
  }

  async function initViewer() {
    setProgress(15);
    if (ION_TOKEN) C.Ion.defaultAccessToken = ION_TOKEN;

    let baseLayer;
    try {
      baseLayer = C.ImageryLayer.fromProviderAsync(
        C.TileMapServiceImageryProvider.fromUrl(C.buildModuleUrl('Assets/Textures/NaturalEarthII'))
      );
    } catch (e) {
      console.warn('NaturalEarth fallback', e);
      baseLayer = false;
    }
    setProgress(35);

    viewer = new C.Viewer('globe', {
      baseLayer: baseLayer || false,
      terrainProvider: new TerrariumTerrainProvider(),
      animation: false,
      timeline: false,
      baseLayerPicker: false,
      geocoder: false,
      homeButton: false,
      sceneModePicker: false,
      navigationHelpButton: false,
      fullscreenButton: false,
      vrButton: false,
      infoBox: false,
      selectionIndicator: false,
      shadows: false,
      requestRenderMode: true,
      maximumRenderTimeChange: Number.POSITIVE_INFINITY,
      creditContainer: $('cesium-attributions'),
    });

    viewer.scene.globe.enableLighting = false; // Lecture des lieux à toute heure, sans simuler une heure historique.
    viewer.scene.globe.atmosphereLightIntensity = 10.0;
    viewer.scene.fog.enabled = true;
    viewer.scene.skyAtmosphere.show = true;
    viewer.scene.backgroundColor = C.Color.fromCssColorString('#0B0E14');
    setProgress(55);

    // Esri World Imagery (same as original)
    try {
      const satellite = viewer.imageryLayers.addImageryProvider(new C.UrlTemplateImageryProvider({
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        maximumLevel: 19,
        credit: new C.Credit('Imagerie : Esri, Maxar, Earthstar Geographics, GIS User Community'),
      }));
      satellite.brightness = 1.02;
      satellite.contrast = 1.06;
      satellite.gamma = 1.04;
    } catch (e) { console.warn('Imagerie Esri', e); }
    setProgress(75);

    if (ION_TOKEN) {
      try {
        const t = await C.createWorldTerrainAsync({ requestVertexNormals: true, requestWaterMask: true });
        viewer.terrainProvider = t;
      } catch (e) { console.warn('Terrain Ion indisponible', e); }
    }

    // Full free camera controls always available; soft zoom floor only in tour.
    unlockCamera();
    tourCameraLimits();
    addMarkers();
    setProgress(100);
    btnStart.disabled = false;
    btnStart.textContent = 'Commencer';
    if (location.hash === '#exploration') { revealUI(); setMode('explore'); }
  }

  function revealUI() {
    loader.classList.add('hide');
    ['topbar','place-nav','card','dock'].forEach((id) => { $(id).hidden = false; });
    goTo(0, true);
    $('btn-explore').focus();
  }

  function beginJourney() {
    if (cinematicState === 'playing') return;
    if (introSeen() || location.hash === '#exploration') { revealUI(); return; }
    cinematicState = 'playing'; btnStart.disabled = true;
    loader.classList.add('hide');
    viewer.camera.cancelFlight();
    window.fatihaIntroApi = FatihaIntro.play(viewer, { base: 'intro/', autoStart: true, onDone: (result) => {
      cinematicState = 'done'; cinematicResult = result.reason; rememberIntro();
      revealUI();
    } });
  }
  window.fatihaCinemaDiagnostic = () => ({ state: cinematicState, result: cinematicResult, seen: introSeen() });

  // Diagnostic en lecture seule pour la vérification locale.
  window.fatihaDiagnostic = () => ({mode, index, ready: !!viewer, labelMaxDistance: 75000, labelsNearCamera: viewer ? labelsEntity.filter(e => e.label.show.getValue(viewer.clock.currentTime) && C.Cartesian3.distance(viewer.camera.positionWC, e.position.getValue(viewer.clock.currentTime)) <= 75000).length : 0, camera: viewer ? {inputs: viewer.scene.screenSpaceCameraController.enableInputs, rotate: viewer.scene.screenSpaceCameraController.enableRotate, zoom: viewer.scene.screenSpaceCameraController.enableZoom, tilt: viewer.scene.screenSpaceCameraController.enableTilt, look: viewer.scene.screenSpaceCameraController.enableLook, max: String(viewer.scene.screenSpaceCameraController.maximumZoomDistance), collision: viewer.scene.screenSpaceCameraController.enableCollisionDetection, position: [viewer.camera.positionWC.x,viewer.camera.positionWC.y,viewer.camera.positionWC.z], tilesLoaded: viewer.scene.globe.tilesLoaded} : null});

  // Wire controls
  buildPlaceList();
  fetch(PHOTOS_MANIFEST_URL, { cache: 'no-cache' })
    .then((r) => { if (!r.ok) throw new Error('photos.json ' + r.status); return r.json(); })
    .then((manifest) => mergePhotos(manifest))
    .catch((e) => { console.warn('Photos officielles indisponibles', e); buildCredits([]); });

  $('btn-start').addEventListener('click', beginJourney);
  $('btn-next').addEventListener('click', () => { setMode('tour'); goTo(index + 1, true); });
  $('btn-prev').addEventListener('click', () => { setMode('tour'); goTo(index - 1, true); });
  $('btn-next2').addEventListener('click', () => { setMode('tour'); goTo(index + 1, true); });
  $('btn-prev2').addEventListener('click', () => { setMode('tour'); goTo(index - 1, true); });
  $('btn-explore').addEventListener('click', () => setMode('explore'));
  $('btn-tour').addEventListener('click', () => setMode('tour'));
  $('banner-back').addEventListener('click', () => setMode('tour'));
  $('btn-labels').addEventListener('click', () => {
    const on = !$('btn-labels').classList.contains('on');
    $('btn-labels').classList.toggle('on', on);
    $('btn-labels').setAttribute('aria-pressed',String(on));
    labelsEntity.forEach((e) => { if (e.label) e.label.show = on; });
  });
  $('btn-labels').classList.add('on');
  $('btn-credits').addEventListener('click', () => {
    const box = $('credits');
    const open = !box.classList.contains('open');
    box.classList.toggle('open', open);
    $('btn-credits').classList.toggle('on', open);
    $('btn-credits').setAttribute('aria-expanded',String(open));
  });

  // Keyboard
  window.addEventListener('keydown', (ev) => {
    if (cinematicState === 'playing') return;
    if (ev.key === 'ArrowRight') { setMode('tour'); goTo(index + 1, true); }
    if (ev.key === 'ArrowLeft') { setMode('tour'); goTo(index - 1, true); }
    if (ev.key === 'Escape' && mode === 'explore') setMode('tour');
  });

  initViewer().catch((err) => {
    console.error(err);
    btnStart.disabled = false;
    btnStart.textContent = 'Réessayer';
    btnStart.onclick = () => location.reload();
    fill.style.width = '100%';
  });
})();
