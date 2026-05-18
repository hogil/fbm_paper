"""Generate FCM-PM demo chips with complementary partition (group of 2).

User intent: chip 을 격자 P / ~P 두 그룹 (complementary) 으로 나누고,
한쪽 group 멤버가 P 를 차지하면 다른 group 멤버는 ~P (남은 그리드) 를 차지하게
한다. 두 mixed chip 의 같은 chip pixel 을 합치면 원본 chip 이 복원된다.

배치:
- mixed_A (label A ∪ B): A at P, B at ~P  (A 의 선택 그리드 = P)
- mixed_B (label A ∪ B): A at ~P, B at P  (A 의 선택 그리드 = ~P, complementary)
  -> A 측 cell coverage: mixed_A 의 P + mixed_B 의 ~P = full A
  -> B 측 cell coverage: mixed_A 의 ~P + mixed_B 의 P = full B

- masked_A (label A only): A at P, ~P 흰색       (mixed_A 에서 A 부분만 추출)
- masked_B (label B only): B at ~P, P 흰색       (mixed_A 에서 B 부분만 추출)
  -> 두 mask 의 visible cell 도 P ∪ ~P = 전체 그리드, mask 위치는 서로 다름.
"""

from __future__ import annotations
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FIGURES = Path(r"D:/project/fbm_paper/recommendation/figures")
SEED = 20260518
GRID = 4
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


def fcm_pair_complementary(a: np.ndarray, b: np.ndarray, grid: int, rng: np.random.Generator):
    H, W = a.shape[:2]
    n_cells = grid * grid
    half = n_cells // 2
    perm = rng.permutation(n_cells)
    P_idx = perm[:half].tolist()
    notP_idx = perm[half:].tolist()
    P_rects = [cell_rect(int(ci), grid, H, W) for ci in P_idx]
    notP_rects = [cell_rect(int(ci), grid, H, W) for ci in notP_idx]

    # mixed_A: A at P (kept), B overlaid at ~P
    mixed_a = a.copy()
    for y0, y1, x0, x1 in notP_rects:
        mixed_a[y0:y1, x0:x1] = b[y0:y1, x0:x1]

    # mixed_B: B at P (kept), A overlaid at ~P  -> A is at ~P, B is at P
    mixed_b = b.copy()
    for y0, y1, x0, x1 in notP_rects:
        mixed_b[y0:y1, x0:x1] = a[y0:y1, x0:x1]

    # masked_A (label A-only): A at P, ~P white
    masked_a = a.copy()
    for y0, y1, x0, x1 in notP_rects:
        masked_a[y0:y1, x0:x1] = WHITE

    # masked_B (label B-only): B at ~P, P white (DIFFERENT mask position from masked_A)
    masked_b = b.copy()
    for y0, y1, x0, x1 in P_rects:
        masked_b[y0:y1, x0:x1] = WHITE

    return mixed_a, mixed_b, masked_a, masked_b


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

    mixed_a, mixed_b, masked_a, masked_b = fcm_pair_complementary(a, b, GRID, rng)

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

    print(f"GRID={GRID}  half={GRID*GRID//2}  complementary partition: P + ~P = full grid")
    print(f"wrote: a, b, mixed_a, mixed_b, masked_a, masked_b, panel ({OUT_PANEL.name})")


if __name__ == "__main__":
    main()
