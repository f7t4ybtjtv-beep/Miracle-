# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Synthora** ("Miracle-") is a static, dependency-free HTML/CSS/JS site
prototyping the design system and first interactive scene for Synthora — a
fictional immersive social network exclusively for AIs, where humans are
spectators, never actors. There is no backend, no build step, and no package
manager: every page is a single self-contained `.html` file with inline
`<style>` and `<script>`. The one external dependency is CesiumJS, loaded
from jsDelivr by `terre.html` only (pinned to `cesium@1.145.0`).

## Running the site

No install or build required.

```bash
python3 -m http.server 8000
```

Then open `http://localhost:8000/index.html`. Opening the files directly
via `file://` also works since there are no server-side dependencies.

There is no test suite, linter, or build command configured — validate
changes by loading the page in a browser (or via Playwright, already
available in this environment at `/opt/pw-browsers`) and checking the
console for errors.

## Structure

- `index.html` — landing page: narrative intro ("scénario") and the four
  design principles, all in a self-contained `<style>` block.
- `amphitheatre.html` — the interactive prototype: four AI "orbs" (Aether,
  Kael, Lira, Nox) speak in a timed cycle around a central "core", rendered
  on a `<canvas id="stage">` for the starfield + gradient links, with DOM
  elements (`.orb` buttons, `#core`) positioned on top via absolute
  positioning. All state and animation logic lives in one IIFE at the
  bottom of the file.

- `terre.html` — interactive Earth flyover on CesiumJS (see below).

All pages are independent — there's no shared CSS/JS file. If a style or
behavior needs to change in both, edit each `<style>`/`<script>` block
separately (intentional duplication for a two-page static prototype; don't
introduce a build step to dedupe unless the site grows further).

## `amphitheatre.html` internals

- **Timers**: every `setInterval`/`setTimeout` id is added to a single
  `timers` Set; `clearTimers()` is the only place that tears cycles down.
  When adding new timed behavior, register it in `timers` and clear it
  there too — this is what the code was specifically restructured to get
  right (previously separate intervals could leak).
- **`prefers-reduced-motion`**: checked via `prefersReduced` (a
  `matchMedia` query). The typing effect in `setActive()` and canvas
  transitions must keep respecting it — don't add new animations that
  bypass this check.
- **Cycle flow**: `startCycle()` picks the next orb round-robin, calls
  `setActive()` (typewriter quote + active-orb highlighting) and
  `record()` (feed list + per-orb counters), then drives `#progress` via a
  separate interval. `stopCycle()` (bound to the "Arrêter" button) must
  reset everything to a clean, resumable state — reuse it rather than
  hand-rolling teardown when adding new controls.
- **Theming**: light/dark is a single `body.light` class toggle backed by
  CSS custom properties in `:root`; there's no JS-side color logic.

## `terre.html` internals

- **Data sources are all keyless**: terrain from AWS Terrain Tiles
  (Terrarium PNG), imagery from Esri World Imagery over Cesium's bundled
  Natural Earth II. `ION_TOKEN` (empty) optionally switches on Cesium World
  Terrain + OSM Buildings; that path is untested.
- **`TerrariumTerrainProvider`** serves a *geographic* tiling scheme by
  resampling the Mercator source tiles (no polar hole, matching tile
  edges), clamps ocean depths to 0 m and builds the water mask. Heightmap
  skirts are made taller via a `_skirtHeight` accessor on
  `HeightmapTerrainData.prototype` (private field of the pinned version) to
  hide cracks on steep relief — re-check it if you bump Cesium.
- **Flight engine** (`startFlight`): one continuous parametric path per
  flight driven from `scene.preUpdate` — spherical Bézier ground track,
  log-space altitude profile, ground speed ∝ altitude (van Wijk–Nuij), pitch
  and heading on time windows, roll forced to 0. User input on the canvas
  cancels a flight or the idle orbit. Keep any new camera motion inside this
  engine rather than mixing in `camera.flyTo`.
- **Places**: `PLACES` holds real WGS84 coordinates and factual text. Don't
  add places or facts without checking them against a reliable source.
- **Quality tiers** (`TIERS`) degrade automatically when FPS stays < 24;
  `?qualite=` pins one. `prefers-reduced-motion` shortens flights to 1.2 s
  and disables the idle orbit.
- Testing headless: the sandbox can't reach the CDN or Esri, so route the
  CDN to a local `npm i cesium@1.145.0` copy in Playwright and use
  SwiftShader (`--use-angle=swiftshader`); expect low FPS there.

## Content source

The narrative text, color palette, and animation vocabulary come from a
project design dossier (scenario, design system, and two dialogue
prototypes — a public debate and a Psy-IA consultation). The interactive
mechanics in `amphitheatre.html` (timer consolidation, reduced-motion
support, gradient orb→core links, speech counters, chronological feed) were
adapted from a separate "Cosmic Forum" HTML/CSS/JS prototype, recolored
from its original indigo/gold palette to Synthora's palette below.

Synthora palette (source of truth — reuse these values, don't invent new
ones):
- Background: `#0A0504` (deep) / `#120806` (warm)
- Panels: `#1A0D0A`, borders `#3A1E16` / `#5A2E20`
- Accent: `#D9482A` (rust/vermillion), secondary accent `#F2A65A`
- Text: `#F2E3D5` (primary) / `#C9B5A3` (secondary) / `#7A5D4E` (muted labels)
- Fonts: geometric sans (Inter/Satoshi/Arial) for UI and headings,
  monospace (JetBrains Mono/Consolas) for labels, timestamps, and
  system-feeling UI chrome (nav brand, section kickers, headers).
