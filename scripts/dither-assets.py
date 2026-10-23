#!/usr/bin/env python3
"""Pre-generate the dithered assets used by static/dither/dither.js and dither.css.

Run by hand after adding images to a post (not part of `zola build`):
    python3 scripts/dither-assets.py
Needs Pillow and numpy. Writes into static/dither/:
  images/...           Bayer 4x4 copy of every raster image a post references
                       (black, #202020, signal green #78e772)
  manifest.json        original path -> dithered path + original size
  banner.png           halftone dot banner (signal green on black)
  rule.png             dithered section marker
"""
import json, re, pathlib
import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "dither"
PALETTE = ["#000000", "#202020", "#78e772"]
GREEN = (0x78, 0xE7, 0x72)
LUMA = np.array([0.2126, 0.7152, 0.0722])
MAX_W = 800


def bayer(n):
    m = np.array([[0, 2], [3, 1]])
    while m.shape[0] < n:
        m = np.block([[4 * m, 4 * m + 2], [4 * m + 3, 4 * m + 1]])
    return (m + 0.5) / m.size


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def save_png(arr, path, colours):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr).quantize(colors=colours, dither=Image.Dither.NONE).save(path, optimize=True)


def ordered(src, dst, gamma=0.8):
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
    im = Image.alpha_composite(bg, im).convert("RGB")
    w = min(MAX_W, im.width)
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    img = np.asarray(im, np.float32) / 255.0
    cols = np.array([rgb(c) for c in PALETTE], np.float32)
    lum = (cols / 255.0) @ LUMA
    h, w, _ = img.shape
    t = np.tile(bayer(4), (h // 4 + 1, w // 4 + 1))[:h, :w]
    idx = np.interp((img @ LUMA) ** gamma, lum, np.arange(len(lum)))
    base = np.floor(idx).clip(0, len(lum) - 2)
    out = (base + ((idx - base) > t)).astype(int)
    save_png(cols[out].astype(np.uint8), dst, len(PALETTE))


def halftone(src, dst, width=1024, height=360, cell=8, gamma=0.85):
    im = Image.open(src).convert("RGB")
    s = max(width / im.width, height / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0 = round((im.width - width) * 0.6); y0 = round((im.height - height) * 0.45)
    L = (np.asarray(im.crop((x0, y0, x0 + width, y0 + height)), np.float32) / 255.0 @ LUMA) ** gamma
    out = np.zeros((height, width, 3), np.uint8)
    yy, xx = np.mgrid[0:cell, 0:cell] + 0.5
    dist = np.hypot(xx - cell / 2, yy - cell / 2)
    for cy in range(0, height, cell):
        for cx in range(0, width, cell):
            blk = L[cy:cy + cell, cx:cx + cell]
            mask = dist[:blk.shape[0], :blk.shape[1]] <= np.sqrt(blk.mean()) * cell * 0.72
            out[cy:cy + cell, cx:cx + cell][mask] = GREEN
    save_png(out, dst, 2)


def rule(dst, w=512, h=6):
    t = np.tile(bayer(8), (1, w // 8))[:h, :w]
    on = np.tile(np.linspace(1, 0, w) ** 1.6, (h, 1)) > t
    out = np.zeros((h, w, 3), np.uint8); out[on] = GREEN
    save_png(out, dst, 2)


def main():
    refs = set()
    for md in (ROOT / "content").rglob("*.md"):
        body = md.read_text().split("+++", 2)[-1]  # body only; heroes are not figures
        refs |= set(re.findall(r'(/images/[^\s)"\']+\.(?:png|jpe?g|webp))', body))
    manifest = {}
    for ref in sorted(refs):
        src = ROOT / "static" / ref.lstrip("/")
        if not src.exists():
            continue
        dst_rel = "/dither" + ref.rsplit(".", 1)[0] + ".png"
        ordered(src, ROOT / "static" / dst_rel.lstrip("/"))
        with Image.open(src) as im:
            manifest[ref] = {"src": dst_rel, "w": im.width, "h": im.height}
        print(ref, "->", dst_rel)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    halftone(ROOT / "themes/ampersand/static/images/kiln-landscape.webp", OUT / "banner.png")
    rule(OUT / "rule.png")


if __name__ == "__main__":
    main()
