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

NAVY = "#0F1E3D"; ACC = "#12B5B0"; INK = "#1A1F2E"; MUT = "#6B7280"; LINE = "#C4D0E2"; PANEL = "#EFF3F8"
GRADE = ["#EAF2F7", "#CFE6EC", "#9FD3D0", "#5FC1B8", "#F2C94C", "#F0954A", "#E0683A", "#CC3328"]


def rbox(ax, x, y, w, h, fc, ec=LINE, lw=1.2, r=0.12, t=None, tc=None, fs=10, bold=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=2))
    if t:
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center",
                color=tc or NAVY, fontsize=fs, fontweight="bold" if bold else "normal", zorder=3)


def arr(ax, x1, x2, y, label=None):
    ax.add_patch(FancyArrowPatch((x1, y), (x2, y), arrowstyle="-|>", mutation_scale=15,
                                 color=ACC, lw=2.0, zorder=2))
    if label:
        ax.text((x1 + x2) / 2, y + 0.55, label, ha="center", va="bottom", color=MUT, fontsize=8.6)


def header(ax, no, name, what):
    ax.text(0.25, 9.5, no + " " + name, ha="left", va="top", color=NAVY, fontsize=13.5, fontweight="bold")
    ax.text(0.25, 8.45, what, ha="left", va="top", color=MUT, fontsize=10)


def foot(ax, txt):
    ax.add_patch(FancyBboxPatch((0.4, 0.25), 9.2, 1.0, boxstyle="round,pad=0.0,rounding_size=0.15",
                                fc=PANEL, ec="none", zorder=1))
    ax.text(5.0, 0.75, txt, ha="center", va="center", color=NAVY, fontsize=11, fontweight="bold", zorder=3)


fig, axs = plt.subplots(2, 2, figsize=(12.6, 5.6), dpi=175)
fig.patch.set_facecolor("white")
fig.subplots_adjust(left=0.012, right=0.988, top=0.97, bottom=0.02, wspace=0.10, hspace=0.16)
for ax in axs.flat:
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

# ① Cython — hex log → Grade 0-7 색 격자
ax = axs[0, 0]
header(ax, "①", "Cython", "hex 로그를 Grade(0-7) 격자로 변환")
for i, hx in enumerate(["9A", "3F", "C1"]):
    rbox(ax, 0.6, 6.0 - i * 1.05, 1.0, 0.85, "#FFFFFF", t=hx, fs=10, tc=INK)
ax.text(1.1, 7.4, "hex log", ha="center", color=MUT, fontsize=9)
arr(ax, 2.0, 3.7, 5.4, "C 컴파일")
for r in range(3):
    for c in range(3):
        g = (r * 3 + c) % 8
        ax.add_patch(Rectangle((4.6 + c * 0.62, 3.5 + r * 0.62), 0.58, 0.58, fc=GRADE[g], ec="white", lw=1, zorder=3))
ax.text(5.5, 7.4, "Grade 0-7 격자", ha="center", color=MUT, fontsize=9)
foot(ax, "Python loop → C 컴파일   ·   ~100× 가속")

# ② 32색 palette PNG — RGB 3byte vs index 1byte + 색 팔레트
ax = axs[0, 1]
header(ax, "②", "32색 palette PNG", "유한한 색 → 1바이트 인덱스로 저장")
for i, (cc, nm) in enumerate([("#CC3328", "R"), ("#3BA55D", "G"), ("#2E6FD6", "B")]):
    ax.add_patch(Rectangle((0.7, 5.6 - i * 0.85), 1.5, 0.7, fc=cc, ec="white", lw=1, zorder=3))
ax.text(1.45, 6.9, "RGB · 3 byte/px", ha="center", color=MUT, fontsize=9)
arr(ax, 2.6, 4.6, 5.4, "색 32개뿐")
for c in range(8):
    ax.add_patch(Rectangle((5.0 + c * 0.5, 5.5), 0.46, 0.7, fc=GRADE[c], ec="white", lw=1, zorder=3))
ax.text(7.0, 6.9, "32색 팔레트", ha="center", color=MUT, fontsize=9)
rbox(ax, 5.6, 3.9, 2.7, 0.85, "#FFFFFF", t="index · 1 byte/px", fs=10, tc=NAVY)
foot(ax, "RGB 3 byte → index 1 byte   ·   저장 ~75%↓")

# ③ ProcessPool — wafer 변환을 24 프로세스 병렬
ax = axs[1, 0]
header(ax, "③", "ProcessPool (CPU 24)", "CPU-bound 변환·렌더를 프로세스 병렬")
rbox(ax, 0.6, 4.4, 2.2, 1.5, "#FFFFFF", t="wafer\n변환·렌더", fs=10, tc=NAVY)
for i in range(4):
    yy = 6.3 - i * 1.15
    ax.add_patch(FancyArrowPatch((2.9, 5.15), (5.0, yy + 0.35), arrowstyle="-|>",
                                 mutation_scale=11, color=ACC, lw=1.4, zorder=2))
    rbox(ax, 5.1, yy, 2.6, 0.78, PANEL, ec=LINE, t="process " + str(i + 1), fs=9.5, tc=NAVY)
ax.text(6.4, 7.5, "… × 24 (CPU)", ha="center", color=MUT, fontsize=9)
foot(ax, "GIL 회피 · 동시 처리   ·   일 2만 wafer 자동 적재")

# ④ Numba + pyvips — 운영 viewer (다수 wafer → composite hot-spot)
ax = axs[1, 1]
header(ax, "④", "Numba + pyvips (viewer)", "대용량 합성·조회 가속")
for r in range(3):
    for c in range(3):
        ax.add_patch(Circle((0.95 + c * 0.78, 5.1 + r * 0.78), 0.3, fc="#DCE6F0", ec="white", lw=1, zorder=3))
ax.text(1.7, 7.5, "wafer 다수", ha="center", color=MUT, fontsize=9)
arr(ax, 3.5, 5.7, 5.9, "Numba 합성\npyvips 로드")
ax.add_patch(Circle((7.4, 5.9), 1.2, fc="#EAF2F7", ec=LINE, lw=1.3, zorder=3))
ax.add_patch(Circle((7.4, 5.9), 1.2, fc="none", ec="#CC3328", lw=2.4, zorder=4))
ax.text(7.4, 5.9, "hot-spot", ha="center", va="center", color="#CC3328", fontsize=8.5, fontweight="bold", zorder=5)
ax.text(7.4, 7.5, "composite map", ha="center", color=MUT, fontsize=9)
foot(ax, "256장 합성 · pyramid+cache   ·   composite 10장 약 2.9s")

out = r"D:/project/fbm_paper/recommendation/figures/p1_pipeline_concept.png"
fig.savefig(out, facecolor="white", bbox_inches="tight")
print("saved", out)
