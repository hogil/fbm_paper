"""P3(계측 trend 이상탐지 데이터 생성) 발표 figure — 실제 생성/렌더 방식에 충실하게.
근거(anomaly-detection 코드): scatter(선 없음), fleet=회색 다수 + highlighted member 1개(정상 파랑/이상 빨강),
거의 평탄한 OU baseline + 가로 기준선, 영역(episode)마다 '밀도'만 다르고 산포 폭은 동일, 결핍=빈 구간,
이상은 오른쪽 끝(context만 전체). 표준용어: piecewise/regime segment, Mean shift/Variance/Spike/Trend/Contextual,
노이즈 Gaussian iid / AR(1) correlated / Laplacian heavy-tail.
출력: p3_deck_baseline.png (영역+노이즈), p3_deck_anomaly.png (이상 5종)
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

NAVY = "#0F1E3D"; TEAL = "#12B5B0"; MUT = "#6B7280"
GRAYF = "#AEB4BD"   # fleet member (회색, 뒤로 물러남)
BL = "#3A6FD0"      # highlighted member 정상(파랑)
RD = "#D62728"      # highlighted member 이상(빨강)
FIG = r"D:/project/fbm_paper/recommendation/figures"


def _spines(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#C7CDD6")
    ax.tick_params(labelsize=8, length=0, colors=MUT)
    ax.grid(True, color="#EEF1F5", lw=0.7, zorder=0)


# ── 정상 baseline + episode(영역) 구조: fleet 회색 + highlighted 파랑, 밀도만 변함 ──
def draw_baseline_chart(ax, rng):
    # (라벨, 길이, density) — 산포 폭은 모든 구간 동일, density(점이 찍히는 비율)만 다름
    episodes = [("밀집", 60, 0.90, "dense"), ("희소", 46, 0.50, "sparse"),
                ("결핍", 30, 0.0, "missing"), ("밀집", 64, 0.90, "dense"),
                ("희소", 42, 0.48, "sparse"), ("thin", 34, 0.16, "thin"),
                ("밀집", 58, 0.88, "dense"), ("결핍", 26, 0.0, "missing"),
                ("밀집", 52, 0.85, "dense")]
    band = {"dense": "#EAF0F8", "sparse": "#FBF4E5", "missing": "#FBECEA",
            "thin": "#F2F3F6", "vs": "#F2F3F6"}
    edge = {"dense": NAVY, "sparse": "#C98A22", "missing": "#CC3328", "thin": MUT}
    nfleet = 5
    foff = rng.normal(0, 0.018, nfleet)
    sigma = 0.05  # 모든 구간 동일한 산포 폭
    x0 = 0; shown = set()
    for label, length, dens, kind in episodes:
        x1 = x0 + length
        ax.axvspan(x0, x1, color=band[kind], zorder=0)
        ax.axvline(x1, color="#DDE2EA", lw=0.7, zorder=1)
        if dens > 0:
            npts = max(2, int(length * dens))
            for m in range(nfleet):
                ax.scatter(rng.uniform(x0, x1, npts), foff[m] + rng.normal(0, sigma, npts),
                           s=6, color=GRAYF, alpha=0.40, edgecolors="none", zorder=2)
            ax.scatter(rng.uniform(x0, x1, npts), rng.normal(0, sigma, npts),
                       s=12, color=BL, alpha=0.85, edgecolors="none", zorder=3)
        if kind not in shown:
            ax.text((x0 + x1) / 2, 0.295, label, ha="center", va="top", fontsize=9.5,
                    color=edge.get(kind, MUT), fontweight="bold")
            shown.add(kind)
        x0 = x1
    ax.axhline(0, color="#8A929E", lw=1.0, ls=(0, (5, 4)), zorder=1)
    ax.set_xlim(0, x0); ax.set_ylim(-0.33, 0.31)
    ax.set_ylabel("Measurement (정규화)", fontsize=8.5, color=MUT)
    ax.set_xlabel("time index — episode(구간)를 이어 붙임", fontsize=8.5, color=MUT)
    _spines(ax)


# ── 노이즈 3종: 도메인 의미 + 통계 모델 1:1 ──
def draw_noise(axs, rng):
    n = 120; t = np.arange(n)
    g = rng.normal(0, 0.3, n)
    axs[0].plot(t, g, color=NAVY, lw=0.9, alpha=0.9, marker="o", ms=2.0, mfc=NAVY, mec="none")
    axs[0].set_title("산포 — Gaussian iid", fontsize=10.5, color=NAVY, fontweight="bold", pad=5)
    axs[0].set_xlabel("기본 계측 산포", fontsize=8.5, color=MUT)
    a = np.zeros(n)
    for i in range(1, n):
        a[i] = 0.93 * a[i - 1] + rng.normal(0, 0.12)
    axs[1].plot(t, a, color=TEAL, lw=1.7); axs[1].fill_between(t, a, color=TEAL, alpha=0.10)
    axs[1].set_title("설비 상태변동 — AR(1)", fontsize=10.5, color=NAVY, fontweight="bold", pad=5)
    axs[1].set_xlabel("천천히 끌리는 상관 변동", fontsize=8.5, color=MUT)
    lp = rng.laplace(0, 0.10, n)
    axs[2].plot(t, lp, color=NAVY, lw=0.8, alpha=0.85, marker="o", ms=1.8, mfc=NAVY, mec="none")
    big = np.argsort(np.abs(lp))[-4:]
    axs[2].scatter(t[big], lp[big], s=40, color=RD, zorder=5, edgecolors="white", lw=0.7)
    axs[2].set_title("계측 헌팅 — Laplacian", fontsize=10.5, color=NAVY, fontweight="bold", pad=5)
    axs[2].set_xlabel("한 번씩 크게 튀는 heavy-tail", fontsize=8.5, color=MUT)
    for ax in axs:
        ax.set_ylim(-1.15, 1.15); ax.axhline(0, color="#D5DBE3", lw=0.7, zorder=1)
        _spines(ax); ax.set_xticks([])


# ── 이상 5종: fleet(회색) 대비 highlighted member가 어떻게 벗어나나 ──
def draw_anomaly(axs, rng):
    n = 100; t = np.arange(n); cut = 66
    names = ["Mean shift", "Variance", "Spike", "Trend drift", "Contextual"]
    subs = ["평균 이동 (avg)", "산포 확대 (std)", "순간 급등 (spike)", "선형 상승 (drift)", "전체 이탈 (context)"]

    def fleet(ax):
        for _ in range(4):
            off = rng.normal(0, 0.05)
            ax.scatter(t, off + rng.normal(0, 0.17, n), s=5, color=GRAYF, alpha=0.38, edgecolors="none", zorder=1)

    def setup(ax, cutline=True):
        ax.set_ylim(-1.5, 2.7); _spines(ax); ax.set_xticks([]); ax.set_yticks([])
        ax.axhline(0, color="#E4E8EE", lw=0.7)
        if cutline:
            ax.axvline(cut, color="#CBD2DC", lw=0.9, ls=(0, (3, 3)))

    def hl_normal(ax, upto):
        ax.scatter(t[:upto], rng.normal(0, 0.17, upto), s=9, color=BL, alpha=0.85, edgecolors="none", zorder=3)

    # Mean shift — 오른쪽이 평행하게 위로
    ax = axs[0]; setup(ax); fleet(ax); hl_normal(ax, cut)
    ax.scatter(t[cut:], rng.normal(1.5, 0.16, n - cut), s=10, color=RD, alpha=0.9, edgecolors="none", zorder=4)
    ax.plot([cut, n - 1], [1.5, 1.5], color=RD, lw=2.0)
    ax.annotate("", xy=(cut + 2, 1.4), xytext=(cut + 2, 0.15), arrowprops=dict(arrowstyle="->", color=RD, lw=1.4))

    # Variance — 평균 그대로, 오른쪽 산포만 넓게
    ax = axs[1]; setup(ax); fleet(ax); hl_normal(ax, cut)
    ax.scatter(t[cut:], rng.normal(0, 0.9, n - cut), s=10, color=RD, alpha=0.85, edgecolors="none", zorder=4)
    for s in (1, -1):
        ax.plot([cut, n - 1], [0.3 * s, 1.9 * s], color=RD, lw=1.3, ls=(0, (4, 3)))

    # Spike — 오른쪽 몇 점만 솟구침
    ax = axs[2]; setup(ax); fleet(ax); hl_normal(ax, cut)
    base_r = rng.normal(0, 0.17, n - cut)
    ax.scatter(t[cut:], base_r, s=9, color=RD, alpha=0.5, edgecolors="none", zorder=3)
    for s in sorted(rng.choice(np.arange(3, n - cut - 3), 3, replace=False)):
        ax.plot([cut + s, cut + s], [0, 2.4], color=RD, lw=1.6, zorder=4)
        ax.scatter([cut + s], [2.4], s=44, color=RD, zorder=5, edgecolors="white", lw=0.8)

    # Trend drift — 오른쪽으로 선형 상승
    ax = axs[3]; setup(ax); fleet(ax); hl_normal(ax, cut)
    ramp = np.linspace(0, 2.2, n - cut)
    ax.scatter(t[cut:], ramp + rng.normal(0, 0.12, n - cut), s=10, color=RD, alpha=0.85, edgecolors="none", zorder=4)
    ax.plot(t[cut:], ramp, color=RD, lw=2.2)

    # Contextual — 오른쪽 국소가 아니라 전체가 fleet 위로
    ax = axs[4]; setup(ax, cutline=False); fleet(ax)
    ax.scatter(t, rng.normal(1.5, 0.16, n), s=9, color=RD, alpha=0.85, edgecolors="none", zorder=4)
    ax.annotate("fleet", xy=(8, 0.1), fontsize=8, color=MUT)

    for ax, nm, su in zip(axs, names, subs):
        ax.set_title(nm, fontsize=10.5, color=NAVY, fontweight="bold", pad=5)
        ax.set_xlabel(su, fontsize=8.5, color=MUT)


def fig_baseline():
    fig = plt.figure(figsize=(13.8, 5.4), dpi=200); fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 0.78], hspace=0.62,
                          left=0.06, right=0.985, top=0.88, bottom=0.10)
    ax_b = fig.add_subplot(gs[0])
    ng = gs[1].subgridspec(1, 3, wspace=0.26)
    ax_n = [fig.add_subplot(ng[i]) for i in range(3)]
    draw_baseline_chart(ax_b, np.random.default_rng(7))
    draw_noise(ax_n, np.random.default_rng(3))

    def sec(aL, aR, text):
        p0 = aL.get_position(); p1 = aR.get_position()
        fig.text((p0.x0 + p1.x1) / 2, p0.y1 + 0.04, text, ha="center", va="bottom",
                 fontsize=12.5, color=NAVY, fontweight="bold")
    sec(ax_b, ax_b, "(a) 정상 baseline — 회색 fleet + 파랑 highlighted, 영역마다 측정 밀도만 다름")
    sec(ax_n[0], ax_n[2], "(b) 계측 노이즈 3종 (chart당 1종)")
    fig.savefig(FIG + "/p3_deck_baseline.png", facecolor="white"); print("wrote baseline"); plt.close(fig)


def fig_anomaly():
    fig, axs = plt.subplots(1, 5, figsize=(16.0, 3.3), dpi=200); fig.patch.set_facecolor("white")
    draw_anomaly(axs, np.random.default_rng(11))
    fig.tight_layout()
    fig.savefig(FIG + "/p3_deck_anomaly.png", facecolor="white", bbox_inches="tight")
    print("wrote anomaly"); plt.close(fig)


if __name__ == "__main__":
    fig_baseline()
    fig_anomaly()
