# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10", "numpy>=1.26"]
# ///
"""Erzeugt Cover (600x800) und Hero (1920x620) für Mett-Client: HUD-Kacheln, Tasten und Crosshair auf dunklem Grund.

Aufruf:  uv run tools/make-mettclient-art.py <pfad-zu-ArchivoBlack-Regular.ttf>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).resolve().parent.parent / "covers"
BG, PANEL, EDGE = (18, 14, 11), (36, 29, 23), (74, 60, 48)
CREAM, METT, GOLD = (232, 224, 209), (232, 92, 84), (194, 161, 63)
rng = np.random.default_rng(7)


def ground(w: int, h: int, cx: float, cy: float) -> Image.Image:
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot((xx - cx * w) / w, (yy - cy * h) / h)
    glow = np.clip(1 - r * 1.6, 0, 1)[..., None] ** 2
    a = np.array(BG, np.float32) + glow * (np.array((96, 40, 32), np.float32))
    # Ruhiges Raster aus großen Feldern.
    step = 64
    cells = rng.random((h // step + 1, w // step + 1)) * 9 - 4
    a += np.kron(cells, np.ones((step, step)))[:h, :w, None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def tile(d: ImageDraw.ImageDraw, box, text: str, font, on: bool = False) -> None:
    d.rounded_rectangle(box, 12, fill=METT if on else PANEL, outline=EDGE, width=2)
    d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), text, font=font, fill=BG if on else CREAM, anchor="mm")


def keys(d: ImageDraw.ImageDraw, x: int, y: int, s: int, font) -> None:
    g = s + 10
    tile(d, (x + g, y, x + g + s, y + s), "W", font, True)
    for i, t in enumerate("ASD"):
        tile(d, (x + i * g, y + g, x + i * g + s, y + g + s), t, font, t == "D")
    tile(d, (x, y + 2 * g, x + 2 * g + s, y + 2 * g + s // 2), "", font)


def crosshair(img: Image.Image, x: int, y: int, n: int) -> None:
    glow = Image.new("RGB", img.size)
    for target in (glow, img):
        d = ImageDraw.Draw(target)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = (x + dx * n * 0.4, y + dy * n * 0.4), (x + dx * n, y + dy * n)
            d.line([a, b], fill=CREAM if target is img else METT, width=max(4, n // 9))
    halo = np.asarray(glow.filter(ImageFilter.GaussianBlur(n / 3)), np.float32) * 1.6
    img.paste(Image.fromarray(np.clip(np.asarray(img, np.float32) + halo, 0, 255).astype(np.uint8)))


def main() -> None:
    f = lambda n: ImageFont.truetype(sys.argv[1], n)
    hero = ground(1920, 620, 0.68, 0.5)
    crosshair(hero, 1300, 300, 110)
    d = ImageDraw.Draw(hero)
    keys(d, 1560, 170, 84, f(38))
    for i, t in enumerate(("144 FPS", "12 | 9 CPS", "24 ms")):
        tile(d, (940, 170 + i * 96, 1140, 244 + i * 96), t, f(28), i == 0)
    hero.save(OUT / "mettclient-hero.png", optimize=True)

    cover = ground(600, 800, 0.5, 0.58)
    crosshair(cover, 300, 440, 96)
    d = ImageDraw.Draw(cover)
    d.text((40, 36), "METT", font=f(128), fill=METT)
    d.text((40, 156), "CLIENT", font=f(104), fill=CREAM)
    d.text((44, 286), "MINECRAFT BEDROCK", font=f(26), fill=GOLD)
    keys(d, 40, 570, 68, f(30))
    for i, t in enumerate(("144 FPS", "12 | 9 CPS", "24 ms")):
        tile(d, (350, 570 + i * 64, 560, 622 + i * 64), t, f(24), i == 0)
    cover.save(OUT / "mettclient.png", optimize=True)


if __name__ == "__main__":
    main()
