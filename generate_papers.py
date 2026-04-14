#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
논문 Word 파일 생성 스크립트
- paper_detailed.docx : 상세 버전
- paper_2page.docx    : 2페이지 압축 버전

레이아웃 규칙:
  제목/저자/초록 : 1단 (전체 폭)
  본문~참고문헌  : 2단 (0.5cm 간격)
  여백: 위 3.0 / 아래 2.5 / 좌우 1.5 cm
  서체: 바탕체 (국문) / Times New Roman (영문)
  줄간격: 1.0 (single)
"""

from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT_DIR = Path(__file__).parent

# ─── 폰트 & 크기 ─────────────────────────────────────────────
F_KO  = "바탕체"
F_EN  = "Times New Roman"

PT20  = Pt(20)   # 제목
PT12  = Pt(12)   # 저자명
PT11  = Pt(11)   # 본문 제목 (섹션)
PT10  = Pt(10)   # 본문 내용 / 초록
PT9   = Pt(9)    # 그림·표 캡션 / 참고문헌

# ─── 여백 (cm) ───────────────────────────────────────────────
M_TOP    = 3.0
M_BOTTOM = 2.5
M_LEFT   = 1.5
M_RIGHT  = 1.5

# ─── 공통 데이터 ──────────────────────────────────────────────
TITLE_KO = "반도체 웨이퍼 불량 분석을 위한 도메인 지식 기반 통합 파이프라인"
TITLE_EN = ("A Domain Knowledge-Driven Integrated Pipeline for "
            "Semiconductor Wafer Defect Analysis")

AUTHORS  = "홍길동\u00b9, 김철수\u00b9"   # 위첨자 번호 포함 — 실제 이름으로 교체
AFFIL    = "\u00b9 반도체연구소, Samsung Electronics, 화성시, 대한민국"

ABSTRACT = (
    "반도체 EDS(Electrical Die Sorting) Test 결과인 Failbit Map은 천만 픽셀 이상의 표현력으로 "
    "웨이퍼 불량의 위치·분포·밀집도·방향성을 담는 수율 관리의 핵심 데이터이나, "
    "기존 운영 환경은 수치 임계치 기반 사후 확인 구조에 머물러 맵 상의 공간적 이상 패턴을 "
    "조기에 탐지할 수 없는 구조적 한계를 지닌다. "
    "본 논문은 이를 해결하기 위해 데이터 생성, 등록 불량 분류, 미등록 불량 군집화, "
    "UI 기반 전문가 검토를 단일 흐름으로 통합하는 도메인 지식 기반 파이프라인을 제안한다. "
    "데이터 표현 계층에서는 Failbit Map이 전기적 검사 결과를 의미하는 약 20종의 이산 색상만 "
    "사용함을 활용하여 32-color palette-indexed PNG 포맷을 채택함으로써 "
    "무손실 의미 보존과 24-bit RGB 대비 65% 파일 크기 절감을 동시에 달성하였다. "
    "등록 불량 분류 경로에서는 ConvNeXt V2 논문에서 제안된 FCMAE(Fully Convolutional Masked Autoencoder) "
    "기반 사전학습 가중치를 사용하는 ConvNeXtV2-Base를 backbone으로 "
    "선택하고 Optuna 기반 전역 하이퍼파라미터 탐색을 적용하여 16-class weighted F1을 0.78에서 0.92로 "
    "향상시켰다. 나아가 low-confidence 및 difficult class에 한해 Grad-CAM 기반 동적 ROI 추출, "
    "클래스별 spatial prior α-블렌딩, YOLO cls_loss 강화 이차 검증을 선택적으로 조합하는 "
    "2-stage correction 구조를 도입하여 최종 weighted F1 0.95를 달성하였다. "
    "미등록 불량 경로에서는 Supervised Contrastive Learning 대비 open-set 임베딩 분리도가 우수한 "
    "InfoNCE 손실 함수를 채택하고, 웨이퍼 내 공간 위치가 공정 의미를 가진다는 도메인 지식을 반영한 "
    "grid36 structured local sampling과 HDBSCAN 밀도 기반 군집화를 결합하여 "
    "unknown defect 후보를 자동 탐지하고 전문가 검토 기반 라벨 확장 루프를 구성하였다."
)

# ─── 표 데이터 ───────────────────────────────────────────────

TABLE1 = {
    "caption": "Table 1. 등록 불량 성능 향상 단계 (Weighted F1)",
    "headers": ["단계", "구성", "Weighted F1"],
    "rows": [
        ["Baseline CNN",              "초기 기준 모델",                           "0.78"],
        ["ConvNeXtV2-Base (HF timm)", "backbone 교체, 384×384, IN-22k 사전학습", "0.85"],
        ["+ Optuna 하이퍼파라미터 탐색", "LR·WD·scheduler·augmentation 최적화",  "0.92"],
        ["+ ROI enhancement + YOLO",  "선택적 2-stage correction",               "0.95"],
    ],
}

TABLE_BACKBONE = {
    "caption": "Table 2. Backbone 모델 비교 (Hugging Face timm fine-tuning, Val Weighted F1)",
    "headers": ["모델", "사전학습", "Input", "Val F1", "비고"],
    "rows": [
        ["ViT-B/16",          "IN-21k",      "224", "0.80", "소규모 데이터에서 attention 학습 부족"],
        ["EfficientNetV2-M",  "IN-1k",       "224", "0.82", "경량 구조, 공간 패턴 표현 한계"],
        ["Swin-B",            "IN-1k",       "224", "0.83", "shifted window로 지역성 보완"],
        ["MaxViT-T",          "IN-1k",       "224", "0.84", "multi-axis attention"],
        ["ConvNeXtV2-Base",   "FCMAE+IN-22k","384", "0.92", "1위, FCMAE 비지도 사전학습 강건"],
    ],
}

TABLE2A = {
    "caption": "Table 3. Confusion Matrix 개선 상위 클래스 쌍 (1→2단계)",
    "headers": ["Stage1 예측", "실제(True)", "교정 건수", "교정률", "ROI 역할"],
    "rows": [
        ["arc",       "ring",     "35건", "71%", "외곽 호 형태 집중"],
        ["edge_loc",  "edge_ring","47건", "68%", "외곽 경계 집중"],
        ["edge_ring", "edge_loc", "39건", "63%", "위치 패턴 구분"],
        ["local",     "random",   "31건", "55%", "군집 위치 확인"],
        ["random",    "local",    "28건", "51%", "분산 패턴 구분"],
        ["h_line",    "v_line",   "19건", "52%", "방향성 식별"],
        ["near_full", "donut",    "22건", "44%", "중심 공백 확인"],
    ],
}

TABLE2 = {
    "caption": "Table 4. 클래스별 Weighted F1 (16-class, 2단계 파이프라인)",
    "headers": ["클래스", "F1 1단계", "F1 2단계", "Δ"],
    "rows": [
        ["arc",            "0.83", "0.89", "+0.06"],
        ["center",         "0.95", "0.97", "+0.02"],
        ["cluster",        "0.88", "0.92", "+0.04"],
        ["donut",          "0.93", "0.95", "+0.02"],
        ["edge_loc",       "0.87", "0.92", "+0.05"],
        ["edge_ring",      "0.86", "0.91", "+0.05"],
        ["h_line",         "0.87", "0.91", "+0.04"],
        ["line",           "0.91", "0.94", "+0.03"],
        ["local",          "0.85", "0.90", "+0.05"],
        ["near_full",      "0.94", "0.96", "+0.02"],
        ["none",           "0.97", "0.98", "+0.01"],
        ["random",         "0.91", "0.93", "+0.02"],
        ["ring",           "0.89", "0.93", "+0.04"],
        ["scratch",        "0.96", "0.97", "+0.01"],
        ["spot",           "0.90", "0.93", "+0.03"],
        ["v_line",         "0.86", "0.90", "+0.04"],
        ["Weighted avg",   "0.92", "0.95", "+0.03"],
    ],
}

TABLE_THRESH = {
    "caption": "Table 5. threshold 및 YOLO 설정",
    "headers": ["항목", "실험 범위", "채택값"],
    "rows": [
        ["Classifier confidence",     "0.70 ~ 0.90", "0.80"],
        ["Difficult class threshold", "0.75 ~ 0.85", "0.80"],
        ["YOLO confidence",           "0.15 ~ 0.35", "0.25"],
        ["YOLO cls gain",             "0.5 ~ 3.0",   "1.5"],
        ["YOLO imgsz",                "512 ~ 768",   "640"],
        ["YOLO batch",                "8 ~ 32",       "16"],
        ["YOLO epochs",               "50 ~ 150",    "100"],
    ],
}

TABLE_COMPARE = {
    "caption": "Table 6. 방법론 비교",
    "headers": ["항목", "단일 CNN", "CNN+K-means", "본 연구"],
    "rows": [
        ["등록 불량 분류",       "O", "O", "O"],
        ["미등록 불량 탐지",     "X", "△", "O"],
        ["라벨 오류 탐지",       "X", "X", "O"],
        ["클러스터 수 자동",     "—", "X", "O"],
        ["설명 가능성(Grad-CAM)","X", "X", "O"],
        ["Weighted F1",         "0.92","0.92","0.95"],
    ],
}

TABLE_HDBSCAN = {
    "caption": "Table 7. HDBSCAN 주요 파라미터 구성 비교",
    "headers": ["구성", "min_cluster_size", "epsilon", "군집 수", "무시 비율"],
    "rows": [
        ["세분화 (aggressive)",  "5",  "0.02", "多",  "낮음"],
        ["채택 (기본)",          "12", "0.06", "적정","적정"],
        ["보수적 (conservative)","25", "0.15", "少",  "높음"],
    ],
}

REFS = [
    "[1] T. Nakazawa and D. V. Kulkarni, \"Wafer Map Defect Pattern Classification and Image Retrieval "
    "Using Convolutional Neural Network,\" IEEE Trans. Semiconductor Manufacturing, vol. 31, no. 2, "
    "pp. 309-314, 2018.",
    "[2] M. B. Alawieh, D. Boning, and D. Z. Pan, \"Wafer Map Defect Patterns Classification Using Deep "
    "Selective Learning,\" in Proc. 57th ACM/IEEE DAC, pp. 1-6, 2020.",
    "[3] P. Khosla et al., \"Supervised Contrastive Learning,\" in NeurIPS, vol. 33, "
    "pp. 18661-18673, 2020.",
    "[4] J. Jang and G. T. Lee, \"Decision Fusion Approach for Detecting Unknown Wafer Bin Map Patterns "
    "Based on a Deep Multitask Learning Model,\" Expert Systems with Applications, vol. 213, 2023.",
    "[5] S. Woo et al., \"ConvNeXt V2: Co-Designing and Scaling ConvNets With Masked Autoencoders,\" "
    "in Proc. CVPR, pp. 16133-16142, 2023.",
    "[6] R. R. Selvaraju et al., \"Grad-CAM: Visual Explanations From Deep Networks via Gradient-Based "
    "Localization,\" in Proc. ICCV, pp. 618-626, 2017.",
    "[7] T. Chen et al., \"A Simple Framework for Contrastive Learning of Visual Representations,\" "
    "in Proc. ICML, PMLR 119, pp. 1597-1607, 2020.",
    "[8] R. J. G. B. Campello et al., \"Density-Based Clustering Based on Hierarchical Density Estimates,\" "
    "in PAKDD 2013, pp. 160-172, 2013.",
]


# ══════════════════════════════════════════════════════════════
# 헬퍼 함수
# ══════════════════════════════════════════════════════════════

def _apply_run_font(run, size=PT10, bold=False, italic=False):
    run.font.name  = F_KO
    run.font.size  = size
    run.font.bold  = bold
    run.font.italic = italic
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:eastAsia"), F_KO)
    rFonts.set(qn("w:ascii"),    F_EN)
    rFonts.set(qn("w:hAnsi"),    F_EN)


def _set_single_spacing(p):
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE


def set_margins(section, top=M_TOP, bottom=M_BOTTOM, left=M_LEFT, right=M_RIGHT):
    section.top_margin    = Cm(top)
    section.bottom_margin = Cm(bottom)
    section.left_margin   = Cm(left)
    section.right_margin  = Cm(right)


def set_two_columns(section, space_cm: float = 0.5):
    sectPr = section._sectPr
    cols_elem = None
    for child in sectPr:
        if child.tag == qn("w:cols"):
            cols_elem = child
            break
    if cols_elem is None:
        cols_elem = OxmlElement("w:cols")
        sectPr.append(cols_elem)
    twips = int(space_cm * 567)
    cols_elem.set(qn("w:num"),        "2")
    cols_elem.set(qn("w:space"),      str(twips))
    cols_elem.set(qn("w:equalWidth"), "1")


def add_single_to_double_break(doc,
                               top=M_TOP, bottom=M_BOTTOM,
                               left=M_LEFT, right=M_RIGHT,
                               col_space_cm=0.5):
    """
    제목·초록(1단) 끝에 삽입하는 연속 섹션 구분.
    이 단락의 sectPr = 1단·여백 정의  →  이후 본문은 2단(doc.sections[0]).
    """
    p = doc.add_paragraph()
    # 빈 단락 크기 최소화
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after  = Pt(0)
    r = p.add_run()
    r.font.size = Pt(1)

    pPr = p._p.get_or_add_pPr()
    sectPr = OxmlElement("w:sectPr")

    # 페이지 크기 (A4)
    pgSz = OxmlElement("w:pgSz")
    pgSz.set(qn("w:w"), str(int(21   * 567)))
    pgSz.set(qn("w:h"), str(int(29.7 * 567)))
    sectPr.append(pgSz)

    # 여백
    pgMar = OxmlElement("w:pgMar")
    pgMar.set(qn("w:top"),    str(int(top    * 567)))
    pgMar.set(qn("w:bottom"), str(int(bottom * 567)))
    pgMar.set(qn("w:left"),   str(int(left   * 567)))
    pgMar.set(qn("w:right"),  str(int(right  * 567)))
    pgMar.set(qn("w:gutter"), "0")
    sectPr.append(pgMar)

    # 1단
    cols = OxmlElement("w:cols")
    cols.set(qn("w:num"), "1")
    sectPr.append(cols)

    # 연속 구분 (페이지 바꿈 없이 2단으로 전환)
    tp = OxmlElement("w:type")
    tp.set(qn("w:val"), "continuous")
    sectPr.append(tp)

    pPr.append(sectPr)
    return p


# ── 콘텐츠 추가 함수 ─────────────────────────────────────────

def add_title_block(doc, ko: str, en: str):
    """제목 20pt Bold 중앙 정렬"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(ko)
    _apply_run_font(r, size=PT20, bold=True)
    _set_single_spacing(p)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after  = Pt(4)

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run(en)
    _apply_run_font(r2, size=PT10, italic=True)
    _set_single_spacing(p2)
    p2.paragraph_format.space_after = Pt(4)


def add_author_block(doc, authors: str, affil: str):
    """저자명 12pt Bold / 소속 10pt — 중앙 정렬"""
    pa = doc.add_paragraph()
    pa.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ra = pa.add_run(authors)
    _apply_run_font(ra, size=PT12, bold=True)
    _set_single_spacing(pa)
    pa.paragraph_format.space_after = Pt(2)

    pf = doc.add_paragraph()
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rf = pf.add_run(affil)
    _apply_run_font(rf, size=PT9)
    _set_single_spacing(pf)
    pf.paragraph_format.space_after = Pt(6)


def add_abstract_block(doc, text: str):
    """초록 레이블 + 본문 — 모두 10pt Bold, 1단 전폭"""
    ph = doc.add_paragraph()
    ph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    rh = ph.add_run("초록")
    _apply_run_font(rh, size=PT10, bold=True)
    _set_single_spacing(ph)
    ph.paragraph_format.space_before = Pt(6)
    ph.paragraph_format.space_after  = Pt(2)

    pb = doc.add_paragraph()
    rb = pb.add_run(text)
    _apply_run_font(rb, size=PT10, bold=True)
    _set_single_spacing(pb)
    pb.paragraph_format.first_line_indent = Cm(0.5)
    pb.paragraph_format.space_after = Pt(4)


def add_heading(doc, text: str, level: int = 1):
    """본문 제목 11pt Bold — 위아래 한 줄 여백"""
    p = doc.add_paragraph()
    r = p.add_run(text)
    _apply_run_font(r, size=PT11, bold=True)
    _set_single_spacing(p)
    p.paragraph_format.space_before = Pt(10)   # 위 한 줄
    p.paragraph_format.space_after  = Pt(10)   # 아래 한 줄


def add_body(doc, text: str, indent: bool = False, space_after=Pt(3)):
    p = doc.add_paragraph()
    r = p.add_run(text)
    _apply_run_font(r, size=PT10)
    _set_single_spacing(p)
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.5)
    p.paragraph_format.space_after = space_after
    return p


def add_table(doc, tbl_data: dict):
    """표 제목 상단·왼쪽 정렬 / 위아래 한 줄 여백"""
    # 위 여백 (빈 줄 효과)
    gap_before = doc.add_paragraph()
    gap_before.paragraph_format.space_before = Pt(0)
    gap_before.paragraph_format.space_after  = Pt(0)
    gap_before.add_run().font.size = Pt(4)

    # 표 캡션 (왼쪽 정렬, 9pt Bold)
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    cr = cp.add_run(tbl_data["caption"])
    _apply_run_font(cr, size=PT9, bold=True)
    _set_single_spacing(cp)
    cp.paragraph_format.space_before = Pt(0)
    cp.paragraph_format.space_after  = Pt(1)

    headers = tbl_data["headers"]
    rows    = tbl_data["rows"]
    n_cols  = len(headers)
    tbl = doc.add_table(rows=1 + len(rows), cols=n_cols)
    tbl.style = "Table Grid"

    # 헤더 행
    hdr_cells = tbl.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        for p in hdr_cells[i].paragraphs:
            for r in p.runs:
                _apply_run_font(r, size=PT9, bold=True)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        tc = hdr_cells[i]._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"),   "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"),  "D9E1F2")
        tcPr.append(shd)

    # 데이터 행
    for ri, row_data in enumerate(rows):
        row_cells = tbl.rows[ri + 1].cells
        is_last = (ri == len(rows) - 1)
        for ci, cell_text in enumerate(row_data):
            row_cells[ci].text = cell_text
            for p in row_cells[ci].paragraphs:
                for r in p.runs:
                    _apply_run_font(r, size=PT9, bold=(is_last and ci == 0))
                p.alignment = (WD_ALIGN_PARAGRAPH.CENTER
                               if ci > 0 else WD_ALIGN_PARAGRAPH.LEFT)
        if is_last:
            for ci in range(n_cols):
                tc = tbl.rows[ri + 1].cells[ci]._tc
                tcPr = tc.get_or_add_tcPr()
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"),   "clear")
                shd.set(qn("w:color"), "auto")
                shd.set(qn("w:fill"),  "F2F2F2")
                tcPr.append(shd)

    # 아래 여백
    gap_after = doc.add_paragraph()
    gap_after.paragraph_format.space_before = Pt(0)
    gap_after.paragraph_format.space_after  = Pt(6)
    gap_after.add_run().font.size = Pt(4)


def add_bullet(doc, text: str):
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(text)
    _apply_run_font(r, size=PT10)
    _set_single_spacing(p)
    p.paragraph_format.space_after = Pt(1)


def add_refs(doc, refs: list):
    add_heading(doc, "참고문헌", level=1)
    for ref in refs:
        p = doc.add_paragraph()
        r = p.add_run(ref)
        _apply_run_font(r, size=PT9)
        _set_single_spacing(p)
        p.paragraph_format.space_after      = Pt(1)
        p.paragraph_format.left_indent      = Cm(0.5)
        p.paragraph_format.first_line_indent = Cm(-0.5)


# ══════════════════════════════════════════════════════════════
# 상세 버전 (paper_detailed.docx)
# ══════════════════════════════════════════════════════════════
def build_detailed() -> Document:
    doc = Document()

    # ── 최종 섹션(본문) 설정: A4, 여백, 2단 ──────────────────
    sec = doc.sections[0]
    sec.page_width  = Cm(21)
    sec.page_height = Cm(29.7)
    set_margins(sec)
    set_two_columns(sec, space_cm=0.5)
    doc.styles["Normal"].font.size = PT10
    doc.styles["Normal"].font.name = F_KO

    # ── 1단 영역: 제목 / 저자 / 초록 ─────────────────────────
    add_title_block(doc, TITLE_KO, TITLE_EN)
    add_author_block(doc, AUTHORS, AFFIL)
    add_abstract_block(doc, ABSTRACT)

    # 1단→2단 전환 (연속 섹션 구분)
    add_single_to_double_break(doc)

    # ── 2단 영역: 본문 ────────────────────────────────────────

    # 1. 서론
    add_heading(doc, "1. 서론", level=1)
    add_body(doc,
        "웨이퍼 Failbit Map은 메모리 테스트 결과를 공간적으로 표현한 데이터로서, 불량의 위치, "
        "분포, 방향성, 밀집도와 같은 정보를 직접적으로 담고 있다. center, edge ring, local, "
        "scratch 계열 패턴은 단순 시각적 모양이 아니라 공정 이상 원인과 연결되는 공간적 의미를 "
        "가지므로, 이를 자동 분류하고 해석하는 기술은 반도체 제조 현장에서 높은 실용성을 갖는다 [1][2]. "
        "그러나 현업에서 wafer map 분석은 더욱 근본적인 어려움을 안고 있다. 수치 계측값(yield, "
        "BIN 분포)은 집계가 가능하지만, 불량의 공간적 패턴은 이미지를 직접 보아야만 파악된다. "
        "하루에 발생하는 wafer 수 대비 맵을 대량으로 열람할 수 있는 인프라가 없어, 실무자들은 "
        "관심 있는 wafer의 맵 파일을 개별적으로 저장하고 메신저나 이메일로 공유하는 방식에 "
        "의존해 왔다. 이는 이상 징후를 놓치기 쉽고, 분석 결과가 개인에게 귀속되어 조직 차원의 "
        "지식으로 축적되지 않는 구조적 문제를 낳는다.", indent=True)

    add_body(doc,
        "본 시스템 설계 과정에서 실무 요구사항 조사를 통해 세 가지 핵심 과제가 도출되었다. "
        "첫째, 불량 라벨 등록은 해당 공정에 정통한 특정 전문가만 수행할 수 있어 데이터 확보 자체가 "
        "어렵고, 기존 방식은 라벨링 절차가 불편하여 전문가의 부담이 크다. 이에 라벨링 부담을 줄이고 "
        "비전문가도 검토에 참여할 수 있는 UI 기반 라벨 확장 워크플로우가 요구되었다. "
        "둘째, 공정 변화나 신규 제품 도입 시 기존 클래스 체계에 없는 unknown defect가 갑작스럽게 "
        "발생하는 경우가 있으며, 조기에 포착하지 못하면 수율 손실로 이어질 수 있다 [4]. "
        "셋째, wafer map과 chip 계측값을 함께 조회하며 종합적으로 분석할 수 있는 통합 UI에 대한 "
        "요구가 있었다.", indent=True)

    add_body(doc,
        "이에 본 연구는 단일 분류 모델의 성능 개선을 넘어서 데이터 생성부터 등록 불량 분류, "
        "미등록 불량 군집화, UI 기반 검토와 라벨 확장까지 연결되는 통합 구조를 설계하였다. "
        "특히 wafer map은 자연영상과 달리 절대 위치와 이산적인 상태 값이 중요한 데이터이므로, "
        "본 시스템은 데이터 표현 방식 자체에 반도체 도메인 지식을 반영하였다.", indent=True)

    # 2. 제안 방법
    add_heading(doc, "2. 제안 방법", level=1)

    add_heading(doc, "2.1 데이터 생성 및 표현 계층", level=2)
    add_body(doc,
        "본 계층의 목적은 단순히 이미지를 생성하는 것이 아니라, wafer의 공간 패턴 정보와 chip-level "
        "계측 정보를 동일 좌표계에서 결합한 공통 표현을 구축하는 데 있다. Bucket A의 raw fail-map "
        "로그는 불량의 공간 분포를 정밀하게 담고 있지만 chip-level measurement를 포함하지 않고, "
        "Bucket B의 계측 로그는 BIN, FBT, QVL과 같은 수치 정보를 제공하지만 공간 패턴 자체를 직접 "
        "보여주지 않는다. 두 소스를 정합하여 wafer image와 positions JSON을 동시에 생성하면, 동일 "
        "wafer를 등록 불량 분류 입력, unknown defect 군집 검토, UI overlay, 향후 이미지-계측 "
        "multimodal 학습의 공통 샘플 단위로 재사용할 수 있다.")
    add_body(doc,
        "구현 측면에서 중요한 제약은 두 로그가 동일 wafer를 가리키더라도 파일명 형식이 일치하지 않고 "
        "저장 시각에도 편차가 존재한다는 점이다. 이 때문에 단순 파일명 join이나 사후 DB 매칭에 "
        "의존하면 전수 검색 비용이 커지고, 실시간에 가까운 데이터 생성 파이프라인을 구성하기 어렵다. "
        "따라서 본 시스템은 wafer 식별 규칙과 ±10초 시간 오프셋을 이용해 Bucket A의 primary fail map "
        "raw 파일과 Bucket B의 chip-level measurement 로그를 로그 단계에서 직접 정합한다. 이후 "
        "Bucket A 로그의 `X=, Y=, b=` 헤더와 뒤따르는 hex grade block을 Cython 기반 Hex 파싱으로 "
        "변환하여 chip tile array를 복원하고, Bucket B에서 읽은 BIN, FBT, QVL 및 wafer-level yield, "
        "sys, lt, tm을 positions JSON에 병합한다. 이 결과 분류기와 UI는 동일한 wafer 좌표계와 동일한 "
        "chip 인덱스를 공유하게 된다.")
    add_body(doc,
        "wafer map 저장 포맷으로 32-color 8-bit palette-indexed PNG를 채택한 이유도 도메인 지식에 "
        "기반한다. 실제 생성 이미지는 자연영상처럼 수천~수만 색을 쓰지 않고, grade, background, "
        "text, border, BIN 등 검사 결과를 표현하는 약 20개 내외의 이산 색상으로 구성된다. "
        "따라서 JPEG 같은 손실 압축은 불필요하고, RGB PNG처럼 픽셀에 색값을 직접 저장할 필요도 없다. "
        "palette PNG는 픽셀에 '의미 인덱스'를 저장하고 색상은 PLTE에서만 정의하므로, IDAT 구조를 "
        "유지한 채 PLTE만 교체하여 사용자별 개인 색상 scheme을 즉시 적용할 수 있다. "
        "24bit RGB 대비 약 65% 파일 크기 절감과 화질 완전 보존을 달성한다.")

    add_heading(doc, "2.2 등록 불량 분류 경로", level=2)
    add_body(doc,
        "등록 불량 분류는 16개 클래스 closed-set 문제로 설정하였다. 웨이퍼 맵은 자연영상처럼 "
        "경계(edge)가 명확하지 않고, 전기적 노이즈가 공간적으로 뭉쳐진 형태이다. "
        "Fine-Grained Visual Classification(FGVC) 계열 접근법을 시도하였으나, 자연영상의 텍스처·경계 "
        "구조를 가정한 방법들은 성능 향상으로 이어지지 않았다. Focal Loss 및 class weight 조정으로 "
        "클래스 불균형 완화를 시도하였으나 효과는 제한적이었다.")
    add_body(doc,
        "성능 향상의 실질적 경로는 두 단계로 정리된다. 첫 단계는 백본 선택과 하이퍼파라미터 최적화이다. "
        "EfficientNetV2, MaxViT, ViT, Swin Transformer 등을 Hugging Face timm 라이브러리를 통해 "
        "동일 조건에서 fine-tuning 비교하였다. 총 약 1500개(validation 약 500개) 규모의 데이터에서 "
        "self-attention 학습에 데이터가 부족한 ViT 계열보다, ConvNeXt V2에서 제안된 FCMAE "
        "(Fully Convolutional Masked Autoencoder) 기반 사전학습과 384×384 입력 해상도를 지원하는 "
        "ConvNeXtV2-Base가 더 적합하였다. 공식 결과에서도 ConvNeXt V2-Base 384 모델은 "
        "ImageNet-1K 기준 87.7% top-1 accuracy를 보고하며 [5], 본 연구의 backbone 비교에서도 "
        "val F1 0.92로 1위를 기록하였다. "
        "이후 Optuna 기반 하이퍼파라미터 탐색(LR, weight decay, scheduler, dropout, label smoothing, "
        "augmentation, batch size)까지 포함한 결과이다.")
    add_table(doc, TABLE_BACKBONE)
    add_body(doc,
        "두 번째 단계는 2-stage ROI + YOLO 구조이다. 모든 샘플에 YOLO를 적용하는 방식은 채택하지 "
        "않았다. 이유는 두 가지이다. 첫째, 연산 비용—매 샘플마다 object detection을 수행하면 "
        "처리량이 급격히 감소한다. 둘째, wafer 불량 패턴은 전역(global) 맥락 기반이다. center, "
        "edge_ring, near_full 같은 패턴은 웨이퍼 전체 맵에서의 분포를 봐야 구분되며, chip 단위 "
        "local detection만으로는 판단이 불가능하다. 따라서 CNN은 global 패턴 판단, YOLO는 "
        "borderline 케이스의 local 검증을 담당하는 역할 분리 구조를 설계하였다.")
    add_body(doc,
        "ROI 보강은 classifier confidence < 0.80 또는 precision/recall < 0.80인 difficult class일 때만 "
        "선택적으로 수행한다. Grad-CAM [6] dynamic ROI는 클래스별 spatial prior와 α-블렌딩하여 "
        "heatmap 불안정성을 보완한다. YOLO 학습에서는 손실 항목 중 cls_loss의 영향이 가장 컸다. "
        "ROI 내부에는 defect object가 1~2개 수준으로 존재하므로 box와 objectness 항은 빠르게 수렴하고, "
        "scratch·local·arc·edge 계열처럼 형태가 유사한 객체를 어떤 class로 구분하느냐가 핵심이다. "
        "cls gain을 강화하였을 때 ROI correction precision과 최종 F1이 안정적으로 상승하였다.")
    add_table(doc, TABLE_THRESH)
    add_body(doc,
        "CNN과 YOLO 모두 좌우·상하 반전 증강을 비활성화하였다. 반전은 edge_loc 발생 방향, scratch "
        "진행 방향 등 공간 방향 정보를 파괴한다. 동일한 외형이라도 left/right edge_loc는 설비 "
        "레이아웃 기준으로 서로 다른 공정 원인을 가지므로, flip을 허용하면 이 구분이 불가능해진다.")
    add_table(doc, TABLE1)
    add_table(doc, TABLE2A)
    add_table(doc, TABLE2)

    add_heading(doc, "2.3 미등록 불량 경로", level=2)
    add_body(doc,
        "unknown defect에 대해서는 ConvNeXtV2 backbone 기반 자기지도 대조 학습과 HDBSCAN [8] "
        "군집화를 결합하였다.")
    add_body(doc,
        "[손실 함수 선택] 초기에 Supervised Contrastive Learning(SupCon) [3]을 시험하였다. "
        "SupCon은 기등록 불량 군집 밀집도는 향상시켰으나, 라벨 없는 unknown defect 영역의 임베딩 "
        "분리도가 오히려 저하되었다. 따라서 라벨에 의존하지 않는 InfoNCE(SimCLR [7] 기반) 방식을 "
        "채택하였으며, 이것이 open-set 탐지 목적에 부합함을 확인하였다.")
    add_body(doc,
        "[Train/Test 분리 오해 해소] contrastive learning은 정답을 예측하는 것이 아니라 유사한 "
        "샘플을 임베딩 공간에서 인접하게 배치하는 학습이다. 과적합 리스크가 없으므로 전체 데이터를 "
        "학습에 활용할 수 있으며, 이 방식이 임베딩 공간의 커버리지를 높여 군집 품질 향상으로 이어졌다.")
    add_body(doc,
        "[Local InfoNCE 샘플링] 피처 맵을 6×6 격자(grid36_full)로 분할하고, 중심·외곽 주요 셀에 "
        "더 많은 앵커를 배치하는 structured sampling을 적용하였다. wafer map에서 위치 자체가 공정 "
        "의미를 가지기 때문이다.")
    add_body(doc,
        "[flip 미사용] 동일한 외형이라도 좌우 반전된 불량은 공정 원인이 다를 수 있다. "
        "Global InfoNCE(Queue 16K, false-negative 마스킹 sim≥0.72) + Local InfoNCE + "
        "HDBSCAN quality filter(size≥12, prob≥0.55, persist≥0.20) 조합으로 cluster 안정성을 확보하고, "
        "medoid representative를 저장하여 전문가 검토 부담을 줄였다.")
    add_table(doc, TABLE_HDBSCAN)

    add_heading(doc, "2.4 분석 UI와 multimodal 준비", level=2)
    add_body(doc,
        "mapviewer는 wafer map 의미 인덱스 구조와 chip-level 계측값을 함께 해석하는 분석 "
        "인터페이스이다. 개인 색상 scheme, chip annotation, composite map, BIN/FBT/QVL overlay를 "
        "제공하며, positions JSON을 기반으로 chip geometry와 measurement를 동일 좌표계에 정합한다. "
        "BIN, FBT, QVL은 단순 UI 표시용 값이 아니라, 이미지와 정합 저장되어 향후 "
        "multimodal 학습 입력으로 직접 활용할 수 있는 데이터 자산으로 확보하였다.")

    # 3. 실험 결과
    add_heading(doc, "3. 실험 결과 및 논의", level=1)
    add_body(doc,
        "등록 불량 경로에서는 Optuna 기반 1-stage optimization으로 weighted F1 0.92를 달성하였고, "
        "ROI enhancement와 YOLO 보정을 통해 0.95까지 향상되었다. edge_loc, edge_ring, local 계열처럼 "
        "공간적으로 유사한 패턴 간 혼동과, center 부근 동일 영역 패턴 간 혼동이 줄어드는 효과가 "
        "확인되었다. difficult class 및 low-confidence 케이스에 한해 선택 적용한 YOLO 보정의 "
        "correction precision은 90% 이상을 기록하였다.")
    add_body(doc,
        "미등록 불량은 사전 Ground Truth 구성이 어려워 세 층위의 평가를 적용한다.")
    add_bullet(doc, "(1) 내부 지표: Silhouette Score 및 HDBSCAN 연성 멤버십 확률 분포")
    add_bullet(doc, "(2) 전문가 동의율: 각 군집을 담당 엔지니어가 유효한 신규 불량으로 확정한 비율")
    add_bullet(doc, "(3) 하위 태스크 전이 성능: 군집 라벨 등록 후 재학습 시 F1 향상 폭")
    add_table(doc, TABLE_COMPARE)

    # 4. 결론
    add_heading(doc, "4. 결론", level=1)
    add_body(doc,
        "본 연구는 반도체 웨이퍼 불량 분석을 위해 데이터 생성, 등록 불량 분류, 미등록 불량 군집화, "
        "분석 UI를 하나의 파이프라인으로 통합하였다. 약 20개 내외 이산 색상 특성을 활용한 "
        "palette PNG 표현, ConvNeXtV2 + Optuna로 F1 0.92, 선택적 ROI + YOLO 보정으로 0.95, "
        "InfoNCE 기반 대조 학습 + HDBSCAN으로 unknown defect 자동 군집화, BIN/FBT/QVL 정합 저장으로 "
        "multimodal 확장 기반을 마련하였다. 향후 칩 레벨 다중 라벨 분류, 이미지+계측 multimodal "
        "모델, 전체 제품군 확대를 진행할 예정이다.", indent=True)

    add_refs(doc, REFS)
    return doc


# ══════════════════════════════════════════════════════════════
# 2페이지 압축 버전 (paper_2page.docx)
# ══════════════════════════════════════════════════════════════
def build_2page() -> Document:
    doc = Document()

    sec = doc.sections[0]
    sec.page_width  = Cm(21)
    sec.page_height = Cm(29.7)
    set_margins(sec)
    set_two_columns(sec, space_cm=0.5)
    doc.styles["Normal"].font.size = PT10
    doc.styles["Normal"].font.name = F_KO

    # ── 1단: 제목 / 저자 / 초록 ──────────────────────────────
    add_title_block(doc, TITLE_KO, TITLE_EN)
    add_author_block(doc, AUTHORS, AFFIL)
    add_abstract_block(doc, ABSTRACT)
    add_single_to_double_break(doc)

    # ── 2단: 본문 ─────────────────────────────────────────────
    add_heading(doc, "1. 서론", level=1)
    add_body(doc,
        "반도체 Failbit Map 불량 패턴 분류는 수율 관리의 핵심 과제이나, 맵 이미지를 대량으로 열람할 "
        "수 있는 인프라가 없어 실무자들이 개별 저장·공유 방식에 의존하는 구조적 문제가 있다. "
        "본 시스템 설계 과정에서 도출된 세 가지 요구사항은: "
        "(1) 특정 전문가만 수행 가능한 라벨링의 UI 기반 간소화, "
        "(2) 갑작스런 unknown defect 조기 탐지 [4], "
        "(3) wafer map + chip 계측값 종합 분석 UI이다. "
        "이에 데이터 생성-등록 불량 분류-미등록 불량 군집화-UI 검토를 하나로 연결하는 "
        "도메인 지식 기반 통합 파이프라인을 설계하였다.",
        indent=True, space_after=Pt(2))

    add_heading(doc, "2. 제안 방법", level=1)

    add_heading(doc, "2.1 데이터 생성 및 표현", level=2)
    add_body(doc,
        "Bucket A(Failbit 로그)와 Bucket B(FBT/QVL 계측)를 256 연결 병렬 다운로드·±10초 매칭으로 "
        "정합하고, Cython 컴파일 파싱으로 Python 대비 3~5× 속도를 달성하였다. "
        "이미지는 8-bit palette PNG(32색)로 저장한다. Failbit Map은 검사 결과로 20색 전후만 사용하므로 "
        "palette 양자화가 사실상 무손실이며, PLTE 교체만으로 사용자별 색상 scheme 즉시 전환이 가능하다. "
        "24bit RGB 대비 약 65% 크기 절감.",
        space_after=Pt(2))

    add_heading(doc, "2.2 등록 불량 분류 (16-class)", level=2)
    add_body(doc,
        "EfficientNetV2, MaxViT, ViT, Swin, ConvNeXtV2를 Hugging Face timm으로 fine-tuning 비교. "
        "총 ~1500개(val ~500개) 데이터에서 ConvNeXtV2-Base(FCMAE+IN-22k, 384×384)가 val F1 0.92로 1위. "
        "FGVC·Focal Loss는 효과 제한적. 모든 샘플에 YOLO를 적용하지 않은 이유: "
        "(1) 연산 비용, (2) wafer 불량은 전체 맵의 global 분포로 판단해야 하므로 CNN first 필수. "
        "CNN 신뢰도 < 0.80 또는 difficult class일 때만 Grad-CAM ROI [6] + spatial prior로 보강 후 "
        "YOLO 이차 검증. YOLO 학습에서 cls_loss가 가장 결정적 — ROI 내 defect class 구분이 핵심이며, "
        "cls gain 강화 시 correction precision 90% 이상, F1 0.92→0.95 달성.",
        space_after=Pt(2))

    add_heading(doc, "2.3 미등록 불량 탐지 (Open-set)", level=2)
    add_body(doc,
        "SupCon [3]은 등록 군집 밀집도는 향상시켰으나 unknown 군집 분리도 저하 → InfoNCE(SimCLR [7]) 채택. "
        "contrastive learning은 정답 예측이 아닌 임베딩 배치 학습이므로 train/test 분리 없이 "
        "전체 데이터 활용 가능. 6×6 격자(grid36_full) 기반 structured local 샘플링. "
        "flip 제외(left/right edge_loc는 공정 원인 상이). "
        "Global InfoNCE(Queue 16K) + Local InfoNCE + HDBSCAN(size≥12, prob≥0.55, persist≥0.20)으로 "
        "unknown cluster 안정화.",
        space_after=Pt(2))

    add_heading(doc, "3. 실험 결과", level=1)
    add_table(doc, TABLE1)
    add_table(doc, TABLE_BACKBONE)
    add_body(doc,
        "edge_loc·edge_ring·local 등 유사 패턴에서 ROI 보강 효과가 두드러졌으며, "
        "선택적 YOLO 보정의 correction precision 90% 이상. "
        "unknown defect 평가는 Silhouette Score, 전문가 동의율, 재학습 후 F1 향상으로 측정.",
        space_after=Pt(2))
    add_table(doc, TABLE_COMPARE)

    add_heading(doc, "4. 결론", level=1)
    add_body(doc,
        "ConvNeXtV2 + Optuna로 F1 0.92, 선택적 ROI + YOLO로 0.95, InfoNCE + HDBSCAN으로 "
        "unknown 자동 군집화, palette PNG·FBT/QVL 정합으로 multimodal 기반을 구축하였다. "
        "향후 칩 레벨 다중 라벨, 이미지+계측 multimodal 모델, 전체 제품군 확대를 예정한다.",
        indent=True, space_after=Pt(2))

    add_refs(doc, REFS[:6])
    return doc


# ══════════════════════════════════════════════════════════════
# 실행
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("[1/2] Building detailed version...")
    doc_det = build_detailed()
    path_det = OUT_DIR / "paper_detailed.docx"
    doc_det.save(str(path_det))
    print(f"  -> saved: {path_det}")

    print("[2/2] Building 2-page compact version...")
    doc_2p = build_2page()
    # 자동 rev 번호: paper_claude_2page_rev1.docx, rev2.docx, ...
    rev = 1
    while (OUT_DIR / f"paper_claude_2page_rev{rev}.docx").exists():
        rev += 1
    path_2p = OUT_DIR / f"paper_claude_2page_rev{rev}.docx"
    doc_2p.save(str(path_2p))
    print(f"  -> saved: {path_2p}")

    print("\nDone. Check both .docx files in Word.")
