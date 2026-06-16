import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

for f in ["Malgun Gothic", "맑은 고딕", "NanumGothic", "DejaVu Sans"]:
    try:
        rcParams["font.family"] = f
        break
    except Exception:
        pass
rcParams["axes.unicode_minus"] = False
rng = np.random.default_rng(7)

NAVY = "#0F1E3D"; ACC = "#3F86C4"; INK = "#22303F"; MUT = "#6B7280"; LINE = "#C4D0E2"; PANEL = "#EEF3F8"
BLUE = "#3F86C4"; RED = "#CC3328"; GREEN = "#2BA66B"

fig = plt.figure(figsize=(13.0, 5.4), dpi=185)
fig.patch.set_facecolor("white")

# ── 좌측: 현업 경험 → 생성 규칙 ──
axL = fig.add_axes([0.012, 0.04, 0.34, 0.92]); axL.set_xlim(0, 10); axL.set_ylim(0, 10); axL.axis("off")
axL.text(0.2, 9.6, "기법", ha="left", va="top", color=ACC, fontsize=13, fontweight="bold")
axL.text(1.1, 9.55, "현업 판정 기준을 생성 규칙으로 코드화", ha="left", va="top", color=NAVY, fontsize=11.5, fontweight="bold")
axL.add_patch(FancyBboxPatch((0.4, 7.2), 9.0, 1.2, boxstyle="round,pad=0.0,rounding_size=0.12",
                             fc=PANEL, ec=ACC, lw=1.4))
axL.text(4.9, 7.8, "BBD/Overlay/CD 담당 10년 trend 판정 경험", ha="center", va="center",
         color=NAVY, fontsize=10, fontweight="bold")
axL.add_patch(FancyArrowPatch((4.9, 7.1), (4.9, 6.5), arrowstyle="-|>", mutation_scale=14, color=ACC, lw=1.8))
rules = [
    "계측 밀도 Region 5종",
    "Noise 3종 (Gaussian · Laplacian · Correlated)",
    "Anomaly 5종 (평균이동·산포·spike·drift·context)",
    "정상성 보정 — 정상 산포를 실측 기준선에 가둠",
]
for i, t in enumerate(rules):
    yy = 5.7 - i * 1.05
    axL.add_patch(FancyBboxPatch((0.4, yy), 9.0, 0.85, boxstyle="round,pad=0.0,rounding_size=0.1",
                                 fc="#FFFFFF", ec=LINE, lw=1.1))
    axL.add_patch(FancyBboxPatch((0.4, yy), 0.12, 0.85, boxstyle="square,pad=0", fc=ACC, ec="none"))
    axL.text(0.72, yy + 0.42, t, ha="left", va="center", color=INK, fontsize=9.6)
axL.add_patch(FancyBboxPatch((0.4, 0.25), 9.0, 0.95, boxstyle="round,pad=0.0,rounding_size=0.12",
                             fc="#EAF4EC", ec=GREEN, lw=1.3))
axL.text(4.9, 0.72, "총 10,000장 생성 → 1차 게이트 F1 0.9975 (5-seed)", ha="center", va="center",
         color=NAVY, fontsize=10, fontweight="bold")

# 화살표 (좌→우)
axA = fig.add_axes([0.345, 0.04, 0.05, 0.92]); axA.set_xlim(0, 1); axA.set_ylim(0, 1); axA.axis("off")
axA.add_patch(FancyArrowPatch((0.1, 0.5), (0.95, 0.5), arrowstyle="-|>", mutation_scale=18, color=ACC, lw=2.2))
axA.text(0.5, 0.58, "생성", ha="center", va="bottom", color=MUT, fontsize=9)

# ── 우측: 정상 + 이상 5종 mini trend ──
labels = ["정상 (기준선 주변)", "평균 이동", "산포 변화", "스파이크", "드리프트", "맥락 이탈"]
N = 60
x = np.arange(N)
base = lambda: rng.normal(0, 0.22, N)
data = []
data.append(("normal", base(), None))
y = base(); y[N//2:] += 1.4; data.append(("mean", y, (N//2, N)))
y = base(); y[N//2:] += rng.normal(0, 0.9, N - N//2); data.append(("std", y, (N//2, N)))
y = base(); y[42] += 4.2; data.append(("spike", y, (40, 45)))
y = base() + np.linspace(0, 1.8, N); data.append(("drift", y, (0, N)))
y = base(); y[30:42] += 1.6; data.append(("context", y, (30, 42)))

gx0, gy0, gw, gh = 0.40, 0.06, 0.585, 0.9
cols, rows = 3, 2
cw, ch = gw / cols, gh / rows
for i, (key, y, band) in enumerate(data):
    r, c = divmod(i, cols)
    ax = fig.add_axes([gx0 + c * cw + 0.012, gy0 + (rows - 1 - r) * ch + 0.07, cw - 0.024, ch - 0.16])
    ax.set_xlim(0, N); ax.set_ylim(-1.2, 4.8)
    ax.axhline(0, color=MUT, lw=1.0, ls="-", zorder=1)
    if band:
        ax.axvspan(band[0], band[1], color=RED, alpha=0.08, zorder=0)
    col = GREEN if key == "normal" else BLUE
    ax.scatter(x, y, s=7, c=col, zorder=3, edgecolors="none")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(LINE)
    ax.set_title(labels[i], fontsize=9.6, color=NAVY, fontweight="bold", pad=3)

fig.text(0.69, 0.005, "파랑/초록=계측점 · 가로선=기준선 · 빨강 음영=이상 구간", ha="center", color=MUT, fontsize=8.6)

out = r"D:/project/fbm_paper/recommendation/figures/p3_generator_concept.png"
fig.savefig(out, facecolor="white", bbox_inches="tight")
print("saved", out)
