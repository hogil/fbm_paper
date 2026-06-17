"""논문 figure 스타일(제목+밑줄+개별 박스+monospace/한글)로 설명 figure 생성.
바깥 테두리/가운데 분리선 없음. 한글 줄은 맑은 고딕, 수식 줄은 Consolas. 큰 글씨 + 짧은 내용.
슬라이드에서 2개씩 세로로 쌓아 전체폭으로 크게 보이게 한다(반폭 욱여넣기 금지).
대상: hex / palette / numba / pyvips (2-box), val_margin / nb_reject (3-box).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FIG = Path(r"D:/project/fbm_paper/recommendation/figures")


def font(names, size):
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def is_kr(s):
    return any('가' <= c <= '힣' for c in s)


INK = (22, 26, 38)
HEADC = (28, 34, 50)
MONOC = (55, 61, 75)
LINEC = (172, 172, 178)
BOXLN = (150, 160, 176)


def make(out, title, boxes, W=1320):
    TITLE = font(["malgunbd.ttf", "arialbd.ttf"], 30)
    HEAD = font(["malgunbd.ttf", "arialbd.ttf"], 24)
    MONO = font(["consola.ttf", "cour.ttf"], 22)
    KR = font(["malgun.ttf"], 22)
    PAD = 30
    rule_y = 62
    box_gap = 16
    head_h = 38
    line_h = 33
    box_pad = 16
    top = rule_y + 18
    heights = [box_pad * 2 + head_h + len(lines) * line_h for _, lines in boxes]
    H = top + sum(heights) + box_gap * (len(boxes) - 1) + PAD
    img = Image.new("RGB", (W, H), (252, 252, 252))
    d = ImageDraw.Draw(img)
    d.text((PAD, 14), title, font=TITLE, fill=INK)
    d.line([(PAD, rule_y), (W - PAD, rule_y)], fill=LINEC, width=2)
    cy = top
    for (head, lines), bh in zip(boxes, heights):
        d.rounded_rectangle([PAD, cy, W - PAD, cy + bh], radius=10, outline=BOXLN, width=2, fill=(255, 255, 255))
        d.text((PAD + 20, cy + box_pad), head, font=HEAD, fill=HEADC)
        ly = cy + box_pad + head_h
        for ln in lines:
            d.text((PAD + 26, ly), ln, font=(KR if is_kr(ln) else MONO), fill=MONOC)
            ly += line_h
        cy += bh + box_gap
    img.save(out)
    print("wrote", out)


# ── 생성(fail-map): hex / palette — 한 슬라이드에 세로로 쌓음 ──
make(FIG / "fig_hex_to_grade.png", "Cython hex → Grade conversion",
     [("측정 hex 를 Grade 로 무손실 변환",
       ['raw stream :  090B0C0D0E0F090A0B0C',
        '"0C" -> "C" -> 12 (hex to decimal) -> grade 3',
        'grade row  :  0 2 3 4 5 6 0 1 2 3']),
      ("Cython 가속",
       ['Python : interpreter-based loop',
        'Cython : compiled integer loop  →  약 100배'])])

make(FIG / "fig_palette_png.png", "RGB PNG vs palette-indexed PNG",
     [("픽셀당 저장 방식",
       ['RGB     : [(123,54,24), (123,54,24), ...]   3 byte/px',
        'palette : P[3]=(123,54,24),  [(3),(3),...]   1 byte/px']),
      ("효과",
       ['반복색을 팔레트에 1회만 저장  →  저장 약 75% 축소 (무손실)'])])

# ── 운영 viewer: numba / pyvips — 한 슬라이드에 세로로 쌓음 ──
make(FIG / "numba_composite_formula.png", "Numba @njit composite map",
     [("픽셀 위치별 병렬 누적",
       ['여러 wafer Grade map을 같은 좌표로 합산하고,',
        '@njit + prange 로 Python loop을 기계어 병렬로 컴파일']),
      ("성능",
       ['numpy 대비 약 50배,  10장 합성 약 2.9초'])])

make(FIG / "pyvips_stream_formula.png", "pyvips demand-driven tile streaming",
     [("필요한 tile만 로드 (demand-driven)",
       ['큰 PNG 전체를 메모리에 올리지 않고,',
        '화면에 보이는 부분의 tile만 골라서 디코드']),
      ("pyramid + cache",
       ['축소 레벨 [0.25, 0.5, 0.75, 1.0] 을 미리 캐시 →',
        '대용량 map 즉시 조회, viewer 메모리 절감'])])

# ── P2: val-margin / nb-reject — 좌우 배치(3-box) ──
make(FIG / "val_margin_formula.png", "Validation-margin checkpoint selection",
     [("margin 정의",
       ['margin = mean(p_pos) - mean(p_neg)',
        '정답 bit와 오답 bit 확률의 분리 폭']),
      ("왜 val-F1 대신",
       ['val-F1 <-> test 상관 낮음 (rho = -0.10)',
        'val-margin <-> test 상관 높음 (rho = +0.56)']),
      ("선택 결과",
       ['val-margin 최대 checkpoint 채택',
        '→ bit-F1 0.9943,  FAR 0.00%'])], W=1040)

make(FIG / "nb_reject_formula.png", "Gaussian Naive Bayes reject gate",
     [("클래스별 가능도",
       ['P(x | y) = prod_i  N(x_i ; mu_iy , sigma_iy^2)',
        'x = 모델이 낸 4-bit 확률 벡터']),
      ("판정",
       ['y* = argmax_y  P(y) * prod_i P(x_i | y)',
        'known single / 2-combo 분포처럼 생겼는지']),
      ("reject 규칙",
       ['max 가능도 < tau  →  Normal 로 reject',
        '모호하거나 OOD 인 확률 벡터를 차단'])], W=1040)
