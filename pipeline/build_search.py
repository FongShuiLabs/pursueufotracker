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


# Cap the deep per-doc text that goes into the Lunr index. Cloudflare Pages
# rejects any single asset over 25 MiB; with the full extracted PDF text +
# transcripts of every file, search-index.json hit 27.1 MiB at 294 files
# (Drop 03) and every deploy failed asset validation. Titles and summaries are
# always indexed in full (small, highest-signal); only the long extracted/
# transcript body is capped. ~5k chars/doc keeps the leading, most relevant
# content searchable while leaving comfortable headroom for future drops.
MAX_DOC_BODY_CHARS = 5000


def _doc_text(f: dict) -> str:
    # Title + summary always indexed in full.
    head = "\n".join(p for p in (f.get("title", ""), f.get("summary") or "") if p)
    pieces: list[str] = []
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
    body = "\n".join(p for p in pieces if p)[:MAX_DOC_BODY_CHARS]
    return f"{head}\n{body}".strip()


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
            "url": f"/files/{f['id']}",
        }

    idx = lunr(ref="id", fields=("title", "body"), documents=docs)
    GEN_SEARCH.write_text(json.dumps({
        "index": idx.serialize(),
        "lookup": lookup,
    }, ensure_ascii=False), encoding="utf-8")
    print(f"  search index: {len(docs)} docs -> {GEN_SEARCH}")


if __name__ == "__main__":
    run()
