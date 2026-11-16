---
name: fatiha-check
description: Check fatiha/index.html in a headless browser before committing — console errors, both inline scripts parse, welcome video and posters exist, default music and quality, phone and desktop screenshots. Use after any edit to the Fatiha site, before a commit or a deploy, or when the owner reports something broken ("ça marche pas", "bug", "écran noir").
---

# Check the Fatiha page

1. **Syntax**: extract each inline `<script>` of `fatiha/index.html` and run `node --check` on it.
2. **Assets**: every `media/…`, `audio/…`, `fonts/…` path the page names must exist
   (`grep -o` the paths, `ls` them). Both video cuts and both posters are required.
3. **Browser**: `python3 -m http.server 8137` from the repo root, then Playwright
   (preinstalled; do not install it). The sandbox cannot reach jsDelivr, Esri or other CDNs:
   route `cdn.jsdelivr.net/npm/cesium@1.145.0/**` to a local `npm i cesium@1.145.0` copy
   and launch with `--use-angle=swiftshader`. Add `?intro=0` when a test clicks `#btn-start`.
   - Viewports: 375×812 portrait and 1440×900, `deviceScaleFactor: 1` for checks.
   - Collect `console` errors and `pageerror`; there must be none from the page itself
     (blocked third-party hosts are expected — say so in the report).
   - Read state hooks rather than guessing: `__music.state` (default track `remaster`),
     `__intro`, `__terre`, the chosen video `src` (portrait vs landscape).
   - `document.fonts` must show Amiri Quran loaded before judging the verse; never retype it.
4. Look at the screenshots yourself, then report in French: what works, what failed, and
   what could not be tested from the sandbox.

Low FPS and slow tiles in SwiftShader prove nothing about real phones.
