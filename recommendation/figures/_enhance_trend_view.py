"""trend_*_v2.png: 판독 불가 수준의 좌측 축 숫자/여백을 잘라내고 산점도 영역만 남겨
셀을 더 채우게(*_view.png). 가로 기준선/세로 점선은 유지. 원본 보존.
"""
import os
import numpy as np
from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = ["trend_normal", "trend_mean_shift", "trend_standard_deviation",
         "trend_spike", "trend_drift", "trend_context"]

for nm in NAMES:
    p = os.path.join(HERE, nm + "_v2.png")
    im = Image.open(p).convert("RGB")
    W, H = im.size
    # 좌측 축 숫자 영역(약 x<50)과 상/하 여백을 잘라 산점도가 셀을 채우게 한다.
    # 산점도 본문은 대략 x:52~W, y:8~H-8 (v2는 legend 없음).
    left = 50
    crop = im.crop((left, 4, W, H - 4))
    # 가독성 위해 약간 업스케일
    cw, ch = crop.size
    crop = crop.resize((int(cw * 1.4), int(ch * 1.4)), Image.LANCZOS)
    # 채도·대비 보강: 연한 배경 잡색 대비 정상(파랑)/이상(빨강) 점을 또렷하게(우승작 톤 통일)
    crop = ImageEnhance.Color(crop).enhance(1.28)
    crop = ImageEnhance.Contrast(crop).enhance(1.12)
    out = os.path.join(HERE, nm + "_view.png")
    crop.save(out)
    print("saved", out, crop.size)
