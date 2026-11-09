/*
 * intro.js — Intro cinématique « Fatiha » : la Terre depuis l'espace, piqué à travers les nuages, arrivée à la verticale
 * au-dessus de la place de Zocodover (Tolède, premier lieu de la page), fondu vers une vraie vidéo aérienne verticale
 * d'une rue pavée (Pexels, Altaf Shah). Son synthétisé en Web Audio (battement, souffle) + voix off de synthèse.
 *
 *   FatihaIntro.play(viewer | null, { onDone, base: 'intro/' })
 *     viewer : un Cesium.Viewer existant (la page Fatiha) ou null (l'intro crée son propre globe, sans token).
 *     onDone : appelé à la fin ou après « Passer ».
 *     base   : chemin du dossier intro/ (déduit de l'adresse de ce script si absent).
 *   Retourne { skip() }.
 */
(function (global) {
  'use strict';
  const SCRIPT_BASE = (() => { const s = document.currentScript; return s ? s.src.replace(/[^/]*$/, '') : ''; })();
  const TARGET = { lon: -4.02245, lat: 39.85845 };                 // Plaza de Zocodover, Tolède
  const START = { lon: 6.0, lat: 31.0 };
  const T = { A: 1800, B: 4700, C: 5600, X0: 5150, X1: 6250, V1: 1000, V2: 6050, END: 7900 };
  const H0 = 1.55e7, H1 = 1.0e7, HB = 1200, HC = 380;
  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const sstep = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
  const lerp = (a, b, t) => a + (b - a) * t;
  const easeInOut = (t) => -(Math.cos(Math.PI * t) - 1) / 2;

  function pose(t) {
    let h, s;
    if (t < T.A) { const u = t / T.A; h = lerp(H0, H1, easeInOut(u)); s = 0.10 * u; }
    else if (t < T.B) { const u = (t - T.A) / (T.B - T.A); h = Math.exp(lerp(Math.log(H1), Math.log(HB), Math.pow(u, 2.4))); s = lerp(0.10, 1, 1 - Math.pow(1 - u, 3)); }
    else if (t < T.C) { const u = (t - T.B) / (T.C - T.B); h = Math.exp(lerp(Math.log(HB), Math.log(HC), 1 - Math.pow(1 - u, 3))); s = 1; }
    else { h = HC - 25 * clamp((t - T.C) / 2500, 0, 1); s = 1; }
    return { lon: lerp(START.lon, TARGET.lon, s), lat: lerp(START.lat, TARGET.lat, s), h, heading: 28 * sstep(0, T.C, t) };
  }
  const blurAt = (t) => sstep(T.A + 500, T.B - 450, t) * (1 - sstep(T.B - 200, T.C, t));
  const cloudAt = (t) => clamp((t - (T.B - 950)) / 1300, 0, 1);
  const darkAt = (t) => 0.5 * (1 - sstep(0, T.B - 800, t));

  // ---------------- Audio (one graph, used live and offline for the preview video) ----------------
  function noiseBuffer(ctx, sec) {
    const b = ctx.createBuffer(1, Math.floor(ctx.sampleRate * sec), ctx.sampleRate), d = b.getChannelData(0);
    let last = 0;
    for (let i = 0; i < d.length; i++) { const w = Math.random() * 2 - 1; last = (last + 0.02 * w) / 1.02; d[i] = w * 0.6 + last * 3.0; }
    return b;
  }
  function thump(ctx, out, at, level) {
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.type = 'sine'; o.frequency.setValueAtTime(62, at); o.frequency.exponentialRampToValueAtTime(34, at + 0.16);
    g.gain.setValueAtTime(0.0001, at); g.gain.exponentialRampToValueAtTime(level, at + 0.012); g.gain.exponentialRampToValueAtTime(0.0001, at + 0.32);
    o.connect(g); g.connect(out); o.start(at); o.stop(at + 0.36);
  }
  function buildSound(ctx, t0, voices) {
    const master = ctx.createGain(); master.gain.value = 0.9; master.connect(ctx.destination);
    const lp = ctx.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 180; lp.connect(master);
    // Heartbeat: lub-dub, quickening as the dive starts, then one soft beat on arrival.
    [0.15, 0.98, 1.78, 2.52, 3.18, 3.76].forEach((s, i) => { thump(ctx, lp, t0 + s, 0.95); thump(ctx, lp, t0 + s + 0.27, 0.55 + 0.03 * i); });
    thump(ctx, lp, t0 + 5.75, 0.6); thump(ctx, lp, t0 + 6.02, 0.35);
    // Wind / breath through the dive.
    const n = ctx.createBufferSource(); n.buffer = noiseBuffer(ctx, 8); 
    const bp = ctx.createBiquadFilter(); bp.type = 'bandpass'; bp.Q.value = 0.6;
    bp.frequency.setValueAtTime(260, t0 + 1.6); bp.frequency.exponentialRampToValueAtTime(1900, t0 + 4.4); bp.frequency.exponentialRampToValueAtTime(500, t0 + 5.8);
    const wg = ctx.createGain(); wg.gain.setValueAtTime(0.0001, t0); wg.gain.setValueAtTime(0.0001, t0 + 1.6);
    wg.gain.exponentialRampToValueAtTime(0.5, t0 + 4.3); wg.gain.exponentialRampToValueAtTime(0.08, t0 + 5.2); wg.gain.exponentialRampToValueAtTime(0.0001, t0 + 6.4);
    n.connect(bp); bp.connect(wg); wg.connect(master); n.start(t0 + 1.5); n.stop(t0 + 6.6);
    const r = ctx.createBufferSource(); r.buffer = n.buffer;                       // low rumble under the wind
    const rl = ctx.createBiquadFilter(); rl.type = 'lowpass'; rl.frequency.value = 120;
    const rg = ctx.createGain(); rg.gain.setValueAtTime(0.0001, t0 + 2.2); rg.gain.exponentialRampToValueAtTime(0.7, t0 + 4.4); rg.gain.exponentialRampToValueAtTime(0.0001, t0 + 5.6);
    r.connect(rl); rl.connect(rg); rg.connect(master); r.start(t0 + 2.2); r.stop(t0 + 5.8);
    // Voice-over (synthetic voice files).
    if (voices) [[voices[0], T.V1], [voices[1], T.V2]].forEach(([buf, ms]) => {
      if (!buf) return;
      const s = ctx.createBufferSource(), g = ctx.createGain(); g.gain.value = 1.0; s.buffer = buf; s.connect(g); g.connect(ctx.destination); s.start(t0 + ms / 1000);
    });
  }
  async function loadVoices(ctx, base) {
    return Promise.all(['voix-1.mp3', 'voix-2.mp3'].map((f) => fetch(base + 'media/' + f).then((r) => r.arrayBuffer())
      .then((a) => new Promise((res) => ctx.decodeAudioData(a, res, () => res(null)))).catch(() => null)));
  }

  // ---------------- Clouds (procedural sprites) ----------------
  function cloudSprite(seed) {
    const c = document.createElement('canvas'); c.width = c.height = 384; const g = c.getContext('2d');
    let s = seed; const rnd = () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
    g.filter = 'blur(10px)';
    for (let i = 0; i < 46; i++) {
      const a = rnd() * Math.PI * 2, d = Math.sqrt(rnd()) * 120, x = 192 + Math.cos(a) * d, y = 192 + Math.sin(a) * d * 0.75, r = 30 + rnd() * 70;
      const grd = g.createRadialGradient(x, y, 0, x, y, r);
      const w = 235 + Math.floor(rnd() * 20);
      grd.addColorStop(0, `rgba(${w},${w},${w + 2 > 255 ? 255 : w + 2},0.55)`); grd.addColorStop(1, 'rgba(255,255,255,0)');
      g.fillStyle = grd; g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
    }
    return c;
  }

  const CSS = `
  .fi-root{position:fixed;inset:0;z-index:99999;background:#000;color:#F4ECDF;font-family:Inter,Arial,sans-serif;transition:opacity .6s ease}
  .fi-root.fi-out{opacity:0;pointer-events:none}
  .fi-globe{position:absolute;inset:0}
  .fi-globe .cesium-viewer-bottom,.fi-globe .cesium-widget-credits{display:none!important}
  .fi-fx,.fi-video{position:absolute;inset:0;width:100%;height:100%}
  .fi-video{object-fit:cover;opacity:0;will-change:opacity,transform}
  .fi-vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at center,transparent 45%,rgba(0,0,0,.72) 100%)}
  .fi-start{position:absolute;inset:0;display:grid;place-items:center;background:radial-gradient(ellipse at 50% 45%,#17120d,#000 75%);transition:opacity .5s}
  .fi-start.fi-gone{opacity:0;pointer-events:none}
  .fi-btn{font:600 15px Inter,Arial,sans-serif;letter-spacing:.04em;color:#0B0E14;background:linear-gradient(180deg,#F1CF8E,#E3B062);border:0;border-radius:999px;padding:15px 34px;cursor:pointer;box-shadow:0 10px 40px rgba(227,176,98,.25)}
  .fi-btn:focus-visible,.fi-skip:focus-visible{outline:2px solid #F1CF8E;outline-offset:3px}
  .fi-skip{position:absolute;right:18px;bottom:calc(18px + env(safe-area-inset-bottom));z-index:2;font:500 12px 'JetBrains Mono',monospace;color:rgba(244,236,223,.75);background:rgba(0,0,0,.35);border:1px solid rgba(244,236,223,.25);border-radius:999px;padding:8px 14px;cursor:pointer}
  .fi-skip:hover{color:#fff;border-color:rgba(244,236,223,.6)}
  .fi-credit{position:absolute;left:16px;bottom:calc(16px + env(safe-area-inset-bottom));z-index:2;font:400 10px 'JetBrains Mono',monospace;color:rgba(244,236,223,.55);opacity:0;transition:opacity .8s}
  .fi-credit.on{opacity:1}
  .fi-skip{top:20px;bottom:auto;right:20px;z-index:5;background:#ffdb9b;color:#171007;border:2px solid #fff0cc;font:700 15px Arial,sans-serif;padding:12px 23px;box-shadow:0 5px 25px #0009}
  .fi-context,.fi-video-note{position:absolute;left:20px;right:160px;top:22px;z-index:3;color:#fff0d8;font:12px/1.5 Arial,sans-serif;text-shadow:0 1px 4px #000;background:#020711c9;border:1px solid #ffffff30;border-radius:10px;padding:9px 12px;width:fit-content;max-width:calc(100% - 180px)}
  .fi-video-note{top:83px;display:none;max-width:calc(100% - 40px);right:20px;font-size:13px;background:#020711ed}.fi-video-note.on{display:block}
  .fi-subtitle{position:absolute;z-index:3;bottom:85px;left:20px;right:20px;color:#fff;text-align:center;text-shadow:0 2px 6px #000;font:500 clamp(18px,3vw,25px)/1.5 Georgia,serif}.fi-subtitle:not(:empty){background:#020711b3;border-radius:10px;padding:8px 12px;margin:auto;width:fit-content;max-width:calc(100% - 40px)}
  .fi-credit{opacity:1;right:18px;bottom:20px;color:#e0e7ef;background:#020711be;padding:7px 10px;border-radius:7px;line-height:1.5;font:10px/1.5 Arial,sans-serif}
  @media(max-width:600px){.fi-context{font-size:10px;top:15px;left:12px;right:125px;max-width:calc(100% - 145px)}.fi-skip{right:12px;top:15px;padding:11px 17px;font-size:14px}.fi-video-note{left:12px;top:95px;font-size:11px;max-width:calc(100% - 24px)}.fi-credit{left:12px;right:12px;font-size:9px}.fi-subtitle{bottom:105px;font-size:20px}}
  `;

  function play(viewer, options) {
    const C = global.Cesium, opts = options || {};
    const base = opts.base || SCRIPT_BASE;
    const capture = !!opts.capture;
    const reduced = global.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!document.getElementById('fi-style')) { const st = document.createElement('style'); st.id = 'fi-style'; st.textContent = CSS; document.head.appendChild(st); }
    const root = document.createElement('section'); root.className = 'fi-root'; root.setAttribute('aria-label','Introduction cinématique'); root.setAttribute('role','dialog'); root.setAttribute('aria-modal','true');
    root.innerHTML = `<div class="fi-globe"></div><video class="fi-video" muted playsinline preload="auto"></video><canvas class="fi-fx"></canvas><div class="fi-vig"></div>
      <div class="fi-context">Séquence artistique · midi simulé · non en direct</div><div class="fi-video-note">Vidéo d’ambiance : rue pavée générique — ce n’est pas Tolède.</div><div class="fi-subtitle" aria-live="polite"></div><div class="fi-credit">Vidéo d’ambiance : Altaf Shah / Pexels · Globe : Esri, Natural Earth, CesiumJS · Voix et sons de synthèse</div>
      <button class="fi-skip" type="button">Passer ›</button>
      <div class="fi-start"><button class="fi-btn" type="button">Commencer</button></div>`;
    document.body.appendChild(root);
    const video = root.querySelector('.fi-video'), fx = root.querySelector('.fi-fx'), g = fx.getContext('2d');
    video.src = base + 'media/rue-pavee.mp4'; video.poster = base + 'media/rue-pavee.jpg';
    const startEl = root.querySelector('.fi-start'), creditEl = root.querySelector('.fi-credit');
    // fx canvas draws everything (globe frame + blur + clouds); the video sits between globe copy and fx for the crossfade
    root.insertBefore(video, root.querySelector('.fi-vig'));

    let own = false;
    if (!viewer) {
      own = true;
      viewer = new C.Viewer(root.querySelector('.fi-globe'), {
        baseLayer: C.ImageryLayer.fromProviderAsync(C.TileMapServiceImageryProvider.fromUrl(C.buildModuleUrl('Assets/Textures/NaturalEarthII'))),
        animation: false, timeline: false, baseLayerPicker: false, geocoder: false, homeButton: false, sceneModePicker: false,
        navigationHelpButton: false, fullscreenButton: false, infoBox: false, selectionIndicator: false,
        useDefaultRenderLoop: !capture, contextOptions: { webgl: { preserveDrawingBuffer: capture } },
      });
      viewer.imageryLayers.addImageryProvider(new C.UrlTemplateImageryProvider({
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', maximumLevel: 19,
        credit: new C.Credit('Imagerie : Esri, Maxar, Earthstar Geographics') }));
      viewer.scene.globe.enableLighting = true;
      viewer.scene.globe.showGroundAtmosphere = true;
    } else {
      root.querySelector('.fi-globe').remove();
    }
    const scene = viewer.scene, camera = scene.camera, ctl = scene.screenSpaceCameraController;
    const saved = { inputs: ctl.enableInputs, time: C.JulianDate.clone(viewer.clock.currentTime), anim: viewer.clock.shouldAnimate };
    ctl.enableInputs = false; viewer.clock.shouldAnimate = false;
    // Noon at Toledo: the real sun high in the sky on arrival.
    { const now = C.JulianDate.toGregorianDate(C.JulianDate.now());
      viewer.clock.currentTime = C.JulianDate.addHours(C.JulianDate.fromGregorianDate(new C.GregorianDate(now.year, now.month, now.day, 0, 0, 0, 0, false)), 12 - TARGET.lon / 15, new C.JulianDate()); }

    const setPose = (p) => camera.setView({ destination: C.Cartesian3.fromDegrees(p.lon, p.lat, p.h),
      orientation: { heading: C.Math.toRadians(p.heading), pitch: C.Math.toRadians(-90), roll: 0 } });
    setPose(pose(T.C + 400));      // while the start screen is up, fetch the arrival tiles

    const sprites = [cloudSprite(7), cloudSprite(91), cloudSprite(1234)];
    let seed = 42; const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
    const parts = Array.from({ length: 30 }, () => { const a = rnd() * 6.283, d = 0.5 + rnd() * 0.9;   // a tunnel: clouds part around the centre
      return { x: Math.cos(a) * d * 1.25, y: Math.sin(a) * d, z: 0.15 + rnd() * 1.25, s: rnd() < .5 ? 0 : rnd() < .5 ? 1 : 2, r: rnd() * 6.28 }; });
    const tmp = document.createElement('canvas'), tg = tmp.getContext('2d');
    let W = 0, H = 0;
    function resize() {
      const dpr = Math.min(global.devicePixelRatio || 1, 1.5);
      W = fx.width = Math.round(root.clientWidth * dpr); H = fx.height = Math.round(root.clientHeight * dpr);
      tmp.width = Math.round(W / 2); tmp.height = Math.round(H / 2);
    }
    resize(); global.addEventListener('resize', resize);

    let t = -1, t0 = 0, done = false, running = false;
    function drawFrame() {
      if (t < 0) return;
      const src = scene.canvas, sw = src.width, sh = src.height;
      const k = Math.max(W / sw, H / sh), dw = sw * k, dh = sh * k;
      const xf = sstep(T.X0, T.X1, t);                       // crossfade globe → video
      g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1; g.clearRect(0, 0, W, H);
      g.globalAlpha = 1 - xf;
      g.drawImage(src, (W - dw) / 2, (H - dh) / 2, dw, dh);
      g.globalAlpha = 1;
      const bl = reduced ? 0 : blurAt(t);
      if (bl > 0.01) {                                       // radial (zoom) blur from the centre
        tg.clearRect(0, 0, tmp.width, tmp.height); tg.drawImage(fx, 0, 0, tmp.width, tmp.height);
        for (let i = 1; i <= 7; i++) {
          const s = 1 + bl * 0.075 * i;
          g.globalAlpha = (0.55 / (i * 0.8 + 0.6)) * bl;
          g.drawImage(tmp, (W - W * s) / 2, (H - H * s) / 2, W * s, H * s);
        }
        g.globalAlpha = 1;
      }
      const cp = cloudAt(t);
      if (cp > 0 && cp < 1) {                                 // through the cloud deck: clouds rush outwards and part
        const zc = cp * 1.55;
        parts.forEach((p) => {
          const rel = p.z - zc; if (rel <= 0.03) return;
          const sc = 0.32 / rel, x = W / 2 + p.x * sc * W * 0.5, y = H / 2 + p.y * sc * H * 0.5, size = Math.max(W, H) * 0.36 * sc;
          const a = sstep(0.03, 0.25, rel) * (1 - sstep(0.75, 1.3, rel)) * 0.6;
          if (a <= 0.01) return;
          g.globalAlpha = a; g.save(); g.translate(x, y); g.rotate(p.r);
          g.drawImage(sprites[p.s], -size / 2, -size / 2 * (1 + bl * 0.6), size, size * (1 + bl * 0.6));
          g.restore();
        });
        const fog = Math.pow(Math.sin(Math.PI * cp), 2) * 0.22;            // white-out in the middle of the deck
        g.globalAlpha = fog; g.fillStyle = '#e9eef2'; g.fillRect(0, 0, W, H); g.globalAlpha = 1;
      }
      const dk = darkAt(t);
      if (dk > 0) { g.globalAlpha = dk; g.fillStyle = '#000'; g.fillRect(0, 0, W, H); g.globalAlpha = 1; }
      // video under the fx canvas: drive its opacity and a slow Ken Burns
      video.style.opacity = String(xf);
      const kb = 1.12 - 0.1 * clamp((t - T.X0) / (T.END - T.X0), 0, 1);
      video.style.transform = `scale(${kb}) rotate(${(-4 + 4 * clamp((t - T.X0) / (T.END - T.X0), 0, 1)).toFixed(2)}deg)`;
      creditEl.classList.toggle('on', t > T.X1 && t < T.END - 400);
      root.querySelector('.fi-video-note').classList.toggle('on', xf > 0.01);
      const subtitle = t >= T.V2 ? 'Il est midi.' : t >= T.V1 && t < 4200 ? 'Commençons par le début.' : '';
      const subtitleEl = root.querySelector('.fi-subtitle'); if (subtitleEl.textContent !== subtitle) subtitleEl.textContent = subtitle;
    }
    const preRender = scene.preRender.addEventListener(() => { if (t >= 0) setPose(pose(t)); });
    const postRender = scene.postRender.addEventListener(() => { if (running || capture) drawFrame(); });

    let audio = null;
    function tick() {
      if (!running) return;
      t = performance.now() - t0;
      if (t >= T.X0 - 250 && video.paused && !video.dataset.started) { video.dataset.started = '1'; video.play().catch(() => {}); }
      if (t >= T.END) { finish('complete'); return; }
      if (!own) scene.requestRender();
      requestAnimationFrame(tick);
    }
    function start() {
      if (done || running) return;
      startEl.inert = true; startEl.querySelector('.fi-btn').disabled = true;
      startEl.classList.add('fi-gone');
      try {
        const AC = global.AudioContext || global.webkitAudioContext;
        audio = new AC();
        const at = audio.currentTime + 0.05;
        loadVoices(audio, base).then((v) => { if (!done) buildSound(audio, at, v); }).catch(() => { if (!done) buildSound(audio, at, null); });
      } catch (e) { /* no audio: the picture still plays */ }
      t0 = performance.now() + 50; t = 0; running = true;
      setPose(pose(0));
      requestAnimationFrame(tick);
      root.querySelector('.fi-skip').focus();
    }
    function finish(reason) {
      if (done) return; done = true; running = false;
      root.classList.add('fi-out'); video.pause();
      if (audio) { try { audio.close(); } catch (e) { /* already closed */ } }
      setTimeout(() => {
        preRender(); postRender(); global.removeEventListener('resize', resize);
        if (own) viewer.destroy(); else { ctl.enableInputs = saved.inputs; viewer.clock.currentTime = saved.time; viewer.clock.shouldAnimate = saved.anim; }
        root.remove();
        if (opts.onDone) opts.onDone({ reason: typeof reason === 'string' ? reason : 'skip' });
      }, 650);
    }
    startEl.querySelector('.fi-btn').addEventListener('click', start);
    root.querySelector('.fi-skip').addEventListener('click', () => finish('skip'));
    root.addEventListener('keydown', (ev) => { if (ev.key === 'Escape') finish('skip'); });
    if (!capture) startEl.querySelector('.fi-btn').focus();

    const api = { skip: () => finish('skip') };
    if (opts.autoStart && !capture) start();
    if (capture) {
      // Deterministic rendering for screenshots / preview video (not used in normal playback).
      api.renderAt = async (ms, waitTiles) => {
        startEl.classList.add('fi-gone'); t = ms;
        if (ms >= T.X0 - 250) { const vt = Math.max(0, (ms - (T.X0 - 250)) / 1000); if (Math.abs(video.currentTime - vt) > 0.01) { video.currentTime = vt; await new Promise((r) => video.addEventListener('seeked', r, { once: true })); } }
        setPose(pose(ms));
        const end = performance.now() + (waitTiles || 0);
        do { viewer.render(); await new Promise((r) => requestAnimationFrame(r)); } while (performance.now() < end && !scene.globe.tilesLoaded);
        viewer.render(); drawFrame();
      };
      api.renderAudioWav = async () => {
        const sr = 44100, ctx = new OfflineAudioContext(2, sr * Math.ceil(T.END / 1000 + 0.5), sr);
        buildSound(ctx, 0.05, await loadVoices(ctx, base));
        const buf = await ctx.startRendering();
        const n = buf.length, out = new DataView(new ArrayBuffer(44 + n * 4));
        const ws = (o, s) => [...s].forEach((c, i) => out.setUint8(o + i, c.charCodeAt(0)));
        ws(0, 'RIFF'); out.setUint32(4, 36 + n * 4, true); ws(8, 'WAVEfmt '); out.setUint32(16, 16, true); out.setUint16(20, 1, true); out.setUint16(22, 2, true);
        out.setUint32(24, sr, true); out.setUint32(28, sr * 4, true); out.setUint16(32, 4, true); out.setUint16(34, 16, true); ws(36, 'data'); out.setUint32(40, n * 4, true);
        const L = buf.getChannelData(0), R = buf.getChannelData(1);
        for (let i = 0; i < n; i++) { out.setInt16(44 + i * 4, clamp(L[i], -1, 1) * 32767, true); out.setInt16(46 + i * 4, clamp(R[i], -1, 1) * 32767, true); }
        let s = ''; const u8 = new Uint8Array(out.buffer); for (let i = 0; i < u8.length; i += 32768) s += String.fromCharCode.apply(null, u8.subarray(i, i + 32768));
        return btoa(s);
      };
      api.T = T;
    }
    return api;
  }
  global.FatihaIntro = { play, TIMELINE: T };
})(window);
