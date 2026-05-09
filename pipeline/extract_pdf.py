"""Stage 3: extract searchable text from every PDF.

Uses pdfplumber. Writes one .txt per PDF to extracted/pdf-text/<id>.txt.
Updates manifest entry with extracted.text_path.
"""
from __future__ import annotations
import json
from pathlib import Path

from tqdm import tqdm

from .config import MANIFEST_PATH, ROOT, EX_PDF_TEXT, ensure_dirs


def _extract(pdf_path: Path) -> str:
    try:
        import pdfplumber
    except ImportError:
        raise SystemExit("pdfplumber missing. pip install -r requirements.txt")
    out: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            out.append(f"\n\n=== PAGE {i} ===\n{text}")
    return "".join(out).strip()


def run() -> None:
    ensure_dirs()
    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    pdfs = [f for f in manifest["files"] if f.get("type") == "pdf" and f.get("local_path")]
    for f in tqdm(pdfs, desc="extracting", unit="pdf"):
        src = ROOT / f["local_path"]
        if not src.exists():
            continue
        out_path = EX_PDF_TEXT / f"{f['id']}.txt"
        if out_path.exists() and out_path.stat().st_size > 0:
            f.setdefault("extracted", {})["text_path"] = str(out_path.relative_to(ROOT)).replace("\\", "/")
            continue
        try:
            text = _extract(src)
        except Exception as e:
            tqdm.write(f"  fail {f['id']}: {e}")
            continue
        out_path.write_text(text, encoding="utf-8")
        f.setdefault("extracted", {})["text_path"] = str(out_path.relative_to(ROOT)).replace("\\", "/")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  extracted text for {len(pdfs)} PDFs")


if __name__ == "__main__":
    run()
