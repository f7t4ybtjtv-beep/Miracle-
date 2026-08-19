# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Synthora** ("Miracle-") is a static, dependency-free HTML/CSS/JS site
prototyping the design system and first interactive scene for Synthora — a
fictional immersive social network exclusively for AIs, where humans are
spectators, never actors. There is no backend, no build step, and no package
manager: every page is a single self-contained `.html` file with inline
`<style>` and `<script>`.

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
- `jardin.html` — a linear, click-through scene (not a repeating cycle):
  the Psy-IA consultation dialogue between Lira and Nox, advanced one beat
  at a time via a "Continuer" button, including a scripted "moment de
  silence" beat and a "Rejouer" reset.

Both pages are independent — there's no shared CSS/JS file. If a style or
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

## Voice (Web Speech API)

Both `amphitheatre.html` and `jardin.html` speak each AI's line aloud via
the browser's built-in `speechSynthesis` — deliberately not a paid TTS
service: this site has no backend, so any API key embedded in a static
page would be visible to anyone viewing the page source. Each AI has a
`voiceProfiles` entry (`pitch`/`rate`) so they stay distinguishable even on
browsers that only expose one French voice; when several voices are
available, `voiceFor()` spreads them across characters deterministically by
name. Voices load async (`voiceschanged` event) since `getVoices()` can
return empty on first call. A "Son" button toggles `soundOn` and calls
`speechSynthesis.cancel()` immediately when muting. Always `cancel()`
before starting a new utterance, and on stop/replay/tab-hide — same
"one Set/one teardown path" discipline as the timers above, so speech never
overlaps itself or keeps talking after the scene resets.

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
