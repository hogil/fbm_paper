"""object_id_*_v2.png: 데이터 군집 주변으로 정사각 crop + 업스케일 + 마커 대비 보강.
원본은 보존하고 *_view.png 로 저장(슬라이드에서 마커가 셀을 더 채우게).
"""
import os
import numpy as np
from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = ["object_id_a_v2.png", "object_id_b_v2.png", "object_id_c_v2.png", "object_id_d_v2.png"]


def marker_bbox(a):
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    red = (R > 150) & (R > G + 40)
    green = (G > 140) & (G > R + 30) & (G > B + 10)
    magenta = (R > 140) & (B > 120) & (G < R - 30) & (G < B - 10)
    blue = (B > 150) & (B > R + 40) & (B > G + 20) & (R > 60)
    mask = red | green | magenta | blue
    ys, xs = np.where(mask)
    return (xs.min(), ys.min(), xs.max(), ys.max())


for f in FILES:
    p = os.path.join(HERE, f)
    im = Image.open(p).convert("RGB")
    a = np.asarray(im).astype(int)
    W, H = im.size
    x0, y0, x1, y1 = marker_bbox(a)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    # 군집 크기에 비례해 정사각 한 변 결정(여백 충분히: 군집의 약 1.9배), 단 너무 작지 않게 하한.
    span = max(x1 - x0, y1 - y0)
    half = int(max(span * 0.62, 55))
    L = int(cx - half); T = int(cy - half); Rr = int(cx + half); Bb = int(cy + half)
    # 경계 보정(이미지 밖으로 나가면 안쪽으로 당김, 정사각 유지)
    if L < 0:
        Rr -= L; L = 0
    if T < 0:
        Bb -= T; T = 0
    if Rr > W:
        L -= (Rr - W); Rr = W
    if Bb > H:
        T -= (Bb - H); Bb = H
    L = max(0, L); T = max(0, T)
    crop = im.crop((L, T, Rr, Bb))
    # 업스케일(LANCZOS) + 약한 대비/채도 보강으로 마커 가독성 향상
    crop = crop.resize((640, 640), Image.LANCZOS)
    crop = ImageEnhance.Color(crop).enhance(1.35)
    crop = ImageEnhance.Contrast(crop).enhance(1.18)
    out = os.path.join(HERE, f.replace("_v2.png", "_view.png"))
    crop.save(out)
    print("saved", out, "crop", (L, T, Rr, Bb))
