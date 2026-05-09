"""Stage 7: build a Lunr.js search index from PDF text + transcripts.

Output: generated/search-index.json with Lunr-compatible serialized index
plus a docs lookup. Client-side JS hydrates Lunr from this file.
"""
from __future__ import annotations
import json
from pathlib import Path

from .config import (
    MANIFEST_PATH, ROOT, GEN_SEARCH, EX_PDF_TEXT, EX_TRANSCRIPTS, ensure_dirs,
)


def _doc_text(f: dict) -> str:
    pieces = [f.get("title", ""), f.get("summary") or ""]
    ex = f.get("extracted") or {}
    tp = ex.get("text_path")
    if tp:
        try:
            pieces.append((ROOT / tp).read_text(encoding="utf-8", errors="ignore"))
        except FileNotFoundError:
            pass
    # Transcript .txt sidecar
    txt = EX_TRANSCRIPTS / f"{f['id']}.txt"
    if txt.exists():
        pieces.append(txt.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(p for p in pieces if p)


def run() -> None:
    ensure_dirs()
    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return
    try:
        from lunr import lunr
    except ImportError:
        print("  lunr missing. pip install -r requirements.txt")
        return

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    docs = []
    lookup = {}
    for f in manifest["files"]:
        body = _doc_text(f)
        docs.append({"id": f["id"], "title": f.get("title", ""), "body": body})
        lookup[f["id"]] = {
            "title": f.get("title"),
            "agency": f.get("agency"),
            "category": f.get("category"),
            "score": (f.get("score") or {}).get("value"),
            "url": f"files/{f['id']}.html",
        }

    idx = lunr(ref="id", fields=("title", "body"), documents=docs)
    GEN_SEARCH.write_text(json.dumps({
        "index": idx.serialize(),
        "lookup": lookup,
    }, ensure_ascii=False), encoding="utf-8")
    print(f"  search index: {len(docs)} docs -> {GEN_SEARCH}")


if __name__ == "__main__":
    run()
