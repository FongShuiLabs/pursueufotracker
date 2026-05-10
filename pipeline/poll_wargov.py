"""War.gov PURSUE poller.

Fetches the canonical UAP CSV at war.gov/Portals/1/Interactive/2026/UFO/uap-csv.csv,
hashes it, and compares against data/poll-state.json. If the hash changed:
  - Saves the new CSV to _scratch/uap-csv.csv
  - Updates poll-state.json with new hash + row count + timestamp
  - Exits 10 (signal: NEW DROP DETECTED) so the GitHub Action can branch.
If unchanged, updates last_polled_at and exits 0.

Run locally:
    python -m pipeline.poll_wargov

Exit codes:
    0  - polled successfully, no change
    10 - NEW DROP detected (CSV hash changed)
    1  - poll failed (network, parse, etc.)
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests

ROOT = Path(__file__).resolve().parent.parent
CSV_URL = "https://www.war.gov/Portals/1/Interactive/2026/UFO/uap-csv.csv"
STATE_PATH = ROOT / "data" / "poll-state.json"
CSV_OUT = ROOT / "_scratch" / "uap-csv.csv"

HEADERS = {
    "Referer": "https://www.war.gov/UFO/",
    "Origin": "https://www.war.gov",
    "User-Agent": "Mozilla/5.0 (compatible; pursueufotracker-poller/1.0; +https://pursueufotracker.com)",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {
        "last_polled_at": None,
        "last_change_at": None,
        "csv_sha256": None,
        "row_count": 0,
        "history": [],
    }


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _row_count(csv_bytes: bytes) -> int:
    text = csv_bytes.decode("utf-8-sig", errors="replace")
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    return max(0, len(rows) - 1)


def main() -> int:
    print(f"[{_now_iso()}] polling {CSV_URL}")
    try:
        resp = requests.get(CSV_URL, headers=HEADERS, impersonate="chrome", timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"FAIL: fetch error: {e}", file=sys.stderr)
        return 1

    csv_bytes = resp.content
    new_hash = hashlib.sha256(csv_bytes).hexdigest()
    new_count = _row_count(csv_bytes)
    state = _load_state()
    prev_hash = state.get("csv_sha256")
    prev_count = state.get("row_count", 0)

    state["last_polled_at"] = _now_iso()

    if prev_hash == new_hash:
        print(f"NO CHANGE: hash={new_hash[:12]} rows={new_count}")
        _save_state(state)
        return 0

    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    CSV_OUT.write_bytes(csv_bytes)

    delta = new_count - prev_count
    state["csv_sha256"] = new_hash
    state["row_count"] = new_count
    state["last_change_at"] = _now_iso()
    state["history"] = (state.get("history") or [])[-19:] + [{
        "at": state["last_change_at"],
        "sha256": new_hash,
        "row_count": new_count,
        "delta": delta,
    }]
    _save_state(state)

    print(f"NEW DROP: hash={new_hash[:12]} rows={new_count} delta={delta:+d}")
    gh_out = sys.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"new_drop=true\n")
            f.write(f"row_count={new_count}\n")
            f.write(f"delta={delta}\n")
            f.write(f"sha256={new_hash}\n")
    return 10


if __name__ == "__main__":
    sys.exit(main())
