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
    """5종을 한눈에 구분되게: 각 유형에 고유한 가이드(계단/엔벨로프/스템/추세선/오프셋)를 얹는다."""
    n = 100; t = np.arange(n); cut = 64
    tn = t[:cut]; ta = t[cut:]; na = n - cut
    titles = ["avg", "std", "spike", "drift", "context"]
    subs = ["평균이 한 단계 위로", "산포가 넓게 퍼짐", "몇 점만 튀어오름", "기울기로 상승", "전체가 위로 이탈"]

    def setup(ax):
        ax.set_ylim(-2.0, 3.0)
        ax.axhspan(-0.65, 0.65, color="#EEF1F5", zorder=0)        # 정상 범위 참조 띠
        ax.axvline(cut, color="#CBD2DC", lw=0.9, ls=(0, (3, 3)))
        _spines(ax); ax.set_xticks([]); ax.set_yticks([])

    def normal(ax):
        ax.scatter(tn, rng.normal(0, 0.2, cut), s=8, color=BLUE, alpha=0.8, edgecolors="none")

    # avg — 계단처럼 평균이 위로
    ax = axs[0]; setup(ax); normal(ax)
    ax.scatter(ta, rng.normal(1.7, 0.18, na), s=9, color=RED, alpha=0.9, edgecolors="none")
    ax.plot([0, cut], [0, 0], color=BLUE, lw=1.6)
    ax.plot([cut, n - 1], [1.7, 1.7], color=RED, lw=2.0)
    ax.annotate("", xy=(cut + 2, 1.6), xytext=(cut + 2, 0.1),
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.4))

    # std — 평균 그대로, 위아래로 넓게 퍼짐 (엔벨로프)
    ax = axs[1]; setup(ax); normal(ax)
    ax.scatter(ta, rng.normal(0, 0.95, na), s=9, color=RED, alpha=0.85, edgecolors="none")
    for s in (1, -1):
        ax.plot([cut, n - 1], [0.25 * s, 2.0 * s], color=RED, lw=1.4, ls=(0, (4, 3)))

    # spike — 평소 잠잠, 몇 점만 솟구침 (스템)
    ax = axs[2]; setup(ax); normal(ax)
    ax.scatter(ta, rng.normal(0, 0.18, na), s=8, color=RED, alpha=0.5, edgecolors="none")
    for s in sorted(rng.choice(np.arange(4, na - 3), 3, replace=False)):
        ax.plot([cut + s, cut + s], [0, 2.5], color=RED, lw=1.6, zorder=4)
        ax.scatter([cut + s], [2.5], s=42, color=RED, zorder=5, edgecolors="white", lw=0.8)

    # drift — 추세선 따라 서서히 상승
    ax = axs[3]; setup(ax); normal(ax)
    ramp = np.linspace(0, 2.3, na)
    ax.scatter(ta, ramp + rng.normal(0, 0.12, na), s=9, color=RED, alpha=0.85, edgecolors="none")
    ax.plot(ta, ramp, color=RED, lw=2.2)

    # context — 오른쪽 끝이 아니라 전체가 fleet 위로
    ax = axs[4]; setup(ax)
    for _ in range(4):
        ax.plot(t, rng.normal(0, 0.16, n) + rng.uniform(-0.12, 0.12), color=GRY, lw=0.9, alpha=0.7)
    ax.plot(t, rng.normal(0, 0.14, n) + 1.7, color=RED, lw=2.0)

    for ax, ti, su in zip(axs, titles, subs):
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


def fig_regions():
    rng = np.random.default_rng(7)
    fig, ax = plt.subplots(figsize=(13.0, 4.0), dpi=200); fig.patch.set_facecolor("white")
    draw_regions(ax, rng)
    fig.tight_layout()
    fig.savefig(FIG + "/p3_deck_regions.png", facecolor="white", bbox_inches="tight")
    print("wrote regions"); plt.close(fig)


def fig_noise():
    rng = np.random.default_rng(3)
    fig, axs = plt.subplots(1, 3, figsize=(13.4, 3.5), dpi=200); fig.patch.set_facecolor("white")
    draw_noise(axs, rng)
    fig.tight_layout()
    fig.savefig(FIG + "/p3_deck_noise.png", facecolor="white", bbox_inches="tight")
    print("wrote noise"); plt.close(fig)


def fig_anomaly():
    rng = np.random.default_rng(11)
    fig, axs = plt.subplots(1, 5, figsize=(16.0, 3.3), dpi=200); fig.patch.set_facecolor("white")
    draw_anomaly(axs, rng)
    fig.tight_layout()
    fig.savefig(FIG + "/p3_deck_anomaly.png", facecolor="white", bbox_inches="tight")
    print("wrote anomaly"); plt.close(fig)


def fig_baseline():
    """정상 baseline 한 장: (a) 영역(위 전폭) + (b) 노이즈 3종(아래). slide 3 용."""
    fig = plt.figure(figsize=(13.8, 5.3), dpi=200); fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 0.8], hspace=0.6,
                          left=0.055, right=0.985, top=0.89, bottom=0.10)
    ax_reg = fig.add_subplot(gs[0])
    ng = gs[1].subgridspec(1, 3, wspace=0.26)
    ax_n = [fig.add_subplot(ng[i]) for i in range(3)]
    draw_regions(ax_reg, np.random.default_rng(7))
    draw_noise(ax_n, np.random.default_rng(3))

    def sec(aL, aR, text):
        p0 = aL.get_position(); p1 = aR.get_position()
        fig.text((p0.x0 + p1.x1) / 2, p0.y1 + 0.045, text, ha="center", va="bottom",
                 fontsize=13, color=NAVY, fontweight="bold")
    sec(ax_reg, ax_reg, "(a) 정상 baseline — 밀집/희소/결핍 영역")
    sec(ax_n[0], ax_n[2], "(b) 계측 노이즈 3종")
    out = FIG + "/p3_deck_baseline.png"
    fig.savefig(out, facecolor="white"); print("wrote baseline"); plt.close(fig)


if __name__ == "__main__":
    fig_combined()
    fig_regions()
    fig_noise()
    fig_anomaly()
    fig_baseline()
