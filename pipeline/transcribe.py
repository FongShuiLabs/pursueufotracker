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


def _vtt_has_speech(path: Path) -> bool:
    """True only if the .vtt carries real transcribed content. Most PURSUE
    videos are SILENT military infrared/EO sensor captures - Whisper yields an
    empty cue list for them, and an empty transcript must NOT be linked (it
    would render a blank transcript box and back a false 'transcripts on every
    video' claim). Only NASA astronaut audio recordings have real speech."""
    try:
        txt = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False
    body = "".join(
        line for line in txt.splitlines()
        if line.strip() and "-->" not in line and line.strip() != "WEBVTT"
        and not line.strip().isdigit()
    )
    return len(body.strip()) >= 20


def _relink_existing(videos: list[dict]) -> int:
    """Point manifest entries at any transcript that already exists on disk AND
    contains real speech. Runs regardless of whether Whisper is installed, so a
    freshly-parsed manifest (which has no transcript_path) or a machine without
    Whisper still surfaces the transcripts that were generated on a prior run.
    Silent-sensor-video VTTs (empty) are deliberately left unlinked."""
    linked = 0
    for f in videos:
        out_vtt = EX_TRANSCRIPTS / f"{f['id']}.vtt"
        if out_vtt.exists() and _vtt_has_speech(out_vtt):
            f.setdefault("extracted", {})["transcript_path"] = str(out_vtt.relative_to(ROOT)).replace("\\", "/")
            linked += 1
        else:
            # Ensure a stale/empty link never survives a re-parse.
            ex = f.get("extracted") or {}
            if ex.get("transcript_path"):
                ex["transcript_path"] = None
    return linked


def run() -> None:
    ensure_dirs()
    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    videos = [f for f in manifest["files"] if f.get("type") == "video" and f.get("local_path")]
    if not videos:
        print("  (no videos to transcribe)")
        return

    # Always relink transcripts already on disk first - independent of Whisper.
    linked = _relink_existing(videos)

    try:
        import whisper
    except ImportError:
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  openai-whisper missing - linked {linked} existing transcripts, skipped new transcription")
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
            # Already transcribed on a prior run; _relink_existing handled the
            # link (content-gated), so nothing more to do here.
            continue
        try:
            result = model.transcribe(str(src), language=WHISPER_LANG, verbose=False)
        except Exception as e:
            tqdm.write(f"  fail transcribe {f['id']}: {e}")
            continue
        out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        out_vtt.write_text(_segments_to_vtt(result.get("segments", [])), encoding="utf-8")
        out_txt.write_text((result.get("text") or "").strip(), encoding="utf-8")
        if _vtt_has_speech(out_vtt):
            f.setdefault("extracted", {})["transcript_path"] = str(out_vtt.relative_to(ROOT)).replace("\\", "/")

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    linked = sum(1 for f in videos if (f.get("extracted") or {}).get("transcript_path"))
    print(f"  transcripts linked for {linked}/{len(videos)} videos (rest are silent sensor captures)")


if __name__ == "__main__":
    run()
