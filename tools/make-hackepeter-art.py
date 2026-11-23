# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10", "numpy>=1.26"]
# ///
"""Erzeugt Cover (600x800) und Hero (1920x620) für HACKEPETER – ohne Spiel-Screenshots.

Motiv: bunte Stadtstraße mit drei Gleisen in Fluchtperspektive, Häuserblöcke in Bonbonfarben,
goldene Zwiebelringe über den Spuren, blauer Himmel mit warmem Horizont.
Aufruf:  uv run tools/make-hackepeter-art.py <pfad-zu-ArchivoBlack-Regular.ttf>
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "covers"
rng = np.random.default_rng(2026)

CANDY = [(255, 92, 120), (255, 176, 46), (70, 200, 120), (60, 150, 255), (180, 100, 255),
         (255, 120, 200), (40, 210, 210), (255, 220, 70)]
METT = (232, 92, 84)
MUSTARD = (255, 205, 40)


def lerp(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def scene(w: int, h: int, horizon: float) -> Image.Image:
    vy = h * horizon
    vx = w * 0.5
    # Himmel: oben kräftig blau, am Horizont warm
    y = np.linspace(0, 1, h)[:, None, None]
    sky_top = np.array([38, 122, 255], np.float32)
    sky_low = np.array([255, 219, 189], np.float32)
    t = np.clip(y / horizon, 0, 1) ** 1.4
    arr = np.broadcast_to(sky_top * (1 - t) + sky_low * t, (h, w, 3)).copy()
    img = Image.fromarray(arr.astype(np.uint8))
    d = ImageDraw.Draw(img)

    def px(lane_x: float, depth: float):
        """Punkt auf dem Boden: lane_x in Straßenbreiten (0 = Mitte), depth 0 = vorn, 1 = Horizont."""
        s = (1 - depth) ** 2.2
        return vx + lane_x * w * 0.55 * s, vy + (h - vy) * s

    # Häuserzeilen links und rechts (von hinten nach vorn zeichnen)
    for side in (-1, 1):
        depths = np.linspace(0.97, 0.0, 14)
        for i, dep in enumerate(depths):
            nxt = max(dep - 0.07, -0.05)
            x0, y0 = px(side * 1.15, dep)
            x1, y1 = px(side * 1.15, nxt)
            s0 = (1 - dep) ** 2.2
            s1 = (1 - nxt) ** 2.2
            tall = (0.9 + 0.8 * rng.random()) * h * 0.55
            col = CANDY[(i * 3 + (side > 0)) % len(CANDY)]
            top0, top1 = y0 - tall * s0, y1 - tall * s1
            outer = side * w * 2
            d.polygon([(x0, y0), (x1, y1), (x1, top1), (x0, top0)], fill=lerp(col, (255, 255, 255), 0.1))
            # Fensterreihen
            for k in range(1, 6):
                f = k / 6
                ya, yb = y0 - (y0 - top0) * f, y1 - (y1 - top1) * f
                d.line([(x0, ya), (x1, yb)], fill=lerp(col, (40, 30, 60), 0.35), width=max(1, int(4 * s1)))
            d.polygon([(x0, top0), (x1, top1), (x1 + outer, top1), (x0 + outer, top0)],
                      fill=lerp(col, (20, 20, 40), 0.2))

    # Straße
    l0, l1 = px(-1.15, 0), px(1.15, 0)
    d.polygon([px(-1.15, 1), px(1.15, 1), (l1[0], h + 2), (l0[0], h + 2)], fill=(122, 82, 168))
    # Bordsteine
    for side in (-1, 1):
        d.polygon([px(side * 1.15, 1), px(side * 1.05, 1), px(side * 1.05, -0.05), px(side * 1.15, -0.05)],
                  fill=MUSTARD)
    # Schwellen und Schienen je Spur
    for lane in (-0.68, 0.0, 0.68):
        for k in range(40):
            dep = 1 - (k / 40) ** 0.6
            a, b = px(lane - 0.22, dep), px(lane + 0.22, dep)
            th = max(1, int(10 * (1 - dep) ** 2.2))
            d.line([a, b], fill=(120, 74, 52), width=th)
        for r in (-0.14, 0.14):
            d.line([px(lane + r, 0.999), px(lane + r, -0.05)], fill=(225, 230, 240),
                   width=max(2, int(w * 0.006)))

    # Zwiebelringe über der mittleren und rechten Spur
    glow = Image.new("RGB", (w, h), 0)
    gd = ImageDraw.Draw(glow)
    for lane, start in ((0.0, 0.15), (0.68, 0.45)):
        for k in range(6):
            dep = start + k * 0.06
            cx, cy = px(lane, dep)
            s = (1 - dep) ** 2.2
            r = min(w, h) * 0.05 * s
            cy -= r * 2.4
            box = [cx - r, cy - r * 0.8, cx + r, cy + r * 0.8]
            for g in (d, gd):
                g.ellipse(box, outline=MUSTARD, width=max(2, int(r * 0.35)))
    halo = glow.filter(ImageFilter.GaussianBlur(w * 0.012))
    a = np.asarray(img, np.float32) + np.asarray(halo, np.float32) * 0.8
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def finish(img: Image.Image) -> Image.Image:
    a = np.asarray(img, np.float32)
    h, w, _ = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    v = 1 - 0.35 * (((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) ** 1.5
    a = a * np.clip(v, 0.55, 1)[..., None]
    # etwas Sättigung oben drauf
    grey = a.mean(axis=2, keepdims=True)
    a = grey + (a - grey) * 1.15
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def outlined(d: ImageDraw.ImageDraw, xy, text, font, fill):
    x, y = xy
    d.text((x + 6, y + 7), text, font=font, fill=(30, 18, 40))
    d.text(xy, text, font=font, fill=fill, stroke_width=4, stroke_fill=(30, 18, 40))


def main() -> None:
    font_path = sys.argv[1]
    OUT.mkdir(exist_ok=True)

    hero = finish(scene(1920, 620, horizon=0.40))
    hero.save(OUT / "hackepeter-hero.png", optimize=True)

    cover = finish(scene(600, 800, horizon=0.52))
    d = ImageDraw.Draw(cover)
    big = ImageFont.truetype(font_path, 104)
    small = ImageFont.truetype(font_path, 28)
    outlined(d, (40, 40), "HACKE", big, METT)
    outlined(d, (40, 150), "PETER", big, MUSTARD)
    d.text((44, 272), "DIE METTBRÖTCHEN-FLUCHT", font=small, fill=(255, 255, 255),
           stroke_width=3, stroke_fill=(30, 18, 40))
    cover.save(OUT / "hackepeter.png", optimize=True)
    print("geschrieben:", OUT / "hackepeter.png", OUT / "hackepeter-hero.png")


if __name__ == "__main__":
    main()
