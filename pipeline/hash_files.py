"""Stage 2: SHA-256 every downloaded file, write into manifest.

Idempotent: skips files whose hash is already in manifest and whose
size hasn't changed.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

from tqdm import tqdm

from .config import MANIFEST_PATH, ROOT, ensure_dirs


def _sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def run() -> None:
    ensure_dirs()
    if not MANIFEST_PATH.exists():
        print("  (no manifest; download first)")
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = manifest["files"]
    for f in tqdm(files, desc="hashing", unit="file"):
        if not f.get("local_path"):
            continue
        p = ROOT / f["local_path"]
        if not p.exists():
            continue
        size = p.stat().st_size
        if f.get("sha256") and f.get("size_bytes") == size:
            continue
        f["sha256"] = _sha256(p)
        f["size_bytes"] = size
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  hashes written to {MANIFEST_PATH}")


if __name__ == "__main__":
    run()
