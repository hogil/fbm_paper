"""pptx -> slide PNG 렌더러 (PowerPoint COM). 평가 에이전트의 시각 검수용.
사용: python render_pptx.py <pptx_path> <out_dir> [width] [height]
"""
import sys, os, time


def render(pptx_path, out_dir, width=1600, height=900):
    """우선 PDF 경로(PowerPoint→PDF→PyMuPDF 래스터)로 렌더한다. PDF 경로는 slide.Export 의
    간헐적 '어두운 밴드' 비트맵 글리치가 없는 결정적 렌더라 톤 일관성을 보장한다.
    PDF 경로가 불가하면 기존 slide.Export 경로로 폴백한다."""
    pptx_path = os.path.abspath(pptx_path)
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    try:
        n = _render_via_pdf(pptx_path, out_dir, int(width), int(height))
        if n:
            _montage(out_dir)
            return n
    except Exception as e:
        print("pdf-render fallback:", e)
    n = _render_via_export(pptx_path, out_dir, int(width), int(height))
    _montage(out_dir)
    return n


def _render_via_pdf(pptx_path, out_dir, width, height):
    import win32com.client
    import fitz  # PyMuPDF
    pdf_path = os.path.join(out_dir, "_deck.pdf")
    if os.path.exists(pdf_path):
        try:
            os.remove(pdf_path)
        except Exception:
            pass
    ppt = win32com.client.DispatchEx("PowerPoint.Application")
    shared = False
    try:
        shared = ppt.Presentations.Count > 0  # 사용자가 이미 PPT를 열어둔 인스턴스에 붙은 경우
    except Exception:
        pass
    if not shared:
        try:
            ppt.Visible = 0
        except Exception:
            pass
    pres = ppt.Presentations.Open(pptx_path, ReadOnly=True, Untitled=False, WithWindow=False)
    try:
        pres.SaveAs(pdf_path, 32)  # ppSaveAsPDF
    finally:
        pres.Close()
        if not shared:  # 우리가 띄운 인스턴스만 종료 — 사용자 PPT 창은 건드리지 않음
            try:
                ppt.Quit()
            except Exception:
                pass
    time.sleep(0.5)
    doc = fitz.open(pdf_path)
    n = 0
    for i, page in enumerate(doc, 1):
        # 페이지 폭 기준으로 목표 픽셀 폭(width)에 맞는 배율 계산 → 고품질 래스터
        zoom = width / page.rect.width
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        out = os.path.join(out_dir, f"slide_{i:02d}.png")
        pix.save(out)
        # 목표 크기로 정확히 맞춤(종횡비 보정)
        _exact_resize(out, width, height)
        n += 1
    doc.close()
    return n


def _exact_resize(path, w, h):
    try:
        from PIL import Image
        im = Image.open(path).convert("RGB")
        if im.size != (w, h):
            im = im.resize((w, h), Image.LANCZOS)
            im.save(path)
    except Exception:
        pass


def _render_via_export(pptx_path, out_dir, width, height):
    import win32com.client
    ppt = win32com.client.Dispatch("PowerPoint.Application")
    try:
        ppt.Visible = 0
    except Exception:
        pass
    pres = ppt.Presentations.Open(pptx_path, ReadOnly=True, Untitled=False, WithWindow=False)
    NW, NH = 1920, 1080
    n = 0
    try:
        for i, slide in enumerate(pres.Slides, 1):
            out = os.path.join(out_dir, f"slide_{i:02d}.png")
            slide.Export(out, "PNG", NW, NH)
            time.sleep(0.2)
            if (width, height) != (NW, NH):
                _exact_resize(out, width, height)
            n += 1
    finally:
        pres.Close()
        ppt.Quit()
    return n


def _montage(out_dir, cols=3, scale=0.42):
    """렌더된 슬라이드들을 _contact.png 한 장으로 합침(디자인 평가 에이전트 전체 조망용)."""
    try:
        from PIL import Image
        import glob
        fs = sorted(glob.glob(os.path.join(out_dir, "slide_*.png")))
        if not fs:
            return
        ims = [Image.open(f) for f in fs]
        w, h = ims[0].size
        tw, th = int(w * scale), int(h * scale)
        rows = (len(ims) + cols - 1) // cols
        pad = 12
        sheet = Image.new("RGB", (cols * tw + pad * (cols + 1), rows * th + pad * (rows + 1)), (32, 36, 48))
        from PIL import ImageDraw
        dr = ImageDraw.Draw(sheet)
        for i, im in enumerate(ims):
            r, c = divmod(i, cols)
            x = pad + c * (tw + pad); y = pad + r * (th + pad)
            sheet.paste(im.resize((tw, th)), (x, y))
            dr.text((x + 4, y + 2), str(i + 1), fill=(255, 209, 0))
        sheet.save(os.path.join(out_dir, "_contact.png"))
    except Exception as e:
        print("montage skip:", e)


if __name__ == "__main__":
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "_render"
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 1600
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 900
    cnt = render(src, out, w, h)
    print(f"rendered {cnt} slides -> {out}")
