"""Stage 1b: download all files from the manifest.

For each entry:
- Videos -> entry["video_url"] (DVIDS CloudFront, public)
- PDFs/images -> entry["source_url"] (war.gov/medialink, needs curl_cffi Chrome impersonation)
- Captions -> entry["caption_vtt_url"] (DVIDS, public)
- Thumbnails -> entry["thumbnail_url"] (DVIDS / war.gov)

Saves into downloads/{video,pdf,image}/<id>.<ext>
Updates manifest.local_path, manifest.size_bytes (sha256 stage hashes later).

Resumable: skips files already on disk that match the expected size from a previous run.
"""
from __future__ import annotations
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

from curl_cffi import requests
from tqdm import tqdm

from .config import (
    MANIFEST_PATH, DOWNLOADS_DIR, EX_THUMBNAILS, EX_TRANSCRIPTS, ROOT, ensure_dirs,
)
DOWNLOAD_DIR = DOWNLOADS_DIR
EX_THUMBS = EX_THUMBNAILS


WARGOV_HEADERS = {
    "Referer": "https://www.war.gov/UFO/",
    "Origin": "https://www.war.gov",
}

EXT_FOR_TYPE = {"pdf": ".pdf", "video": ".mp4", "image": ".jpg"}
SUBDIR_FOR_TYPE = {"pdf": "pdf", "video": "video", "image": "image"}


def _ext_from_url(url: str, fallback: str) -> str:
    p = urlparse(url).path
    for ext in (".mp4", ".mov", ".webm", ".pdf", ".jpg", ".jpeg", ".png", ".gif"):
        if p.lower().endswith(ext):
            return ext
    return fallback


def _download_url(url: str, dest: Path, label: str) -> tuple[bool, int, str | None]:
    """Returns (success, size_bytes, error_msg)."""
    try:
        r = requests.get(url, impersonate="chrome131", headers=WARGOV_HEADERS,
                         timeout=120, stream=True)
        if r.status_code != 200:
            return False, 0, f"HTTP {r.status_code}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        size = 0
        with dest.open("wb") as fh:
            for chunk in r.iter_content(chunk_size=64 * 1024):
                if chunk:
                    fh.write(chunk)
                    size += len(chunk)
        return True, size, None
    except Exception as e:
        return False, 0, f"{type(e).__name__}: {e}"


def _process_one(f: dict) -> dict:
    """Download primary asset + caption + thumbnail. Returns updated entry."""
    type_ = f["type"]
    ext = EXT_FOR_TYPE.get(type_, ".bin")
    subdir = SUBDIR_FOR_TYPE.get(type_, "other")

    # Primary URL: video uses video_url, others use source_url
    if type_ == "video":
        primary = f.get("video_url") or f.get("source_url")
    else:
        primary = f.get("source_url")

    if not primary:
        f["_download_status"] = "no_url"
        return f

    # Use the URL's extension if it has one (preserves quality marker in filename)
    real_ext = _ext_from_url(primary, ext)
    dest = DOWNLOAD_DIR / subdir / f"{f['id']}{real_ext}"

    if dest.exists() and f.get("size_bytes") and dest.stat().st_size == f["size_bytes"]:
        f["_download_status"] = "cached"
    else:
        ok, size, err = _download_url(primary, dest, f["id"])
        if ok:
            f["local_path"] = str(dest.relative_to(ROOT)).replace("\\", "/")
            f["size_bytes"] = size
            f["_download_status"] = "downloaded"
        else:
            f["_download_status"] = f"failed: {err}"

    # Captions for videos
    if type_ == "video" and f.get("caption_vtt_url"):
        vtt_dest = EX_TRANSCRIPTS / f"{f['id']}.vtt"
        if not vtt_dest.exists():
            ok, _, _ = _download_url(f["caption_vtt_url"], vtt_dest, f["id"] + " vtt")
            if ok:
                f.setdefault("extracted", {})["transcript_path"] = str(vtt_dest.relative_to(ROOT)).replace("\\", "/")

    # Thumbnail
    if f.get("thumbnail_url"):
        thumb_dest = EX_THUMBS / f"{f['id']}.jpg"
        if not thumb_dest.exists():
            ok, _, _ = _download_url(f["thumbnail_url"], thumb_dest, f["id"] + " thumb")
            if ok:
                f.setdefault("extracted", {})["thumbnail_path"] = str(thumb_dest.relative_to(ROOT)).replace("\\", "/")

    return f


def run(concurrency: int = 4) -> None:
    ensure_dirs()
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    EX_THUMBS.mkdir(parents=True, exist_ok=True)
    EX_TRANSCRIPTS.mkdir(parents=True, exist_ok=True)

    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = manifest["files"]
    print(f"  downloading {len(files)} files (concurrency={concurrency})...")

    results: list[dict] = []
    statuses: dict[str, int] = {}

    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = {ex.submit(_process_one, f): f for f in files}
        with tqdm(total=len(futures), desc="files", unit="file") as pbar:
            for fut in as_completed(futures):
                try:
                    f = fut.result()
                except Exception as e:
                    f = futures[fut]
                    f["_download_status"] = f"exception: {e}"
                results.append(f)
                s = f.get("_download_status", "?")
                key = s.split(":")[0]
                statuses[key] = statuses.get(key, 0) + 1
                pbar.update(1)
                pbar.set_postfix(statuses)

    # Strip the temporary status field before writing
    by_id = {f["id"]: f for f in results}
    manifest["files"] = [by_id[f["id"]] for f in files]  # preserve original order
    for f in manifest["files"]:
        f.pop("_download_status", None)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  status counts: {statuses}")
    downloaded = sum(1 for f in manifest["files"] if f.get("local_path"))
    print(f"  files now mirrored locally: {downloaded}/{len(manifest['files'])}")


if __name__ == "__main__":
    run()
