#!/usr/bin/env python3
"""Bake the site's riso look into photos, so they match the wallpaper and the heading overprint.

This is a development tool, not part of the site (the site has no build step): run it once on a photo, review the
result, and commit the output file under assets/images/. Needs Python 3 with numpy and Pillow.

    python3 tools/riso-bake.py photo.jpg another.png --out-dir assets/images/riso
    python3 tools/riso-bake.py photo.jpg --preset duo --display-width 300

What it does (the same recipe the headings use, so photos and text read as one print):
  1. Separates the photo into three inks, cyan / magenta / yellow (the heading inks), as coverage maps.
  2. Breaks each ink up with grain: soft speckle at the same coarseness as the page's own grain, mostly shared between the
     three plates (as on a real print, where the specks line up) with a little per-plate difference so the colours fringe.
     (The site's paper texture has a regular fine mesh that prints as a halftone screen when used as an ink threshold, so by
     default it is not used; --texture mixes some of it back in.)
  3. Prints the plates slightly off-register: yellow up-left, magenta down-right, cyan in place (as on the headings).
  4. Multiplies the plates onto the paper colour (#fffdf8) like overprinted inks.

--display-width is how wide the photo is shown on the page, in CSS pixels. The grain and the misregistration are scaled to it,
so they look the same size on the page whatever the file's resolution. Check the file size afterwards: grain compresses
poorly, and a bigger photo costs load time (lower --quality, or --grain, if it matters).
"""
import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
TEXTURE = HERE.parent / "assets" / "images" / "paper-texture.webp"
PAPER = np.array([255, 253, 248], dtype=np.float32)
# the heading inks (index.html: --riso-yellow, --riso-magenta, and the overprint text ink --riso-ink)
INKS = {"cyan": (0x1A, 0x84, 0xC4), "magenta": (0xFF, 0x3D, 0x9A), "yellow": (0xFF, 0xE6, 0x00)}
PRESETS = {
    # three inks, off-register, light grain: the closest match to the heading overprint that still reads as a photo
    "overprint": dict(strength=0.95, grain=0.5, shift=2.5, contrast=1.0, gamma=1.08, saturation=1.25, cyan="#2aa5df", mode="cmy", texture=0.0, decorrelate=0.45),
    # calmer still, for busy or dark photos
    "soft": dict(strength=0.9, grain=0.32, shift=2.0, contrast=0.95, gamma=1.12, saturation=1.2, cyan="#2aa5df", mode="cmy", texture=0.0, decorrelate=0.35),
    # two inks only, the wallpaper's blue and pink: blue shadows, pink midtones
    "duo": dict(strength=0.95, grain=0.5, shift=2.5, contrast=1.0, gamma=1.0, saturation=1.0, cyan="#1a84c4", mode="duo", texture=0.0, decorrelate=0.35),
}


def rank_uniform(a):
    """Map any array to uniformly distributed values in 0..1 (so 'coverage > noise' means that fraction of the area gets ink)."""
    order = np.argsort(a.ravel(), kind="stable")
    r = np.empty(order.size, dtype=np.float32)
    r[order] = (np.arange(order.size, dtype=np.float32) + 0.5) / order.size
    return r.reshape(a.shape)


def blur(a, sigma):
    """Separable Gaussian blur on a float array (Pillow's own blur has no float mode)."""
    if sigma <= 0.05:
        return a
    r = max(1, int(np.ceil(sigma * 3)))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2).astype(np.float32)
    k /= k.sum()
    for axis in (0, 1):
        pad = [(0, 0), (0, 0)]
        pad[axis] = (r, r)
        b = np.pad(a, pad, mode="reflect")
        n = a.shape[axis]
        a = sum(k[i] * np.take(b, np.arange(i, i + n), axis=axis) for i in range(2 * r + 1)).astype(np.float32)
    return a


def load_noise(shape, px_per_css, phase, seed, texture_mix):
    """Grain in 0..1, uniformly distributed, at the photo's size.

    The site's paper texture has a regular fine mesh on top of its speckle (fine as a faint overlay, but as an ink threshold it
    prints as a halftone screen), so the mesh is blurred out and the result is mixed with synthetic speckle of the same coarseness.
    """
    h, w = shape
    speck = blur(np.random.default_rng(seed).random((h, w), dtype=np.float32), 0.75 * px_per_css)
    speck = rank_uniform(speck)
    if texture_mix <= 0:
        return speck
    tex = Image.open(TEXTURE).convert("L")
    tile_px = max(16, int(round(1126 * px_per_css)))     # the page shows the texture tile at 1126 CSS px
    t = np.asarray(tex.resize((tile_px, tile_px), Image.LANCZOS), dtype=np.float32) / 255.0
    t = np.roll(t, (int(phase[1] * tile_px), int(phase[0] * tile_px)), axis=(0, 1))
    t = np.tile(t, (h // tile_px + 2, w // tile_px + 2))[:h, :w]
    t = rank_uniform(blur(t, 1.1 * px_per_css))
    return rank_uniform((1.0 - texture_mix) * speck + texture_mix * t)


def shifted(a, dx, dy):
    """Move a 2-D array by whole pixels, repeating the edge instead of wrapping."""
    dx, dy = int(round(dx)), int(round(dy))
    if not dx and not dy:
        return a
    p = max(abs(dx), abs(dy))
    b = np.pad(a, p, mode="edge")
    h, w = a.shape
    return b[p - dy : p - dy + h, p - dx : p - dx + w]


def coverage_maps(rgb, mode, contrast, gamma):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    if mode == "duo":
        lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
        t = np.clip((lum - 0.10) / 0.82, 0.0, 1.0)                  # levels: black point 10%, white point 92%, so light areas stay paper
        cyan = (1.0 - t) ** 1.35                                     # shadows: blue
        magenta = 0.9 * np.clip(np.sin(np.pi * t), 0.0, 1.0) ** 1.4                    # midtones: pink (purple where it overlaps the blue)
        maps = {"cyan": cyan, "magenta": magenta, "yellow": np.zeros_like(lum)}
    else:
        maps = {"cyan": 1.0 - r, "magenta": 1.0 - g, "yellow": 1.0 - b}
    out = {}
    for k, v in maps.items():
        v = np.clip((v - 0.5) * contrast + 0.5, 0.0, 1.0) ** gamma     # gamma > 1 prints lighter (less ink in the midtones)
        out[k] = v.astype(np.float32)
    return out


def bake(src, dst, preset, display_width, quality, overrides):
    p = {**PRESETS[preset], **{k: v for k, v in overrides.items() if v is not None}}
    im = Image.open(src)
    if im.mode == "P" and "transparency" in im.info:    # palette PNGs with transparency
        im = im.convert("RGBA")
    alpha = im.getchannel("A") if im.mode in ("RGBA", "LA") else None
    rgb = np.asarray(im.convert("RGB"), dtype=np.float32) / 255.0
    if p["saturation"] != 1.0:                           # a little more colour in, so the three inks have something to print
        lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2])[..., None]
        rgb = np.clip(lum + (rgb - lum) * p["saturation"], 0.0, 1.0)
    h, w = rgb.shape[:2]
    css_w = display_width or w / 2.5                    # a sensible guess: photos are shown at roughly 2-3x downscale
    px_per_css = w / css_w
    shift = p["shift"] * px_per_css
    cov = coverage_maps(rgb, p["mode"], p["contrast"], p["gamma"])
    plates = {"cyan": (0, 0), "yellow": (-shift, -shift), "magenta": (shift, shift)}
    phases = {"cyan": (0.0, 0.0), "magenta": (0.37, 0.61), "yellow": (0.71, 0.23)}
    seeds = {"cyan": 11, "magenta": 23, "yellow": 37}
    out = np.tile(PAPER / 255.0, (h, w, 1)).astype(np.float32)
    shared = load_noise((h, w), px_per_css, (0.0, 0.0), 1, p["texture"])      # one grain for all three plates, as on a real print: the specks line up
    for name, (dx, dy) in plates.items():
        c = shifted(cov[name], dx, dy)
        own = load_noise((h, w), px_per_css, phases[name], seeds[name], p["texture"])
        n = rank_uniform((1.0 - p["decorrelate"]) * shared + p["decorrelate"] * own)
        # grain: the noise moves each pixel's ink coverage up or down around its tone, so midtones break up into speckle while
        # clean paper and solid ink stay mostly clean. grain=0 would be smooth tone, 1 a very rough print.
        a = np.clip(c + p["grain"] * 1.3 * (n - 0.5), 0.0, 1.0)
        hexv = p["cyan"] if name == "cyan" else None
        rgb_ink = tuple(int(hexv[i : i + 2], 16) for i in (1, 3, 5)) if hexv else INKS[name]
        ink = np.array(rgb_ink, dtype=np.float32) / 255.0
        out *= 1.0 - (a[..., None] * p["strength"]) * (1.0 - ink)   # multiply, like overprinted ink
    img = Image.fromarray(np.clip(out * 255.0 + 0.5, 0, 255).astype(np.uint8), "RGB")
    if alpha is not None:
        img.putalpha(alpha)
    dst.parent.mkdir(parents=True, exist_ok=True)
    img.save(dst, "WEBP", quality=quality, method=6)
    return dst.stat().st_size


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--out-dir", type=Path, default=Path("riso-out"), help="where the baked WebP files go (default riso-out/)")
    ap.add_argument("--preset", choices=sorted(PRESETS), default="overprint")
    ap.add_argument("--display-width", type=float, help="width the photo is shown at on the page, in CSS px (default: file width / 2.5)")
    ap.add_argument("--quality", type=int, default=80, help="WebP quality (default 80)")
    ap.add_argument("--strength", type=float, help="ink strength 0-1")
    ap.add_argument("--grain", type=float, help="grain amplitude: 0 = smooth tone, 1 = very rough")
    ap.add_argument("--shift", type=float, help="misregistration in CSS px (yellow up-left, magenta down-right)")
    ap.add_argument("--contrast", type=float, help="contrast applied to the ink maps")
    ap.add_argument("--gamma", type=float, help="above 1 prints lighter, below 1 darker")
    ap.add_argument("--saturation", type=float, help="colour boost applied before the inks are separated (1 = none)")
    ap.add_argument("--cyan", help="cyan ink as #rrggbb (the headings use #1a84c4; photos print better with the lighter #2aa5df)")
    ap.add_argument("--decorrelate", type=float, help="0-1: how much each plate's grain differs from the shared grain (0 = specks line up exactly)")
    ap.add_argument("--texture", type=float, help="0-1: how much of the grain comes from the site's paper texture (the rest is synthetic speckle)")
    a = ap.parse_args()
    if not TEXTURE.exists():
        sys.exit(f"missing {TEXTURE}")
    over = dict(strength=a.strength, grain=a.grain, shift=a.shift, contrast=a.contrast, gamma=a.gamma, saturation=a.saturation, cyan=a.cyan, texture=a.texture, decorrelate=a.decorrelate)
    for f in a.files:
        dst = a.out_dir / (f.stem + ".webp")
        size = bake(f, dst, a.preset, a.display_width, a.quality, over)
        print(f"{f} -> {dst}  ({f.stat().st_size // 1024} KB -> {size // 1024} KB)")


if __name__ == "__main__":
    main()
