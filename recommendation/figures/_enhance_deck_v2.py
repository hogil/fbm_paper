"""Deck image fixes v2 (non-destructive; writes new *_v2 / split panel PNGs).

Targets the design-review findings:
- slide 10 (roi_yolo_cascade): 3 panels split into uniform square tiles on a light-grey tint,
  faint wafer specks darkened, the harsh red frame of panel (c) neutralised. Each tile is a
  standalone square so the deck can lay them out at equal size with individual (a)/(b)/(c) labels.
- slide 11 (object_id_evolution): 4 panels split into uniform square tiles, faint pale panels
  lifted onto a light-grey tint so the white-dot panels read as wafers (not blank boxes).
- slide 22 (trend_*_nolegend): crop the wide left/bottom axis-label margins so the scatter fills
  more of the frame (bigger dots on the projector); keep the dashed split + red anomaly dots.

Run from figures/: python _enhance_deck_v2.py
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TINT = (228, 233, 242)   # light cool-grey tile background (separates faint panels from white page)


def _square_pad(im, bg):
    """Pad a panel to a square on the given bg colour (centred)."""
    w, h = im.size
    s = max(w, h)
    canvas = Image.new("RGB", (s, s), bg)
    canvas.paste(im, ((s - w) // 2, (s - h) // 2))
    return canvas


def _lift_faint(a):
    """Per-pixel: near-white page->tint, pale disk->cool band, faint specks->bold slate,
    saturated marks kept. Returns uint8 array."""
    a = a.astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    sat = np.max(a, axis=-1) - np.min(a, axis=-1)
    out = a.copy()
    colored = sat > 40
    page_bg = (lum > 234) & (sat < 18) & (~colored)
    out[page_bg] = TINT
    # disk = the bright wafer body (lum 210..234) -> cool light band
    disk = (lum > 210) & (lum <= 234) & (sat < 22) & (~colored) & (~page_bg)
    t = np.clip((lum - 210) / (234 - 210), 0, 1)
    out[..., 0] = np.where(disk, 198 + t * 30, out[..., 0])
    out[..., 1] = np.where(disk, 208 + t * 26, out[..., 1])
    out[..., 2] = np.where(disk, 222 + t * 20, out[..., 2])
    # real defect cells render at lum ~185..210 (darker than disk): make them a bold navy speck.
    speck_strong = (lum <= 200) & (sat < 40) & (~colored)
    speck_soft = (lum > 200) & (lum <= 210) & (sat < 40) & (~colored)
    out[..., 0] = np.where(speck_strong, 33.0, out[..., 0])
    out[..., 1] = np.where(speck_strong, 50.0, out[..., 1])
    out[..., 2] = np.where(speck_strong, 110.0, out[..., 2])
    out[..., 0] = np.where(speck_soft, 120.0, out[..., 0])
    out[..., 1] = np.where(speck_soft, 142.0, out[..., 1])
    out[..., 2] = np.where(speck_soft, 184.0, out[..., 2])
    return np.clip(out, 0, 255).astype(np.uint8)


def split_object_id():
    src = os.path.join(HERE, "object_id_evolution_panel.png")
    a = np.asarray(Image.open(src).convert("RGB"))
    bounds = [(18, 379), (396, 599), (774, 1135), (1152, 1366)]  # a,b,c,d columns
    names = ["object_id_a", "object_id_b", "object_id_c", "object_id_d"]
    for (x0, x1), nm in zip(bounds, names):
        panel = a[:, x0:x1]
        panel = _lift_faint(panel)
        im = _square_pad(Image.fromarray(panel), TINT)
        dst = os.path.join(HERE, nm + "_v2.png")
        im.save(dst)
        print("object_id ->", os.path.basename(dst), im.size)


def split_cascade():
    src = os.path.join(HERE, "roi_yolo_cascade_panel.png")
    a = np.asarray(Image.open(src).convert("RGB"))
    bounds = [(22, 642), (664, 1284), (1306, 1926)]  # a,b,c
    names = ["cascade_a", "cascade_b", "cascade_c"]
    for idx, ((x0, x1), nm) in enumerate(zip(bounds, names)):
        panel = a[:, x0:x1].astype(np.float32)
        r, g, b = panel[..., 0], panel[..., 1], panel[..., 2]
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        sat = np.max(panel, axis=-1) - np.min(panel, axis=-1)
        if idx < 2:
            panel = _lift_faint(panel)
        else:
            # panel (c): neutralise the harsh saturated-red border -> soft slate,
            # then lift the near-white page background to the same tint for consistent framing.
            out = panel.copy()
            red_frame = (r > 150) & (g < 100) & (b < 100)
            out[..., 0] = np.where(red_frame, 120.0, out[..., 0])
            out[..., 1] = np.where(red_frame, 132.0, out[..., 1])
            out[..., 2] = np.where(red_frame, 150.0, out[..., 2])
            page_bg = (lum > 234) & (sat < 16)
            for k, c in enumerate(TINT):
                out[..., k] = np.where(page_bg, float(c), out[..., k])
            panel = np.clip(out, 0, 255).astype(np.uint8)
        im = _square_pad(Image.fromarray(panel), TINT)
        dst = os.path.join(HERE, nm + "_v2.png")
        im.save(dst)
        print("cascade ->", os.path.basename(dst), im.size)


def crop_trends():
    """Crop the left y-label/tick margin and bottom x-label margin from each trend chart so the
    scatter region fills more of the tile (larger dots on a projector). Measured on 834x675."""
    names = ["normal", "mean_shift", "standard_deviation", "spike", "drift", "context"]
    # plot area on the 834x675 figure: left ~92px (y ticks+label), bottom ~84px (x ticks+label),
    # top ~14px, right ~10px. Crop to the inked plot box with a small pad.
    L, T, R, B = 78, 8, 826, 600
    for nm in names:
        src = os.path.join(HERE, f"trend_{nm}_nolegend.png")
        im = Image.open(src).convert("RGB")
        im2 = im.crop((L, T, R, B))
        dst = os.path.join(HERE, f"trend_{nm}_v2.png")
        im2.save(dst)
        print("trend ->", os.path.basename(dst), im2.size)


if __name__ == "__main__":
    split_object_id()
    split_cascade()
    crop_trends()
    print("done")
