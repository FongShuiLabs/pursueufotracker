"""Stage 4: generate poster-frame thumbnails for every video via ffmpeg.

Picks the frame at 10% into the video. Writes JPEG to extracted/thumbnails/<id>.jpg.
Requires ffmpeg on PATH.
"""
from __future__ import annotations
import json
import shutil
import subprocess
from pathlib import Path

from tqdm import tqdm

from .config import MANIFEST_PATH, ROOT, EX_THUMBNAILS, ensure_dirs


def _ffprobe_duration(video: Path) -> float:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
            capture_output=True, text=True, timeout=30,
        )
        return float(r.stdout.strip() or 0.0)
    except Exception:
        return 0.0


def _make_thumb(video: Path, out: Path) -> bool:
    duration = _ffprobe_duration(video)
    seek = max(1.0, duration * 0.10) if duration > 0 else 1.0
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(seek), "-i", str(video),
             "-frames:v", "1", "-q:v", "3", "-vf", "scale=1280:-2", str(out)],
            capture_output=True, timeout=120, check=True,
        )
        return out.exists()
    except Exception:
        return False


def run() -> None:
    ensure_dirs()
    if shutil.which("ffmpeg") is None:
        print("  ffmpeg not on PATH - skipping thumbnails")
        return
    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    videos = [f for f in manifest["files"] if f.get("type") == "video" and f.get("local_path")]
    for f in tqdm(videos, desc="thumbnails", unit="video"):
        src = ROOT / f["local_path"]
        if not src.exists():
            continue
        out_path = EX_THUMBNAILS / f"{f['id']}.jpg"
        if not out_path.exists():
            ok = _make_thumb(src, out_path)
            if not ok:
                tqdm.write(f"  fail thumb {f['id']}")
                continue
        f.setdefault("extracted", {})["thumbnail_path"] = str(out_path.relative_to(ROOT)).replace("\\", "/")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  thumbnails for {len(videos)} videos")


if __name__ == "__main__":
    run()
