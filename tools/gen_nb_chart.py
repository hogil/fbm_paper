"""NB reject 설명용 4-class 확률분포 차트. single / 2-combo / OOD 의 4-bit 확률 벡터를
막대로 보여 'max 확률은 비슷해도 분포 패턴이 다르다'를 시각화. 깔끔한 학술 스타일.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams

for f in ("Malgun Gothic", "맑은 고딕", "NanumGothic", "DejaVu Sans"):
    try:
        rcParams["font.family"] = f
        break
    except Exception:
        pass
rcParams["axes.unicode_minus"] = False

NAVY = "#0F1E3D"; ACC = "#3A4150"; RED = "#CC3328"; GRN = "#2BA66B"; MUT = "#6B7280"
classes = ["bb", "fk", "sc", "sr"]
cases = [
    ("single  (bank_boundary)", [0.86, 0.10, 0.13, 0.09], True),
    ("2-combo  (bb + scratch)", [0.80, 0.11, 0.74, 0.12], True),
    ("OOD  (분포 밖)", [0.56, 0.42, 0.47, 0.44], False),
]
fig, axs = plt.subplots(1, 3, figsize=(10.6, 3.0), dpi=190)
fig.patch.set_facecolor("white")
for ax, (title, probs, accept) in zip(axs, cases):
    ax.bar(classes, probs, color=ACC, width=0.62, edgecolor="white", zorder=3)
    ax.axhline(0.55, color="#9AA4B2", ls="--", lw=1.1, zorder=2)
    ax.text(3.45, 0.57, "tau", color=MUT, fontsize=8.5, va="bottom", ha="right")
    ax.set_ylim(0, 1.0); ax.set_yticks([0, 0.5, 1.0])
    ax.set_title(title, fontsize=10.5, color=NAVY, fontweight="bold", pad=8)
    ax.tick_params(labelsize=9.5)
    note = "단일 분포에 부합 → accept" if accept else "어느 분포에도 안 맞음 → reject"
    ax.text(0.5, -0.30, note, transform=ax.transAxes, ha="center", fontsize=9.5,
            color=(GRN if accept else RED), fontweight="bold")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#333740")
fig.suptitle("같은 max 확률이라도 4-bit 분포 패턴이 다르다 → GaussianNB 가능도로 판정",
             fontsize=11.5, color=NAVY, fontweight="bold", y=1.04)
fig.tight_layout()
out = r"D:/project/fbm_paper/recommendation/figures/nb_reject_4class_dist.png"
fig.savefig(out, facecolor="white", bbox_inches="tight")
print("wrote", out)
