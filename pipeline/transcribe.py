"""Stage 5: Whisper transcribe every video.

Writes:
  extracted/transcripts/<id>.json   - full Whisper segments + timestamps
  extracted/transcripts/<id>.vtt    - WebVTT for HTML5 <track>
  extracted/transcripts/<id>.txt    - plain text for search index

Resumable: skips videos whose transcripts already exist.
"""
from __future__ import annotations
import json
from pathlib import Path

from tqdm import tqdm

from .config import (
    MANIFEST_PATH, ROOT, EX_TRANSCRIPTS,
    WHISPER_MODEL, WHISPER_LANG, ensure_dirs,
)


def _segments_to_vtt(segments: list[dict]) -> str:
    def fmt(t: float) -> str:
        h = int(t // 3600); m = int((t % 3600) // 60)
        s = t - h * 3600 - m * 60
        return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ".")
    out = ["WEBVTT", ""]
    for i, seg in enumerate(segments, 1):
        out.append(str(i))
        out.append(f"{fmt(seg['start'])} --> {fmt(seg['end'])}")
        out.append(seg["text"].strip())
        out.append("")
    return "\n".join(out)


def run() -> None:
    ensure_dirs()
    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return
    try:
        import whisper
    except ImportError:
        print("  openai-whisper missing. pip install -r requirements.txt")
        return

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    videos = [f for f in manifest["files"] if f.get("type") == "video" and f.get("local_path")]
    if not videos:
        print("  (no videos to transcribe)")
        return

    print(f"  loading whisper model: {WHISPER_MODEL}")
    model = whisper.load_model(WHISPER_MODEL)

    for f in tqdm(videos, desc="transcribing", unit="video"):
        src = ROOT / f["local_path"]
        if not src.exists():
            continue
        out_json = EX_TRANSCRIPTS / f"{f['id']}.json"
        out_vtt  = EX_TRANSCRIPTS / f"{f['id']}.vtt"
        out_txt  = EX_TRANSCRIPTS / f"{f['id']}.txt"
        if out_json.exists() and out_vtt.exists() and out_txt.exists():
            f.setdefault("extracted", {})["transcript_path"] = str(out_vtt.relative_to(ROOT)).replace("\\", "/")
            continue
        try:
            result = model.transcribe(str(src), language=WHISPER_LANG, verbose=False)
        except Exception as e:
            tqdm.write(f"  fail transcribe {f['id']}: {e}")
            continue
        out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        out_vtt.write_text(_segments_to_vtt(result.get("segments", [])), encoding="utf-8")
        out_txt.write_text((result.get("text") or "").strip(), encoding="utf-8")
        f.setdefault("extracted", {})["transcript_path"] = str(out_vtt.relative_to(ROOT)).replace("\\", "/")

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  transcripts for {len(videos)} videos")


if __name__ == "__main__":
    run()
