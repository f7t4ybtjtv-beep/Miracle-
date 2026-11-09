/* Module « Ciel » — ajouté par 4I•MINE au produit Fatiha (sans modifier le script d’origine).
   Voyage artistique, avions (OpenSky), satellites (CelesTrak + satellite.js), carte des zones
   de webcams (Leaflet/OSM), ambiance sonore, journal local des échecs de sources.
   Aucune donnée n’est fabriquée : si un service ne répond pas, on l’affiche et on le note. */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const el = (tag, attrs = {}, ...kids) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'class') n.className = v; else if (k === 'text') n.textContent = v;
      else if (k.startsWith('on')) n.addEventListener(k.slice(2), v); else n.setAttribute(k, v);
    }
    kids.forEach((c) => n.append(c));
    return n;
  };
  const terre = () => window.__terre || null;
  const viewer = () => (terre() && terre().viewer) || null;
  const C = () => window.Cesium;
  const hhmm = (d) => d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  /* ---------- Journal local des échecs ---------- */
  const LOG_KEY = 'fatiha-ciel-echecs';
  let failures = [];
  try { failures = JSON.parse(localStorage.getItem(LOG_KEY) || '[]'); } catch (_) { failures = []; }
  function logFail(source, message) {
    failures.unshift({ t: new Date().toISOString(), source, message: String(message).slice(0, 200) });
    failures = failures.slice(0, 60);
    try { localStorage.setItem(LOG_KEY, JSON.stringify(failures)); } catch (_) {}
    renderLog();
  }
  function renderLog() {
    const ul = $('ciel-log'); if (!ul) return;
    ul.replaceChildren();
    if (!failures.length) { ul.append(el('li', { text: 'Aucun échec enregistré.' })); return; }
    failures.forEach((f) => ul.append(el('li', {}, el('b', { text: `${hhmm(new Date(f.t))} ${f.source}` }), document.createTextNode(` — ${f.message}`))));
  }
  // Observe every fetch of the page (radios, télés, GDELT…) without changing its result.
  const nativeFetch = window.fetch.bind(window);
  window.fetch = async (input, init) => {
    const url = typeof input === 'string' ? input : (input && input.url) || '';
    let host = ''; try { host = new URL(url, location.href).host; } catch (_) {}
    try {
      const r = await nativeFetch(input, init);
      if (!r.ok) logFail(host || 'réseau', `HTTP ${r.status}`);
      return r;
    } catch (e) {
      if (!(e && e.name === 'AbortError')) logFail(host || 'réseau', e && e.message || 'échec réseau');
      else logFail(host || 'réseau', 'délai dépassé');
      throw e;
    }
  };
  window.addEventListener('error', (e) => {
    const t = e.target;
    if (t && t !== window && (t.src || t.href)) logFail('ressource', `${t.tagName.toLowerCase()} non chargé : ${t.src || t.href}`);
  }, true);

  async function getJSON(url, ms = 15000) {
    const ctl = new AbortController(); const timer = setTimeout(() => ctl.abort(), ms);
    try {
      const r = await window.fetch(url, { signal: ctl.signal, cache: 'no-store' });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return await r.json();
    } finally { clearTimeout(timer); }
  }
  function loadScript(srcs) {
    return srcs.reduce((p, src) => p.catch(() => new Promise((ok, ko) => {
      const s = el('script', { src }); s.onload = ok; s.onerror = () => ko(new Error(src)); document.head.append(s);
    })), Promise.reject());
  }

  /* ---------- Interface ---------- */
  const panel = el('aside', { class: 'ui ciel glass', id: 'ciel', 'aria-label': 'Ciel : voyage, avions, satellites, webcams' });
  panel.innerHTML = `
    <div class="kicker">Ciel · voyage, avions, satellites</div>
    <div class="tabs" role="group" aria-label="Rubriques du ciel">
      <button class="btn" type="button" data-ctab="voyage" aria-pressed="true">Voyage</button>
      <button class="btn" type="button" data-ctab="avions" aria-pressed="false">Avions</button>
      <button class="btn" type="button" data-ctab="sats" aria-pressed="false">Satellites</button>
      <button class="btn" type="button" data-ctab="cams" aria-pressed="false">Webcams</button>
      <button class="btn" type="button" data-ctab="son" aria-pressed="false">Ambiance</button>
      <button class="btn" type="button" data-ctab="log" aria-pressed="false">Journal</button>
    </div>
    <section class="pane on" data-cpane="voyage">
      <button class="btn cta" type="button" id="ciel-voyage">▶ Traverser les planètes</button>
      <p class="note warn">Vue d’artiste : tailles, distances, couleurs et durées ne respectent pas les échelles physiques. Le trou noir est un interlude imaginé, pas un objet réel du Système solaire.</p>
      <p class="note">Environ 45 s. Échap ou « Fermer » pour revenir au globe. L’ambiance sonore se lance si elle est activée.</p>
    </section>
    <section class="pane" data-cpane="avions">
      <div class="row"><button class="btn" type="button" id="ciel-air-load">Charger l’Europe</button><button class="btn" type="button" id="ciel-air-clear">Effacer</button></div>
      <p class="status" id="ciel-air-status">Rien n’est chargé avant ton clic.</p>
      <ul id="ciel-air-list"></ul>
      <p class="note">Positions ADS-B publiques d’OpenSky Network (accès anonyme, quotas limités, peut refuser ou ne pas répondre). Points jaunes sur le globe. Aucune position n’est inventée : sans réponse, rien n’est affiché.</p>
    </section>
    <section class="pane" data-cpane="sats">
      <div class="row">
        <select id="ciel-sat-group" aria-label="Groupe de satellites">
          <option value="stations">Stations spatiales</option>
          <option value="visual">100 plus brillants</option>
          <option value="gps-ops">GPS</option>
          <option value="galileo">Galileo</option>
          <option value="weather">Météo</option>
          <option value="geo">Géostationnaires</option>
        </select>
        <button class="btn" type="button" id="ciel-sat-load">Charger</button>
        <button class="btn" type="button" id="ciel-sat-clear">Effacer</button>
      </div>
      <div class="row" role="group" aria-label="Vitesse du temps">
        <span class="note" style="margin:0">Temps</span>
        <button class="btn" type="button" data-speed="1" aria-pressed="true">×1</button>
        <button class="btn" type="button" data-speed="60" aria-pressed="false">×60</button>
        <button class="btn" type="button" data-speed="600" aria-pressed="false">×600</button>
      </div>
      <div class="legend"><span><i style="background:#7fd1ff"></i>LEO</span><span><i style="background:#9cff8a"></i>MEO</span><span><i style="background:#ffb35c"></i>GEO</span><span><i style="background:#ff7ad9"></i>HEO</span></div>
      <p class="status" id="ciel-sat-status">Rien n’est chargé avant ton clic.</p>
      <ul id="ciel-sat-list"></ul>
      <p class="note">Éléments orbitaux OMM (JSON) de CelesTrak, propagés dans ton navigateur par SGP4 (satellite.js). Précision de l’ordre du kilomètre, qui se dégrade loin de l’époque des données. Mis en cache 2 h pour respecter CelesTrak.</p>
    </section>
    <section class="pane" data-cpane="cams">
      <div id="ciel-map" role="region" aria-label="Carte des zones de recherche de webcams"></div>
      <p class="status" id="ciel-map-status"></p>
      <p class="note">Les repères sont des zones de recherche autour des lieux, pas des caméras vérifiées. Les liens ouvrent des annuaires publics (Windy, YouTube) dans un nouvel onglet. Fond © contributeurs OpenStreetMap.</p>
    </section>
    <section class="pane" data-cpane="son">
      <div class="row"><button class="btn" type="button" id="ciel-sound" aria-pressed="false">Activer l’ambiance</button></div>
      <div class="row"><span class="note" style="margin:0">Volume</span><input type="range" id="ciel-vol" min="0" max="100" value="45" aria-label="Volume de l’ambiance"></div>
      <p class="note">Nappe sonore originale synthétisée en direct dans le navigateur (Web Audio). Aucun fichier, aucun service externe.</p>
    </section>
    <section class="pane" data-cpane="log">
      <div class="row"><button class="btn" type="button" id="ciel-log-clear">Vider le journal</button></div>
      <ul id="ciel-log"></ul>
      <p class="note">Journal local (stocké seulement dans ce navigateur) des sources qui n’ont pas répondu : radios, télés, actualité, avions, satellites, scripts.</p>
    </section>`;
  document.body.append(panel);

  const tools = document.querySelector('.ui.top .tools');
  const btnCiel = el('button', { class: 'btn', id: 'btn-ciel', type: 'button', 'aria-pressed': 'false', 'aria-controls': 'ciel', text: 'Ciel' });
  if (tools) tools.insertBefore(btnCiel, $('btn-clouds') || null); else document.body.append(btnCiel);
  function setOpen(open) {
    panel.classList.toggle('open', open); btnCiel.setAttribute('aria-pressed', String(open));
    if (open) ['btn-watch', 'btn-live'].forEach((id) => { const b = $(id); if (b && b.getAttribute('aria-pressed') === 'true') b.click(); });
    if (open && currentTab === 'cams') initMap();
  }
  btnCiel.addEventListener('click', () => setOpen(!panel.classList.contains('open')));
  ['btn-watch', 'btn-live'].forEach((id) => { const b = $(id); if (b) b.addEventListener('click', () => { if (b.getAttribute('aria-pressed') !== 'true') return; setOpen(false); }); });
  // The original handlers set aria-pressed synchronously; check after them.
  ['btn-watch', 'btn-live'].forEach((id) => { const b = $(id); if (b) b.addEventListener('click', () => setTimeout(() => { if (b.getAttribute('aria-pressed') === 'true') setOpen(false); }, 0)); });

  let currentTab = 'voyage';
  panel.querySelectorAll('[data-ctab]').forEach((b) => b.addEventListener('click', () => {
    currentTab = b.dataset.ctab;
    panel.querySelectorAll('[data-ctab]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    panel.querySelectorAll('[data-cpane]').forEach((p) => p.classList.toggle('on', p.dataset.cpane === currentTab));
    if (currentTab === 'cams') initMap();
    if (currentTab === 'log') renderLog();
  }));
  $('ciel-log-clear').addEventListener('click', () => { failures = []; try { localStorage.removeItem(LOG_KEY); } catch (_) {} renderLog(); });
  renderLog();

  /* ---------- Avions : OpenSky ---------- */
  let airPoints = null;
  function clearAir() { const v = viewer(); if (airPoints && v) { v.scene.primitives.remove(airPoints); } airPoints = null; $('ciel-air-list').replaceChildren(); }
  async function loadAir() {
    const st = $('ciel-air-status'); st.textContent = 'Interrogation d’OpenSky…';
    const url = 'https://opensky-network.org/api/states/all?lamin=34&lomin=-12&lamax=72&lomax=42';
    let data;
    try { data = await getJSON(url, 20000); } catch (e) {
      st.textContent = `OpenSky n’a pas répondu (${e.name === 'AbortError' ? 'délai dépassé' : e.message}). Aucun avion affiché. Réessaie plus tard : l’accès anonyme est limité.`;
      if (e.name === 'AbortError') logFail('opensky-network.org', 'délai dépassé');
      return;
    }
    const rows = (data && Array.isArray(data.states) ? data.states : []).filter((s) => s[5] != null && s[6] != null && !s[8]);
    clearAir();
    const v = viewer(), Ce = C();
    if (v && Ce) {
      airPoints = new Ce.PointPrimitiveCollection();
      rows.forEach((s) => airPoints.add({ position: Ce.Cartesian3.fromDegrees(s[5], s[6], (s[7] || 0) * 1), pixelSize: 3, color: Ce.Color.fromCssColorString('#F1CF8E') }));
      v.scene.primitives.add(airPoints); v.scene.requestRender && v.scene.requestRender();
    }
    const when = data && data.time ? new Date(data.time * 1000) : new Date();
    st.textContent = `${rows.length} avions en vol reçus · état OpenSky de ${hhmm(when)} (heure locale)` + (v ? '' : '\nGlobe indisponible : liste seulement.');
    const ul = $('ciel-air-list');
    rows.slice().sort((a, b) => (b[7] || 0) - (a[7] || 0)).slice(0, 25).forEach((s) => {
      ul.append(el('li', {}, el('b', { text: (s[1] || s[0] || '').trim() || '—' }), document.createTextNode(` · ${s[2] || '?'} · ${s[7] != null ? Math.round(s[7]) + ' m' : 'alt. ?'} · ${s[9] != null ? Math.round(s[9] * 3.6) + ' km/h' : ''}`)));
    });
  }
  $('ciel-air-load').addEventListener('click', loadAir);
  $('ciel-air-clear').addEventListener('click', () => { clearAir(); $('ciel-air-status').textContent = 'Effacé.'; });

  /* ---------- Satellites : CelesTrak + SGP4 ---------- */
  let satLib = null, sats = [], satPoints = null, satTimer = 0, speed = 1, simBase = Date.now(), realBase = Date.now();
  const simNow = () => new Date(simBase + (Date.now() - realBase) * speed);
  function orbitClass(o) {
    const period = 1440 / o.MEAN_MOTION, e = o.ECCENTRICITY || 0;
    if (e > 0.25) return 'HEO';
    if (period < 128) return 'LEO';
    if (period > 1380 && period < 1500) return 'GEO';
    return 'MEO';
  }
  const CLASS_COLOR = { LEO: '#7fd1ff', MEO: '#9cff8a', GEO: '#ffb35c', HEO: '#ff7ad9' };
  async function ensureSatLib() {
    if (satLib) return satLib;
    await loadScript(['https://cdn.jsdelivr.net/npm/satellite.js@6.0.2/dist/satellite.min.js', 'assets/vendor/satellite.min.js']);
    satLib = window.satellite; if (!satLib || !satLib.json2satrec) throw new Error('satellite.js incomplet');
    return satLib;
  }
  async function getOmm(group) {
    const key = 'fatiha-ciel-omm-' + group;
    try { const c = JSON.parse(localStorage.getItem(key) || 'null'); if (c && Date.now() - c.t < 2 * 3600e3) return { list: c.list, cached: c.t }; } catch (_) {}
    const list = await getJSON(`https://celestrak.org/NORAD/elements/gp.php?GROUP=${encodeURIComponent(group)}&FORMAT=json`, 20000);
    if (!Array.isArray(list)) throw new Error('réponse inattendue');
    try { localStorage.setItem(key, JSON.stringify({ t: Date.now(), list })); } catch (_) {}
    return { list, cached: 0 };
  }
  function clearSats() {
    clearInterval(satTimer); satTimer = 0; const v = viewer();
    if (satPoints && v) v.scene.primitives.remove(satPoints); satPoints = null; sats = [];
    $('ciel-sat-list').replaceChildren();
  }
  function tickSats() {
    const lib = satLib, Ce = C(), t = simNow(), gmst = lib.gstime(t);
    let ok = 0;
    sats.forEach((s) => {
      let pv = null; try { pv = lib.propagate(s.rec, t); } catch (_) {}
      const p = pv && pv.position;
      if (!p || typeof p === 'boolean' || !isFinite(p.x)) { s.geo = null; if (s.pt) s.pt.show = false; return; }
      const g = lib.eciToGeodetic(p, gmst); s.geo = g; ok++;
      if (s.pt && Ce) { s.pt.show = true; s.pt.position = Ce.Cartesian3.fromRadians(g.longitude, g.latitude, g.height * 1000); }
    });
    const v = viewer(); if (v && v.scene.requestRender) v.scene.requestRender();
    $('ciel-sat-status').textContent = `${ok}/${sats.length} propagés · instant simulé ${t.toLocaleString('fr-FR')} (×${speed})` + (sats.cachedNote || '') + (v ? '' : '\nGlobe indisponible : liste seulement.');
    const ul = $('ciel-sat-list'); ul.replaceChildren();
    sats.filter((s) => s.geo).slice(0, 20).forEach((s) => {
      const lat = s.geo.latitude * 180 / Math.PI, lon = s.geo.longitude * 180 / Math.PI;
      ul.append(el('li', {}, el('b', { text: s.name }), document.createTextNode(` · ${s.cls} · ${Math.round(s.geo.height)} km · ${lat.toFixed(1)}°, ${lon.toFixed(1)}°`)));
    });
  }
  async function loadSats() {
    const st = $('ciel-sat-status'); const group = $('ciel-sat-group').value;
    st.textContent = 'Chargement de satellite.js et des données CelesTrak…';
    let lib, res;
    try { lib = await ensureSatLib(); } catch (e) { st.textContent = 'satellite.js indisponible : propagation impossible.'; logFail('satellite.js', e.message); return; }
    try { res = await getOmm(group); } catch (e) {
      st.textContent = `CelesTrak n’a pas répondu (${e.name === 'AbortError' ? 'délai dépassé' : e.message}). Aucun satellite affiché.`;
      if (e.name === 'AbortError') logFail('celestrak.org', 'délai dépassé');
      return;
    }
    clearSats();
    const v = viewer(), Ce = C();
    if (v && Ce) { satPoints = new Ce.PointPrimitiveCollection(); v.scene.primitives.add(satPoints); }
    res.list.slice(0, 3000).forEach((o) => {
      let rec; try { rec = lib.json2satrec(o); } catch (_) { return; }
      if (!rec || rec.error) return;
      const cls = orbitClass(o);
      const s = { name: o.OBJECT_NAME, cls, rec, geo: null, pt: null };
      if (satPoints) s.pt = satPoints.add({ position: Ce.Cartesian3.ZERO, pixelSize: 5, color: Ce.Color.fromCssColorString(CLASS_COLOR[cls]), outlineColor: Ce.Color.BLACK, outlineWidth: 1, show: false });
      sats.push(s);
    });
    sats.cachedNote = res.cached ? `\nDonnées en cache depuis ${hhmm(new Date(res.cached))}` : '';
    simBase = Date.now(); realBase = Date.now();
    tickSats(); satTimer = setInterval(tickSats, 1000);
  }
  $('ciel-sat-load').addEventListener('click', loadSats);
  $('ciel-sat-clear').addEventListener('click', () => { clearSats(); $('ciel-sat-status').textContent = 'Effacé.'; });
  panel.querySelectorAll('[data-speed]').forEach((b) => b.addEventListener('click', () => {
    simBase = simNow().getTime(); realBase = Date.now(); speed = +b.dataset.speed;
    panel.querySelectorAll('[data-speed]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
  }));

  /* ---------- Webcams : carte Leaflet ---------- */
  let map = null;
  async function initMap() {
    if (map) { setTimeout(() => map.invalidateSize(), 50); return; }
    const st = $('ciel-map-status');
    if (!window.L) {
      const css = el('link', { rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css' });
      css.onerror = () => { document.head.append(el('link', { rel: 'stylesheet', href: 'assets/vendor/leaflet.css' })); };
      document.head.append(css);
      try { await loadScript(['https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js', 'assets/vendor/leaflet.js']); }
      catch (e) { st.textContent = 'Leaflet indisponible : carte impossible.'; logFail('leaflet', e.message); return; }
    }
    if (map) return;
    const L = window.L;
    map = L.map('ciel-map', { worldCopyJump: true, attributionControl: true }).setView([30, 20], 2);
    const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 18, attribution: '© OpenStreetMap' }).addTo(map);
    let tileErr = 0; tiles.on('tileerror', () => { if (tileErr++ === 0) { st.textContent = 'Certaines tuiles OpenStreetMap ne se chargent pas.'; logFail('tile.openstreetmap.org', 'tuile non chargée'); } });
    const places = (terre() && terre().PLACES) || [];
    if (!places.length) st.textContent = 'Lieux indisponibles (globe non chargé).';
    places.forEach((p) => {
      const q = encodeURIComponent(`webcam live ${p.name} ${p.country || ''}`.trim());
      const html = `<b>${p.name}</b><br><small>Zone de recherche — aucune caméra vérifiée</small><br>` +
        `<a href="https://www.windy.com/-Webcams-webcams?${p.lat.toFixed(3)},${p.lon.toFixed(3)},10" target="_blank" rel="noopener noreferrer">Windy autour du lieu ↗</a><br>` +
        `<a href="https://www.youtube.com/results?search_query=${q}&sp=EgJAAQ%253D%253D" target="_blank" rel="noopener noreferrer">Directs YouTube ↗</a>`;
      L.circle([p.lat, p.lon], { radius: 25000, color: '#E3B062', weight: 1, fillOpacity: 0.15 }).addTo(map);
      L.circleMarker([p.lat, p.lon], { radius: 6, color: '#F1CF8E', weight: 2, fillColor: '#E3B062', fillOpacity: 0.9 }).bindPopup(html).addTo(map);
    });
    if (places.length) st.textContent = `${places.length} zones de recherche autour des lieux du parcours.`;
    setTimeout(() => map.invalidateSize(), 80);
  }

  /* ---------- Ambiance sonore ---------- */
  let audio = null;
  function startSound() {
    const AC = window.AudioContext || window.webkitAudioContext; if (!AC) { logFail('Web Audio', 'non pris en charge'); return false; }
    const ctx = new AC(), master = ctx.createGain(); master.gain.value = 0; master.connect(ctx.destination);
    const vol = () => (+$('ciel-vol').value / 100) * 0.35;
    master.gain.linearRampToValueAtTime(vol(), ctx.currentTime + 3);
    const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 900; lp.Q.value = 0.7; lp.connect(master);
    const nodes = [];
    [55, 82.41, 110.3, 164.8].forEach((f, i) => {
      const o = ctx.createOscillator(), g = ctx.createGain(); o.type = i % 2 ? 'triangle' : 'sine'; o.frequency.value = f; o.detune.value = (i - 1.5) * 4;
      g.gain.value = 0.18 / (i + 1); o.connect(g); g.connect(lp); o.start(); nodes.push(o);
      const lfo = ctx.createOscillator(), lg = ctx.createGain(); lfo.frequency.value = 0.05 + i * 0.03; lg.gain.value = 0.06 / (i + 1);
      lfo.connect(lg); lg.connect(g.gain); lfo.start(); nodes.push(lfo);
    });
    const cut = ctx.createOscillator(), cg = ctx.createGain(); cut.frequency.value = 0.02; cg.gain.value = 500; cut.connect(cg); cg.connect(lp.frequency); cut.start(); nodes.push(cut);
    // Soft wind: filtered noise.
    const buf = ctx.createBuffer(1, ctx.sampleRate * 2, ctx.sampleRate), d = buf.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    const noise = ctx.createBufferSource(); noise.buffer = buf; noise.loop = true;
    const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.frequency.value = 500; bp.Q.value = 0.6;
    const ng = ctx.createGain(); ng.gain.value = 0.025; noise.connect(bp); bp.connect(ng); ng.connect(master); noise.start(); nodes.push(noise);
    // Sparse bell notes (pentatonic).
    const scale = [440, 493.9, 587.3, 659.3, 784, 880];
    const bell = setInterval(() => {
      if (Math.random() < 0.45) return;
      const o = ctx.createOscillator(), g = ctx.createGain(), t = ctx.currentTime;
      o.type = 'sine'; o.frequency.value = scale[Math.floor(Math.random() * scale.length)] / (Math.random() < 0.5 ? 2 : 1);
      g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(0.05, t + 0.05); g.gain.exponentialRampToValueAtTime(0.0001, t + 4);
      o.connect(g); g.connect(master); o.start(t); o.stop(t + 4.2);
    }, 2600);
    audio = { ctx, master, nodes, bell, vol };
    return true;
  }
  function stopSound() {
    if (!audio) return; const a = audio; audio = null; clearInterval(a.bell);
    a.master.gain.linearRampToValueAtTime(0, a.ctx.currentTime + 1);
    setTimeout(() => a.ctx.close(), 1200);
  }
  $('ciel-sound').addEventListener('click', (e) => {
    const on = !audio && startSound(); if (!on) stopSound();
    e.currentTarget.setAttribute('aria-pressed', String(!!audio)); e.currentTarget.textContent = audio ? 'Couper l’ambiance' : 'Activer l’ambiance';
  });
  $('ciel-vol').addEventListener('input', () => { if (audio) audio.master.gain.setTargetAtTime(audio.vol(), audio.ctx.currentTime, 0.2); });

  /* ---------- Voyage cinématographique (artistique) ---------- */
  const vy = el('div', { id: 'voyage', role: 'dialog', 'aria-label': 'Voyage artistique à travers les planètes' });
  vy.innerHTML = `<canvas></canvas><div class="vy-badge">Vue d’artiste · échelles non physiques</div>
    <button class="btn vy-close" type="button">Fermer ✕</button><div class="vy-title"></div><div class="vy-bar"><i></i></div>`;
  document.body.append(vy);
  const cv = vy.querySelector('canvas'), cx = cv.getContext('2d');
  const SCENES = [
    { name: 'Terre', sub: 'Point de départ', dur: 6, draw: 'earth', c: ['#9fd3ff', '#2a6fb5', '#0a1f3d'] },
    { name: 'Lune', sub: 'Notre satellite naturel', dur: 5.5, draw: 'rock', c: ['#e8e4dc', '#9a958c', '#2b2926'] },
    { name: 'Mars', sub: 'La planète rouge', dur: 6, draw: 'rock', c: ['#ffb38a', '#c1532b', '#3d140a'] },
    { name: 'Jupiter', sub: 'La plus grande des planètes', dur: 6.5, draw: 'bands', c: ['#f3dcb8', '#c48a5a', '#5a3620'] },
    { name: 'Saturne', sub: 'Et ses anneaux', dur: 7, draw: 'rings', c: ['#f6e6bf', '#cfae72', '#5d4826'] },
    { name: 'Interlude : trou noir', sub: 'Imaginé · hors du Système solaire', dur: 9, draw: 'hole' },
    { name: 'Retour', sub: 'Vers la Terre', dur: 5.5, draw: 'earth', c: ['#9fd3ff', '#2a6fb5', '#0a1f3d'] },
  ];
  const TOTAL = SCENES.reduce((s, x) => s + x.dur, 0);
  let stars = [], raf = 0, t0 = 0, W = 0, H = 0, DPR = 1, lastScene = -1, soundByVoyage = false;
  function resize() {
    DPR = Math.min(window.devicePixelRatio || 1, 2); W = cv.clientWidth; H = cv.clientHeight;
    cv.width = W * DPR; cv.height = H * DPR; cx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }
  function seedStars() { stars = Array.from({ length: 700 }, () => ({ x: (Math.random() - 0.5) * 2, y: (Math.random() - 0.5) * 2, z: Math.random(), h: Math.random() })); }
  const ease = (x) => x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  function drawStars(speedK, swirl) {
    const cxm = W / 2, cym = H / 2, f = Math.max(W, H) * 0.6;
    stars.forEach((s) => {
      s.z -= 0.0025 * speedK; if (s.z <= 0.02) { s.z = 1; s.x = (Math.random() - 0.5) * 2; s.y = (Math.random() - 0.5) * 2; }
      let x = s.x, y = s.y;
      if (swirl) { const a = swirl * (1 - s.z) * 2.2, r = Math.hypot(x, y), th = Math.atan2(y, x) + a; x = Math.cos(th) * r; y = Math.sin(th) * r; }
      const px = cxm + (x / s.z) * f * 0.5, py = cym + (y / s.z) * f * 0.5;
      if (px < -50 || px > W + 50 || py < -50 || py > H + 50) return;
      const a = Math.min(1, (1 - s.z) * 1.4), sz = (1 - s.z) * 1.8 + 0.3;
      cx.fillStyle = s.h > 0.85 ? `rgba(255,210,160,${a})` : `rgba(220,230,255,${a})`;
      if (speedK > 3) { const px2 = cxm + (x / (s.z + 0.02 * speedK)) * f * 0.5, py2 = cym + (y / (s.z + 0.02 * speedK)) * f * 0.5;
        cx.strokeStyle = cx.fillStyle; cx.lineWidth = sz; cx.beginPath(); cx.moveTo(px, py); cx.lineTo(px2, py2); cx.stroke(); }
      else { cx.beginPath(); cx.arc(px, py, sz, 0, 7); cx.fill(); }
    });
  }
  function sphere(x, y, r, c, kind, time) {
    cx.save(); cx.beginPath(); cx.arc(x, y, r, 0, 7); cx.clip();
    const g = cx.createRadialGradient(x - r * 0.35, y - r * 0.35, r * 0.1, x, y, r);
    g.addColorStop(0, c[0]); g.addColorStop(0.55, c[1]); g.addColorStop(1, c[2]); cx.fillStyle = g; cx.fillRect(x - r, y - r, 2 * r, 2 * r);
    if (kind === 'bands' || kind === 'rings') {
      for (let i = -8; i <= 8; i++) { cx.fillStyle = `rgba(${i % 2 ? '120,70,40' : '255,240,220'},${0.10 + 0.05 * Math.sin(i * 1.7)})`;
        const yy = y + (i / 8) * r, w = r * (0.06 + 0.04 * Math.abs(Math.sin(i * 2.3)));
        cx.beginPath(); cx.ellipse(x + Math.sin(time * 0.3 + i) * r * 0.02, yy, r * 1.1, w, 0, 0, 7); cx.fill(); }
      if (kind === 'bands') { cx.fillStyle = 'rgba(190,80,50,.55)'; cx.beginPath(); cx.ellipse(x + r * 0.3, y + r * 0.35, r * 0.16, r * 0.08, 0, 0, 7); cx.fill(); }
    } else if (kind === 'rock') {
      for (let i = 0; i < 26; i++) { const a = i * 2.39996, d = Math.sqrt(i / 26) * r * 0.9;
        cx.fillStyle = 'rgba(0,0,0,.12)'; cx.beginPath(); cx.arc(x + Math.cos(a) * d, y + Math.sin(a) * d, r * (0.03 + (i % 5) * 0.012), 0, 7); cx.fill(); }
    } else if (kind === 'earth') {
      cx.fillStyle = 'rgba(70,140,80,.55)';
      [[-.3, -.1, .35, .22], [.25, .2, .25, .35], [.1, -.45, .3, .12], [-.45, .4, .2, .15]].forEach(([a, b, w, h], i) => {
        cx.beginPath(); cx.ellipse(x + (a + Math.sin(time * 0.05) * 0.05) * r, y + b * r, w * r, h * r, i, 0, 7); cx.fill(); });
      cx.fillStyle = 'rgba(255,255,255,.18)';
      for (let i = 0; i < 8; i++) { cx.beginPath(); cx.ellipse(x + Math.cos(i * 1.3 + time * 0.08) * r * 0.6, y + Math.sin(i * 2.1) * r * 0.6, r * 0.25, r * 0.04, i, 0, 7); cx.fill(); }
    }
    const sh = cx.createLinearGradient(x - r, y - r, x + r, y + r); sh.addColorStop(0.45, 'rgba(0,0,0,0)'); sh.addColorStop(1, 'rgba(0,0,0,.85)');
    cx.fillStyle = sh; cx.fillRect(x - r, y - r, 2 * r, 2 * r); cx.restore();
    if (kind === 'earth') { const a = cx.createRadialGradient(x, y, r * 0.95, x, y, r * 1.12); a.addColorStop(0, 'rgba(120,190,255,.5)'); a.addColorStop(1, 'rgba(120,190,255,0)'); cx.fillStyle = a; cx.beginPath(); cx.arc(x, y, r * 1.12, 0, 7); cx.fill(); }
  }
  function rings(x, y, r, front) {
    cx.save(); cx.translate(x, y); cx.rotate(-0.35);
    for (let i = 0; i < 26; i++) { const rr = r * (1.35 + i * 0.035);
      cx.strokeStyle = `rgba(230,205,150,${0.08 + 0.18 * Math.abs(Math.sin(i * 1.9))})`; cx.lineWidth = r * 0.03;
      cx.beginPath(); cx.ellipse(0, 0, rr, rr * 0.28, 0, front ? 0 : Math.PI, front ? Math.PI : 2 * Math.PI); cx.stroke(); }
    cx.restore();
  }
  function blackHole(p, time) {
    const x = W / 2, y = H / 2, r = Math.min(W, H) * (0.08 + 0.1 * ease(Math.min(1, p * 1.6)));
    const glow = cx.createRadialGradient(x, y, r, x, y, r * 6); glow.addColorStop(0, 'rgba(255,170,80,.35)'); glow.addColorStop(1, 'rgba(255,120,40,0)');
    cx.fillStyle = glow; cx.fillRect(0, 0, W, H);
    const disk = (front) => { cx.save(); cx.translate(x, y); cx.rotate(-0.18);
      for (let i = 0; i < 40; i++) { const rr = r * (1.6 + i * 0.07), a = 0.5 * (1 - i / 40);
        cx.strokeStyle = `rgba(255,${180 - i * 2},${90 - i},${a * (0.6 + 0.4 * Math.sin(time * 3 + i))})`; cx.lineWidth = r * 0.06;
        cx.beginPath(); cx.ellipse(0, 0, rr, rr * 0.22, 0, front ? 0 : Math.PI, front ? Math.PI : 2 * Math.PI); cx.stroke(); }
      cx.restore(); };
    disk(false);
    // Lensed image of the disk over the top (artistic).
    cx.save(); cx.translate(x, y);
    for (let i = 0; i < 14; i++) { cx.strokeStyle = `rgba(255,200,130,${0.25 * (1 - i / 14)})`; cx.lineWidth = r * 0.05; cx.beginPath(); cx.arc(0, 0, r * (1.15 + i * 0.05), Math.PI * 1.05, Math.PI * 1.95); cx.stroke(); }
    cx.restore();
    cx.fillStyle = '#000'; cx.beginPath(); cx.arc(x, y, r, 0, 7); cx.fill();
    cx.strokeStyle = 'rgba(255,230,190,.9)'; cx.lineWidth = Math.max(1.5, r * 0.025); cx.beginPath(); cx.arc(x, y, r * 1.04, 0, 7); cx.stroke();
    disk(true);
  }
  function frame(now) {
    const t = (now - t0) / 1000; if (t >= TOTAL) { closeVoyage(); return; }
    let acc = 0, i = 0; while (i < SCENES.length - 1 && t > acc + SCENES[i].dur) { acc += SCENES[i].dur; i++; }
    const sc = SCENES[i], p = (t - acc) / sc.dur;
    if (i !== lastScene) { lastScene = i; const tt = vy.querySelector('.vy-title'); tt.style.opacity = 0;
      setTimeout(() => { tt.replaceChildren(document.createTextNode(sc.name), el('small', { text: sc.sub })); tt.style.opacity = 1; }, 300); }
    const title = vy.querySelector('.vy-title'); if (p > 0.82) title.style.opacity = 0;
    cx.fillStyle = sc.draw === 'hole' ? 'rgba(0,0,0,.45)' : 'rgba(2,4,10,.55)'; cx.fillRect(0, 0, W, H);
    const transit = p < 0.12 || p > 0.88;
    drawStars(transit ? 9 : 1.2, sc.draw === 'hole' ? 0.6 + p : 0);
    if (sc.draw === 'hole') blackHole(p, t);
    else {
      const k = ease(p), r = Math.min(W, H) * (0.05 + 0.42 * k) * (sc.draw === 'rings' ? 0.7 : 1);
      const x = W / 2 + (0.5 - k) * W * 0.35 + (p > 0.85 ? (p - 0.85) * W * 3 : 0), y = H / 2 - (0.5 - k) * H * 0.1;
      cx.globalAlpha = p < 0.06 ? p / 0.06 : 1;
      if (sc.draw === 'rings') rings(x, y, r, false);
      sphere(x, y, r, sc.c, sc.draw, t);
      if (sc.draw === 'rings') rings(x, y, r, true);
      cx.globalAlpha = 1;
    }
    vy.querySelector('.vy-bar i').style.width = `${(t / TOTAL) * 100}%`;
    raf = requestAnimationFrame(frame);
  }
  function openVoyage() {
    vy.classList.add('on'); resize(); seedStars(); cx.fillStyle = '#000'; cx.fillRect(0, 0, W, H);
    lastScene = -1; t0 = performance.now();
    raf = requestAnimationFrame(frame); vy.querySelector('.vy-close').focus();
  }
  function closeVoyage() { cancelAnimationFrame(raf); raf = 0; vy.classList.remove('on'); if (soundByVoyage) { stopSound(); soundByVoyage = false; } }
  $('ciel-voyage').addEventListener('click', openVoyage);
  vy.querySelector('.vy-close').addEventListener('click', closeVoyage);
  window.addEventListener('keydown', (e) => { if (e.key === 'Escape' && vy.classList.contains('on')) closeVoyage(); });
  window.addEventListener('resize', () => { if (vy.classList.contains('on')) resize(); });

  window.__ciel = { logFail, get failures() { return failures.slice(); }, openVoyage, closeVoyage, seek(sec) { t0 = performance.now() - sec * 1000; }, loadSats, loadAir, get satCount() { return sats.length; } };
})();
