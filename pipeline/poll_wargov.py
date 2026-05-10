"""War.gov PURSUE poller.

Polls https://www.war.gov/UFO/ (the public landing page that lists all PURSUE
release links) and hashes the embedded file-link list. If the list changes,
it's a strong signal a new drop has dropped. We tried the canonical CSV
endpoint first but war.gov blocks that path at the edge with HTTP 403; the
HTML landing page is the next-most-canonical signal and is reachable.

Behavior:
  - Fetches the /UFO/ page via curl_cffi (TLS-fingerprinted Chrome).
  - Extracts all anchor hrefs that match the war.gov/medialink/ufo/ pattern.
  - Hashes the sorted, deduped list of file URLs.
  - Compares against data/poll-state.json.
  - If changed: saves the HTML, updates state, exits 10 (NEW DROP).
  - Else: updates last_polled_at, exits 0.

Run locally:
    python -m pipeline.poll_wargov

Exit codes:
    0  - polled successfully, no change
    10 - NEW DROP detected (file list changed)
    1  - poll failed (network, parse, etc.)
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests

ROOT = Path(__file__).resolve().parent.parent
LANDING_URL = "https://www.war.gov/UFO/"
STATE_PATH = ROOT / "data" / "poll-state.json"
HTML_OUT = ROOT / "_scratch" / "war-gov-ufo-latest.html"

# Don't send a custom User-Agent - curl_cffi's impersonate=chromeXXX sets the
# browser-matching UA. Custom UAs like 'pursueufotracker-poller' get blacklisted
# at the war.gov edge, defeating the whole TLS-fingerprint impersonation.
HEADERS = {
    "Referer": "https://www.google.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

LINK_PATTERN = re.compile(
    r'href=["\']([^"\']*medialink/ufo/[^"\']+\.(?:pdf|jpg|jpeg|png|mp4|webm|csv))["\']',
    re.IGNORECASE,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {
        "last_polled_at": None,
        "last_change_at": None,
        "links_sha256": None,
        "row_count": 0,
        "history": [],
    }


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _fetch_landing_html() -> str | None:
    """Fetch war.gov/UFO/ HTML via TLS-impersonated client. Returns text or None."""
    last_err = None
    for profile in ("chrome120", "chrome119", "chrome116", "edge101"):
        try:
            r = requests.get(LANDING_URL, headers=HEADERS, impersonate=profile, timeout=30)
            if r.status_code == 200 and len(r.content) > 5000:
                print(f"  fetched via {profile}: {len(r.content)} bytes")
                return r.text
            last_err = f"HTTP {r.status_code} ({len(r.content)} bytes)"
            print(f"  {profile}: {last_err}, trying next")
        except Exception as e:
            last_err = str(e)
            print(f"  {profile}: {last_err[:80]}")
    print(f"FAIL: all profiles rejected. Last error: {last_err}", file=sys.stderr)
    return None


def _normalize_html(html: str) -> str:
    """Strip volatile bits (cache-busters, build IDs, csrf nonces) so the hash
    only changes when meaningful page content changes."""
    h = html
    h = re.sub(r'\?cdv=\d+', '', h)              # cache-buster query
    h = re.sub(r'name="__RequestVerificationToken"\s+value="[^"]+"', 'name="__RequestVerificationToken" value=""', h)
    h = re.sub(r'<input[^>]*name="ScrollTop"[^>]*>', '', h)
    h = re.sub(r'<input[^>]*name="__dnnVariable"[^>]*>', '', h)  # DNN per-request token
    h = re.sub(r'\s+', ' ', h)                   # whitespace-collapse
    return h


def _try_fetch_csv() -> tuple[int | None, str | None]:
    """Best-effort secondary signal. Returns (row_count, sha256) or (None, None)
    if blocked. From GH Actions IPs this often succeeds even when local doesn't."""
    csv_url = "https://www.war.gov/Portals/1/Interactive/2026/UFO/uap-csv.csv"
    for profile in ("chrome120", "chrome119"):
        try:
            s = requests.Session()
            warm = s.get(LANDING_URL, impersonate=profile, timeout=15)
            if warm.status_code != 200:
                continue
            r = s.get(csv_url, headers={"Referer": LANDING_URL},
                      impersonate=profile, timeout=20)
            if r.status_code == 200 and len(r.content) > 1000:
                # Use csv module - simple line-counting overcounts because file
                # descriptions contain embedded newlines inside quoted cells.
                import csv as _csv, io as _io
                reader = _csv.reader(_io.StringIO(r.text))
                rows = max(0, sum(1 for _ in reader) - 1)
                return rows, hashlib.sha256(r.content).hexdigest()
        except Exception:
            continue
    return None, None


def main() -> int:
    print(f"[{_now_iso()}] polling {LANDING_URL}")
    html = _fetch_landing_html()
    if html is None:
        return 1

    normalized = _normalize_html(html)
    new_hash = hashlib.sha256(normalized.encode("utf-8", errors="replace")).hexdigest()
    csv_rows, csv_hash = _try_fetch_csv()
    new_count = csv_rows if csv_rows is not None else 0
    print(f"  html_hash={new_hash[:12]} csv_rows={csv_rows} csv_hash={csv_hash[:12] if csv_hash else 'BLOCKED'}")

    state = _load_state()
    prev_html_hash = state.get("html_sha256") or state.get("links_sha256")
    prev_csv_hash = state.get("csv_sha256")
    prev_count = state.get("row_count", 0)

    state["last_polled_at"] = _now_iso()

    html_changed = prev_html_hash != new_hash
    csv_changed = csv_hash is not None and prev_csv_hash != csv_hash

    if not html_changed and not csv_changed:
        print(f"NO CHANGE")
        _save_state(state)
        return 0

    HTML_OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML_OUT.write_text(html, encoding="utf-8")

    delta = new_count - prev_count if csv_rows is not None else 0
    state["html_sha256"] = new_hash
    if csv_hash:
        state["csv_sha256"] = csv_hash
    if csv_rows is not None:
        state["row_count"] = csv_rows
    state["last_change_at"] = _now_iso()
    reason = "csv" if csv_changed else "html"
    state["history"] = (state.get("history") or [])[-19:] + [{
        "at": state["last_change_at"],
        "html_sha256": new_hash,
        "csv_sha256": csv_hash,
        "row_count": csv_rows,
        "delta": delta,
        "trigger": reason,
    }]
    _save_state(state)

    print(f"NEW DROP ({reason}): html={new_hash[:12]} csv_rows={csv_rows} delta={delta:+d}")
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"new_drop=true\n")
            f.write(f"row_count={new_count}\n")
            f.write(f"delta={delta}\n")
            f.write(f"sha256={new_hash}\n")
    return 10


if __name__ == "__main__":
    sys.exit(main())
