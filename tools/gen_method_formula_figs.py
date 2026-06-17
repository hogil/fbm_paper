"""논문 figure 스타일(data_*_formula.png와 동일)로 method 설명 figure 생성.
제목 + 가로 밑줄 + 세로로 쌓인 박스(굵은 헤더 + monospace 수식/텍스트). 컬러 장식 없음.
대상: numba_composite / pyvips_stream / val_margin / nb_reject (논문 figure가 없는 기법).
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

TITLE = font(["arialbd.ttf", "Arialbd.ttf"], 26)
HEAD = font(["arialbd.ttf"], 19)
MONO = font(["consola.ttf", "cour.ttf", "DejaVuSansMono.ttf"], 17)

INK = (22, 26, 38)
HEADC = (28, 34, 50)
MONOC = (60, 66, 80)
LINEC = (172, 172, 178)
BOXLN = (150, 160, 176)


def make(out, title, boxes, W=1120):
    PAD = 28
    rule_y = 56
    box_gap = 16
    head_h = 30
    line_h = 25
    box_pad = 15
    top = rule_y + 20
    heights = [box_pad * 2 + head_h + len(lines) * line_h for _, lines in boxes]
    H = top + sum(heights) + box_gap * (len(boxes) - 1) + PAD
    img = Image.new("RGB", (W, H), (252, 252, 252))
    d = ImageDraw.Draw(img)
    d.text((PAD, 14), title, font=TITLE, fill=INK)
    d.line([(PAD, rule_y), (W - PAD, rule_y)], fill=LINEC, width=2)
    cy = top
    for (head, lines), bh in zip(boxes, heights):
        d.rounded_rectangle([PAD, cy, W - PAD, cy + bh], radius=10, outline=BOXLN, width=2, fill=(255, 255, 255))
        d.text((PAD + 18, cy + box_pad), head, font=HEAD, fill=HEADC)
        ly = cy + box_pad + head_h
        for ln in lines:
            d.text((PAD + 24, ly), ln, font=MONO, fill=MONOC)
            ly += line_h
        cy += bh + box_gap
    img.save(out)
    print("wrote", out)


make(FIG / "numba_composite_formula.png", "Numba @njit composite map",
     [("Per-pixel accumulation",
       ["acc[p] += grade[w][p]      for each wafer map w",
        "@njit(parallel=True): compiled to machine code"]),
      ("Parallel reduction",
       ["N aligned wafer maps  ->  per-pixel grade count",
        "prange spreads the pixel loop across CPU cores"]),
      ("Speedup",
       ["Python loop  ->  JIT machine code + prange",
        "~50x vs numpy ;  10-map composite ~2.9 s"])])

make(FIG / "pyvips_stream_formula.png", "pyvips demand-driven tile streaming",
     [("Demand-driven pipeline",
       ["source -> op -> op -> sink",
        "executes only when the sink is connected (lazy)"]),
      ("Rolling windows",
       ["large image: keep a few scanline windows in memory",
        "threads move windows up/down as pixels are demanded"]),
      ("Memory / pyramid",
       ["full RGB load (large mem)  ->  tile stream (low mem)",
        "pyramid levels [0.25, 0.5, 0.75, 1.0] + cache"])])

make(FIG / "val_margin_formula.png", "Validation-margin checkpoint selection",
     [("Margin",
       ["margin = mean(p_pos) - mean(p_neg)",
        "gap between positive-bit and negative-bit probs"]),
      ("Why not val-F1",
       ["val-F1  <->  test  corr:  rho = -0.10  (misleading)",
        "val-margin <-> test corr:  rho = +0.56  (tracks test)"]),
      ("Selection",
       ["pick checkpoint with max val-margin",
        "->  bit-F1 0.9943 ,  FAR 0.00%"])])

make(FIG / "nb_reject_formula.png", "Gaussian Naive Bayes reject gate",
     [("Class-conditional likelihood",
       ["P(x | y) = prod_i  N(x_i ; mu_iy , sigma_iy^2)",
        "x = 4-bit probability vector from the model"]),
      ("Decision",
       ["y* = argmax_y   P(y) * prod_i P(x_i | y)",
        "is x shaped like a known single / 2-combo class?"]),
      ("Reject rule",
       ["if max_y likelihood < tau  ->  reject to Normal",
        "blocks ambiguous / OOD probability vectors"])])
