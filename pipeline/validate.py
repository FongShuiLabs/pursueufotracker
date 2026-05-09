"""Sanity check current state. Read-only. Reports gaps."""
from __future__ import annotations
import json
from pathlib import Path

from .config import (
    MANIFEST_PATH, ROOT, EX_PDF_TEXT, EX_TRANSCRIPTS, EX_THUMBNAILS,
    GEN_FILES, GEN_OG, GEN_SEARCH,
)


def run() -> None:
    if not MANIFEST_PATH.exists():
        print("[FAIL] no manifest.json")
        return
    m = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = m["files"]
    n = len(files)
    print(f"manifest:           {n} files")

    types = {}
    for f in files:
        types[f["type"]] = types.get(f["type"], 0) + 1
    for k, v in sorted(types.items()):
        print(f"  type {k:6s}      {v}")

    missing_local = sum(1 for f in files if not f.get("local_path") or not (ROOT / f["local_path"]).exists())
    print(f"missing on disk:    {missing_local}")
    no_hash = sum(1 for f in files if not f.get("sha256"))
    print(f"missing sha256:     {no_hash}")
    pdfs = [f for f in files if f["type"] == "pdf"]
    no_text = sum(1 for f in pdfs if not (f.get("extracted") or {}).get("text_path"))
    print(f"pdfs no text:       {no_text} / {len(pdfs)}")
    videos = [f for f in files if f["type"] == "video"]
    no_thumb = sum(1 for f in videos if not (f.get("extracted") or {}).get("thumbnail_path"))
    no_trans = sum(1 for f in videos if not (f.get("extracted") or {}).get("transcript_path"))
    print(f"videos no thumb:    {no_thumb} / {len(videos)}")
    print(f"videos no trans:    {no_trans} / {len(videos)}")
    no_score = sum(1 for f in files if not (f.get("score") or {}).get("value"))
    print(f"unscored:           {no_score}")
    print(f"page htmls:         {sum(1 for _ in GEN_FILES.glob('*.html'))}")
    print(f"og cards:           {sum(1 for _ in GEN_OG.glob('*.png'))}")
    print(f"search index:       {'yes' if GEN_SEARCH.exists() else 'no'}")


if __name__ == "__main__":
    run()
