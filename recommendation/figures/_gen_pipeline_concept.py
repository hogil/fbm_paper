import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle

for f in ["Malgun Gothic", "맑은 고딕", "NanumGothic", "DejaVu Sans"]:
    try:
        rcParams["font.family"] = f
        break
    except Exception:
        pass
rcParams["axes.unicode_minus"] = False

NAVY = "#0F1E3D"; ACC = "#3F86C4"; INK = "#22303F"; MUT = "#6B7280"; LINE = "#C4D0E2"; PANEL = "#EEF3F8"
GRADE = ["#EAF2F7", "#CFE6EC", "#9FD3D0", "#5FC1B8", "#F2C94C", "#F0954A", "#E0683A", "#CC3328"]


def rrect(ax, x, y, w, h, fc, ec=LINE, lw=1.2, r=0.10, t=None, tc=None, fs=11, bold=True, va="center"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=2))
    if t:
        ax.text(x + w / 2, y + h / 2, t, ha="center", va=va,
                color=tc or NAVY, fontsize=fs, fontweight="bold" if bold else "normal", zorder=3)


def arr(ax, x1, y1, x2, y2, label=None, c=ACC, lw=2.4):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=18, color=c, lw=lw, zorder=2))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my + 0.45, label, ha="center", va="bottom", color=MUT, fontsize=9.5)


def title(ax, no, txt):
    ax.text(0.2, 9.55, no, ha="left", va="top", color=ACC, fontsize=17, fontweight="bold")
    ax.text(1.05, 9.5, txt, ha="left", va="top", color=NAVY, fontsize=13.5, fontweight="bold")


def effect(ax, txt):
    ax.add_patch(FancyBboxPatch((0.35, 0.3), 9.3, 1.05, boxstyle="round,pad=0.0,rounding_size=0.18",
                                fc=PANEL, ec="none", zorder=1))
    ax.text(5.0, 0.82, txt, ha="center", va="center", color=NAVY, fontsize=12, fontweight="bold", zorder=3)


fig, axs = plt.subplots(2, 2, figsize=(13.0, 6.0), dpi=185)
fig.patch.set_facecolor("white")
fig.subplots_adjust(left=0.01, right=0.99, top=0.975, bottom=0.015, wspace=0.07, hspace=0.13)
for ax in axs.flat:
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

# ① Cython — hex 로그를 픽셀마다 Grade로 (hot loop → C 컴파일)
ax = axs[0, 0]
title(ax, "①", "Cython · hex 로그 → Grade 격자")
for i, hx in enumerate(["9A", "3F", "C1", "0E"]):
    rrect(ax, 0.55 + i * 0.92, 7.0, 0.8, 0.8, "#FFFFFF", t=hx, fs=11, tc=INK)
ax.text(0.55, 8.1, "raw hex (픽셀마다)", ha="left", color=MUT, fontsize=9.5)
rrect(ax, 1.4, 4.95, 3.0, 0.95, "#FFFFFF", ec=ACC, lw=1.6, t="lookup table[256]", fs=10.5, tc=ACC)
arr(ax, 2.9, 6.85, 2.9, 5.95)
arr(ax, 4.6, 5.42, 6.1, 5.42, label="C 컴파일")
for r in range(2):
    for c in range(4):
        g = (r * 4 + c) % 8
        ax.add_patch(Rectangle((6.2 + c * 0.7, 4.7 + r * 0.7), 0.66, 0.66, fc=GRADE[g], ec="white", lw=1.2, zorder=3))
ax.text(6.2, 6.35, "Grade 0-7 격자", ha="left", color=MUT, fontsize=9.5)
effect(ax, "픽셀 반복 hot loop → C 코드 컴파일   ·   ~100× 가속")

# ② 32색 palette PNG — 색이 32개뿐 → 번호로 저장
ax = axs[0, 1]
title(ax, "②", "32색 palette PNG · 색을 번호로 저장")
ax.text(0.5, 8.1, "이 이미지가 쓰는 색 = 32개뿐", ha="left", color=MUT, fontsize=9.5)
for c in range(8):
    ax.add_patch(Rectangle((0.6 + c * 0.62, 6.7), 0.56, 0.7, fc=GRADE[c], ec="white", lw=1.2, zorder=3))
ax.text(5.7, 7.05, "팔레트(색표)", ha="left", va="center", color=NAVY, fontsize=10, fontweight="bold")
rrect(ax, 0.6, 4.45, 4.0, 1.05, "#FBE9E7", ec="#E0683A", lw=1.4,
      t="RGB: 픽셀마다 3 byte", fs=11, tc="#B23A2A")
rrect(ax, 5.1, 4.45, 4.1, 1.05, "#E8F2FB", ec=ACC, lw=1.6,
      t="palette: 번호 1 byte", fs=11, tc=ACC)
arr(ax, 4.65, 4.97, 5.05, 4.97)
effect(ax, "RGB 3 byte/px → 색 번호 1 byte/px   ·   저장 ~75%↓ (무손실)")

# ③ ProcessPool — 변환·렌더를 CPU 24개로 동시에
ax = axs[1, 0]
title(ax, "③", "ProcessPool · CPU 24개 동시 처리")
rrect(ax, 0.5, 4.7, 2.5, 1.6, "#FFFFFF", ec=ACC, lw=1.5, t="wafer\n변환·렌더\n(CPU-bound)", fs=10, tc=NAVY)
for i in range(5):
    yy = 7.4 - i * 1.15
    ax.add_patch(FancyArrowPatch((3.1, 5.5), (5.2, yy + 0.35), arrowstyle="-|>",
                                 mutation_scale=12, color=ACC, lw=1.5, zorder=2))
    lab = "process " + str(i + 1) if i < 4 else "…  process 24"
    rrect(ax, 5.3, yy, 3.2, 0.78, PANEL, ec=LINE, t=lab, fs=9.5, tc=NAVY)
effect(ax, "GIL 회피, 24 프로세스 병렬   ·   일 약 2만 wafer 자동 적재")

# ④ Numba + pyvips — 여러 wafer를 픽셀 위치별로 합산
ax = axs[1, 1]
title(ax, "④", "Numba+pyvips · 다수 wafer 합성")
for r in range(3):
    for c in range(3):
        ax.add_patch(Circle((0.95 + c * 0.72, 4.9 + r * 0.78), 0.3, fc="#DCE6F0", ec="white", lw=1.2, zorder=3))
ax.text(0.5, 7.55, "여러 wafer", ha="left", color=MUT, fontsize=9.5)
arr(ax, 3.6, 5.7, 5.5, 5.7, label="픽셀 위치별 합산\n(Numba 병렬)")
ax.add_patch(Circle((7.5, 5.7), 1.4, fc="#EAF2F7", ec=LINE, lw=1.4, zorder=3))
ax.add_patch(Circle((7.5, 5.7), 1.4, fc="none", ec="#CC3328", lw=2.6, zorder=4))
ax.text(7.5, 5.7, "hot-spot", ha="center", va="center", color="#CC3328", fontsize=9.5, fontweight="bold", zorder=5)
ax.text(6.1, 7.55, "composite map", ha="left", color=MUT, fontsize=9.5)
effect(ax, "Numba 병렬 합산 · pyvips 대용량 로드   ·   10장 약 2.9s")

out = r"D:/project/fbm_paper/recommendation/figures/p1_pipeline_concept.png"
fig.savefig(out, facecolor="white", bbox_inches="tight")
print("saved", out)
