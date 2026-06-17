"""P3(계측 trend 이상탐지 데이터 생성) 발표 figure — 실제 생성/렌더 방식 + 검증 결과에 충실하게.
근거: anomaly-detection 코드/문서 + 논문/웹(piecewise/regime, Mean shift/Variance/Spike/Trend/Contextual).
규약: scatter(선X), 회색 fleet + highlighted member(정상 파랑/이상 빨강), 평탄 baseline+가로 기준선,
episode(구간)마다 측정 밀도와 산포가 함께 변함, 결핍=빈 구간, 이상은 오른쪽 끝(context만 전체), 빨강 음영=이상 구간.
출력: p3_deck_baseline.png(영역+노이즈), p3_deck_types.png(정상+이상 6종), p3_deck_result.png(검증 결과)
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
GRAYF = "#AEB4BD"; BL = "#3A6FD0"; RD = "#CC3328"; GRN = "#2BA66B"
RBAND = "#F6E4E2"  # 이상 구간 음영
FIG = r"D:/project/fbm_paper/recommendation/figures"


def _spines(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#C7CDD6")
    ax.tick_params(labelsize=8, length=0, colors=MUT)
    ax.grid(True, color="#EEF1F5", lw=0.7, zorder=0)


# ── (a) 정상 baseline: episode 구조 — 회색 fleet + 파랑 highlighted, 밀도와 산포가 구간마다 변함 ──
def draw_baseline_chart(ax, rng):
    episodes = [("밀집", 60, 0.90, "dense"), ("희소", 46, 0.50, "sparse"),
                ("결핍", 30, 0.0, "missing"), ("밀집", 64, 0.90, "dense"),
                ("희소", 42, 0.48, "sparse"), ("thin", 34, 0.16, "thin"),
                ("밀집", 58, 0.88, "dense"), ("결핍", 26, 0.0, "missing"),
                ("밀집", 52, 0.85, "dense")]
    band = {"dense": "#EAF0F8", "sparse": "#FBF4E5", "missing": "#FBECEA", "thin": "#F2F3F6"}
    edge = {"dense": NAVY, "sparse": "#C98A22", "missing": "#CC3328", "thin": MUT}
    nfleet = 5
    foff = rng.normal(0, 0.018, nfleet)
    sig = 0.05   # 노이즈는 chart당 1종 → 산포 폭 동일. episode마다 변하는 건 밀도/결측/길이
    x0 = 0; shown = set()
    for label, length, dens, kind in episodes:
        x1 = x0 + length
        ax.axvspan(x0, x1, color=band[kind], zorder=0)
        ax.axvline(x1, color="#DDE2EA", lw=0.7, zorder=1)
        if dens > 0:
            npts = max(2, int(length * dens))
            for m in range(nfleet):
                ax.scatter(rng.uniform(x0, x1, npts), foff[m] + rng.normal(0, sig, npts),
                           s=6, color=GRAYF, alpha=0.40, edgecolors="none", zorder=2)
            ax.scatter(rng.uniform(x0, x1, npts), rng.normal(0, sig, npts),
                       s=12, color=BL, alpha=0.85, edgecolors="none", zorder=3)
        if kind not in shown:
            ax.text((x0 + x1) / 2, 0.305, label, ha="center", va="top", fontsize=9.5,
                    color=edge.get(kind, MUT), fontweight="bold")
            shown.add(kind)
        x0 = x1
    ax.axhline(0, color="#8A929E", lw=1.0, ls=(0, (5, 4)), zorder=1)
    ax.set_xlim(0, x0); ax.set_ylim(-0.36, 0.33)
    ax.set_ylabel("Measurement (정규화)", fontsize=8.5, color=MUT)
    ax.set_xlabel("time index — episode(구간)마다 측정 밀도/결측/길이가 다름 (노이즈는 chart당 1종)", fontsize=8.5, color=MUT)
    _spines(ax)


# ── (b) 노이즈 3종 ──
def draw_noise(axs, rng):
    n = 120; t = np.arange(n)
    axs[0].plot(t, rng.normal(0, 0.3, n), color=NAVY, lw=0.9, alpha=0.9, marker="o", ms=2.0, mfc=NAVY, mec="none")
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
    sec(ax_b, ax_b, "(a) 정상 baseline — 회색 fleet + 파랑 highlighted, episode 구간마다 밀도/결측이 변함")
    sec(ax_n[0], ax_n[2], "(b) 계측 노이즈 3종 (chart당 1종)")
    fig.savefig(FIG + "/p3_deck_baseline.png", facecolor="white"); print("wrote baseline"); plt.close(fig)


# ── 정상 + 이상 5종: fleet(회색) + highlighted, 이상 구간 빨강 음영 ──
def _type_panel(ax, kind, rng):
    n = 100; t = np.arange(n); cut = 66
    ax.set_ylim(-1.5, 2.8); _spines(ax); ax.set_xticks([]); ax.set_yticks([])
    ax.axhline(0, color="#E4E8EE", lw=0.7)
    for _ in range(4):  # fleet
        ax.scatter(t, rng.normal(0, 0.05) + rng.normal(0, 0.16, n), s=5, color=GRAYF, alpha=0.36, edgecolors="none", zorder=1)
    if kind == "normal":
        ax.scatter(t, rng.normal(0, 0.16, n), s=9, color=BL, alpha=0.85, edgecolors="none", zorder=3)
        return
    if kind == "context":  # 전체가 fleet 위로
        ax.axvspan(0, n, color=RBAND, zorder=0)
        ax.scatter(t, rng.normal(1.5, 0.16, n), s=9, color=RD, alpha=0.85, edgecolors="none", zorder=3)
        return
    ax.axvspan(cut, n, color=RBAND, zorder=0)   # 이상 구간(오른쪽 끝) 음영
    ax.scatter(t[:cut], rng.normal(0, 0.16, cut), s=9, color=BL, alpha=0.85, edgecolors="none", zorder=3)
    if kind == "mean":
        ax.scatter(t[cut:], rng.normal(1.5, 0.16, n - cut), s=10, color=RD, alpha=0.9, edgecolors="none", zorder=4)
        ax.plot([cut, n - 1], [1.5, 1.5], color=RD, lw=1.8)
    elif kind == "std":
        ax.scatter(t[cut:], rng.normal(0, 0.9, n - cut), s=10, color=RD, alpha=0.85, edgecolors="none", zorder=4)
        for s in (1, -1):
            ax.plot([cut, n - 1], [0.3 * s, 1.9 * s], color=RD, lw=1.2, ls=(0, (4, 3)))
    elif kind == "spike":
        ax.scatter(t[cut:], rng.normal(0, 0.16, n - cut), s=9, color=RD, alpha=0.5, edgecolors="none", zorder=3)
        for s in sorted(rng.choice(np.arange(3, n - cut - 3), 3, replace=False)):
            ax.plot([cut + s, cut + s], [0, 2.4], color=RD, lw=1.5, zorder=4)
            ax.scatter([cut + s], [2.4], s=40, color=RD, zorder=5, edgecolors="white", lw=0.7)
    elif kind == "drift":
        ramp = np.linspace(0, 2.2, n - cut)
        ax.scatter(t[cut:], ramp + rng.normal(0, 0.12, n - cut), s=10, color=RD, alpha=0.85, edgecolors="none", zorder=4)
        ax.plot(t[cut:], ramp, color=RD, lw=2.0)


def fig_types():
    specs = [("normal", "Normal — 정상"), ("mean", "Mean shift — 평균 이동"),
             ("std", "Variance — 산포 확대"), ("spike", "Spike — 순간 급등"),
             ("drift", "Trend drift — 선형 상승"), ("context", "Contextual — 전체 이탈")]
    fig, axs = plt.subplots(2, 3, figsize=(13.8, 6.0), dpi=195); fig.patch.set_facecolor("white")
    axs = axs.ravel()
    rng = np.random.default_rng(11)
    for ax, (kind, title) in zip(axs, specs):
        _type_panel(ax, kind, rng)
        ax.set_title(title, fontsize=11, color=(NAVY if kind == "normal" else NAVY), fontweight="bold", pad=5)
    fig.text(0.5, 0.012, "회색 = fleet(다른 설비) · 파랑 = 판정 대상 정상 · 빨강 = 주입된 이상 · 분홍 음영 = 이상 구간",
             ha="center", color=MUT, fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG + "/p3_deck_types.png", facecolor="white"); print("wrote types"); plt.close(fig)


# ── 1차 binary gate 검증 결과: confusion + NT trade-off + 유형별 오류 ──
def fig_result():
    fig, axs = plt.subplots(1, 3, figsize=(14.6, 3.9), dpi=195,
                            gridspec_kw=dict(width_ratios=[1.0, 1.05, 1.15]))
    fig.patch.set_facecolor("white")

    # (1) Confusion 2x2 (746/4 // 1/749)
    ax = axs[0]; ax.set_xlim(0, 2); ax.set_ylim(0, 2); ax.axis("off")
    cells = [[("746", "TN", GRN), ("4", "FP", RD)], [("1", "FN", RD), ("749", "TP", GRN)]]
    for r in range(2):
        for c in range(2):
            val, tag, col = cells[r][c]
            yy = 1 - r
            ax.add_patch(plt.Rectangle((c, yy), 1, 1, fc=col, alpha=0.12, ec=col, lw=1.4))
            ax.text(c + 0.5, yy + 0.60, val, ha="center", va="center", fontsize=19, color=NAVY, fontweight="bold")
            ax.text(c + 0.5, yy + 0.24, tag, ha="center", va="center", fontsize=10, color=col, fontweight="bold")
    ax.text(0.5, 2.18, "예측 정상", ha="center", fontsize=9.5, color=MUT)
    ax.text(1.5, 2.18, "예측 불량", ha="center", fontsize=9.5, color=MUT)
    ax.text(-0.08, 1.5, "실제\n정상", ha="center", va="center", fontsize=9.5, color=MUT)
    ax.text(-0.08, 0.5, "실제\n불량", ha="center", va="center", fontsize=9.5, color=MUT)
    ax.set_title("Confusion (test 1,500, NT 0.9)", fontsize=11, color=NAVY, fontweight="bold", pad=10)

    # (2) NT trade-off (319-run 평균)
    ax = axs[1]
    nts = ["0.9", "0.99", "0.999"]; fn = [3.80, 2.74, 1.75]; fp = [2.91, 3.65, 5.12]
    ax.plot(nts, fn, marker="o", color=RD, lw=2.0, label="FN (놓친 불량)")
    ax.plot(nts, fp, marker="o", color=BL, lw=2.0, label="FP (정상 오경보)")
    ax.set_ylim(0, 6); _spines(ax)
    ax.set_xlabel("normal threshold (NT)", fontsize=8.5, color=MUT)
    ax.legend(fontsize=8.5, frameon=False, loc="upper center")
    ax.set_title("NT 올릴수록 FN↓ / FP↑ (평균)", fontsize=11, color=NAVY, fontweight="bold", pad=10)

    # (3) 유형별 오류 (정상 FP 4, std FN 1, 나머지 0)
    ax = axs[2]
    cats = ["정상", "std", "mean", "spike", "drift", "context"]
    fp_t = [4, 0, 0, 0, 0, 0]; fn_t = [0, 1, 0, 0, 0, 0]
    xpos = np.arange(len(cats))
    ax.bar(xpos - 0.18, fp_t, width=0.34, color=BL, label="FP")
    ax.bar(xpos + 0.18, fn_t, width=0.34, color=RD, label="FN")
    ax.set_xticks(xpos); ax.set_xticklabels(cats, fontsize=8.5, color=MUT)
    ax.set_ylim(0, 5); _spines(ax); ax.tick_params(labelbottom=True)
    ax.legend(fontsize=8.5, frameon=False, loc="upper right")
    ax.set_title("유형별 오류 — std만 FN 1, 나머지 0", fontsize=11, color=NAVY, fontweight="bold", pad=10)

    fig.tight_layout()
    fig.savefig(FIG + "/p3_deck_result.png", facecolor="white"); print("wrote result"); plt.close(fig)


def fig_ablation():
    """조건별 단독(single-axis) 실험 — baseline 대비 F1↑ / 놓친 불량 FN↓ (5-seed 평균)."""
    conds = [("baseline", 0.9944, 4.6, "ref"),
             ("Focal γ\n2.0", 0.9964, 2.4, "imp"),
             ("EMA\n0.95", 0.9964, 2.2, "imp"),
             ("Label smooth\n0.02", 0.9981, 0.8, "imp"),
             ("Stoch.Depth\n0.05", 0.9985, 0.8, "imp"),
             ("정상비율↑\n(3300)", 0.9988, 0.8, "best")]
    labels = [c[0] for c in conds]; f1 = [c[1] for c in conds]; fn = [c[2] for c in conds]
    cmap = {"ref": GRAYF, "imp": TEAL, "best": NAVY}
    cols = [cmap[c[3]] for c in conds]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13.8, 4.3), dpi=195); fig.patch.set_facecolor("white")
    x = np.arange(len(conds))
    a1.bar(x, f1, color=cols, width=0.62, zorder=3)
    a1.axhline(0.9944, color=GRAYF, ls=(0, (4, 3)), lw=1, zorder=2)
    a1.set_ylim(0.992, 0.9995)
    for i, v in enumerate(f1):
        a1.text(i, v + 0.00004, f"{v:.4f}", ha="center", fontsize=8.5, color=NAVY, fontweight="bold")
    a1.set_title("binary F1  (↑ 좋음)", fontsize=12, color=NAVY, fontweight="bold", pad=8)
    a2.bar(x, fn, color=cols, width=0.62, zorder=3)
    a2.axhline(4.6, color=GRAYF, ls=(0, (4, 3)), lw=1, zorder=2)
    a2.set_ylim(0, 5.4)
    for i, v in enumerate(fn):
        a2.text(i, v + 0.12, f"{v:.1f}", ha="center", fontsize=8.5, color=NAVY, fontweight="bold")
    a2.set_title("놓친 불량 FN  (↓ 좋음)", fontsize=12, color=NAVY, fontweight="bold", pad=8)
    for a in (a1, a2):
        _spines(a); a.set_xticks(x); a.set_xticklabels(labels, fontsize=8.5, color=MUT)
        a.tick_params(labelbottom=True, labelleft=True)
    fig.tight_layout()
    fig.savefig(FIG + "/p3_deck_ablation.png", facecolor="white"); print("wrote ablation"); plt.close(fig)


if __name__ == "__main__":
    fig_baseline()
    fig_types()
    fig_ablation()
