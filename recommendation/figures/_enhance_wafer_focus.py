"""wafer_*_hc.png: 정상영역(연한 파랑)이 너무 밝아 결함(빨강 군집)과 저대비이고
빈 영역이 넓어 '무엇을 봐야 하는지' 신호가 약함. 다음을 적용한 *_focus.png 생성(원본 보존):
 1) 정상영역 명도를 약간 낮춰(연파랑 -> 중간 청회색) 결함 빨강과 대비 강화
 2) 결함 빨강의 채도/진하기를 높여 또렷하게
 3) 결함 군집 위치를 가리키는 가이드 원 + 우하단 확대 인셋(zoom-in) 합성
"""
import os
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ["wafer_center_scratch", "wafer_edge_top_scratch", "wafer_edge_ring_scratch_rot"]

# 정상(연파랑) 대체색: 약간 더 진한 청회색 -> 빨강과 대비 ↑
NORMAL_NEW = np.array([0x9F, 0xB2, 0xCC], dtype=np.float32)
RED_NEW = np.array([0xD3, 0x1F, 0x2B], dtype=np.float32)   # 진한 빨강


def classify(arr):
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    # 흰 배경(원 바깥)
    white = (r > 235) & (g > 235) & (b > 235)
    # 빨강 결함: R 우세
    red = (r.astype(int) - g.astype(int) > 40) & (r.astype(int) - b.astype(int) > 40) & (r > 110)
    # 정상(연파랑): 나머지(원 안)
    normal = (~white) & (~red)
    return white, red, normal


def recolor(im):
    arr = np.asarray(im.convert("RGB")).astype(np.float32)
    white, red, normal = classify(arr)
    out = arr.copy()
    out[normal] = NORMAL_NEW
    out[red] = RED_NEW
    return Image.fromarray(out.astype(np.uint8)), red


def defect_bbox(redmask):
    ys, xs = np.where(redmask)
    if len(xs) == 0:
        return None
    return xs.min(), ys.min(), xs.max(), ys.max()


for nm in NAMES:
    p = os.path.join(HERE, nm + "_hc.png")
    if not os.path.exists(p):
        print("skip(missing)", p)
        continue
    im = Image.open(p)
    recolored, red = recolor(im)
    W, H = recolored.size
    bb = defect_bbox(red)
    draw = ImageDraw.Draw(recolored)
    # 결함이 프레임 대부분에 퍼져 있으면(가장자리 링 등) 가이드 원/인셋은 오히려 산만 -> 대비 보정만 적용
    spread = bb is not None and ((bb[2] - bb[0]) > 0.8 * W or (bb[3] - bb[1]) > 0.8 * H)
    if bb and not spread:
        x0, y0, x1, y1 = bb
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rad = max(x1 - x0, y1 - y0) / 2 + W * 0.045
        # 가이드 원(결함 위치 강조)
        draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                     outline=(0x12, 0xB5, 0xB0), width=max(6, W // 220))
        # 확대 인셋: 결함 영역 crop을 우하단에 합성
        pad = int(max(x1 - x0, y1 - y0) * 0.35) + 30
        cl = (max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad))
        crop = recolored.crop(cl)
        ins = int(W * 0.34)
        crop = crop.resize((ins, ins), Image.LANCZOS)
        # 인셋 테두리
        cd = ImageDraw.Draw(crop)
        cd.rectangle([0, 0, ins - 1, ins - 1], outline=(0x12, 0xB5, 0xB0), width=max(5, ins // 90))
        ix, iy = W - ins - int(W * 0.02), H - ins - int(H * 0.02)
        recolored.paste(crop, (ix, iy))
        # 인셋 라벨
        draw.rectangle([ix, iy - int(H * 0.045), ix + ins, iy], fill=(0x12, 0xB5, 0xB0))
        try:
            from PIL import ImageFont
            fnt = ImageFont.truetype("malgun.ttf", int(H * 0.032))
        except Exception:
            fnt = None
        draw.text((ix + 10, iy - int(H * 0.043)), "결함 확대", fill=(255, 255, 255), font=fnt)
    out = os.path.join(HERE, nm + "_focus.png")
    recolored.save(out)
    print("saved", out, recolored.size, "bbox", bb)
