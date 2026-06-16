import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

for f in ["Malgun Gothic", "맑은 고딕", "NanumGothic", "DejaVu Sans"]:
    try:
        rcParams["font.family"] = f
        break
    except Exception:
        pass
rcParams["axes.unicode_minus"] = False

NAVY = "#0F1E3D"; ACC = "#3F86C4"; INK = "#22303F"; MUT = "#6B7280"; LINE = "#C4D0E2"; PANEL = "#EEF3F8"
A_C = "#2BA6A0"; B_C = "#E0843A"; BG = "#EAF0F6"; RED = "#CC3328"; GREEN = "#2BA66B"


def title(ax, no, txt):
    ax.text(0.2, 9.55, no, ha="left", va="top", color=ACC, fontsize=16, fontweight="bold")
    ax.text(1.0, 9.5, txt, ha="left", va="top", color=NAVY, fontsize=12.5, fontweight="bold")


def effect(ax, txt):
    ax.add_patch(FancyBboxPatch((0.35, 0.3), 9.3, 1.0, boxstyle="round,pad=0.0,rounding_size=0.16",
                                fc=PANEL, ec="none", zorder=0))
    ax.text(5.0, 0.8, txt, ha="center", va="center", color=NAVY, fontsize=10.5, fontweight="bold", zorder=3)


def grid(ax, x, y, s, cells, n=4):
    for r in range(n):
        for c in range(n):
            ax.add_patch(Rectangle((x + c * s, y + (n - 1 - r) * s), s * 0.94, s * 0.94,
                                    fc=cells[r][c], ec="white", lw=1.0, zorder=3))


def arr(ax, x1, y1, x2, y2, label=None):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=15, color=ACC, lw=2.0, zorder=2))
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.4, label, ha="center", va="bottom", color=MUT, fontsize=8.6)


fig, axs = plt.subplots(2, 2, figsize=(13.0, 6.0), dpi=185)
fig.patch.set_facecolor("white")
fig.subplots_adjust(left=0.01, right=0.99, top=0.975, bottom=0.015, wspace=0.07, hspace=0.13)
for ax in axs.flat:
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

A = [[A_C if (r in (0, 1) and c == r) else BG for c in range(4)] for r in range(4)]
B = [[B_C if (c in (2, 3) and r == 3 - c + 2) else BG for c in range(4)] for r in range(4)]
MIX = [[A[r][c] if (r + c) % 2 == 0 else B[r][c] for c in range(4)] for r in range(4)]

# ① Full-Cover Mixup
ax = axs[0, 0]
title(ax, "①", "Full-Cover Mixup — 단일결함 2장 → 2-combo")
grid(ax, 0.5, 5.2, 0.62, A); ax.text(1.27, 4.7, "single A", ha="center", color=A_C, fontsize=9, fontweight="bold")
grid(ax, 0.5, 2.2, 0.62, B); ax.text(1.27, 1.7, "single B", ha="center", color=B_C, fontsize=9, fontweight="bold")
arr(ax, 3.3, 4.6, 5.1, 4.6, label="격자 전면 교차")
grid(ax, 5.4, 3.6, 0.7, MIX); ax.text(6.78, 3.05, "2-combo (A+B)", ha="center", color=NAVY, fontsize=9.5, fontweight="bold")
effect(ax, "격자 단위로 빈틈없이 합성 → 결함 신호 안 잘리고 중복결함 학습")

# ② Pair Mask
ax = axs[0, 1]
title(ax, "②", "Pair Mask — 합성 가짜 배경을 loss에서 가림")
grid(ax, 0.6, 4.0, 0.78, MIX)
# mask overlay on background cells
for r in range(4):
    for c in range(4):
        if MIX[r][c] == BG:
            ax.add_patch(Rectangle((0.6 + c * 0.78, 4.0 + (3 - r) * 0.78), 0.73, 0.73,
                                    fc="none", ec=RED, lw=1.4, hatch="////", zorder=4))
ax.text(2.16, 3.4, "합성 chip", ha="center", color=NAVY, fontsize=9.5, fontweight="bold")
ax.text(5.3, 6.2, "빗금 = 합성으로 생긴", ha="left", color=RED, fontsize=9.5)
ax.text(5.3, 5.5, "가짜 배경 cell", ha="left", color=RED, fontsize=9.5)
ax.text(5.3, 4.3, "→ 이 cell은 loss 계산에서 제외", ha="left", color=INK, fontsize=9.5)
effect(ax, "가짜 배경을 '정상'으로 잘못 배우지 않게 → 오경보율(FAR) 차단")

# ③ val-margin
ax = axs[1, 0]
title(ax, "③", "val-margin — 분리 마진으로 best 선택")
ax.add_patch(FancyBboxPatch((0.6, 2.0), 3.2, 5.8, boxstyle="round,pad=0.0,rounding_size=0.1",
                            fc="#F7FAFD", ec=LINE, lw=1.1, zorder=1))
ax.add_patch(Rectangle((1.1, 6.0), 2.2, 0.55, fc=GREEN, ec="white", zorder=3))
ax.text(2.2, 6.95, "결함 점수 (높게)", ha="center", color=GREEN, fontsize=8.8, fontweight="bold")
ax.add_patch(Rectangle((1.1, 3.0), 2.2, 0.55, fc=GRAY if False else "#9AA7B5", ec="white", zorder=3))
ax.text(2.2, 2.5, "정상 점수 (낮게)", ha="center", color=MUT, fontsize=8.8)
ax.add_patch(FancyArrowPatch((3.55, 6.27), (3.55, 3.27), arrowstyle="<|-|>", mutation_scale=12, color=ACC, lw=1.8))
ax.text(3.8, 4.75, "margin", ha="left", color=ACC, fontsize=9.5, fontweight="bold", rotation=90, va="center")
ax.text(5.0, 6.0, "정상↔결함 점수 분리 마진이", ha="left", color=INK, fontsize=9.5)
ax.text(5.0, 5.3, "가장 큰 시점을 best로 선택", ha="left", color=INK, fontsize=9.5)
ax.text(5.0, 4.2, "(val-F1은 실성능과 무관, val-margin이 따라옴)", ha="left", color=MUT, fontsize=8.8)
effect(ax, "criterion만 바꿔 무비용 개선 (val-F1 ρ −0.10 → val-margin ρ +0.56)")

# ④ NB reject
ax = axs[1, 1]
title(ax, "④", "NB reject — 추론 시 정상/OOD 차단")
ax.add_patch(Rectangle((0.6, 4.9), 1.6, 1.6, fc=BG, ec=LINE, lw=1.1, zorder=3))
ax.text(1.4, 4.4, "chip", ha="center", color=MUT, fontsize=9)
arr(ax, 2.3, 5.7, 3.1, 5.7)
ax.add_patch(FancyBboxPatch((3.2, 5.0), 1.7, 1.4, boxstyle="round,pad=0.0,rounding_size=0.1",
                            fc=PANEL, ec=ACC, lw=1.4, zorder=3))
ax.text(4.05, 5.7, "model\nmax prob", ha="center", va="center", color=NAVY, fontsize=9, fontweight="bold", zorder=4)
ax.add_patch(FancyArrowPatch((4.95, 6.1), (6.3, 7.0), arrowstyle="-|>", mutation_scale=13, color=GREEN, lw=1.7))
ax.add_patch(FancyArrowPatch((4.95, 5.2), (6.3, 4.0), arrowstyle="-|>", mutation_scale=13, color=RED, lw=1.7))
ax.text(5.5, 6.8, "≥ 0.55", ha="center", color=GREEN, fontsize=8.6, fontweight="bold")
ax.text(5.5, 4.6, "< 0.55", ha="center", color=RED, fontsize=8.6, fontweight="bold")
ax.add_patch(FancyBboxPatch((6.4, 6.5), 2.9, 0.95, boxstyle="round,pad=0.0,rounding_size=0.12",
                            fc="#EAF4EC", ec=GREEN, lw=1.3, zorder=3))
ax.text(7.85, 6.97, "결함으로 검출", ha="center", color=NAVY, fontsize=9.5, fontweight="bold", zorder=4)
ax.add_patch(FancyBboxPatch((6.4, 3.5), 2.9, 0.95, boxstyle="round,pad=0.0,rounding_size=0.12",
                            fc="#FBE9E7", ec=RED, lw=1.3, zorder=3))
ax.text(7.85, 3.97, "Normal로 강제 (reject)", ha="center", color=NAVY, fontsize=9.5, fontweight="bold", zorder=4)
effect(ax, "최대 확률 낮으면 Normal 처리 → Normal/Invalid/OOD 오경보 차단")

out = r"D:/project/fbm_paper/recommendation/figures/p2_fcmpm_concept.png"
fig.savefig(out, facecolor="white", bbox_inches="tight")
print("saved", out)
