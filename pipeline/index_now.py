"""IndexNow ping. Pushes sitemap URLs to Bing/Yandex/Naver/Seznam for instant
indexing (typically picked up within hours instead of days).

Reads sitemap.xml at the repo root, extracts all <loc> URLs, and POSTs them
to https://api.indexnow.org/indexnow with our verified key file.

Run after any rebuild that adds or changes URLs:
    python -m pipeline.index_now

Or pass a specific URL list:
    python -m pipeline.index_now https://pursueufotracker.com/files/foo.html

Returns 0 on HTTP 200/202, non-zero otherwise. Safe to run repeatedly -
the API is idempotent and rate-limited per host.
"""
from __future__ import annotations
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "pursueufotracker.com"
KEY = "87d67c40b0bc51fb6a63060e6e0d4575"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"


def _urls_from_sitemap() -> list[str]:
    sitemap = ROOT / "sitemap.xml"
    if not sitemap.exists():
        print(f"WARN: {sitemap} not found", file=sys.stderr)
        return []
    text = sitemap.read_text(encoding="utf-8")
    return re.findall(r"<loc>([^<]+)</loc>", text)


def submit(urls: list[str]) -> int:
    if not urls:
        print("No URLs to submit.")
        return 0
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls,
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"IndexNow {r.status} {r.reason} for {len(urls)} URLs")
            body = r.read().decode("utf-8", errors="replace").strip()
            if body:
                print(f"  body: {body[:400]}")
            return 0 if r.status in (200, 202) else 1
    except urllib.error.HTTPError as e:
        print(f"IndexNow HTTP {e.code} {e.reason}", file=sys.stderr)
        body = e.read().decode("utf-8", errors="replace")
        if body:
            print(f"  body: {body[:600]}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"IndexNow request failed: {e}", file=sys.stderr)
        return 1


def main() -> int:
    args = sys.argv[1:]
    urls = args if args else _urls_from_sitemap()
    return submit(urls)


def run() -> None:
    """Pipeline-stage entry point - never raises, never blocks the build."""
    try:
        rc = main()
        if rc != 0:
            print("  (IndexNow non-zero exit; continuing build)")
    except Exception as e:
        print(f"  IndexNow unexpected error (ignored): {e}")


if __name__ == "__main__":
    sys.exit(main())
