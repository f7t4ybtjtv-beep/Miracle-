---
name: fatiha-video
description: Re-render the Fatiha welcome video (slow push-in on a NASA EPIC full-Earth photo, stars, blue halo, Moon, owner's soundtrack) in its portrait 1080x1920 and landscape 1920x1080 cuts, with posters. Use whenever the owner asks to remake, sharpen, re-time or re-score the entry/welcome video ("vidéo d'accueil", "intro", "refais la vidéo", "plus net"), or to change its music or add an element to it.
---

# Fatiha welcome video

The page `fatiha/index.html` picks `media/intro-<cut>.mp4` and `media/intro-poster-<cut>.jpg`
by orientation (`cut` = `portrait` | `landscape`). Both files must exist for each cut.

## 1. Source photo
NASA EPIC natural-colour images are keyless on `epic.gsfc.nasa.gov` (the `api.nasa.gov`
key is not injected here):
```
curl -s https://epic.gsfc.nasa.gov/api/natural            # latest list (image, date, centroid)
curl -sO https://epic.gsfc.nasa.gov/archive/natural/YYYY/MM/DD/png/<image>.png   # 2048 px
```
Pick a frame whose centroid longitude is near 0 (Africa / Mediterranean in view). Save it in
the scratchpad, never in the repo.

## 2. Calibrate
`scripts/render.py` hard-codes the disc `CX, CY, R` (centre and radius in px) and the end
point `U1` (Mediterranean). For a new photo, measure the disc (threshold > ~12, bounding box)
and update those constants; check `U1` on a preview.

## 3. Preview, then render
Run from the repo root.
```
python3 -I .claude/skills/fatiha-video/scripts/render.py <epic.png> 1080 1920 59.2 <scratch>/p   # p-005/050/100.jpg
.claude/skills/fatiha-video/scripts/go.sh <epic.png> 1080 1920 <scratch>/intro-portrait.mp4
.claude/skills/fatiha-video/scripts/go.sh <epic.png> 1920 1080 <scratch>/intro-landscape.mp4
```
Optional 5th/6th args: audio file (default `fatiha/audio/fond-remaster.mp3`) and duration.
A render takes several minutes; run both in the background. Look at the preview frames
before the full render.

## 4. Check and install
- `ffprobe` each file: size, ~59 s, one h264 and one aac stream.
- Look at 3 extracted frames per cut: sharp, Moon visible and behind the Earth, no cropping.
- Copy to `fatiha/media/intro-<cut>.mp4` and the posters to `fatiha/media/intro-poster-<cut>.jpg`.
- Update the credit line in the page if the photo date changed.
- Then test (`fatiha-check`) and deploy (`fatiha-deploy`).
