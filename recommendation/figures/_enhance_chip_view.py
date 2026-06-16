"""chip_*_selected.png(200x200): 회색(155) 노이즈 + 흩뿌려진 결함 픽셀이 섞여
결함 '구조(세로 스크래치선 등)'가 잘 안 보임. 다음을 적용한 chip_*_view.png 생성(원본 보존):
 1) 회색(155) 노이즈 -> 연한 청회색 배경으로 낮춤(대비 ↓)
 2) 결함 픽셀(녹색/고등급 유채색)을 이진 마스크로 잡고 '국소 밀도'로 가중:
    - 밀집(구조적) 결함 -> 진한 빨강 강조
    - 희소(흩뿌려진 노이즈성) 결함 -> 배경 쪽으로 흐리게
    => normal 패널은 거의 깨끗, scratch/fork/combo는 결함 구조가 또렷
 3) 3배 업스케일 + 약 평활화
대상: scratch / fork / fork+scratch(combo) / normal / starburst(OOD)
"""
import os
import numpy as np
from PIL import Image, ImageFilter
from scipy.ndimage import uniform_filter

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = [
    "chip_eval_scratch_selected", "chip_eval_fork_selected",
    "chip_combo_fork_scratch_selected", "chip_eval_normal_selected",
    "chip_ood_starburst_selected",
]

BG = np.array([236, 239, 244], dtype=np.float32)        # 연한 배경
RED = np.array([0xCB, 0x18, 0x22], dtype=np.float32)     # 진한 결함 빨강


def enhance(im):
    arr = np.asarray(im.convert("RGB")).astype(np.float32)
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    white = (r > 240) & (g > 240) & (b > 240)
    gray = (np.abs(r - 155) < 35) & (np.abs(g - 155) < 35) & (np.abs(b - 155) < 35)
    defect = (~white) & (~gray)                          # 결함 후보(유채색 전부)
    dm = defect.astype(np.float32)
    # 국소 밀도(7x7 평균) -> 밀집 결함일수록 1에 가까움
    dens = uniform_filter(dm, size=7)
    # 밀도 가중 alpha: 희소(노이즈) 결함은 거의 사라지고, 밀집 구조만 강조
    alpha = np.clip((dens - 0.18) / 0.42, 0.0, 1.0) * dm   # 결함 픽셀에만 적용
    alpha = alpha[..., None]
    out = np.empty_like(arr)
    out[...] = BG
    out[white] = [247, 249, 252]
    # 결함은 alpha로 배경↔진빨강 보간
    out = out * (1 - alpha) + RED * alpha
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


for nm in NAMES:
    p = os.path.join(HERE, nm + ".png")
    if not os.path.exists(p):
        print("skip(missing)", p)
        continue
    im = enhance(Image.open(p))
    W, H = im.size
    im = im.resize((W * 3, H * 3), Image.NEAREST).filter(ImageFilter.GaussianBlur(0.7))
    out = os.path.join(HERE, nm.replace("_selected", "_view") + ".png")
    im.save(out)
    print("saved", out, im.size)
