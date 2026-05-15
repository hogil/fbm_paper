#!/usr/bin/env python3
"""One-shot: build raw PNG + obj-id PNG for Center_bank_boundary + Center_fork.

Steps per wafer:
  1) Read raw wafer PNG from E:/data/wm-811k/unknown/<class>/<basename>.png
  2) Stage it to D:/project/data/wm-811k/unknown/<class>/<basename>.png (PNG_ROOT for builder)
  3) Run regen_positions.process_image -> D:/project/data/positions/unknown/<class>/<basename>.json
  4) After both wafers staged, exec _build_obj_id_maps.py with --limit-per-class 1
  5) Copy raw + obj-id PNGs to D:/project/fbm_paper/recommendation/figures/
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

# ---- config ----
PAIRS = [
    ("Center_bank_boundary", "AHF571_00C_17_20260501_010000_97.6_2_PE_ENGINEER"),
    ("Center_fork", "ACJ930_00P_20_20260501_010000_97.5_2_PE_ENGINEER"),
]
SRC_PNG_ROOT = Path("E:/data/wm-811k/unknown")
STAGE_PNG_ROOT = Path("D:/project/data/wm-811k/unknown")
STAGE_JSON_ROOT = Path("D:/project/data/positions/unknown")
OBJ_OUT_ROOT = Path("D:/project/data/wm-811k/obj_id_maps")
CKPT = "D:/project/known-cnn/outputs/logs_chip/_v14_keepsafe/best_model.pth"
BUILD_SCRIPT = Path("D:/project/known-cnn/compound_train/_build_obj_id_maps.py")
REGEN_SCRIPT = Path("E:/data/regen_positions.py")
FIGURES_DIR = Path("D:/project/fbm_paper/recommendation/figures")

# ---- load regen_positions as a module ----
spec = importlib.util.spec_from_file_location("regen_positions", REGEN_SCRIPT)
regen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(regen)


def stage_and_make_json(wafer_class: str, basename: str) -> tuple[Path, Path]:
    src_png = SRC_PNG_ROOT / wafer_class / f"{basename}.png"
    if not src_png.exists():
        raise FileNotFoundError(src_png)

    dst_png = STAGE_PNG_ROOT / wafer_class / f"{basename}.png"
    dst_json = STAGE_JSON_ROOT / wafer_class / f"{basename}.json"
    dst_png.parent.mkdir(parents=True, exist_ok=True)
    dst_json.parent.mkdir(parents=True, exist_ok=True)

    if not dst_png.exists():
        shutil.copy2(src_png, dst_png)
    rel_from_images = f"unknown/{wafer_class}/{basename}.png"
    err = regen.process_image(str(dst_png), rel_from_images, str(dst_json))
    if err:
        raise RuntimeError(f"regen failed: {err}")

    # ---- patch b values ----
    # regen_positions outputs b = grade 0..7. The obj-id builder filters b >= 200.
    # _sample_gen marks defect chips with border palette indices 11..24 (border_inv,
    # border_b285/286/287/288/290/291/300/385/386/388/389/390, border_etc) and fills
    # invalid chips with palette idx 31 (white). For any chip whose 200x200 rect
    # contains those defect-marker palette indices, we overwrite b = "250" so the
    # builder picks it up. The original grade is preserved nowhere because the PNG
    # palette has lost the bin value — that's fine for our purpose (we just need
    # the chip crop fed through the classifier).
    DEFECT_BORDER_IDX = set(range(11, 25))   # border_inv..border_etc
    INVALID_FILL_IDX = 31
    arr = np.asarray(Image.open(dst_png), dtype=np.uint8)
    with open(dst_json, "r", encoding="utf-8") as f:
        j = json.load(f)
    n_patched = 0
    for c in j.get("chips", []):
        r = c.get("rect", {})
        x0, y0, x1, y1 = int(r["x0"]), int(r["y0"]), int(r["x1"]), int(r["y1"])
        tile = arr[y0:y1, x0:x1]
        has_defect = bool(np.isin(tile, list(DEFECT_BORDER_IDX)).any()) or bool((tile == INVALID_FILL_IDX).any())
        if has_defect:
            c["b"] = "250"
            n_patched += 1
    with open(dst_json, "w", encoding="utf-8") as f:
        json.dump(j, f, ensure_ascii=False, indent=2)
    print(f"  [patch] {n_patched} chips marked as defect (b=250)")
    return dst_png, dst_json


def run_builder():
    # one wafer per class via --limit-per-class 1; only our two classes
    cmd = [
        sys.executable,
        str(BUILD_SCRIPT),
        "--chip-model", CKPT,
        "--out-root", str(OBJ_OUT_ROOT),
        "--limit-per-class", "1",
        "--overwrite",
        "--batch", "32",
        "--workers", "0",
        "--save-png",
    ]
    print(">>>", " ".join(cmd), flush=True)
    p = subprocess.run(cmd, cwd=str(BUILD_SCRIPT.parent))
    if p.returncode != 0:
        raise SystemExit(f"builder failed rc={p.returncode}")


def find_obj_png(basename: str, wafer_class: str) -> Path | None:
    # subfolder is <device>_<date> from basename tokens[8]_tokens[3]; fall back to wafer_class.
    # easiest: scan obj_id_maps recursively for matching name.
    for p in OBJ_OUT_ROOT.rglob(f"{basename}.png"):
        return p
    return None


def copy_results():
    short = {
        "Center_bank_boundary": "wafer_center_bank_boundary",
        "Center_fork": "wafer_center_fork",
    }
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    out_pairs = []
    for wafer_class, basename in PAIRS:
        raw_src = STAGE_PNG_ROOT / wafer_class / f"{basename}.png"
        obj_src = find_obj_png(basename, wafer_class)
        if obj_src is None:
            print(f"[WARN] obj-id png not found for {basename}")
            continue
        raw_dst = FIGURES_DIR / f"{short[wafer_class]}_raw.png"
        obj_dst = FIGURES_DIR / f"{short[wafer_class]}_objid.png"
        shutil.copy2(raw_src, raw_dst)
        shutil.copy2(obj_src, obj_dst)
        out_pairs.append((wafer_class, str(raw_dst), str(obj_dst)))
    return out_pairs


def main():
    # filter to active classes only so the builder doesn't scan everything
    # (--limit-per-class 1 still iterates over all class dirs in PNG_ROOT).
    # Solution: temporarily move other class dirs aside? No — simpler: delete them
    # in the stage root. But we never want to touch raw wm-811k. Instead, we stage
    # ONLY our two classes into D:/project/data/wm-811k/unknown/. Builder scans
    # whatever is present in PNG_ROOT.
    # Caller should ensure STAGE_PNG_ROOT only contains our wafers; that's fine
    # because we mkdir on demand.
    for wafer_class, basename in PAIRS:
        dst_png, dst_json = stage_and_make_json(wafer_class, basename)
        print(f"[staged] {wafer_class}/{basename} -> {dst_png}  + JSON")

    # check there are no leftover classes in stage root that would slow down the builder
    extras = [p for p in STAGE_PNG_ROOT.iterdir() if p.is_dir() and p.name not in {c for c, _ in PAIRS}]
    if extras:
        print(f"[note] extra classes in stage root (will be scanned but each capped at 1): {[p.name for p in extras]}")

    run_builder()

    out_pairs = copy_results()
    print("\n=== Done ===")
    for wc, raw, obj in out_pairs:
        print(f"{wc}:")
        print(f"  raw : {raw}")
        print(f"  obj : {obj}")


if __name__ == "__main__":
    main()
