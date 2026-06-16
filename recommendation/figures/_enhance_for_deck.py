"""One-time figure enhancement for the executive deck (non-destructive: writes new *_hc / *_nolegend files).
- Wafer maps: lift the pale disk to a clear mid-tone and make defect markers bold so patterns read at a glance.
- Trend panels: crop off the right-side legend (which contains a duplicate RCP_X2 label) so only the clean scatter remains.
Run from the figures/ directory: python _enhance_for_deck.py
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))

WAFERS = [
    "wafer_center_scratch.png",
    "wafer_edge_top_scratch.png",
]
TRENDS = [
    "trend_normal.png", "trend_mean_shift.png", "trend_standard_deviation.png",
    "trend_spike.png", "trend_drift.png", "trend_context.png",
]


def enhance_wafer(name):
    src = os.path.join(HERE, name)
    im = Image.open(src).convert("RGB")
    # downscale to a deck-appropriate size with NEAREST so we do NOT introduce green/purple
    # antialiasing fringes that would be mistaken for defects.
    if max(im.size) > 1600:
        im = im.resize((1600, 1600), Image.NEAREST)
    a = np.asarray(im).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = (0.299 * r + 0.587 * g + 0.114 * b)

    out = a.copy()

    # Color-based segmentation (the page bg is pale BLUE [~220,238,255], the disk is pale
    # neutral grey, defects are GREEN or PURPLE specks). Use channel-dominance with a strict
    # threshold: disk/grid antialiasing has green-dominance <=6, true defects reach 60-80.
    gdom = g - np.maximum(r, b)        # green dominance
    pdom = np.minimum(r, b) - g        # purple dominance (r&b both above g)
    defect = (gdom > 12) | ((pdom > 10) & (b > g + 8))
    page_bg = (b > r + 14) & (lum > 215) & (~defect)                      # pale-blue outside disk
    disk = (~defect) & (~page_bg)                                          # everything else = disk

    # 1) page background -> clean white
    out[page_bg] = 255.0

    # 2) disk -> clear mid blue-grey band so it separates from the white page
    target = np.clip((lum - 150) / (255 - 150), 0, 1)   # 0=darker, 1=brighter
    out[..., 0] = np.where(disk, 150 + target * 70, out[..., 0])   # 150..220
    out[..., 1] = np.where(disk, 168 + target * 67, out[..., 1])   # 168..235
    out[..., 2] = np.where(disk, 190 + target * 60, out[..., 2])   # 190..250 (cool tint)

    # 3) Failbit maps have sparse failing cells scattered across the whole disk; the *pattern*
    #    of interest is where defect cells are DENSE. Compute a local density and only paint
    #    dense regions bold red, so isolated background specks don't create a speckle storm.
    d = defect.astype(np.float32)
    # box-blur density via cumulative-sum integral image, window K
    K = 9
    pad = np.pad(d, ((1, 0), (1, 0)))
    ii = pad.cumsum(0).cumsum(1)
    H, W = d.shape
    ys = np.arange(H)
    xs = np.arange(W)
    y0 = np.clip(ys - K, 0, H); y1 = np.clip(ys + K + 1, 0, H)
    x0 = np.clip(xs - K, 0, W); x1 = np.clip(xs + K + 1, 0, W)
    Y0, X0 = np.meshgrid(y0, x0, indexing="ij")
    Y1, X1 = np.meshgrid(y1, x1, indexing="ij")
    area = (Y1 - Y0) * (X1 - X0)
    dens = (ii[Y1, X1] - ii[Y0, X1] - ii[Y1, X0] + ii[Y0, X0]) / np.maximum(area, 1)
    dense_region = dens > 0.075         # >7.5% of the local window are defect cells = real cluster
    # paint dense cluster bold red (dilate a couple px for a solid, legible blob without speckle)
    dr = dense_region.astype(np.float32)
    for _ in range(2):
        src = dr.copy()
        for sh in (1, -1):
            dr = np.maximum(dr, np.roll(src, sh, axis=0))
            dr = np.maximum(dr, np.roll(src, sh, axis=1))
    cluster = (dr > 0.5)
    out[..., 0] = np.where(cluster, 206.0, out[..., 0])
    out[..., 1] = np.where(cluster, 38.0, out[..., 1])
    out[..., 2] = np.where(cluster, 38.0, out[..., 2])
    # isolated (non-clustered) defect specks: fold them back into the disk tone so they vanish
    stray = defect & (~cluster)
    out[..., 0] = np.where(stray, 188.0, out[..., 0])
    out[..., 1] = np.where(stray, 203.0, out[..., 1])
    out[..., 2] = np.where(stray, 222.0, out[..., 2])

    # 3b) suppress the small grey/white micro-label boxes (the "xx" tags on the disk). They are
    #     near-neutral (low saturation) white-filled rects with a thin grey border + tiny text.
    #     Detect a LOCAL DENSITY of near-neutral pixels and repaint that whole window to disk tone
    #     so the entire box (interior + border + text) vanishes, not just the dark outline.
    sat = np.max(a, axis=-1) - np.min(a, axis=-1)
    neutral = disk & (sat < 16)                 # disk itself is cool-tinted (sat ~45+)
    nd = neutral.astype(np.float32)
    Kl = 14
    padl = np.pad(nd, ((1, 0), (1, 0)))
    iil = padl.cumsum(0).cumsum(1)
    yl0 = np.clip(ys - Kl, 0, H); yl1 = np.clip(ys + Kl + 1, 0, H)
    xl0 = np.clip(xs - Kl, 0, W); xl1 = np.clip(xs + Kl + 1, 0, W)
    YL0, XL0 = np.meshgrid(yl0, xl0, indexing="ij")
    YL1, XL1 = np.meshgrid(yl1, xl1, indexing="ij")
    areal = (YL1 - YL0) * (XL1 - XL0)
    densl = (iil[YL1, XL1] - iil[YL0, XL1] - iil[YL1, XL0] + iil[YL0, XL0]) / np.maximum(areal, 1)
    label_box = (densl > 0.18) & (~cluster)     # dense neutral patch = a label box
    # dilate to fully cover the box footprint
    lb = label_box.astype(np.float32)
    for _ in range(2):
        srcl = lb.copy()
        for sh in (1, -1):
            lb = np.maximum(lb, np.roll(srcl, sh, axis=0))
            lb = np.maximum(lb, np.roll(srcl, sh, axis=1))
    label_box = (lb > 0.5) & (~cluster)
    out[..., 0] = np.where(label_box, 188.0, out[..., 0])
    out[..., 1] = np.where(label_box, 203.0, out[..., 1])
    out[..., 2] = np.where(label_box, 222.0, out[..., 2])

    out = np.clip(out, 0, 255).astype(np.uint8)

    # 4) trim the white corner margin (the octagonal disk leaves white triangles in the 4
    #    corners). A modest uniform inset removes that dead margin so the disk + defect
    #    cluster fill the panel and read larger, while keeping edge-located clusters intact.
    H0, W0 = out.shape[:2]
    inset = int(0.035 * min(H0, W0))
    out = out[inset:H0 - inset, inset:W0 - inset]

    dst = os.path.join(HERE, name.replace(".png", "_hc.png"))
    Image.fromarray(out).save(dst)
    print("wafer ->", os.path.basename(dst), Image.open(dst).size)


def crop_trend(name):
    src = os.path.join(HERE, name)
    im = Image.open(src).convert("RGB")
    W, H = im.size
    # The scatter plot area ends ~x=0.78W; the right-side legend block (which exposes raw internal
    # column names RCP_X1..RCP_X6) sits at ~x=0.80..0.90W. Cut at 0.795W to drop the ENTIRE legend
    # while keeping the full scatter + y-axis (earlier 0.855 left legend swatches visible).
    cut = int(W * 0.795)
    im2 = im.crop((0, 0, cut, H))
    # Also blank the top raw chart title strip ("DEV_E / S01 / OVL2") so no internal device/recipe
    # identifiers leak onto an executive slide. Paint the title band white.
    a = np.asarray(im2).astype(np.uint8).copy()
    title_h = int(H * 0.065)
    a[:title_h, :, :] = 255
    dst = os.path.join(HERE, name.replace(".png", "_nolegend.png"))
    Image.fromarray(a).save(dst)
    print("trend ->", os.path.basename(dst), (a.shape[1], a.shape[0]))


if __name__ == "__main__":
    for w in WAFERS:
        enhance_wafer(w)
    for t in TRENDS:
        crop_trend(t)
    print("done")
