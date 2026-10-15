#!/usr/bin/env python3
"""Convert INFO/Images -> images/ (WebP 640/1280/1920 + JPEG fallback), logo, favicons, OG images.

Run:  python3 -I tools/images.py
Writes images/manifest.json (slug -> variants, width, height) that tools/build.py reads.
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "INFO", "Images")
OUT = os.path.join(ROOT, "images")
OGDIR = os.path.join(OUT, "og")
os.makedirs(OGDIR, exist_ok=True)

# slug -> source file. Image 3 (bar shelf with third-party spirit brands) is deliberately not used.
IMAGES = {
    "gozo-cottage-gift-selection-shelf": "475763832_1054772220000596_2474210764009071042_n.jpg",
    "gaulos-dry-gin-grapefruit-tonic": "489788711_1108976254580192_7864180447740359330_n.jpg",
    "gozo-cottage-salami-syrah-pistachio-piccante": "490278894_1109094314568386_5080061952045013743_n.jpg",
    "gaulos-dry-gin-three-bottles": "490698992_1113632064114611_5518926073903571301_n.jpg",
    "gin-tonic-grapefruit-juniper-glass": "491047332_1112438584233959_3453917809284973448_n.jpg",
    "gaulos-dry-gin-bottle-juniper-berries": "494174282_1126468642830953_7651394165354233812_n.jpg",
    "gozo-cottage-merlot-oak-barrel": "494439099_1130164142461403_5623865717822635148_n.jpg",
    "gin-grapefruit-glasses-marble-table": "495586670_1132055618938922_2865227457990791512_n.jpg",
    "gaulos-dry-gin-teal-label-grapefruit": "498188346_1168849345259549_2779686558609874611_n.jpg",
    "gozo-sundried-tomatoes": "535105683_1229615652516251_1772757021701442558_n.jpg",
    "gozo-cottage-merlot-steel-tank": "542688393_1234883111989505_2662585883910127010_n.jpg",
    "gozo-extra-virgin-olive-oil-olives-bowl": "556965252_1260136622797487_7636679127173833108_n.jpg",
    "gozo-olive-oil-on-bread-olive-grove": "572912986_1290256653118817_6879993162524956748_n.jpg",
    "gaulos-dry-gin-gift-bottles-gold-bow": "601348646_1332814422196373_4500287804421694643_n.jpg",
    "gozo-cottage-orange-marmalade-jar": "627760286_1369139991897149_5653654794277939056_n.jpg",
    "gozo-cottage-winery-steel-tanks-green-light": "651899293_1405779064899908_3595906630583132123_n.jpg",
    "gozo-cottage-clay-amphora-wine-tasting": "668975679_1428795645931583_5802299322563372454_n.jpg",
    "gozo-cottage-sweet-tomato-paste-sundried-tomatoes": "703170411_1464369325707548_5365683364521392327_n.jpg",
    "eu-rural-development-funding-notice": "WhatsApp-Image-2023-09-27-at-12.16.27.jpeg",
    "gozo-green-olives-harvest": "olives.jpg",
}
WIDTHS = (480, 800, 1280, 1920)
manifest = {}


def load(name):
    return ImageOps.exif_transpose(Image.open(os.path.join(SRC, name))).convert("RGB")


for slug, fn in IMAGES.items():
    im = load(fn)
    w, h = im.size
    ws = [x for x in WIDTHS if x <= w] or [w]
    if w not in ws and w < WIDTHS[-1] and w > ws[-1] * 1.15:
        ws.append(w)  # keep the native width as the top step, never upscale
    variants = []
    for tw in ws:
        th = round(h * tw / w)
        r = im.resize((tw, th), Image.LANCZOS) if tw != w else im
        r.save(os.path.join(OUT, f"{slug}-{tw}.webp"), "WEBP", quality=76, method=6)
        variants.append({"w": tw, "h": th})
    fb = min(1280, w)
    fh = round(h * fb / w)
    (im.resize((fb, fh), Image.LANCZOS) if fb != w else im).save(
        os.path.join(OUT, f"{slug}.jpg"), "JPEG", quality=80, optimize=True, progressive=True
    )
    manifest[slug] = {"variants": variants, "fallback": {"w": fb, "h": fh}, "src": fn}

# ---- logo: key the light plate to transparency, crop to content ----
logo = load("Logo.jpg")
px = logo.load()
W, H = logo.size
minx, miny, maxx, maxy = W, H, 0, 0
for y in range(H):
    for x in range(W):
        if min(px[x, y]) < 170:
            minx, miny, maxx, maxy = min(minx, x), min(miny, y), max(maxx, x), max(maxy, y)
pad = 24
box = (max(minx - pad, 0), max(miny - pad, 0), min(maxx + pad, W), min(maxy + pad, H))
crop = logo.crop(box)
rgba = Image.new("RGBA", crop.size)
cp, rp = crop.load(), rgba.load()
for y in range(crop.height):
    for x in range(crop.width):
        r, g, b = cp[x, y]
        m = min(r, g, b)
        a = max(0, min(255, round((228 - m) * 255 / (228 - 60))))
        if a == 0:
            rp[x, y] = (0, 0, 0, 0)
        else:
            # un-blend from the ~white plate so edges stay clean on cream/dark
            k = a / 255
            rp[x, y] = tuple(max(0, min(255, round((c - 238 * (1 - k)) / k))) for c in (r, g, b)) + (a,)
for tw in (240, 480):
    th = round(rgba.height * tw / rgba.width)
    rgba.resize((tw, th), Image.LANCZOS).save(os.path.join(OUT, f"gozo-cottage-logo-{tw}.webp"), "WEBP", quality=80, alpha_quality=80, method=6)
    manifest.setdefault("gozo-cottage-logo", {"variants": []})["variants"].append({"w": tw, "h": th})
solid = Image.new("RGB", rgba.size, (250, 246, 238))
solid.paste(rgba, mask=rgba.split()[3])
solid.save(os.path.join(OUT, "gozo-cottage-logo.jpg"), "JPEG", quality=88)
manifest["gozo-cottage-logo"]["solid"] = {"w": solid.width, "h": solid.height}
logo_rgba = rgba

# ---- fonts for generated graphics ----
def font(size):
    for p in ("/tmp/gc/fonts/fraunces600.ttf", "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def sans(size):
    for p in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


RED, GREEN, CREAM = (160, 24, 30), (47, 74, 44), (250, 246, 238)

# ---- favicons ----
def icon(size):
    im = Image.new("RGB", (size, size), CREAM)
    d = ImageDraw.Draw(im)
    d.ellipse((size * .04, size * .04, size * .96, size * .96), fill=RED)
    f = font(int(size * .5))
    t = "GC"
    bb = d.textbbox((0, 0), t, font=f)
    d.text(((size - (bb[2] - bb[0])) / 2 - bb[0], (size - (bb[3] - bb[1])) / 2 - bb[1]), t, font=f, fill=CREAM)
    return im


icon(180).save(os.path.join(ROOT, "apple-touch-icon.png"))
icon(32).save(os.path.join(ROOT, "favicon-32.png"))
icon(512).save(os.path.join(OUT, "icon-512.png"))
icon(64).save(os.path.join(ROOT, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])

# ---- OG images 1200x630 ----
def og(name, photo_slug, focus, kicker, headline):
    base = load(IMAGES[photo_slug])
    tw, th = 1200, 630
    sc = max(tw / base.width, th / base.height)
    b = base.resize((round(base.width * sc), round(base.height * sc)), Image.LANCZOS)
    cx = int((b.width - tw) * 0.5)
    cy = int((b.height - th) * focus)
    b = b.crop((cx, cy, cx + tw, cy + th)).convert("RGBA")
    ov = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for x in range(tw):  # left-to-right dark gradient so text stays readable
        a = int(225 * max(0, 1 - x / 880) ** 1.2)
        od.line([(x, 0), (x, th)], fill=(24, 30, 20, a))
    b = Image.alpha_composite(b, ov)
    lg = logo_rgba.copy()
    lw = 300
    lg = lg.resize((lw, round(lg.height * lw / lg.width)), Image.LANCZOS)
    plate = Image.new("RGBA", (lg.width + 48, lg.height + 36), CREAM + (255,))
    plate.paste(lg, (24, 18), lg)
    b.paste(plate, (56, 52), plate)
    d = ImageDraw.Draw(b)
    d.text((60, 300), kicker.upper(), font=sans(24), fill=(235, 214, 160))
    y = 340
    for line in headline:
        d.text((60, y), line, font=font(56), fill=(255, 255, 255))
        y += 68
    d.text((60, 556), "gozocottage.com  ·  Xewkija, Gozo, Malta", font=sans(26), fill=(255, 255, 255))
    out = os.path.join(OGDIR, name)
    rgb = b.convert("RGB")
    q = 82
    while True:
        rgb.save(out, "JPEG", quality=q, optimize=True, progressive=True)
        if os.path.getsize(out) < 280_000 or q <= 50:
            break
        q -= 6


og("og-home.jpg", "gozo-olive-oil-on-bread-olive-grove", 0.55, "Genuine produce of Gozo", ["Authentic Gozitan", "Produce & Delicacies"])
og("og-privacy.jpg", "gozo-green-olives-harvest", 0.4, "Privacy Policy", ["How we handle", "your information"])
og("og-legal.jpg", "gozo-cottage-sweet-tomato-paste-sundried-tomatoes", 0.45, "Legal Notice", ["Company details &", "funding information"])

json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
print("ok", len(manifest), "entries")
for f in sorted(os.listdir(OGDIR)):
    print(f, os.path.getsize(os.path.join(OGDIR, f)) // 1024, "KB", Image.open(os.path.join(OGDIR, f)).size)
