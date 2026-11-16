"""Render the Fatiha entry video from a NASA EPIC full-disc photo.

Usage: python3 -I render.py <epic.png> <W> <H> <seconds> <out.rgb-pipe-target>
Writes raw RGB24 frames to stdout (pipe into ffmpeg).
Camera: slow eased push-in from the whole Earth to the Mediterranean, slight
image-plane rotation settling to 0, static star field and a thin blue halo
outside the disc. Downscaled frames are supersampled 2x (Lanczos) so the
start does not shimmer; near 1:1 the source is sampled directly (bicubic).
"""
import math
import sys

import numpy as np
from PIL import Image, ImageFilter

src_path, W, H, secs = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
FPS = 30
N = int(round(secs * FPS))

SRC = Image.open(src_path).convert("RGB")
MOON_PATH = sys.argv[6] if len(sys.argv) > 6 else "fatiha/media/planets/moon.webp"
CX, CY, R = 1028.0, 1024.5, 829.0          # measured disc centre and radius (px)

# Start: whole disc at 85 % of the short side, centred. End: Mediterranean / Morocco.
s0 = 0.85 * min(W, H) / (2 * R)
s1 = 1.15
U0 = (CX, CY)
U1 = (1060.0, 560.0) if H > W else (990.0, 520.0)
TH0, TH1 = math.radians(2.5), 0.0


def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * t * (t * (t * 6 - 15) + 10)


# Static star field (screen space), soft.
rng = np.random.default_rng(7)
stars = Image.new("L", (W, H), 0)
px = stars.load()
for _ in range(int(W * H / 2600)):
    x, y = int(rng.integers(0, W)), int(rng.integers(0, H))
    m = rng.random() ** 3
    px[x, y] = int(40 + 215 * m)
stars = np.asarray(stars.filter(ImageFilter.GaussianBlur(0.6)), dtype=np.float32)
stars = np.clip(stars * 2.2, 0, 255)
star_rgb = np.stack([stars, stars * 0.97, stars * 0.92 + 8 * (stars > 0)], axis=2)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
HALO = np.array([90, 150, 255], dtype=np.float32)

# The Moon (NASA/JPL Galileo photo, the one the site's journey uses): small, in a corner of the sky, drifting a little
# outwards and growing slowly (parallax), always behind the Earth (masked by the disc).
MOON = Image.open(MOON_PATH).convert("RGBA")
if H > W:
    M0, M1 = (0.80 * W, 0.115 * H), (0.84 * W, 0.085 * H)
else:
    M0, M1 = (0.86 * W, 0.17 * H), (0.895 * W, 0.12 * H)
MD0 = 0.075 * min(W, H)


def moon_layer(k):
    d = MD0 * (1 + 0.3 * k)
    cx, cy = M0[0] + (M1[0] - M0[0]) * k, M0[1] + (M1[1] - M0[1]) * k
    w = max(2, int(round(d)))
    h = max(2, int(round(d * MOON.height / MOON.width)))
    sprite = MOON.resize((w * 2, h * 2), Image.LANCZOS).resize((w, h), Image.LANCZOS)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.paste(sprite, (int(round(cx - w / 2)), int(round(cy - h / 2))), sprite)
    m = np.asarray(canvas, dtype=np.float32)
    return m[..., :3], m[..., 3:4] / 255.0


def frame(i):
    t = i / max(1, N - 1)
    k = smooth(t)
    s = math.exp(math.log(s0) + (math.log(s1) - math.log(s0)) * k)
    ux = U0[0] + (U1[0] - U0[0]) * k
    uy = U0[1] + (U1[1] - U0[1]) * k
    th = TH0 + (TH1 - TH0) * smooth(t * 1.2)
    ss = 2 if s < 0.9 else 1                  # supersample when shrinking
    w, h, sc = W * ss, H * ss, s * ss
    c, sn = math.cos(th) / sc, math.sin(th) / sc
    a, b, d, e = c, sn, -sn, c
    cc = ux - a * w / 2 - b * h / 2
    ff = uy - d * w / 2 - e * h / 2
    img = SRC.transform((w, h), Image.AFFINE, (a, b, cc, d, e, ff), resample=Image.BICUBIC)
    if ss > 1:
        img = img.resize((W, H), Image.LANCZOS)
    arr = np.asarray(img, dtype=np.float32)
    # Disc centre on screen (forward transform of CX, CY).
    dx, dy = CX - ux, CY - uy
    ox = W / 2 + s * (math.cos(th) * dx - math.sin(th) * dy)
    oy = H / 2 + s * (math.sin(th) * dx + math.cos(th) * dy)
    rs = R * s
    dist = np.hypot(xx - ox, yy - oy)
    out = np.clip(dist - rs, 0, None)
    outside = (dist > rs + 1.5)[..., None]
    halo = (np.exp(-out / (0.035 * rs)) * (dist > rs - 1))[..., None] * HALO * 0.30
    arr = arr + halo + star_rgb * outside * 0.85
    mrgb, ma = moon_layer(k)
    ma = ma * outside
    arr = arr * (1 - ma) + mrgb * 0.95 * ma
    # 1 s fade in from black.
    fade = min(1.0, i / FPS)
    arr *= fade
    return np.clip(arr, 0, 255).astype(np.uint8)


if len(sys.argv) > 5 and sys.argv[5] != "-":   # preview: save a few frames as JPEG
    for f in (0.05, 0.5, 1.0):
        i = min(N - 1, int(f * (N - 1)))
        Image.fromarray(frame(i)).save(f"{sys.argv[5]}-{int(f * 100):03d}.jpg", quality=92)
    sys.exit(0)

out = sys.stdout.buffer
for i in range(N):
    out.write(frame(i).tobytes())
