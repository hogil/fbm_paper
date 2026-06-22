"""발표 pptx 이미지 다운샘플 compact + 공식 파일로 안전 덮어쓰기.
중요: 덮어쓸 대상(공식 파일)이 열려 있으면 그 파일만 닫는다. 다른 PowerPoint 창은 절대 닫지 않는다.
사용: python _compact.py
"""
import io, os, zipfile
from PIL import Image

MAX = 1200
SRC = "발표_AI인증_최호길.pptx"
DST = "'26년 AI Specialist 면접 심사 자료_메모리사업부_최호길.pptx"
TMP = DST + ".tmp"


def build_tmp():
    zin = zipfile.ZipFile(SRC, "r")
    zout = zipfile.ZipFile(TMP, "w", zipfile.ZIP_DEFLATED)
    for it in zin.infolist():
        d = zin.read(it.filename); low = it.filename.lower()
        if low.startswith("ppt/media/") and low.endswith((".png", ".jpg", ".jpeg")):
            try:
                im = Image.open(io.BytesIO(d)); w, h = im.size
                if max(w, h) > MAX:
                    sc = MAX / float(max(w, h)); im = im.resize((int(w * sc), int(h * sc)), Image.LANCZOS)
                b = io.BytesIO()
                if low.endswith(".png"):
                    im.save(b, "PNG", optimize=True)
                else:
                    im.convert("RGB").save(b, "JPEG", quality=85, optimize=True)
                nd = b.getvalue()
                if len(nd) < len(d):
                    d = nd
            except Exception:
                pass
        zout.writestr(it, d)
    zout.close(); zin.close()


def close_only_target():
    """실행 중인 PowerPoint에서 대상 파일만 닫는다 (Quit 안 함 → 다른 창/앱 유지)."""
    try:
        import win32com.client
        ppt = win32com.client.GetActiveObject("PowerPoint.Application")
    except Exception:
        return  # 실행 중인 PowerPoint 없음
    target = os.path.basename(DST).lower()
    for p in list(ppt.Presentations):
        try:
            if os.path.basename(p.FullName).lower() == target:
                p.Close()
        except Exception:
            pass


if __name__ == "__main__":
    build_tmp()
    try:
        os.replace(TMP, DST)
    except PermissionError:
        close_only_target()
        os.replace(TMP, DST)
    print("compact", round(os.path.getsize(DST) / 1e6, 2), "MB")
