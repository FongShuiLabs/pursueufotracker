"""Stage 9.6 (optional): generate 9:16 vertical clips with burned-in captions
for TikTok / Reels / Shorts distribution.

For each video:
- Take a CLIP_LEN_S segment (start at 10% into the video by default)
- Crop center to 9:16 (1080x1920)
- Burn in caption track from extracted/transcripts/<id>.vtt

Requires ffmpeg with libass on PATH.
Output: generated/clips/<id>.mp4
"""
from __future__ import annotations
import json
import shutil
import subprocess
from pathlib import Path

from tqdm import tqdm

from .config import (
    MANIFEST_PATH, ROOT, GENERATED_DIR, EX_TRANSCRIPTS, ensure_dirs,
)


CLIP_LEN_S = 45
CLIP_W, CLIP_H = 1080, 1920


def _make_clip(src: Path, vtt: Path, out: Path, file_id: str) -> bool:
    sub_arg = ""
    if vtt.exists():
        sub_arg = (
            f",subtitles='{vtt.as_posix()}':force_style="
            f"'Fontsize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
            f"BorderStyle=3,Outline=2,Shadow=0,Alignment=2,MarginV=120'"
        )
    vf = (
        f"scale=-2:{CLIP_H},crop={CLIP_W}:{CLIP_H}:(in_w-{CLIP_W})/2:0"
        f"{sub_arg}"
    )
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", str(int(CLIP_LEN_S * 0.1)),
                "-i", str(src),
                "-t", str(CLIP_LEN_S),
                "-vf", vf,
                "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart",
                str(out),
            ],
            capture_output=True, timeout=600, check=True,
        )
        return out.exists()
    except subprocess.CalledProcessError as e:
        print(f"  ffmpeg fail {file_id}: {e.stderr.decode()[-300:]}")
        return False


def run() -> None:
    ensure_dirs()
    if shutil.which("ffmpeg") is None:
        print("  ffmpeg not on PATH - skipping clips")
        return
    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return
    out_dir = GENERATED_DIR / "clips"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    videos = [f for f in manifest["files"] if f.get("type") == "video" and f.get("local_path")]
    for f in tqdm(videos, desc="clips", unit="video"):
        src = ROOT / f["local_path"]
        vtt = EX_TRANSCRIPTS / f"{f['id']}.vtt"
        out = out_dir / f"{f['id']}.mp4"
        if not src.exists() or out.exists():
            continue
        _make_clip(src, vtt, out, f["id"])
    print(f"  clips: up to {len(videos)} short-form videos")


if __name__ == "__main__":
    run()
