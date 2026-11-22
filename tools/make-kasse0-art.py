# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10", "numpy>=1.26"]
# ///
"""Erzeugt Cover (600x800) und Hero (1920x620) für KASSE 0 – ohne Spiel-Screenshots.

Motiv: Supermarktdecke mit Neonröhren in Fluchtperspektive, olivgrüner Stich, VHS-Rauschen.
Aufruf:  uv run tools/make-kasse0-art.py <pfad-zu-ArchivoBlack-Regular.ttf>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "covers"
rng = np.random.default_rng(1994)


def scene(w: int, h: int, horizon: float) -> Image.Image:
    """Deckenraster mit Röhren, die zum Fluchtpunkt laufen."""
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(0, 1, w)[None, :]
    base = np.zeros((h, w, 3), np.float32)
    # dunkler, leicht grüner Verlauf, unten fast schwarz
    top = np.array([0.20, 0.23, 0.15]); bottom = np.array([0.05, 0.04, 0.035])
    t = np.clip(y / 1.0, 0, 1)[..., None]
    base[:] = top * (1 - t) + bottom * t
    img = Image.fromarray((base * 255).astype(np.uint8))

    glow = Image.new("RGB", (w, h), 0)
    d = ImageDraw.Draw(glow)
    vx, vy = w * 0.5, h * horizon
    rows = 9
    for r in range(rows):
        depth = (r + 1) / rows                      # 0 = nah, 1 = fern
        yy = vy - (vy + h * 0.1) * (1 - depth) ** 1.6
        spread = (1 - depth) * w * 0.9 + w * 0.04
        length = max(6, (1 - depth) ** 1.3 * w * 0.16)
        thick = max(1, int((1 - depth) * h * 0.022))
        for col in (-1.5, -0.5, 0.5, 1.5):
            cx = vx + col * spread * 0.42
            flicker = 0.45 if (r == 3 and col == 0.5) else 1.0  # eine Röhre flackert
            c = tuple(int(v * (1 - depth * 0.55) * flicker) for v in (236, 245, 214))
            d.rounded_rectangle([cx - length / 2, yy - thick / 2, cx + length / 2, yy + thick / 2], radius=thick, fill=c)
    halo = glow.filter(ImageFilter.GaussianBlur(h * 0.03))
    core = glow.filter(ImageFilter.GaussianBlur(1.2))
    img = Image.fromarray(np.clip(np.asarray(img, np.float32) + np.asarray(halo, np.float32) * 0.9
                                  + np.asarray(core, np.float32) * 0.8, 0, 255).astype(np.uint8))

    # Regalkanten links/rechts als dunkle Silhouetten
    sil = Image.new("L", (w, h), 0)
    sd = ImageDraw.Draw(sil)
    for side in (-1, 1):
        x0 = 0 if side < 0 else w
        sd.polygon([(x0, h * 0.18), (vx + side * w * 0.07, vy), (vx + side * w * 0.07, vy + h * 0.06), (x0, h)], fill=200)
    sil = sil.filter(ImageFilter.GaussianBlur(w * 0.004))
    dark = Image.new("RGB", (w, h), (10, 8, 7))
    img = Image.composite(dark, img, sil)
    # Boden glänzt schwach
    floor = np.asarray(img, np.float32)
    yy = np.arange(h)[:, None]
    refl = np.clip((yy - vy) / (h - vy + 1), 0, 1)[..., None]
    floor = floor * (1 - 0.35 * refl)
    img = Image.fromarray(np.clip(floor, 0, 255).astype(np.uint8))
    return img


def vhs(img: Image.Image) -> Image.Image:
    a = np.asarray(img, np.float32)
    h, w, _ = a.shape
    noise = rng.normal(0, 7, (h, w, 1))
    lines = (np.arange(h) % 3 == 0)[:, None, None] * -6.0
    # Vignette
    yy, xx = np.mgrid[0:h, 0:w]
    v = 1 - 0.55 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) ** 1.2
    a = a * np.clip(v, 0.25, 1)[..., None] + noise + lines
    # leichter Farbversatz (Chroma-Bleed)
    a[..., 0] = np.roll(a[..., 0], 2, axis=1)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def main() -> None:
    font_path = sys.argv[1]
    OUT.mkdir(exist_ok=True)

    hero = vhs(scene(1920, 620, horizon=0.42))
    hero.save(OUT / "kasse0-hero.png", optimize=True)

    cover = vhs(scene(600, 800, horizon=0.30))
    d = ImageDraw.Draw(cover)
    big = ImageFont.truetype(font_path, 132)
    small = ImageFont.truetype(font_path, 26)
    for dx, dy, col in ((4, 4, (0, 0, 0)), (0, 0, (232, 224, 209))):
        d.text((44 + dx, 520 + dy), "KASSE", font=big, fill=col)
        d.text((44 + dx, 640 + dy), "0", font=big, fill=col)
    d.text((48, 470), "LIMINALER SUPERMARKT-HORROR", font=small, fill=(194, 164, 127))
    cover.save(OUT / "kasse0.png", optimize=True)
    print("geschrieben:", OUT / "kasse0.png", OUT / "kasse0-hero.png")


if __name__ == "__main__":
    main()
