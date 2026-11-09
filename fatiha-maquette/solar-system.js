/*
 * solar-system.js — Système solaire (échelle artistique) pour un viewer CesiumJS existant.
 * Textures : Solar System Scope, CC BY 4.0 (https://www.solarsystemscope.com/textures/), dans ./textures/.
 * Tailles et distances NON réelles : les astres sont rapprochés pour être visibles en dézoomant depuis la Terre.
 * Le Soleil est placé dans sa vraie direction à l'heure de l'horloge Cesium (éclairage cohérent avec le jour/nuit terrestre).
 *
 * Usage :
 *   const ss = FatihaSolarSystem.attach(viewer, { texturePath: 'textures/' });
 *   ss.flyTo('saturne'); ss.overview(); ss.flyHome(); ss.bodies  // [{id, name, ...}]
 */
(function (global) {
  'use strict';
  const BODIES_DEF = [
    { id: 'soleil',  name: 'Soleil',  tex: '2k_sun.jpg',              r: 6.0e7,  d: 7.0e8, a: 0,    h: 0,      spin: 0.004, sun: true },
    { id: 'mercure', name: 'Mercure', tex: '2k_mercury.jpg',          r: 3.2e6,  d: 4.2e8, a: 14,   h: 2.0e7,  spin: 0.01 },
    { id: 'venus',   name: 'Vénus',   tex: '2k_venus_atmosphere.jpg', r: 6.6e6,  d: 2.6e8, a: -22,  h: -1.5e7, spin: -0.006 },
    { id: 'lune',    name: 'Lune',    tex: '2k_moon.jpg',             r: 2.0e6,  d: 5.0e7, a: 64,   h: 6.0e6,  spin: 0.004 },
    { id: 'mars',    name: 'Mars',    tex: '2k_mars.jpg',             r: 4.2e6,  d: 1.6e8, a: 146,  h: 1.5e7,  spin: 0.02 },
    { id: 'jupiter', name: 'Jupiter', tex: '2k_jupiter.jpg',          r: 3.0e7,  d: 3.4e8, a: -152, h: -2.5e7, spin: 0.03 },
    { id: 'saturne', name: 'Saturne', tex: '2k_saturn.jpg',           r: 2.5e7,  d: 5.0e8, a: 124,  h: 4.0e7,  spin: 0.028, ring: true, tilt: 26.7 },
    { id: 'uranus',  name: 'Uranus',  tex: '2k_uranus.jpg',           r: 1.4e7,  d: 6.4e8, a: -126, h: 3.0e7,  spin: 0.02, tilt: 82 },
    { id: 'neptune', name: 'Neptune', tex: '2k_neptune.jpg',          r: 1.35e7, d: 7.8e8, a: 170,  h: -3.5e7, spin: 0.02, tilt: 28 },
  ];
  const BODY_FS = `
    uniform sampler2D image;
    czm_material czm_getMaterial(czm_materialInput m) {
      czm_material mat = czm_getDefaultMaterial(m);
      vec3 c = texture(image, m.st).rgb;
      vec3 nEC = normalize(m.normalEC);
      vec3 n = normalize(czm_inverseViewRotation * nEC);
      float facing = clamp(dot(nEC, normalize(m.positionToEyeEC)), 0.0, 1.0);
      if (emissive > 0.5) {
        mat.diffuse = c * (0.55 + 0.95 * pow(facing, 0.45)) * vec3(1.18, 1.0, 0.82);
      } else {
        float l = clamp(dot(n, lightDir), 0.0, 1.0);
        float rim = pow(1.0 - facing, 3.0) * 0.25 * smoothstep(0.0, 0.3, l);
        mat.diffuse = c * (0.03 + 1.08 * l) + vec3(1.0, 0.85, 0.65) * rim;
      }
      mat.alpha = 1.0;
      return mat;
    }`;
  const RING_FS = `
    uniform sampler2D image;
    czm_material czm_getMaterial(czm_materialInput m) {
      czm_material mat = czm_getDefaultMaterial(m);
      float r = length(m.st - 0.5) * 2.0;
      if (r < 0.53 || r > 1.0) discard;
      vec4 t = texture(image, vec2((r - 0.53) / 0.47, 0.5));
      mat.diffuse = t.rgb * vec3(1.25, 1.18, 1.05);
      mat.alpha = t.a;
      return mat;
    }`;

  function attach(viewer, options) {
    const C = global.Cesium, opts = options || {};
    const path = opts.texturePath || 'textures/';
    const scene = viewer.scene, camera = scene.camera, clock = viewer.clock, ctl = scene.screenSpaceCameraController;
    const D2R = C.Math.toRadians, V = () => new C.Cartesian3();
    const reduced = global.matchMedia && global.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const onPhase = opts.onPhase || (() => {});
    camera.frustum.far = 1e12;
    if (opts.freeCamera !== false) { ctl.minimumZoomDistance = 1; ctl.maximumZoomDistance = Number.POSITIVE_INFINITY; }

    const TEX = C.MaterialAppearance.MaterialSupport.TEXTURED;
    const bodies = BODIES_DEF.map((d) => Object.assign({}, d));
    const frame = { x: new C.Cartesian3(1, 0, 0), y: new C.Cartesian3(0, 1, 0), z: new C.Cartesian3(0, 0, 1) };
    const sunPos = V(), icrf = new C.Matrix3();
    let focus = null, lastT = null, flight = null, orbitRate = 0;
    const sunBody = bodies[0];

    bodies.forEach((b) => {
      b.center = V(); b.angle = 0;
      b.material = new C.Material({ fabric: { uniforms: { image: path + b.tex, lightDir: new C.Cartesian3(1, 0, 0), emissive: b.sun ? 1 : 0 }, source: BODY_FS } });
      b.prim = scene.primitives.add(new C.Primitive({
        geometryInstances: new C.GeometryInstance({ id: `body:${b.id}`, geometry: new C.EllipsoidGeometry({
          radii: new C.Cartesian3(b.r, b.r, b.r), stackPartitions: 96, slicePartitions: 128, vertexFormat: TEX.vertexFormat }) }),
        appearance: new C.MaterialAppearance({ material: b.material, materialSupport: TEX, flat: true, faceForward: false, closed: true }),
        modelMatrix: C.Matrix4.IDENTITY.clone(), asynchronous: false,
      }));
      if (b.ring) b.ringPrim = scene.primitives.add(new C.Primitive({
        geometryInstances: new C.GeometryInstance({ id: `body:${b.id}`, geometry: new C.PlaneGeometry({ vertexFormat: TEX.vertexFormat }) }),
        appearance: new C.MaterialAppearance({ material: new C.Material({ fabric: { uniforms: { image: path + '2k_saturn_ring_alpha.png' }, source: RING_FS }, translucent: true }),
          materialSupport: TEX, flat: true, faceForward: true, closed: false, translucent: true }),
        modelMatrix: C.Matrix4.IDENTITY.clone(), asynchronous: false,
      }));
    });
    const glow = document.createElement('canvas'); glow.width = glow.height = 256;
    { const g = glow.getContext('2d'), grd = g.createRadialGradient(128, 128, 30, 128, 128, 128);
      grd.addColorStop(0, 'rgba(255,214,140,0.85)'); grd.addColorStop(0.35, 'rgba(255,170,80,0.28)'); grd.addColorStop(1, 'rgba(255,140,60,0)');
      g.fillStyle = grd; g.fillRect(0, 0, 256, 256); }
    const bbs = scene.primitives.add(new C.BillboardCollection());
    const sunGlow = bbs.add({ image: glow, sizeInMeters: true, width: sunBody.r * 4.6, height: sunBody.r * 4.6, position: V() });
    const labels = scene.primitives.add(new C.LabelCollection());
    bodies.forEach((b) => { b.label = labels.add({ text: b.name, font: '600 20px "Cormorant Garamond", Georgia, serif',
      fillColor: C.Color.fromCssColorString('#F4ECDF'), outlineColor: C.Color.fromCssColorString('#0B0E14'), outlineWidth: 3,
      style: C.LabelStyle.FILL_AND_OUTLINE, verticalOrigin: C.VerticalOrigin.BOTTOM, pixelOffset: new C.Cartesian2(0, -6),
      disableDepthTestDistance: Number.POSITIVE_INFINITY, position: V() }); });

    function layout(force) {
      const t = clock.currentTime;
      if (!force && (focus || (lastT && Math.abs(C.JulianDate.secondsDifference(t, lastT)) < 60))) return;
      lastT = C.JulianDate.clone(t);
      C.Simon1994PlanetaryPositions.computeSunPositionInEarthInertialFrame(t, sunPos);
      const m = C.Transforms.computeIcrfToFixedMatrix(t, icrf) || C.Transforms.computeTemeToPseudoFixedMatrix(t, icrf);
      C.Matrix3.multiplyByVector(m, sunPos, sunPos);
      C.Cartesian3.normalize(sunPos, frame.x);
      C.Cartesian3.normalize(C.Cartesian3.cross(C.Cartesian3.UNIT_Z, frame.x, frame.y), frame.y);
      C.Cartesian3.cross(frame.x, frame.y, frame.z);
      bodies.forEach((b) => {
        const a = D2R(b.a), v = C.Cartesian3.multiplyByScalar(frame.x, b.d * Math.cos(a), V());
        C.Cartesian3.add(v, C.Cartesian3.multiplyByScalar(frame.y, b.d * Math.sin(a), V()), v);
        C.Cartesian3.add(v, C.Cartesian3.multiplyByScalar(frame.z, b.h, V()), b.center);
      });
      bodies.forEach((b) => { if (!b.sun) C.Cartesian3.normalize(C.Cartesian3.subtract(sunBody.center, b.center, V()), b.material.uniforms.lightDir); });
      sunGlow.position = sunBody.center;
    }
    const basis = new C.Matrix3(), tiltM = new C.Matrix3(), spinM = new C.Matrix3(), rot = new C.Matrix3();
    let lastFrame = performance.now();
    const smooth = (e0, e1, x) => { const t = C.Math.clamp((x - e0) / (e1 - e0), 0, 1); return t * t * t * (t * (t * 6 - 15) + 10); };
    const ease = (t) => -(Math.cos(Math.PI * t) - 1) / 2;
    const remove = [];
    remove.push(scene.preUpdate.addEventListener(() => {
      const now = performance.now(), dtMs = now - lastFrame;
      if (flight && flight.step(now)) { const f = flight; flight = null; if (f.done) f.done(); }
      else if (!flight && focus && orbitRate >= 0 && !C.Matrix4.equals(camera.transform, C.Matrix4.IDENTITY) && !reduced) {
        orbitRate = Math.min(orbitRate + dtMs * 0.000004, D2R(1.6) / 1000); camera.rotateLeft(orbitRate * dtMs);
      }
    }));
    remove.push(scene.preRender.addEventListener(() => {
      const now = performance.now(), dt = Math.min(0.1, (now - lastFrame) / 1000); lastFrame = now;
      layout(false);
      C.Matrix3.setColumn(basis, 0, frame.x, basis); C.Matrix3.setColumn(basis, 1, frame.y, basis); C.Matrix3.setColumn(basis, 2, frame.z, basis);
      const cam = camera.positionWC, high = camera.positionCartographic.height > 1.2e7;
      bodies.forEach((b) => {
        if (!reduced) b.angle += b.spin * dt * 6;
        C.Matrix3.fromRotationX(D2R(b.tilt || 0), tiltM); C.Matrix3.fromRotationZ(b.angle, spinM);
        C.Matrix3.multiply(basis, tiltM, rot);
        if (b.ringPrim) {
          C.Matrix4.fromRotationTranslation(rot, b.center, b.ringPrim.modelMatrix);
          C.Matrix4.multiplyByUniformScale(b.ringPrim.modelMatrix, b.r * 2.27 * 2, b.ringPrim.modelMatrix);
        }
        C.Matrix3.multiply(rot, spinM, rot);
        C.Matrix4.fromRotationTranslation(rot, b.center, b.prim.modelMatrix);
        const dist = C.Cartesian3.distance(cam, b.center);
        b.label.show = dist > b.r * 7 && dist < b.r * 4000 && (!!focus || high);
        b.label.position = C.Cartesian3.add(b.center, C.Cartesian3.multiplyByScalar(frame.z, b.r * (b.ring ? 1.25 : 1.12), V()), V());
      });
    }));
    layout(true);

    function release() { camera.lookAtTransform(C.Matrix4.IDENTITY); }
    function spaceFlight(end, lookPt, upHint, done) {
      const start = C.Cartesian3.clone(camera.positionWC), d0 = C.Cartesian3.clone(camera.directionWC), u0 = C.Cartesian3.clone(camera.upWC);
      const lenS = C.Cartesian3.magnitude(start);
      const ctrl = lenS < 4e7 ? C.Cartesian3.multiplyByScalar(C.Cartesian3.normalize(start, V()), Math.max(8e7, C.Cartesian3.magnitude(end) * 0.5), V())
        : C.Cartesian3.midpoint(start, end, V());
      const duration = reduced ? 1200 : C.Math.clamp(5000 + Math.log10(C.Cartesian3.distance(start, end) + 1) * 600, 7000, 12000);
      const t0 = performance.now(), P = V(), a = V(), dir = V(), up = V(), tl = V();
      flight = { done, step(now) {
        const t = C.Math.clamp((now - t0) / duration, 0, 1), s = reduced ? t : ease(t);
        C.Cartesian3.multiplyByScalar(start, (1 - s) * (1 - s), P);
        C.Cartesian3.add(P, C.Cartesian3.multiplyByScalar(ctrl, 2 * (1 - s) * s, a), P);
        C.Cartesian3.add(P, C.Cartesian3.multiplyByScalar(end, s * s, a), P);
        const floor = 1.4e7 * Math.sin(Math.PI * s), r = C.Cartesian3.magnitude(P);
        if (r < floor) C.Cartesian3.multiplyByScalar(P, floor / r, P);
        C.Cartesian3.normalize(C.Cartesian3.subtract(lookPt, P, tl), tl);
        C.Cartesian3.normalize(C.Cartesian3.lerp(d0, tl, smooth(0, 0.45, t), dir), dir);
        C.Cartesian3.lerp(u0, upHint, smooth(0, 0.8, t), up);
        C.Cartesian3.subtract(up, C.Cartesian3.multiplyByScalar(dir, C.Cartesian3.dot(up, dir), a), up);
        if (C.Cartesian3.magnitude(up) < 1e-6) C.Cartesian3.clone(upHint, up);
        C.Cartesian3.normalize(up, up);
        camera.setView({ destination: P, orientation: { direction: dir, up } });
        return t >= 1;
      } };
    }
    function startOrbitAt(target) {
      const inv = C.Matrix4.inverseTransformation(C.Transforms.eastNorthUpToFixedFrame(target), new C.Matrix4());
      const local = C.Matrix4.multiplyByPoint(inv, camera.positionWC, V()), range = C.Cartesian3.magnitude(local);
      camera.lookAt(target, new C.HeadingPitchRange(Math.atan2(-local.x, -local.y), -Math.asin(C.Math.clamp(local.z / range, -1, 1)), range));
      orbitRate = 0;
    }
    function leave() { focus = null; ctl.minimumZoomDistance = 1; }
    function flyTo(id) {
      const b = bodies.find((x) => x.id === id); if (!b) return;
      flight = null; release(); leave(); layout(true);
      const target = C.Cartesian3.clone(b.center);
      const toCam = C.Cartesian3.normalize(C.Cartesian3.subtract(camera.positionWC, target, V()), V());
      let side = toCam;
      if (!b.sun) {
        const toSun = C.Cartesian3.normalize(C.Cartesian3.subtract(sunBody.center, target, V()), V());
        side = C.Cartesian3.add(C.Cartesian3.multiplyByScalar(toSun, 0.6, V()), C.Cartesian3.multiplyByScalar(toCam, 0.4, V()), V());
        C.Cartesian3.add(C.Cartesian3.normalize(side, side), C.Cartesian3.multiplyByScalar(frame.z, 0.25, V()), side);
        C.Cartesian3.normalize(side, side);
      }
      const end = C.Cartesian3.add(target, C.Cartesian3.multiplyByScalar(side, b.r * (b.ring ? 4.4 : b.sun ? 3.6 : 3.2), V()), V());
      onPhase(`Vers ${b.name}`);
      spaceFlight(end, target, frame.z, () => { focus = b; ctl.minimumZoomDistance = b.r * 1.15; onPhase(b.name); startOrbitAt(target); });
    }
    function overview() {
      flight = null; release(); leave(); layout(true);
      const look = C.Cartesian3.multiplyByScalar(frame.x, 1.0e8, V());
      const end = C.Cartesian3.add(C.Cartesian3.multiplyByScalar(frame.x, -6.5e8, V()), C.Cartesian3.multiplyByScalar(frame.z, 1.15e9, V()), V());
      C.Cartesian3.add(end, C.Cartesian3.multiplyByScalar(frame.y, 2.5e8, V()), end);
      onPhase('Système solaire');
      spaceFlight(end, look, frame.x, () => onPhase('Système solaire'));
    }
    function flyHome() {
      flight = null; release(); leave();
      const dir = C.Cartesian3.normalize(C.Cartesian3.add(frame.x, C.Cartesian3.multiplyByScalar(frame.z, 0.3, V()), V()), V());
      onPhase('Terre');
      spaceFlight(C.Cartesian3.multiplyByScalar(dir, 2.6e7, V()), C.Cartesian3.ZERO, frame.z, () => onPhase('Terre'));
    }
    // Any user input takes over: no lock on the camera (around a planet, the camera keeps orbiting it).
    const stop = () => { if (flight) { flight = null; onPhase(focus ? focus.name : 'Exploration libre'); } orbitRate = -1; };
    ['pointerdown', 'wheel', 'touchstart'].forEach((ev) => scene.canvas.addEventListener(ev, stop, { passive: true }));
    // Click on a body to fly there.
    const handler = new C.ScreenSpaceEventHandler(scene.canvas);
    handler.setInputAction((m) => {
      const p = scene.pick(m.position), id = p && typeof p.id === 'string' ? p.id : '';
      if (id.startsWith('body:')) flyTo(id.slice(5));
    }, C.ScreenSpaceEventType.LEFT_CLICK);
    return { bodies, flyTo, overview, flyHome, layout, get flying() { return !!flight; }, get focus() { return focus && focus.id; },
      destroy() { remove.forEach((r) => r()); handler.destroy(); bodies.forEach((b) => { scene.primitives.remove(b.prim); if (b.ringPrim) scene.primitives.remove(b.ringPrim); }); scene.primitives.remove(bbs); scene.primitives.remove(labels); } };
  }
  global.FatihaSolarSystem = { attach, BODIES: BODIES_DEF,
    CREDITS: 'Textures : Solar System Scope (solarsystemscope.com/textures), CC BY 4.0 · échelle artistique' };
})(window);
