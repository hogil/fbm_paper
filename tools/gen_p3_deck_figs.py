"""P3(계측 trend 이상탐지 데이터 생성) 발표용 figure 생성.
raw scatter 가 아니라, 주석/라벨이 들어간 발표 품질의 figure 를 직접 그린다.
팔레트: navy #0F1E3D, teal #12B5B0, red #CC3328, 회색 grid. Korean=맑은고딕.
출력: recommendation/figures/p3_deck_*.png
"""
import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch

for f in ("Malgun Gothic", "맑은 고딕", "NanumGothic", "DejaVu Sans"):
    try:
        rcParams["font.family"] = f; break
    except Exception:
        pass
rcParams["axes.unicode_minus"] = False

NAVY = "#0F1E3D"; TEAL = "#12B5B0"; RED = "#CC3328"; GRY = "#9AA4B2"
INK = "#222630"; MUT = "#6B7280"; BLUE = "#2B66D9"
FIG = r"D:/project/fbm_paper/recommendation/figures"


def _clean(ax, title=None, sub=None):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#C7CDD6")
    ax.tick_params(labelleft=False, labelbottom=False, length=0)
    ax.grid(True, color="#EEF1F5", lw=0.8, zorder=0)
    if title:
        ax.set_title(title, fontsize=14, color=NAVY, fontweight="bold", pad=9)
    if sub:
        ax.text(0.5, -0.11, sub, transform=ax.transAxes, ha="center", va="top",
                fontsize=11, color=MUT)


# ───────────────────────── 1. 영역(Region) ─────────────────────────
def fig_regions():
    rng = np.random.default_rng(7)
    fig, ax = plt.subplots(figsize=(13.2, 4.5), dpi=200)
    fig.patch.set_facecolor("white")
    regions = [("밀집", 0, 52, "dense"), ("희소", 52, 96, "sparse"),
               ("결핍", 96, 130, "missing"), ("밀집", 130, 196, "dense"),
               ("희소", 196, 246, "sparse"), ("결핍", 246, 285, "missing")]
    band = {"dense": "#E7ECF5", "sparse": "#FBF3E2", "missing": "#FBE9E7"}
    edge = {"dense": NAVY, "sparse": "#C98A22", "missing": RED}
    drift = 0.0
    for name, x0, x1, kind in regions:
        ax.axvspan(x0, x1, color=band[kind], zorder=0)
        ax.axvline(x1, color="#D5DBE3", lw=0.8, ls=(0, (4, 4)), zorder=1)
        if kind == "dense":
            xs = np.arange(x0 + 1, x1, 1.0)
        elif kind == "sparse":
            xs = np.arange(x0 + 2, x1, 4.0)
        else:
            xs = np.array([])
        if len(xs):
            ys = 0.0 + rng.normal(0, 0.16, len(xs))
            ax.scatter(xs, ys, s=14, color=NAVY, alpha=0.75, edgecolors="none", zorder=3)
        lbl = {"dense": "밀집 (Dense)", "sparse": "희소 (Sparse)", "missing": "결핍 (Missing)"}[kind]
        ax.text((x0 + x1) / 2, 0.92, lbl, ha="center", va="top", fontsize=11.5,
                color=edge[kind], fontweight="bold")
    ax.set_xlim(0, 285); ax.set_ylim(-1.0, 1.05)
    _clean(ax)
    ax.annotate("측정 빈도가 높은 구간", xy=(26, -0.5), xytext=(26, -0.92),
                ha="center", fontsize=10, color=NAVY,
                arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.2))
    ax.annotate("측정이 비는 구간", xy=(113, 0.0), xytext=(113, -0.7),
                ha="center", fontsize=10, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.2))
    fig.tight_layout()
    out = FIG + "/p3_deck_regions.png"
    fig.savefig(out, facecolor="white", bbox_inches="tight"); print("wrote", out)
    plt.close(fig)


# ───────────────────────── 2. 노이즈(Noise) 3종 ─────────────────────────
def fig_noise():
    rng = np.random.default_rng(3)
    n = 120; t = np.arange(n)
    fig, axs = plt.subplots(1, 3, figsize=(13.6, 3.9), dpi=200)
    fig.patch.set_facecolor("white")

    g = rng.normal(0, 0.3, n)
    axs[0].plot(t, g, color=NAVY, lw=1.0, alpha=0.9, marker="o", ms=2.4, mfc=NAVY, mec="none")
    _clean(axs[0], "Gaussian — 기본 계측 산포", "무작위로 고르게 흩어짐")

    a = np.zeros(n)
    for i in range(1, n):
        a[i] = 0.93 * a[i - 1] + rng.normal(0, 0.12)
    axs[1].plot(t, a, color=TEAL, lw=1.8)
    axs[1].fill_between(t, a, color=TEAL, alpha=0.10)
    _clean(axs[1], "Correlated AR(1) — 설비 변동", "천천히 끌리며 흐름 (자기상관)")

    lp = rng.laplace(0, 0.10, n)
    axs[2].plot(t, lp, color=NAVY, lw=0.9, alpha=0.85, marker="o", ms=2.2, mfc=NAVY, mec="none")
    big = np.argsort(np.abs(lp))[-4:]
    axs[2].scatter(t[big], lp[big], s=46, color=RED, zorder=5, edgecolors="white", lw=0.8)
    _clean(axs[2], "Laplacian — 계측 헌팅", "평소 작다가 한 번씩 크게 튐 (heavy-tail)")

    for ax in axs:
        ax.set_ylim(-1.15, 1.15); ax.axhline(0, color="#D5DBE3", lw=0.8, zorder=1)
    fig.tight_layout()
    out = FIG + "/p3_deck_noise.png"
    fig.savefig(out, facecolor="white", bbox_inches="tight"); print("wrote", out)
    plt.close(fig)


# ───────────────────────── 3. 이상(Anomaly) 5종 ─────────────────────────
def fig_anomaly():
    rng = np.random.default_rng(11)
    n = 100; t = np.arange(n); cut = 64
    fig, axs = plt.subplots(1, 5, figsize=(16.2, 3.5), dpi=200)
    fig.patch.set_facecolor("white")

    def base():
        return rng.normal(0, 0.22, n)

    def split(ax, y, ab):
        ax.scatter(t[:cut], y[:cut], s=11, color=BLUE, alpha=0.8, edgecolors="none")
        ax.scatter(t[cut:], ab, s=13, color=RED, alpha=0.9, edgecolors="none")
        ax.axvline(cut, color="#D5DBE3", lw=0.9, ls=(0, (3, 3)))
        ax.set_ylim(-1.7, 2.7); ax.axhline(0, color="#E4E8EE", lw=0.8)

    y = base(); ab = y[cut:] + 1.5
    split(axs[0], y, ab); _clean(axs[0], "avg", "평균이 한 단계 이동")
    y = base(); ab = rng.normal(0, 0.7, n - cut)
    split(axs[1], y, ab); _clean(axs[1], "std", "산포(흩어짐)가 커짐")
    y = base(); ab = y[cut:].copy()
    sp = rng.choice(np.arange(n - cut), 5, replace=False); ab[sp] += rng.uniform(1.8, 2.4, 5)
    split(axs[2], y, ab); _clean(axs[2], "spike", "일부 점만 순간 급등")
    y = base(); ab = y[cut:] + np.linspace(0, 2.0, n - cut)
    split(axs[3], y, ab); _clean(axs[3], "drift", "서서히 선형 증가")
    # context: fleet(gray) vs target(red) 전체 이탈
    axc = axs[4]
    for _ in range(4):
        axc.plot(t, rng.normal(0, 0.18, n) + rng.uniform(-0.15, 0.15), color=GRY, lw=0.9, alpha=0.7)
    axc.plot(t, rng.normal(0, 0.18, n) + 1.3, color=RED, lw=1.8)
    axc.set_ylim(-1.7, 2.7); axc.axhline(0, color="#E4E8EE", lw=0.8)
    _clean(axc, "context", "fleet 대비 전체가 이탈")

    fig.tight_layout()
    out = FIG + "/p3_deck_anomaly.png"
    fig.savefig(out, facecolor="white", bbox_inches="tight"); print("wrote", out)
    plt.close(fig)


if __name__ == "__main__":
    fig_regions(); fig_noise(); fig_anomaly()
