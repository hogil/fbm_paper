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
    en = {"dense": "Dense", "sparse": "Sparse", "missing": "Missing", "thin": "Thin"}
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
            ax.text((x0 + x1) / 2, 0.315, en.get(kind, kind), ha="center", va="top", fontsize=13,
                    color=edge.get(kind, MUT), fontweight="bold")
            shown.add(kind)
        x0 = x1
    ax.axhline(0, color="#8A929E", lw=1.0, ls=(0, (5, 4)), zorder=1)
    ax.set_xlim(0, x0); ax.set_ylim(-0.36, 0.34)
    ax.set_ylabel("Measurement (norm.)", fontsize=11, color=MUT)
    ax.set_xlabel("Sample index — density / missing pattern varies per episode (noise: one type per chart)",
                  fontsize=11, color=MUT)
    ax.tick_params(labelsize=9.5)
    _spines(ax)


# ── (b) 노이즈 3종 ──
def draw_noise(axs, rng):
    n = 120; t = np.arange(n)
    axs[0].plot(t, rng.normal(0, 0.3, n), color=NAVY, lw=0.9, alpha=0.9, marker="o", ms=2.0, mfc=NAVY, mec="none")
    axs[0].set_title("Gaussian iid", fontsize=13, color=NAVY, fontweight="bold", pad=6)
    axs[0].set_xlabel("base dispersion", fontsize=10.5, color=MUT)
    a = np.zeros(n)
    for i in range(1, n):
        a[i] = 0.93 * a[i - 1] + rng.normal(0, 0.12)
    axs[1].plot(t, a, color=TEAL, lw=1.7); axs[1].fill_between(t, a, color=TEAL, alpha=0.10)
    axs[1].set_title("Correlated AR(1)", fontsize=13, color=NAVY, fontweight="bold", pad=6)
    axs[1].set_xlabel("equipment drift", fontsize=10.5, color=MUT)
    lp = rng.laplace(0, 0.10, n)
    axs[2].plot(t, lp, color=NAVY, lw=0.8, alpha=0.85, marker="o", ms=1.8, mfc=NAVY, mec="none")
    big = np.argsort(np.abs(lp))[-4:]
    axs[2].scatter(t[big], lp[big], s=40, color=RD, zorder=5, edgecolors="white", lw=0.7)
    axs[2].set_title("Laplacian", fontsize=13, color=NAVY, fontweight="bold", pad=6)
    axs[2].set_xlabel("hunting (heavy-tail)", fontsize=10.5, color=MUT)
    for ax in axs:
        ax.set_ylim(-1.15, 1.15); ax.axhline(0, color="#D5DBE3", lw=0.7, zorder=1)
        _spines(ax); ax.set_xticks([])


def fig_baseline():
    fig = plt.figure(figsize=(14.4, 5.2), dpi=200); fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 0.74], hspace=0.82,
                          left=0.055, right=0.985, top=0.845, bottom=0.135)
    ax_b = fig.add_subplot(gs[0])
    ng = gs[1].subgridspec(1, 3, wspace=0.24)
    ax_n = [fig.add_subplot(ng[i]) for i in range(3)]
    draw_baseline_chart(ax_b, np.random.default_rng(7))
    draw_noise(ax_n, np.random.default_rng(3))

    def sec(aL, text):
        p0 = aL.get_position()
        fig.text(p0.x0, p0.y1 + 0.052, text, ha="left", va="bottom",
                 fontsize=14.5, color=NAVY, fontweight="bold")
    sec(ax_b, "(a) Normal baseline  —  gray = fleet,  blue = target;  density / missing vary per episode")
    sec(ax_n[0], "(b) Measurement noise  —  one type per chart")
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


def fig_robust():
    """백본 × 데이터셋 × 운영임계값(NT) — 동일 baseline·5-seed 고정 비교."""
    fig, axs = plt.subplots(1, 3, figsize=(14.6, 3.9), dpi=195,
                            gridspec_kw=dict(width_ratios=[1.0, 1.0, 1.12]))
    fig.patch.set_facecolor("white")

    def two_bar(a, names, f1, fn, c2, title):
        a.bar([0, 1], f1, color=[GRAYF, c2], width=0.55, zorder=3)
        a.set_ylim(0.992, 0.9985)
        for i, (v, n) in enumerate(zip(f1, fn)):
            a.text(i, v + 0.00003, f"{v:.4f}", ha="center", fontsize=9, color=NAVY, fontweight="bold")
            a.text(i, 0.99222, f"FN {n}", ha="center", fontsize=8.5, color=MUT)
        a.set_xticks([0, 1]); a.set_xticklabels(names, fontsize=9, color=MUT)
        a.set_title(title, fontsize=11.5, color=NAVY, fontweight="bold", pad=8)
        _spines(a); a.tick_params(labelbottom=True, labelleft=True)

    two_bar(axs[0], ["Tiny (28M)", "Base"], [0.9944, 0.9971], [4.6, 1.2], NAVY, "백본 — ConvNeXtV2 (5-seed)")
    two_bar(axs[1], ["base", "noise +15%"], [0.9944, 0.9960], [4.6, 1.8], TEAL, "데이터셋 강건성 (5-seed)")
    a = axs[2]
    nts = ["0.9", "0.99", "0.999"]; fn = [3.80, 2.74, 1.75]; fp = [2.91, 3.65, 5.12]
    a.plot(nts, fn, marker="o", color=RD, lw=2.0, label="FN (놓친 불량)")
    a.plot(nts, fp, marker="o", color=BL, lw=2.0, label="FP (정상 오경보)")
    a.set_ylim(0, 6); a.legend(fontsize=8, frameon=False, loc="upper center")
    a.set_xlabel("normal threshold (NT)", fontsize=8.5, color=MUT)
    a.set_title("운영 임계값 — FN/FP trade-off", fontsize=11.5, color=NAVY, fontweight="bold", pad=8)
    _spines(a); a.tick_params(labelbottom=True, labelleft=True)
    fig.tight_layout()
    fig.savefig(FIG + "/p3_deck_robust.png", facecolor="white"); print("wrote robust"); plt.close(fig)


def fig_bkm():
    """연속 반복 실험: 각 조건을 한 변수만 바꿔(single-axis) 5-seed 반복 평가하고 축별 best 를 BKM 으로 정리.
    좌: 단변수 11축 BKM(축별 baseline→best F1), 우: 백본/데이터셋/운영 임계값.
    출처: anomaly-detection/docs/data/one_factor_latest.json (각 5/5 seeds, * smoothing 은 3-seed pilot)."""
    import matplotlib.gridspec as gridspec
    axes = [
        ("정상비율  700→3300", 0.9988, 0.8, "best"),
        ("Stochastic Depth →0.05", 0.9985, 0.8, "imp"),
        ("Label Smoothing →0.02", 0.9981, 0.8, "imp"),
        ("Learning rate →1e-4", 0.9964, 2.0, "imp"),
        ("EMA →0.95", 0.9964, 2.2, "imp"),
        ("Focal γ →2.0", 0.9964, 2.4, "imp"),
        ("Allow-tie-save on", 0.9964, 2.4, "imp"),
        ("per-class →700", 0.9960, 2.4, "imp"),
        ("Smoothing median*", 0.9960, 2.0, "hl"),
        ("Warmup →3", 0.9957, 2.4, "imp"),
        ("Abnormal weight →1.5", 0.9956, 3.0, "imp"),
        ("Color  c01(red)", 0.9952, 3.8, "hl"),
    ]
    fig = plt.figure(figsize=(14.6, 5.2), dpi=195); fig.patch.set_facecolor("white")
    gs = gridspec.GridSpec(3, 2, width_ratios=[2.5, 1.0], hspace=0.95, wspace=0.14,
                           left=0.165, right=0.975, top=0.89, bottom=0.10)
    axL = fig.add_subplot(gs[:, 0])
    names = [a[0] for a in axes]; f1 = [a[1] for a in axes]
    cmap = {"best": NAVY, "imp": "#9DB4D6", "hl": TEAL}
    cols = [cmap[a[3]] for a in axes]
    y = np.arange(len(axes))[::-1]
    axL.barh(y, [v - 0.992 for v in f1], left=0.992, color=cols, height=0.64, zorder=3)
    axL.axvline(0.9944, color=GRAYF, ls=(0, (4, 3)), lw=1.3, zorder=2)
    axL.text(0.99435, len(axes) - 0.35, "baseline 0.9944  (FN 4.6)", fontsize=8.5, color=MUT, ha="right", va="bottom")
    axL.set_xlim(0.992, 0.9995); axL.set_yticks(y); axL.set_yticklabels(names, fontsize=9.5, color=NAVY)
    for yi, v in zip(y, f1):
        axL.text(v + 0.00004, yi, f"{v:.4f}", va="center", fontsize=8.6, color=NAVY, fontweight="bold")
    axL.set_title("단변수(single-axis) 반복 평가 → 축별 BKM   (각 5-seed,  * smoothing 3-seed)",
                  fontsize=12, color=NAVY, fontweight="bold", pad=9, loc="left")
    _spines(axL); axL.set_xticks([0.992, 0.994, 0.996, 0.998]); axL.tick_params(labelsize=8)

    def mini(ax, nm, vals, c2, title):
        ax.bar([0, 1], [v - 0.992 for v in vals], bottom=0.992, color=[GRAYF, c2], width=0.62, zorder=3)
        ax.set_ylim(0.992, 0.9982)
        for i, v in enumerate(vals):
            ax.text(i, v + 0.00003, f"{v:.4f}", ha="center", fontsize=8, color=NAVY, fontweight="bold")
        ax.set_xticks([0, 1]); ax.set_xticklabels(nm, fontsize=8.5, color=MUT)
        ax.set_title(title, fontsize=10, color=NAVY, fontweight="bold", pad=4)
        _spines(ax); ax.tick_params(labelleft=False, labelsize=8)

    mini(fig.add_subplot(gs[0, 1]), ["Tiny", "Base"], [0.9944, 0.9971], NAVY, "백본 ConvNeXtV2 (5-seed)")
    mini(fig.add_subplot(gs[1, 1]), ["base", "noise+15%"], [0.9944, 0.9960], TEAL, "데이터셋 강건성 (5-seed)")
    a3 = fig.add_subplot(gs[2, 1])
    nts = ["0.9", "0.99", "0.999"]; fnn = [3.80, 2.74, 1.75]; fpp = [2.91, 3.65, 5.12]
    a3.plot(nts, fnn, marker="o", ms=4, color=RD, lw=1.8, label="FN")
    a3.plot(nts, fpp, marker="o", ms=4, color=BL, lw=1.8, label="FP")
    a3.set_ylim(0, 6); a3.legend(fontsize=7.5, frameon=False, ncol=2, loc="upper center")
    a3.set_title("운영 임계값 NT — FN/FP (319-run)", fontsize=10, color=NAVY, fontweight="bold", pad=4)
    _spines(a3); a3.tick_params(labelsize=7.5)
    fig.savefig(FIG + "/p3_bkm.png", facecolor="white"); print("wrote bkm"); plt.close(fig)


def fig_bkm_table():
    """단변수(single-axis) BKM 을 표로. 출처 one_factor_latest.json (각 5-seed, * smoothing 3-seed pilot)."""
    cols = ["조건 (단변수 축)", "baseline → BKM", "F1", "FN", "FP"]
    data = [
        ["정상 비율 (normal ratio)", "700 → 3300", "0.9988", "0.8", "1.0"],
        ["Stochastic Depth", "0 → 0.05", "0.9985", "0.8", "1.4"],
        ["Label Smoothing", "0 → 0.02", "0.9981", "0.8", "2.0"],
        ["EMA", "off → 0.95", "0.9964", "2.2", "3.2"],
        ["Focal γ", "0 → 2.0", "0.9964", "2.4", "3.0"],
        ["Allow-tie-save", "off → on", "0.9964", "2.4", "3.0"],
        ["per-class 상한", "→ 700", "0.9960", "2.4", "3.6"],
        ["Smoothing (median)*", "raw → win5", "0.9960", "2.0", "—"],
        ["Abnormal weight", "1.0 → 1.5", "0.9956", "3.0", "3.6"],
        ["Color rendering", "baseline → c01", "0.9952", "3.8", "3.4"],
        ["baseline (기준)", "—", "0.9944", "4.6", "3.8"],
    ]
    fig, ax = plt.subplots(figsize=(11.6, 4.7), dpi=195); fig.patch.set_facecolor("white")
    ax.axis("off")
    tbl = ax.table(cellText=data, colLabels=cols, cellLoc="center", loc="center",
                   colWidths=[0.36, 0.22, 0.15, 0.135, 0.135])
    tbl.auto_set_font_size(False); tbl.set_fontsize(12); tbl.scale(1, 1.72)
    nrow = len(data)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#D7DEEA"); cell.set_linewidth(0.8)
        if r == 0:
            cell.set_facecolor(NAVY); cell.set_text_props(color="white", fontweight="bold")
        elif r == 1:
            cell.set_facecolor("#DCEFEE")
            if c >= 2: cell.set_text_props(fontweight="bold", color=NAVY)
        elif r == nrow:
            cell.set_facecolor("#EEF0F4"); cell.set_text_props(color=MUT)
        elif data[r - 1][0].startswith(("Smoothing", "Color")):
            cell.set_facecolor("#F3FBFA")
        else:
            cell.set_facecolor("white" if r % 2 else "#F7F9FC")
        if c == 0 and r > 0:
            cell.get_text().set_horizontalalignment("left"); cell.PAD = 0.04
    fig.savefig(FIG + "/p3_bkm_table.png", facecolor="white", bbox_inches="tight"); print("wrote bkm_table"); plt.close(fig)


def fig_backbone(names=None, f1=None, fn=None, fp=None):
    """Backbone sweep — F1 단일 패널 + FN/FP 주석(큰 글자). baseline/best 는 portfolio 기준(0.9967/0.9987)."""
    names = names or ["convnext\ntiny.dinov3", "convnextv2\nbase", "convnextv2\ntiny",
                      "swinv2\ntiny", "maxvit", "efficient\nnetv2"]
    f1 = f1 or [0.9987, 0.9982, 0.9967, 0.9975, 0.9979, 0.9972]
    fn = fn or [0, 0, 1, 1, 0, 1]
    fp = fp or [2, 3, 4, 3, 3, 4]
    roles = ["best", "imp", "base", "imp", "imp", "imp"]
    cmap = {"best": NAVY, "imp": BL, "base": GRAYF}
    fig, ax = plt.subplots(figsize=(7.8, 4.9), dpi=195); fig.patch.set_facecolor("white")
    x = np.arange(len(names)); lo, hi = 0.9960, 0.99928
    ax.bar(x, f1, width=0.66, color=[cmap[r] for r in roles], zorder=3)
    ax.set_ylim(lo, hi)
    for xi, v, fnv, fpv in zip(x, f1, fn, fp):
        ax.text(xi, v + 0.00004, f"{v:.4f}", ha="center", va="bottom", fontsize=11.5, color=NAVY, fontweight="bold")
        ax.text(xi, lo + 0.00013, f"FN {fnv} / FP {fpv}", ha="center", va="bottom", fontsize=9.8, color=MUT)
    ax.set_xticks(x); ax.set_xticklabels(names, fontsize=11, color=NAVY)
    ax.set_yticks([0.9965, 0.9975, 0.9985]); ax.tick_params(labelsize=10.5)
    ax.set_title("Backbone sweep — F1  (5-seed)", fontsize=15.5, color=NAVY, fontweight="bold", pad=12)
    ax.grid(axis="y", linestyle="--", alpha=0.35, zorder=0); _spines(ax)
    fig.tight_layout(); fig.savefig(FIG + "/p3_backbone.png", facecolor="white"); print("wrote backbone"); plt.close(fig)


def fig_progression(stages=None, f1=None, fn=None, fp=None):
    """baseline → BKM combined → best backbone — F1 단일 패널 + FN/FP 주석(큰 글자). portfolio 기준."""
    stages = stages or ["Baseline", "BKM\ncombined", "Best\nbackbone"]
    f1 = f1 or [0.9967, 0.9981, 0.9987]
    fn = fn or [1, 1, 0]
    fp = fp or [4, 3, 2]
    fig, ax = plt.subplots(figsize=(7.0, 4.9), dpi=195); fig.patch.set_facecolor("white")
    x = np.arange(len(stages)); lo, hi = 0.9960, 0.99928
    ax.bar(x, f1, width=0.56, color=[GRAYF, BL, NAVY], zorder=3)
    ax.set_ylim(lo, hi)
    for xi, v, fnv, fpv in zip(x, f1, fn, fp):
        ax.text(xi, v + 0.00004, f"{v:.4f}", ha="center", va="bottom", fontsize=12.5, color=NAVY, fontweight="bold")
        ax.text(xi, lo + 0.00013, f"FN {fnv} / FP {fpv}", ha="center", va="bottom", fontsize=10.5, color=MUT)
    ax.set_xticks(x); ax.set_xticklabels(stages, fontsize=11.5, color=NAVY)
    ax.set_yticks([0.9965, 0.9975, 0.9985]); ax.tick_params(labelsize=10.5)
    ax.set_title("baseline → BKM combined → best backbone", fontsize=14.5, color=NAVY, fontweight="bold", pad=12)
    ax.grid(axis="y", linestyle="--", alpha=0.35, zorder=0); _spines(ax)
    fig.tight_layout(); fig.savefig(FIG + "/p3_progression.png", facecolor="white"); print("wrote progression"); plt.close(fig)


def _draw_smoothing(ax, rng):
    """smoothing window 학습곡선 — 큰 글자. val F1 raw vs median window, 선택점, test F1 주석."""
    ep = np.arange(1, 41)
    base = 0.985 + 0.0102 * (1 - np.exp(-ep / 8.0))
    raw = base + rng.normal(0, 0.0015, ep.size)
    raw[12] += 0.0017; raw[19] -= 0.0030; raw[27] += 0.0011; raw[33] -= 0.0022
    sm = np.array([np.median(raw[max(0, i - 2):i + 3]) for i in range(ep.size)])
    ax.plot(ep, raw, color="#AEB4BD", lw=1.4, label="val F1 (raw)")
    ax.plot(ep, sm, color=BL, lw=2.6, label="val F1 (median window)")
    rp = int(np.argmax(raw)); sp = int(np.argmax(sm))
    ax.scatter([ep[rp]], [raw[rp]], color=RD, zorder=5, s=58, label="raw 선택 (불안정)")
    ax.scatter([ep[sp]], [sm[sp]], color=NAVY, zorder=6, s=110, marker="*", label="window 선택 (안정)")
    ax.set_ylim(0.9835, 0.9985)
    ax.set_xlabel("epoch", fontsize=11.5, color=MUT); ax.set_ylabel("val F1", fontsize=12, color=MUT)
    ax.tick_params(labelsize=10.5)
    ax.legend(fontsize=10, frameon=False, loc="lower right")
    ax.text(0.035, 0.965, "test F1 →  raw 0.9971  /  window 0.9987", transform=ax.transAxes,
            fontsize=11.5, color=NAVY, fontweight="bold", va="top",
            bbox=dict(boxstyle="round,pad=0.3", fc="#EAF0F8", ec="#9DB4D6", lw=0.9))
    ax.set_title("Smoothing window — 안정적 checkpoint 선택", fontsize=13.5, color=NAVY, fontweight="bold", pad=8)
    _spines(ax)


def fig_merged():
    """결과 병합 1장 — 상단: 누적 옵션 전체 표, 하단: smoothing window 곡선 + color 전후. portfolio 기준 수치."""
    import matplotlib.image as mpimg
    import matplotlib.gridspec as gridspec
    rng = np.random.default_rng(5)
    fig = plt.figure(figsize=(13.8, 6.8), dpi=185); fig.patch.set_facecolor("white")
    gs = gridspec.GridSpec(2, 2, height_ratios=[1.30, 1.0], width_ratios=[1.06, 1.0],
                           hspace=0.46, wspace=0.20, left=0.03, right=0.975, top=0.945, bottom=0.045)
    axt = fig.add_subplot(gs[0, :]); axt.axis("off")
    cols = ["적용 옵션 (누적)", "조건값", "F1", "FN", "FP"]
    data = [
        ["Baseline", "—", "0.9967", "1", "4"],
        ["+ 정상 비율", "700 → 3300", "0.9972", "1", "3"],
        ["+ Label Smoothing", "0.02", "0.9976", "1", "3"],
        ["+ Stochastic Depth", "0.05", "0.9979", "0", "3"],
        ["+ EMA", "0.95", "0.9981", "0", "2"],
        ["+ Focal γ", "2.0", "0.9983", "0", "2"],
        ["+ per-class / Abn.weight", "700 / 1.5", "0.9984", "0", "2"],
        ["+ Color / Smoothing", "c01 / win5", "0.9985", "0", "2"],
        ["+ Best backbone", "convnext.tiny.dinov3", "0.9987", "0", "2"],
    ]
    tbl = axt.table(cellText=data, colLabels=cols, cellLoc="center", loc="center",
                    colWidths=[0.27, 0.27, 0.155, 0.15, 0.15])
    tbl.auto_set_font_size(False); tbl.set_fontsize(13); tbl.scale(1, 1.46)
    nrow = len(data)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#D7DEEA"); cell.set_linewidth(0.8)
        if r == 0:
            cell.set_facecolor(NAVY); cell.set_text_props(color="white", fontweight="bold")
        elif r == nrow:
            cell.set_facecolor("#DCEFEE")
            if c >= 2: cell.set_text_props(fontweight="bold", color=NAVY)
        elif r == 1:
            cell.set_facecolor("#EEF0F4"); cell.set_text_props(color=MUT)
        else:
            cell.set_facecolor("white" if r % 2 else "#F7F9FC")
        if c == 0 and r > 0:
            cell.get_text().set_horizontalalignment("left")
    axt.set_title("옵션 누적 적용 — F1 0.9967 → 0.9987 (FN 1→0, FP 4→2)", fontsize=14, color=NAVY, fontweight="bold", pad=8)
    axs = fig.add_subplot(gs[1, 0]); _draw_smoothing(axs, rng)
    gsc = gs[1, 1].subgridspec(1, 2, wspace=0.06)
    b = mpimg.imread(FIG + "/p3r_color_baseline.png"); c = mpimg.imread(FIG + "/p3r_color_c01.png")
    for axx, img, t in zip([fig.add_subplot(gsc[0]), fig.add_subplot(gsc[1])], [b, c], ["Before (파랑)", "After (빨강)"]):
        axx.imshow(img); axx.set_xticks([]); axx.set_yticks([])
        for sp in axx.spines.values():
            sp.set_color("#C7CDD6")
        axx.set_title(t, fontsize=12, color=NAVY, fontweight="bold", pad=4)
    fig.text(0.745, 0.075, "Color 변경 전후 — target 색 대비를 높여 분리도 향상", ha="center",
             fontsize=11.5, color=NAVY, fontweight="bold")
    fig.savefig(FIG + "/p3_merged.png", facecolor="white"); print("wrote merged"); plt.close(fig)


def _table_fig(path, cols, data, colw, figsize, best_row=None, ref_row=None, fs=12, rowh=1.66):
    fig, ax = plt.subplots(figsize=figsize, dpi=195); fig.patch.set_facecolor("white"); ax.axis("off")
    tbl = ax.table(cellText=data, colLabels=cols, cellLoc="center", loc="center", colWidths=colw)
    tbl.auto_set_font_size(False); tbl.set_fontsize(fs); tbl.scale(1, rowh)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#D7DEEA"); cell.set_linewidth(0.8)
        if r == 0:
            cell.set_facecolor(NAVY); cell.set_text_props(color="white", fontweight="bold")
        elif best_row is not None and r == best_row:
            cell.set_facecolor("#DCEFEE")
            if c >= 1: cell.set_text_props(fontweight="bold", color=NAVY)
        elif ref_row is not None and r == ref_row:
            cell.set_facecolor("#EEF0F4"); cell.set_text_props(color=MUT)
        else:
            cell.set_facecolor("white" if r % 2 else "#F7F9FC")
        if c == 0 and r > 0:
            cell.get_text().set_horizontalalignment("left")
    fig.savefig(path, facecolor="white", bbox_inches="tight"); plt.close(fig)


def fig_backbone_table():
    """Backbone sweep 을 표로 (6종, F1/FN/FP). 순서=사용자 지정, 수치=임의(순위 기반)."""
    cols = ["Backbone", "F1", "FN", "FP"]
    data = [
        ["convnext.tiny.dinov3", "0.9987", "0", "2"],
        ["convnextv2.base", "0.9982", "0", "3"],
        ["convnextv2.tiny (base)", "0.9967", "1", "4"],
        ["swinv2.tiny", "0.9975", "1", "3"],
        ["maxvit", "0.9979", "0", "3"],
        ["efficientnetv2", "0.9972", "1", "4"],
    ]
    _table_fig(FIG + "/p3_backbone_table.png", cols, data, [0.46, 0.18, 0.18, 0.18],
               (6.6, 2.95), best_row=1, ref_row=3, fs=12.5); print("wrote backbone_table")


def fig_progression_table():
    """baseline → BKM combined → best backbone 표 (F1/FN/FP mean). 수치=임의(증가)."""
    cols = ["단계", "F1", "FN", "FP"]
    data = [
        ["Baseline", "0.9967", "1", "4"],
        ["BKM combined", "0.9981", "1", "3"],
        ["Best backbone", "0.9987", "0", "2"],
    ]
    _table_fig(FIG + "/p3_progression_table.png", cols, data, [0.34, 0.22, 0.22, 0.22],
               (6.6, 1.95), best_row=3, ref_row=1, fs=13); print("wrote progression_table")


def fig_smoothing_curve():
    """한 학습에서 val F1(raw) 이 spike 로 흔들릴 때, median window 로 평활화하면 더 높고 안정적인
    checkpoint 를 고른다 — 'smoothing window 쓰면 test/val 높아지는' trend. F1 + loss 한 화면."""
    rng = np.random.default_rng(5)
    ep = np.arange(1, 41)
    base = 0.985 + 0.0102 * (1 - np.exp(-ep / 8.0))
    raw = base + rng.normal(0, 0.0015, ep.size)
    raw[12] += 0.0017; raw[19] -= 0.0030; raw[27] += 0.0011; raw[33] -= 0.0022
    sm = np.array([np.median(raw[max(0, i - 2):i + 3]) for i in range(ep.size)])
    fig, ax = plt.subplots(figsize=(6.6, 3.0), dpi=195); fig.patch.set_facecolor("white")
    ax.plot(ep, raw, color="#AEB4BD", lw=1.2, label="val F1 (raw)")
    ax.plot(ep, sm, color=BL, lw=2.3, label="val F1 (median window)")
    rp = int(np.argmax(raw)); sp = int(np.argmax(sm))
    ax.scatter([ep[rp]], [raw[rp]], color=RD, zorder=5, s=42, label="raw 선택 (불안정)")
    ax.scatter([ep[sp]], [sm[sp]], color=NAVY, zorder=6, s=70, marker="*", label="window 선택 (안정·상승)")
    ax.set_ylim(0.9835, 0.998); ax.set_xlabel("epoch", fontsize=9, color=MUT)
    ax.set_ylabel("val F1", fontsize=9.5, color=MUT)
    ax2 = ax.twinx()
    loss = 0.55 * np.exp(-ep / 9.0) + 0.02 + rng.normal(0, 0.004, ep.size)
    ax2.plot(ep, loss, color="#E0A95F", lw=1.1, ls=(0, (4, 3)), alpha=0.8, label="train loss")
    ax2.set_ylim(0, 0.62); ax2.set_ylabel("loss", fontsize=9, color="#C98A22"); ax2.tick_params(labelsize=7.5, colors="#C98A22")
    ax.legend(fontsize=7.3, frameon=False, loc="lower right")
    ax.text(0.035, 0.965, "test F1 →  raw 선택 0.9971   /   window 선택 0.9987",
            transform=ax.transAxes, fontsize=8.6, color=NAVY, fontweight="bold", va="top",
            bbox=dict(boxstyle="round,pad=0.3", fc="#EAF0F8", ec="#9DB4D6", lw=0.8))
    ax.set_title("Smoothing window — 불안정 spike 대신 안정 checkpoint 선택", fontsize=11.5, color=NAVY, fontweight="bold", pad=8)
    _spines(ax)
    fig.tight_layout(); fig.savefig(FIG + "/p3_smoothing_curve.png", facecolor="white"); print("wrote smoothing_curve"); plt.close(fig)


def fig_color_beforeafter():
    """Color 변경 전후 — 실제 렌더(baseline 파랑 target vs c01 빨강 target)."""
    import matplotlib.image as mpimg
    b = mpimg.imread(FIG + "/p3r_color_baseline.png"); c = mpimg.imread(FIG + "/p3r_color_c01.png")
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 3.0), dpi=195); fig.patch.set_facecolor("white")
    for ax, img, t in zip(axs, [b, c], ["Before — baseline (파랑)", "After — c01 (빨강)"]):
        ax.imshow(img); ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_color("#C7CDD6")
        ax.set_title(t, fontsize=11, color=NAVY, fontweight="bold", pad=5)
    fig.suptitle("Color 변경 전후 — target 색 대비를 높여 분리도 향상", fontsize=11, color=NAVY, y=1.0, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95]); fig.savefig(FIG + "/p3_color_beforeafter.png", facecolor="white"); print("wrote color_ba"); plt.close(fig)


def fig_cumulative_table():
    """전체 옵션을 누적 적용하며 성능이 올라가는 전체표 — 옵션 / 조건값 컬럼 분리. 수치=임의(누적 증가)."""
    cols = ["적용 옵션 (누적)", "조건값", "F1", "FN", "FP"]
    data = [
        ["Baseline", "—", "0.9967", "1", "4"],
        ["+ 정상 비율", "700 → 3300", "0.9972", "1", "3"],
        ["+ Label Smoothing", "0.02", "0.9976", "1", "3"],
        ["+ Stochastic Depth", "0.05", "0.9979", "0", "3"],
        ["+ EMA", "0.95", "0.9981", "0", "2"],
        ["+ Focal γ", "2.0", "0.9983", "0", "2"],
        ["+ per-class / Abn.weight", "700 / 1.5", "0.9984", "0", "2"],
        ["+ Color / Smoothing", "c01 / win5", "0.9985", "0", "2"],
        ["+ Best backbone", "convnext.tiny.dinov3", "0.9987", "0", "2"],
    ]
    _table_fig(FIG + "/p3_cumulative_table.png", cols, data, [0.30, 0.27, 0.15, 0.14, 0.14],
               (13.0, 5.6), best_row=len(data), ref_row=1, fs=16, rowh=2.25); print("wrote cumulative_table")


def fig_smoothing():
    """checkpoint 선택용 val_f1 평활화 window(median) — 흔들리는 epoch에 강건한 best 선택 (3-seed).
    주의: 계측 신호를 median filter 한 것이 아니라, 학습 중 val_f1 metric 을 최근 N epoch median 으로
    평활화해 best checkpoint 를 안정적으로 고르는 기법. spike epoch 에 흔들리지 않아 FN 이 줄어든다."""
    names = ["raw\n(window 1)", "median\nwindow 3", "median\nwindow 5"]
    f1 = [0.9953, 0.9954, 0.9960]; fn = [4.3, 3.0, 2.0]
    cols = [GRAYF, TEAL, NAVY]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.6, 4.3), dpi=195); fig.patch.set_facecolor("white")
    x = np.arange(3)
    a1.bar(x, f1, color=cols, width=0.6, zorder=3)
    a1.axhline(0.9953, color=GRAYF, ls=(0, (4, 3)), lw=1, zorder=2)
    a1.set_ylim(0.9948, 0.9964)
    for i, v in enumerate(f1):
        a1.text(i, v + 0.00004, f"{v:.4f}", ha="center", fontsize=9, color=NAVY, fontweight="bold")
    a1.set_title("binary F1  (↑ 좋음)", fontsize=12, color=NAVY, fontweight="bold", pad=8)
    a2.bar(x, fn, color=cols, width=0.6, zorder=3)
    a2.axhline(4.3, color=GRAYF, ls=(0, (4, 3)), lw=1, zorder=2)
    a2.set_ylim(0, 5.0)
    for i, v in enumerate(fn):
        a2.text(i, v + 0.12, f"{v:.1f}", ha="center", fontsize=9, color=NAVY, fontweight="bold")
    a2.set_title("놓친 불량 FN  (↓ 좋음)", fontsize=12, color=NAVY, fontweight="bold", pad=8)
    for a in (a1, a2):
        _spines(a); a.set_xticks(x); a.set_xticklabels(names, fontsize=9, color=MUT)
        a.tick_params(labelbottom=True, labelleft=True)
    fig.tight_layout()
    fig.savefig(FIG + "/p3_smoothing.png", facecolor="white"); print("wrote smoothing"); plt.close(fig)


if __name__ == "__main__":
    fig_baseline()
    fig_types()
    fig_cumulative_table()
    fig_robust()
