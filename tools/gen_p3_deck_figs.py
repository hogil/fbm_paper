"""P3(계측 trend 이상탐지 데이터 생성) 발표용 figure.
논문형 multi-panel 합본: (a) 정상 baseline 영역 + (b) 계측 노이즈 3종 (위) / (c) 이상 5종 (아래).
regions 는 실제 계측(fleet 산점도 + baseline)처럼 그린다. Korean=맑은고딕.
출력: recommendation/figures/p3_deck_combined.png (+ 개별 figure 도 갱신)
"""
import matplotlib
matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

for f in ("Malgun Gothic", "맑은 고딕", "NanumGothic", "DejaVu Sans"):
    try:
        rcParams["font.family"] = f; break
    except Exception:
        pass
rcParams["axes.unicode_minus"] = False

NAVY = "#0F1E3D"; TEAL = "#12B5B0"; RED = "#CC3328"; GRY = "#9AA4B2"
INK = "#222630"; MUT = "#6B7280"; BLUE = "#2B66D9"
FLEET = ["#5B8FD9", "#67B7C8", "#E0A85C", "#D98AA8", "#8AB87A", "#7E78D2"]
FIG = r"D:/project/fbm_paper/recommendation/figures"


def _spines(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#C7CDD6")
    ax.tick_params(labelsize=8, length=0, colors=MUT)
    ax.grid(True, color="#EEF1F5", lw=0.7, zorder=0)


# ── (a) 정상 baseline: 실제 계측처럼 fleet 산점도 + baseline + 영역 밀도 ──
def draw_regions(ax, rng):
    base = 0.085
    regions = [("밀집", 100, 175, "dense"), ("희소", 175, 235, "sparse"),
               ("결핍", 235, 285, "missing"), ("밀집", 285, 400, "dense"),
               ("희소", 400, 470, "sparse"), ("결핍", 470, 520, "missing"),
               ("밀집", 520, 610, "dense")]
    band = {"dense": "#EAF0F8", "sparse": "#FBF4E5", "missing": "#FBECEA"}
    edge = {"dense": NAVY, "sparse": "#C98A22", "missing": RED}
    seen = set()
    for name, x0, x1, kind in regions:
        ax.axvspan(x0, x1, color=band[kind], zorder=0)
        if kind == "dense":
            step, perx = 1.0, 6
        elif kind == "sparse":
            step, perx = 4.0, 2
        else:
            step, perx = None, 0
        if step:
            for x in np.arange(x0, x1, step):
                k = rng.integers(1, perx + 1)
                ys = base + rng.normal(0, 0.028, k)
                cs = rng.choice(len(FLEET), k)
                ax.scatter(np.full(k, x) + rng.normal(0, 0.4, k), ys, s=9,
                           c=[FLEET[i] for i in cs], alpha=0.55, edgecolors="none", zorder=3)
        if kind not in seen:
            ax.text((x0 + x1) / 2, 0.232, {"dense": "밀집", "sparse": "희소", "missing": "결핍"}[kind],
                    ha="center", va="top", fontsize=10, color=edge[kind], fontweight="bold")
            seen.add(kind)
    ax.axhline(base, color="#8A929E", lw=1.0, ls=(0, (5, 4)), zorder=2)
    ax.set_xlim(100, 610); ax.set_ylim(-0.02, 0.24)
    ax.set_ylabel("Measurement (a.u.)", fontsize=8.5, color=MUT)
    ax.set_xlabel("time index", fontsize=8.5, color=MUT)
    _spines(ax)


# ── (b) 계측 노이즈 3종 ──
def draw_noise(axs, rng):
    n = 120; t = np.arange(n)
    g = rng.normal(0, 0.3, n)
    axs[0].plot(t, g, color=NAVY, lw=0.9, alpha=0.9, marker="o", ms=2.0, mfc=NAVY, mec="none")
    axs[0].set_title("Gaussian", fontsize=11, color=NAVY, fontweight="bold", pad=5)
    axs[0].set_xlabel("기본 산포", fontsize=8.5, color=MUT)
    a = np.zeros(n)
    for i in range(1, n):
        a[i] = 0.93 * a[i - 1] + rng.normal(0, 0.12)
    axs[1].plot(t, a, color=TEAL, lw=1.7)
    axs[1].fill_between(t, a, color=TEAL, alpha=0.10)
    axs[1].set_title("Correlated AR(1)", fontsize=11, color=NAVY, fontweight="bold", pad=5)
    axs[1].set_xlabel("설비 변동", fontsize=8.5, color=MUT)
    lp = rng.laplace(0, 0.10, n)
    axs[2].plot(t, lp, color=NAVY, lw=0.8, alpha=0.85, marker="o", ms=1.8, mfc=NAVY, mec="none")
    big = np.argsort(np.abs(lp))[-4:]
    axs[2].scatter(t[big], lp[big], s=40, color=RED, zorder=5, edgecolors="white", lw=0.7)
    axs[2].set_title("Laplacian", fontsize=11, color=NAVY, fontweight="bold", pad=5)
    axs[2].set_xlabel("계측 헌팅", fontsize=8.5, color=MUT)
    for ax in axs:
        ax.set_ylim(-1.15, 1.15); ax.axhline(0, color="#D5DBE3", lw=0.7, zorder=1)
        _spines(ax); ax.set_xticks([])


# ── (c) 이상 5종 ──
def draw_anomaly(axs, rng):
    n = 100; t = np.arange(n); cut = 64
    titles = ["avg", "std", "spike", "drift", "context"]
    subs = ["평균 이동", "산포 확대", "순간 급등", "선형 증가", "fleet 대비 이탈"]

    def base():
        return rng.normal(0, 0.22, n)

    def split(ax, y, ab):
        ax.scatter(t[:cut], y[:cut], s=8, color=BLUE, alpha=0.8, edgecolors="none")
        ax.scatter(t[cut:], ab, s=9, color=RED, alpha=0.9, edgecolors="none")
        ax.axvline(cut, color="#D5DBE3", lw=0.8, ls=(0, (3, 3)))
        ax.set_ylim(-1.7, 2.7); ax.axhline(0, color="#E4E8EE", lw=0.7)

    y = base(); split(axs[0], y, y[cut:] + 1.5)
    y = base(); split(axs[1], y, rng.normal(0, 0.7, n - cut))
    y = base(); ab = y[cut:].copy(); sp = rng.choice(np.arange(n - cut), 5, replace=False)
    ab[sp] += rng.uniform(1.8, 2.4, 5); split(axs[2], y, ab)
    y = base(); split(axs[3], y, y[cut:] + np.linspace(0, 2.0, n - cut))
    axc = axs[4]
    for _ in range(4):
        axc.plot(t, rng.normal(0, 0.18, n) + rng.uniform(-0.15, 0.15), color=GRY, lw=0.8, alpha=0.7)
    axc.plot(t, rng.normal(0, 0.18, n) + 1.3, color=RED, lw=1.6)
    axc.set_ylim(-1.7, 2.7); axc.axhline(0, color="#E4E8EE", lw=0.7)
    for ax, ti, su in zip(axs, titles, subs):
        _spines(ax); ax.set_xticks([]); ax.set_yticks([])
        ax.set_title(ti, fontsize=11, color=NAVY, fontweight="bold", pad=5)
        ax.set_xlabel(su, fontsize=8.5, color=MUT)


def fig_combined():
    rng = np.random.default_rng(7)
    fig = plt.figure(figsize=(15.2, 7.7), dpi=200)
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 0.92], hspace=0.62,
                          left=0.045, right=0.985, top=0.90, bottom=0.075)
    top = gs[0].subgridspec(1, 2, width_ratios=[1.05, 1.3], wspace=0.16)
    ax_reg = fig.add_subplot(top[0])
    noise_gs = top[1].subgridspec(1, 3, wspace=0.28)
    ax_n = [fig.add_subplot(noise_gs[i]) for i in range(3)]
    bot = gs[1].subgridspec(1, 5, wspace=0.26)
    ax_a = [fig.add_subplot(bot[i]) for i in range(5)]

    draw_regions(ax_reg, rng)
    draw_noise(ax_n, rng)
    draw_anomaly(ax_a, rng)

    def section(axleft, axright, text):
        p0 = axleft.get_position(); p1 = axright.get_position()
        fig.text((p0.x0 + p1.x1) / 2, p0.y1 + 0.045, text, ha="center", va="bottom",
                 fontsize=13.5, color=NAVY, fontweight="bold")
    section(ax_reg, ax_reg, "(a) 정상 baseline — 밀집/희소/결핍 영역")
    section(ax_n[0], ax_n[2], "(b) 계측 노이즈 3종")
    section(ax_a[0], ax_a[4], "(c) 이상 합성 5종 (파랑 정상, 빨강 이상)")

    out = FIG + "/p3_deck_combined.png"
    fig.savefig(out, facecolor="white"); print("wrote", out)
    plt.close(fig)


if __name__ == "__main__":
    fig_combined()
