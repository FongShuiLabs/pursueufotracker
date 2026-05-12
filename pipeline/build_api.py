"""Stage 9.4: emit /api/files.json (and /api/files/<id>.json per file).

Public read-only API. CORS-enabled (via Cloudflare Pages headers config or
S3 bucket policy at deploy time). Devs and researchers can build derivative
tools; every reference back to us is a backlink.
"""
from __future__ import annotations
import json

from .config import MANIFEST_PATH, GENERATED_DIR, ensure_dirs


def run() -> None:
    ensure_dirs()
    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return
    api_dir = GENERATED_DIR / "api"
    api_dir.mkdir(parents=True, exist_ok=True)
    files_dir = api_dir / "files"
    files_dir.mkdir(exist_ok=True)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    # Index endpoint
    index = {
        "version": 1,
        "generated_at": manifest.get("generated_at"),
        "count": len(manifest["files"]),
        "files": [
            {
                "id": f["id"],
                "title": f.get("title"),
                "agency": f.get("agency"),
                "category": f.get("category"),
                "type": f.get("type"),
                "date_event": f.get("date_event"),
                "score": (f.get("score") or {}).get("value"),
                "url": f"https://pursueufotracker.com/files/{f['id']}",
                "detail_api": f"https://pursueufotracker.com/api/files/{f['id']}.json",
            }
            for f in manifest["files"]
        ],
    }
    (api_dir / "files.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    # Per-file endpoint
    for f in manifest["files"]:
        (files_dir / f"{f['id']}.json").write_text(
            json.dumps(f, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    print(f"  api: 1 index + {len(manifest['files'])} per-file endpoints")


if __name__ == "__main__":
    run()
