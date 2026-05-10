"""Stage 1c: upload all downloaded files to Cloudflare R2.

Reads credentials from _scratch/r2-creds.json (gitignored):
    {
      "access_key_id":     "...",
      "secret_access_key": "...",
      "endpoint_url":      "https://<account>.r2.cloudflarestorage.com",
      "account_id":        "...",
      "bucket":            "pursueufotracker-media",
      "public_domain":     "https://media.pursueufotracker.com"
    }

For each entry:
- Uploads the local file to R2 with proper Content-Type
- Sets `mirror_url` on the manifest entry to the public R2 URL
- Skips if remote object already exists with matching size

After upload, manifest.mirror_url is the URL the site templates use for
download buttons and viewers.
"""
from __future__ import annotations
import json
import mimetypes
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import boto3
from botocore.config import Config
from tqdm import tqdm

from .config import MANIFEST_PATH, ROOT


CREDS_PATH = ROOT / "_scratch" / "r2-creds.json"
LOCAL_PATHS_PATH = ROOT / "_scratch" / "local-paths.json"

# Special MIME overrides
MIME_OVERRIDES = {".vtt": "text/vtt", ".srt": "application/x-subrip"}


def _content_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in MIME_OVERRIDES:
        return MIME_OVERRIDES[ext]
    ct, _ = mimetypes.guess_type(path.name)
    return ct or "application/octet-stream"


def _key_for(file_id: str, src: Path) -> str:
    """R2 object key. Use type/id.ext so videos/, pdf/, image/ stay organized."""
    rel = src.relative_to(ROOT / "downloads")
    return str(rel).replace("\\", "/")


def _upload_one(client, bucket: str, src: Path, key: str) -> tuple[bool, int, str | None]:
    """Returns (success, size_bytes, error)."""
    try:
        # Check if remote already exists with matching size
        size_local = src.stat().st_size
        try:
            head = client.head_object(Bucket=bucket, Key=key)
            if head.get("ContentLength") == size_local:
                return True, size_local, "cached"
        except client.exceptions.ClientError:
            pass

        client.upload_file(
            str(src), bucket, key,
            ExtraArgs={
                "ContentType": _content_type(src),
                "CacheControl": "public, max-age=86400, immutable",
            },
        )
        return True, size_local, None
    except Exception as e:
        return False, 0, f"{type(e).__name__}: {e}"


def run(concurrency: int = 8) -> None:
    if not CREDS_PATH.exists():
        print(f"  no R2 creds at {CREDS_PATH} - skipping")
        return
    if not MANIFEST_PATH.exists():
        print("  no manifest")
        return

    creds = json.loads(CREDS_PATH.read_text(encoding="utf-8"))
    bucket = creds["bucket"]
    public_domain = creds["public_domain"].rstrip("/")

    client = boto3.client(
        "s3",
        endpoint_url=creds["endpoint_url"],
        aws_access_key_id=creds["access_key_id"],
        aws_secret_access_key=creds["secret_access_key"],
        config=Config(
            region_name="auto",
            retries={"max_attempts": 5, "mode": "standard"},
            max_pool_connections=concurrency * 2,
        ),
    )

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    local_paths = {}
    if LOCAL_PATHS_PATH.exists():
        local_paths = json.loads(LOCAL_PATHS_PATH.read_text(encoding="utf-8"))

    # Build upload tasks
    tasks = []  # list of (entry, src_path, key)
    for f in manifest["files"]:
        local_rel = f.get("local_path") or local_paths.get(f["id"])
        if not local_rel:
            continue
        src = ROOT / local_rel
        if not src.exists():
            print(f"  missing on disk: {src}")
            continue
        key = _key_for(f["id"], src)
        tasks.append((f, src, key))

    print(f"  uploading {len(tasks)} files to R2 bucket {bucket}...")

    statuses = {"uploaded": 0, "cached": 0, "failed": 0}
    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = {ex.submit(_upload_one, client, bucket, src, key): (f, key)
                   for (f, src, key) in tasks}
        with tqdm(total=len(futures), desc="r2", unit="file") as pbar:
            for fut in as_completed(futures):
                f, key = futures[fut]
                ok, size, err = fut.result()
                if ok:
                    if err == "cached":
                        statuses["cached"] += 1
                    else:
                        statuses["uploaded"] += 1
                    f["mirror_url"] = f"{public_domain}/{key}"
                    f["size_bytes"] = size
                else:
                    statuses["failed"] += 1
                    print(f"\n  FAIL {f['id']}: {err}")
                pbar.update(1)
                pbar.set_postfix(statuses)

    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  status: {statuses}")
    mirrored = sum(1 for f in manifest["files"] if f.get("mirror_url"))
    print(f"  files now mirror_url'd: {mirrored}/{len(manifest['files'])}")
    print(f"  example: {manifest['files'][0].get('mirror_url') or '(none)'}")


if __name__ == "__main__":
    run()
