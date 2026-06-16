import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

for f in ["Malgun Gothic", "맑은 고딕", "NanumGothic", "DejaVu Sans"]:
    try:
        rcParams["font.family"] = f
        break
    except Exception:
        pass
rcParams["axes.unicode_minus"] = False

NAVY = "#0F1E3D"; ACC = "#3F86C4"; INK = "#22303F"; MUT = "#6B7280"; LINE = "#C4D0E2"; PANEL = "#EEF3F8"
GREEN = "#2BA66B"; GRAY = "#9AA7B5"; RED = "#CC3328"


def rrect(ax, x, y, w, h, fc, ec=LINE, lw=1.2, r=0.10, t=None, tc=None, fs=10.5, bold=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=2))
    if t:
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center",
                color=tc or NAVY, fontsize=fs, fontweight="bold" if bold else "normal", zorder=3)


def arrow(ax, x1, y1, x2, y2, c=ACC, lw=2.0, label=None, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=15,
                                 color=c, lw=lw, zorder=2, linestyle=ls))
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.4, label, ha="center", va="bottom", color=MUT, fontsize=9)


fig, axs = plt.subplots(1, 2, figsize=(13.0, 5.0), dpi=185)
fig.patch.set_facecolor("white")
fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01, wspace=0.06)
for ax in axs.flat:
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

# ── Panel A: contrastive 원리 (라벨 없이 가깝게/멀게) ──
ax = axs[0]
ax.text(0.2, 9.6, "원리", ha="left", va="top", color=ACC, fontsize=13, fontweight="bold")
ax.text(1.1, 9.55, "정답 label 없이 임베딩 학습 (self-supervised contrastive)",
        ha="left", va="top", color=NAVY, fontsize=11.5, fontweight="bold")
# wafer -> 2 augment views -> encoder
ax.add_patch(Circle((1.3, 6.0), 0.85, fc="#E6EEF6", ec=LINE, lw=1.3, zorder=3))
ax.text(1.3, 4.75, "한 wafer", ha="center", color=MUT, fontsize=9)
rrect(ax, 2.7, 6.6, 1.7, 0.8, "#FFFFFF", t="view 1", fs=10, tc=INK)
rrect(ax, 2.7, 4.7, 1.7, 0.8, "#FFFFFF", t="view 2", fs=10, tc=INK)
arrow(ax, 2.15, 6.2, 2.7, 7.0)
arrow(ax, 2.15, 5.8, 2.7, 5.1)
ax.text(3.55, 8.0, "augmentation 2개", ha="center", color=MUT, fontsize=8.5)
rrect(ax, 4.9, 5.4, 1.6, 1.4, PANEL, ec=ACC, lw=1.5, t="encoder", fs=10, tc=ACC)
arrow(ax, 4.4, 7.0, 4.9, 6.5)
arrow(ax, 4.4, 5.1, 4.9, 5.7)
# embedding space
ax.add_patch(FancyBboxPatch((7.0, 4.0), 2.7, 4.2, boxstyle="round,pad=0.0,rounding_size=0.12",
                            fc="#F7FAFD", ec=LINE, lw=1.2, zorder=1))
ax.text(8.35, 8.0, "embedding 공간", ha="center", color=MUT, fontsize=9)
ax.add_patch(Circle((7.9, 6.6), 0.18, fc=GREEN, ec="white", zorder=4))
ax.add_patch(Circle((8.3, 6.3), 0.18, fc=GREEN, ec="white", zorder=4))
ax.text(8.1, 7.05, "같은 wafer\n가깝게", ha="center", color=GREEN, fontsize=8.6, fontweight="bold")
for (px, py) in [(7.4, 4.8), (9.1, 5.0), (8.9, 4.4), (7.6, 4.4)]:
    ax.add_patch(Circle((px, py), 0.16, fc=GRAY, ec="white", zorder=4))
ax.text(8.3, 4.05, "다른 wafer 멀게", ha="center", color=MUT, fontsize=8.6)
arrow(ax, 6.5, 6.1, 7.0, 6.2)
ax.text(5.0, 3.0, "InfoNCE: 같은 wafer 두 view는 당기고, 다른 wafer는 밀어냄  ·  τ=0.07, 128-D",
        ha="left", va="center", color=INK, fontsize=9.3)
ax.add_patch(FancyBboxPatch((0.35, 0.4), 9.3, 1.5, boxstyle="round,pad=0.0,rounding_size=0.15",
                            fc=PANEL, ec="none", zorder=0))
ax.text(5.0, 1.5, "학습된 임베딩 → HDBSCAN 군집", ha="center", color=NAVY, fontsize=10.5, fontweight="bold")
ax.text(5.0, 0.85, "운영 2,000장 → 13개 후보 군집 → 현업 검토 → 7개 진성 불량 확인",
        ha="center", color=INK, fontsize=9.6)

# ── Panel B: 성능 올린 기법 스택 ──
ax = axs[1]
ax.text(0.2, 9.6, "성능을 올린 기법 스택", ha="left", va="top", color=NAVY, fontsize=12.5, fontweight="bold")
rows = [
    ("Global InfoNCE", "wafer 단위 임베딩 정렬 (기본)"),
    ("+ Local DenseCL", "feature map 격자 단위까지 국소 패턴 대조"),
    ("+ MoCo Queue 4096", "지난 batch 임베딩 누적 → negative 256배 확장"),
    ("+ NV-Retriever", "같은 불량을 negative로 오인(false-neg) 제거"),
    ("+ NeCo", "Normal/defect 경계 안정화"),
]
y0 = 8.2; hh = 1.18; gap = 0.18
for i, (nm, ds) in enumerate(rows):
    yy = y0 - i * (hh + gap) - hh
    fc = "#FFFFFF" if i else PANEL
    rrect(ax, 0.5, yy, 3.3, hh, fc, ec=(ACC if i == 0 else LINE), lw=1.4, t=nm, fs=10.5,
          tc=(NAVY if i == 0 else ACC))
    ax.text(4.0, yy + hh / 2, ds, ha="left", va="center", color=INK, fontsize=9.4)
    if i:
        ax.add_patch(FancyArrowPatch((2.15, yy + hh + gap), (2.15, yy + hh + 0.02),
                                     arrowstyle="-|>", mutation_scale=11, color=ACC, lw=1.4, zorder=2))
ax.add_patch(FancyBboxPatch((8.3, 0.6), 1.45, 8.0, boxstyle="round,pad=0.0,rounding_size=0.15",
                            fc="#EAF4EC", ec=GREEN, lw=1.4, zorder=1))
ax.text(9.02, 7.6, "군집\nnoise", ha="center", color=GREEN, fontsize=10, fontweight="bold")
ax.text(9.02, 5.2, "15.8%", ha="center", color=NAVY, fontsize=12, fontweight="bold")
ax.add_patch(FancyArrowPatch((9.02, 4.7), (9.02, 3.3), arrowstyle="-|>", mutation_scale=15, color=GREEN, lw=2.2))
ax.text(9.02, 2.5, "0%", ha="center", color=GREEN, fontsize=14, fontweight="bold")
ax.text(9.02, 1.3, "단계적\n안정화", ha="center", color=MUT, fontsize=8.6)

out = r"D:/project/fbm_paper/recommendation/figures/p1_unknown_method.png"
fig.savefig(out, facecolor="white", bbox_inches="tight")
print("saved", out)
