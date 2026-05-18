"""Generate FCM-PM demo chips that match the per-class 50 group2 SOTA recipe.

Reference: `D:/project/known-cnn/chip_multilabel/_train_chip_variant.py:1131-1224`
(`cutmix_mode == "complement"`). iter26F (group2 SOTA at per-class 50) = BASE19C
with white-fill: complement mode + GRID=8 + n_groups=2 + pair=masked + label=1.0.

For a pair (anchor, partner) and one random partition of GRID×GRID cells into
groups G0 / G1, complement produces:
  mix_i   = partner base + anchor cells of group_i overlaid     (label = anchor ∪ partner)
  mask_i  = mix_i with the OTHER group cells white-filled       (label = anchor only)

To show both A-only and B-only masks at independent cell positions, we call
complement twice:
  - run 1: anchor=A, partner=B, partition P_A → use mix_0 + mask_0
  - run 2: anchor=B, partner=A, partition P_B (independent) → use mix_0 + mask_0

Outputs (1 row × 6 cols panel):
  chip A | chip B | FCM mixed (A label set) | FCM mixed (B label set)
        | Pair Mask (A-only)               | Pair Mask (B-only)
"""

from __future__ import annotations
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FIGURES = Path(r"D:/project/fbm_paper/recommendation/figures")
SEED = 20260518
GRID = 8           # iter26F default
N_GROUPS = 2       # group2 SOTA
WHITE = np.array([255, 255, 255], dtype=np.uint8)

CHIP_A = FIGURES / "chip_eval_scratch_selected.png"
CHIP_B = FIGURES / "chip_eval_scratch_rot_selected.png"

OUT_A = FIGURES / "fcm_pm_step_a.png"
OUT_B = FIGURES / "fcm_pm_step_b.png"
OUT_MIXED_A = FIGURES / "fcm_pm_step_mixed_a.png"
OUT_MIXED_B = FIGURES / "fcm_pm_step_mixed_b.png"
OUT_MASKED_A = FIGURES / "fcm_pm_step_masked_a.png"
OUT_MASKED_B = FIGURES / "fcm_pm_step_masked_b.png"
OUT_PANEL = FIGURES / "fcm_pm_panel.png"


def load_rgb(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.uint8).copy()


def save_rgb(path: Path, arr: np.ndarray) -> None:
    Image.fromarray(arr, "RGB").save(path)


def cell_rect(idx: int, grid: int, H: int, W: int) -> tuple[int, int, int, int]:
    gi = idx // grid
    gj = idx % grid
    ch = H // grid
    cw = W // grid
    y0 = gi * ch
    y1 = (gi + 1) * ch if gi < grid - 1 else H
    x0 = gj * cw
    x1 = (gj + 1) * cw if gj < grid - 1 else W
    return y0, y1, x0, x1


def complement_one_side(anchor: np.ndarray, partner: np.ndarray, grid: int, n_groups: int,
                         rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Run complement mode for a single anchor and return (mix_0, mask_0).

    mix_0  = partner base + anchor's group-0 cells overlaid  (label = anchor ∪ partner)
    mask_0 = mix_0 with group-1+ cells white-filled          (label = anchor only)
    """
    H, W = anchor.shape[:2]
    n_cells = grid * grid
    cells_per_group = n_cells // n_groups
    perm = rng.permutation(n_cells)
    groups = [perm[i * cells_per_group:(i + 1) * cells_per_group].tolist()
              for i in range(n_groups)]
    leftover = perm[cells_per_group * n_groups:].tolist()
    if leftover:
        groups[-1].extend(leftover)

    mix = partner.copy()
    for ci in groups[0]:
        y0, y1, x0, x1 = cell_rect(int(ci), grid, H, W)
        mix[y0:y1, x0:x1] = anchor[y0:y1, x0:x1]

    mask = mix.copy()
    for j in range(1, n_groups):
        for ci in groups[j]:
            y0, y1, x0, x1 = cell_rect(int(ci), grid, H, W)
            mask[y0:y1, x0:x1] = WHITE
    return mix, mask


def label_panel(img: np.ndarray, text: str) -> np.ndarray:
    H, W = img.shape[:2]
    pad = 30
    canvas = np.full((H + pad, W, 3), 255, dtype=np.uint8)
    canvas[pad:, :, :] = img
    pil = Image.fromarray(canvas, "RGB")
    draw = ImageDraw.Draw(pil)
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except OSError:
        font = ImageFont.load_default()
    draw.text((6, 6), text, fill=(0, 0, 0), font=font)
    return np.asarray(pil, dtype=np.uint8)


def main() -> None:
    rng = np.random.default_rng(SEED)
    a = load_rgb(CHIP_A)
    b = load_rgb(CHIP_B)
    assert a.shape == b.shape, f"shape mismatch: {a.shape} vs {b.shape}"

    mixed_a, masked_a = complement_one_side(a, b, GRID, N_GROUPS, rng)
    mixed_b, masked_b = complement_one_side(b, a, GRID, N_GROUPS, rng)

    save_rgb(OUT_A, a)
    save_rgb(OUT_B, b)
    save_rgb(OUT_MIXED_A, mixed_a)
    save_rgb(OUT_MIXED_B, mixed_b)
    save_rgb(OUT_MASKED_A, masked_a)
    save_rgb(OUT_MASKED_B, masked_b)

    strip = [
        label_panel(a, "A: scratch"),
        label_panel(b, "B: scratch_rot"),
        label_panel(mixed_a, "FCM mixed (A label)"),
        label_panel(mixed_b, "FCM mixed (B label)"),
        label_panel(masked_a, "Pair Mask (A-only)"),
        label_panel(masked_b, "Pair Mask (B-only)"),
    ]
    H, W = strip[0].shape[:2]
    gap = 8
    panel = np.full((H, W * 6 + gap * 5, 3), 255, dtype=np.uint8)
    for i, p in enumerate(strip):
        x0 = i * (W + gap)
        panel[:, x0:x0 + W] = p
    save_rgb(OUT_PANEL, panel)

    print(f"GRID={GRID} N_GROUPS={N_GROUPS} pair_fill=white (iter26F group2 SOTA, per-class 50)")
    print(f"wrote: a, b, mixed_a, mixed_b, masked_a, masked_b, panel ({OUT_PANEL.name})")


if __name__ == "__main__":
    main()
