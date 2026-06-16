import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams

for f in ["Malgun Gothic", "맑은 고딕", "NanumGothic", "DejaVu Sans"]:
    try:
        rcParams["font.family"] = f
        break
    except Exception:
        pass
rcParams["axes.unicode_minus"] = False

recipes = ["Global\nInfoNCE", "+ Local\nDenseCL", "+ MoCo\nQueue", "+ NV-\nRetriever", "+ NeCo", "+ τ=0.5\nreassign"]
noise = [15.78, 13.87, 9.45, 8.23, 6.66, 0.00]
capture = [0.934, 0.936, 0.936, 0.925, 0.956, 0.962]

NAVY = "#0F1E3D"; SKY = "#2E8BC0"; ORANGE = "#E08A1E"

fig, ax1 = plt.subplots(figsize=(8.8, 4.3), dpi=200)
fig.patch.set_facecolor("white"); ax1.set_facecolor("white")

ax1.bar(range(6), noise, color=SKY, width=0.60, zorder=3)
ax1.set_ylabel("군집 noise (%)  ↓", color=NAVY, fontsize=12, fontweight="bold")
ax1.set_ylim(0, 18)
for i, v in enumerate(noise):
    ax1.text(i, v + 0.45, f"{v:.2f}", ha="center", va="bottom", color=NAVY, fontsize=11, fontweight="bold")
ax1.set_xticks(range(6)); ax1.set_xticklabels(recipes, fontsize=10.5, color=NAVY)
ax1.tick_params(axis="y", labelcolor=NAVY)
for s in ["top", "right"]:
    ax1.spines[s].set_visible(False)
ax1.grid(axis="y", color="#E3E9F2", lw=0.8, zorder=0)

ax2 = ax1.twinx()
ax2.plot(range(6), capture, color=ORANGE, marker="o", lw=2.3, ms=7, zorder=4)
ax2.set_ylabel("capture  ↑", color=ORANGE, fontsize=12, fontweight="bold")
ax2.set_ylim(0.90, 0.98)
ax2.tick_params(axis="y", labelcolor=ORANGE)
ax2.spines["top"].set_visible(False)
for i, v in enumerate(capture):
    ax2.text(i, v + 0.0015, f"{v:.3f}", ha="center", va="bottom", color=ORANGE, fontsize=8.5)

ax1.set_title("기법을 더할수록 군집 noise 15.8% → 0%,  capture 0.934 → 0.962",
              color=NAVY, fontsize=12.5, fontweight="bold", pad=12)
fig.tight_layout()
out = r"D:/project/fbm_paper/recommendation/figures/p1_unknown_ablation.png"
fig.savefig(out, facecolor="white", bbox_inches="tight")
print("saved", out)
