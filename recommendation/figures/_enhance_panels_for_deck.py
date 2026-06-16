"""Enhance composite multi-panel figures for the executive deck (non-destructive: writes *_hc.png).

Problem: in object_id_evolution_panel.png the raw-wafer sub-panels (a)/(c) render as faint pale-grey
specks on a near-white disk, so the defect pattern is essentially invisible on a projector. The
identity-map sub-panels (b)/(d) already have vivid red/green/purple clusters and must be preserved.

Approach (per-pixel, color-preserving):
  - near-white page background  -> clean white
  - pale neutral disk           -> clear mid blue-grey band (so the disk reads as a wafer, not page)
  - faint grey defect specks     -> darken to a strong slate so the cluster pattern pops
  - saturated marks (red/green/purple) -> kept (even slightly boosted) so (b)/(d) stay intact
Run from figures/: python _enhance_panels_for_deck.py
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PANELS = ["object_id_evolution_panel.png"]


def enhance_cascade(name="roi_yolo_cascade_panel.png"):
    """3-panel cascade figure: the left two are faint wafer maps (lift like object_id),
    the right panel has a harsh saturated-red frame -> recolor that frame to a neutral grey
    so the three panels share a calm, consistent framing."""
    src = os.path.join(HERE, name)
    a = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
    H, W, _ = a.shape
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    sat = np.max(a, axis=-1) - np.min(a, axis=-1)
    out = a.copy()

    colored = sat > 40
    # lift the pale disk in the faint wafer panels (left ~2/3) to a clear cool band
    left = np.zeros((H, W), bool); left[:, : (2 * W) // 3] = True
    disk = left & (lum > 196) & (lum <= 236) & (sat < 22) & (~colored)
    t = np.clip((lum - 196) / (236 - 196), 0, 1)
    out[..., 0] = np.where(disk, 168 + t * 55, out[..., 0])
    out[..., 1] = np.where(disk, 184 + t * 52, out[..., 1])
    out[..., 2] = np.where(disk, 206 + t * 44, out[..., 2])
    # darken faint grey specks (real defect cells) in the left panels
    speck = left & (lum <= 196) & (sat < 40) & (~colored) & (~disk)
    speck_strong = speck & (lum <= 170)
    out[..., 0] = np.where(speck_strong, 40.0, out[..., 0])
    out[..., 1] = np.where(speck_strong, 58.0, out[..., 1])
    out[..., 2] = np.where(speck_strong, 100.0, out[..., 2])

    # neutralize the third panel's harsh red frame -> soft slate-grey border
    red_frame = (r > 150) & (g < 95) & (b < 95)
    right = np.zeros((H, W), bool); right[:, (2 * W) // 3:] = True
    red_frame = red_frame & right
    out[..., 0] = np.where(red_frame, 120.0, out[..., 0])
    out[..., 1] = np.where(red_frame, 132.0, out[..., 1])
    out[..., 2] = np.where(red_frame, 150.0, out[..., 2])

    out = np.clip(out, 0, 255).astype(np.uint8)
    dst = os.path.join(HERE, name.replace(".png", "_hc.png"))
    Image.fromarray(out).save(dst)
    print("cascade ->", os.path.basename(dst), Image.open(dst).size)


def enhance_panel(name):
    src = os.path.join(HERE, name)
    a = np.asarray(Image.open(src).convert("RGB")).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    sat = np.max(a, axis=-1) - np.min(a, axis=-1)

    out = a.copy()

    # saturated colored marks (defect clusters in id-maps + green outliers) -> keep as-is
    colored = sat > 40

    # near-white page background (very bright, low saturation) -> pure white
    page_bg = (lum > 232) & (sat < 18) & (~colored)
    out[page_bg] = 255.0

    # pale neutral disk: bright-ish, low saturation, not page, not colored
    disk = (lum > 196) & (lum <= 232) & (sat < 22) & (~colored) & (~page_bg)
    # lift disk to a cool mid blue-grey band so it clearly separates from the white page
    t = np.clip((lum - 196) / (232 - 196), 0, 1)   # 0=darker disk, 1=lighter disk
    out[..., 0] = np.where(disk, 168 + t * 55, out[..., 0])   # 168..223
    out[..., 1] = np.where(disk, 184 + t * 52, out[..., 1])   # 184..236
    out[..., 2] = np.where(disk, 206 + t * 44, out[..., 2])   # 206..250 (cool tint)

    # faint grey defect specks (darker than disk, still low saturation) -> strong slate.
    # Split by darkness: the true cell marks are clearly darker (lum<=170) and become a bold
    # navy; the faint grid hairlines (170<lum<=196) only get a soft mid tone so they don't
    # turn into a speckle storm that competes with the real cluster.
    speck_strong = (lum <= 170) & (sat < 40) & (~colored)
    speck_soft = (lum > 170) & (lum <= 196) & (sat < 40) & (~colored)
    out[..., 0] = np.where(speck_strong, 40.0, out[..., 0])
    out[..., 1] = np.where(speck_strong, 58.0, out[..., 1])
    out[..., 2] = np.where(speck_strong, 100.0, out[..., 2])
    out[..., 0] = np.where(speck_soft, 150.0, out[..., 0])
    out[..., 1] = np.where(speck_soft, 168.0, out[..., 1])
    out[..., 2] = np.where(speck_soft, 198.0, out[..., 2])

    out = np.clip(out, 0, 255).astype(np.uint8)
    dst = os.path.join(HERE, name.replace(".png", "_hc.png"))
    Image.fromarray(out).save(dst)
    print("panel ->", os.path.basename(dst), Image.open(dst).size)


if __name__ == "__main__":
    for p in PANELS:
        enhance_panel(p)
    enhance_cascade()
    print("done")
