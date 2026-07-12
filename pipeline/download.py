"""Stage 1: parallel resumable downloader.

Reads data/url-list.txt, downloads each URL into the appropriate
downloads/{pdf,video,image}/ folder. Uses HTTP Range to resume partials.
Writes/updates data/manifest.json with one entry per file.

Usage:
    python -m pipeline.download
    python -m pipeline.download --concurrency 8
    python -m pipeline.download --dry-run
"""
from __future__ import annotations
import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse, unquote

import httpx
from slugify import slugify
from tqdm.asyncio import tqdm

from .config import (
    URL_LIST_PATH, MANIFEST_PATH, USER_AGENT,
    DOWNLOAD_CONCURRENCY, DOWNLOAD_TIMEOUT_S, DOWNLOAD_CHUNK_BYTES,
    RETRY_MAX, RETRY_BASE_DELAY_S,
    file_type_for, download_dir_for, ensure_dirs,
)


def _filename_from_url(url: str) -> str:
    p = urlparse(url).path
    name = unquote(Path(p).name)
    return name or "unnamed"


def _slug_from_url(url: str) -> str:
    name = _filename_from_url(url)
    stem = Path(name).stem
    return slugify(stem)[:80] or "file"


def _load_manifest() -> dict:
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rubric_version": "1.0",
        "files": [],
    }


def _save_manifest(manifest: dict) -> None:
    manifest["generated_at"] = datetime.now(timezone.utc).isoformat()
    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _index_manifest(manifest: dict) -> dict[str, dict]:
    # Guard against None/empty source_url (all video-type entries have one,
    # since video content comes from DVIDS, not this column) colliding on a
    # single dict key.
    return {f["source_url"]: f for f in manifest["files"] if f.get("source_url")}


async def _download_one(
    client: httpx.AsyncClient,
    url: str,
    sem: asyncio.Semaphore,
    manifest_index: dict[str, dict],
    pbar: tqdm,
) -> dict | None:
    async with sem:
        ext = Path(urlparse(url).path).suffix.lower()
        ftype = file_type_for(ext)
        if ftype is None:
            pbar.write(f"  skip (unknown ext): {url}")
            pbar.update(1)
            return None

        dest_dir = download_dir_for(ftype)
        dest_dir.mkdir(parents=True, exist_ok=True)
        fname = _filename_from_url(url)
        dest = dest_dir / fname

        # Resume support: ask server for size, compare to local
        existing = manifest_index.get(url)
        if dest.exists() and existing and existing.get("size_bytes"):
            local_size = dest.stat().st_size
            if local_size == existing["size_bytes"]:
                pbar.write(f"  cached: {fname}")
                pbar.update(1)
                return existing

        # Attempt with retry
        last_err: Exception | None = None
        for attempt in range(1, RETRY_MAX + 1):
            try:
                start = dest.stat().st_size if dest.exists() else 0
                headers = {"User-Agent": USER_AGENT}
                if start > 0:
                    headers["Range"] = f"bytes={start}-"

                async with client.stream("GET", url, headers=headers) as r:
                    if r.status_code == 416:
                        # Range not satisfiable; file likely complete
                        break
                    if r.status_code not in (200, 206):
                        raise httpx.HTTPStatusError(
                            f"HTTP {r.status_code}", request=r.request, response=r
                        )
                    mode = "ab" if start > 0 and r.status_code == 206 else "wb"
                    with dest.open(mode) as fh:
                        async for chunk in r.aiter_bytes(DOWNLOAD_CHUNK_BYTES):
                            fh.write(chunk)
                break
            except Exception as e:
                last_err = e
                if attempt < RETRY_MAX:
                    await asyncio.sleep(RETRY_BASE_DELAY_S * attempt)
                    continue
                pbar.write(f"  FAIL {url}: {e}")
                pbar.update(1)
                return None

        size = dest.stat().st_size if dest.exists() else 0
        record = {
            "id": _slug_from_url(url),
            "title": Path(fname).stem.replace("_", " ").replace("-", " ").title(),
            "category": "other",
            "agency": "OTHER",
            "type": ftype,
            "date_event": None,
            "date_released": "2026-05-08",
            "source_url": url,
            "local_path": str(dest.relative_to(dest.parent.parent.parent)).replace("\\", "/"),
            "size_bytes": size,
            "sha256": None,
            "redacted": False,
            "summary": None,
            "score": None,
            "extracted": {
                "text_path": None,
                "transcript_path": None,
                "thumbnail_path": None,
            },
            "geo": {"lat": None, "lng": None, "place": None},
        }
        # Preserve any prior enrichment (title, category, agency, etc.). Critically
        # this must include "id" and "date_released": the fresh record above builds
        # id from the URL's filename via _slug_from_url(), which does NOT match the
        # stable, title-derived id parse_csv.py assigns (e.g. a CSV row titled
        # "..._Section_001" produces id "...-section-001", but its PDF link filename
        # is "..._section_1.pdf" -> _slug_from_url gives "...-section-1"). Without
        # this, every file whose local download cache misses a byte-exact size match
        # gets silently re-issued a new id/URL, breaking every existing inbound link
        # and violating the site's "never delete/rename a file page" rule.
        if existing:
            for k in ("id", "title", "category", "agency", "type", "date_event",
                      "date_released", "summary", "geo", "redacted", "score"):
                if existing.get(k) not in (None, "", "other", "OTHER"):
                    record[k] = existing[k]
        elif record["agency"] == "OTHER":
            # No existing manifest entry matched this URL, and this generic-download
            # path can only ever produce placeholder agency/category/title data (it
            # has no source of truth for real metadata). Rather than publish a junk
            # file page, drop it. Real new files come from parse_csv.py, which always
            # assigns a real agency; this path is a supplementary asset fetch only.
            pbar.update(1)
            return None

        pbar.update(1)
        return record


async def _run_async(urls: list[str], concurrency: int, dry_run: bool) -> None:
    manifest = _load_manifest()
    manifest_index = _index_manifest(manifest)

    if dry_run:
        for u in urls:
            print(f"  [dry-run] {file_type_for(Path(urlparse(u).path).suffix.lower())} <- {u}")
        return

    sem = asyncio.Semaphore(concurrency)
    timeout = httpx.Timeout(DOWNLOAD_TIMEOUT_S, connect=30)
    limits = httpx.Limits(max_connections=concurrency * 2)

    async with httpx.AsyncClient(
        timeout=timeout, limits=limits, follow_redirects=True, http2=True
    ) as client:
        with tqdm(total=len(urls), desc="downloading", unit="file") as pbar:
            tasks = [_download_one(client, u, sem, manifest_index, pbar) for u in urls]
            results = await asyncio.gather(*tasks)

    new_records = [r for r in results if r is not None]

    # Merge by id, NOT source_url: every video-type CSV row has source_url=None
    # (video content comes from DVIDS, not the PDF|Image Link column), so keying
    # this merge by source_url collapses every video entry into a single dict
    # slot and silently drops the rest (observed: 118 video entries -> 10 on a
    # 334-file manifest). id is always present and unique (parse_csv.py enforces
    # this via seen_ids), so it is the only safe merge key here.
    new_by_id = {r["id"]: r for r in new_records}
    keep = {f["id"]: f for f in manifest["files"] if f["id"] not in new_by_id}
    by_id = {**keep, **new_by_id}
    manifest["files"] = sorted(by_id.values(), key=lambda x: x["id"])
    _save_manifest(manifest)
    print(f"\n  manifest now has {len(manifest['files'])} files -> {MANIFEST_PATH}")


def run(concurrency: int = DOWNLOAD_CONCURRENCY, dry_run: bool = False) -> None:
    ensure_dirs()
    if not URL_LIST_PATH.exists():
        print(f"  (no {URL_LIST_PATH}; run parse-inputs first)")
        return
    urls = [u.strip() for u in URL_LIST_PATH.read_text(encoding="utf-8").splitlines() if u.strip()]
    if not urls:
        print("  (url-list is empty)")
        return
    asyncio.run(_run_async(urls, concurrency, dry_run))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--concurrency", type=int, default=DOWNLOAD_CONCURRENCY)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    run(args.concurrency, args.dry_run)
