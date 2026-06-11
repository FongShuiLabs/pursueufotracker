"""Per-file integrity monitor: detect war.gov silently swapping file bodies.

WHY THIS EXISTS. The CSV poller (poll_wargov.py) only watches the canonical
CSV (row count + CSV hash). It cannot see war.gov replacing a file's BYTES at
the same URL - which is exactly what happened between May and June 2026 (62
Release-01 PDFs were re-compressed and OCR'd at the same URLs without any CSV
change; see /changes). A reader hashing files daily caught it; our row-level
poller did not. This module closes that gap.

HOW. Each run it HEAD-requests every war.gov-hosted file we have a recorded
size for and compares the current Content-Length against the manifest's
size_bytes. A size change at the same URL means the file body was replaced.
HEAD-only means it can run on a daily cron without re-downloading 1+ GB.

It does NOT decide WHY a body changed (re-compression vs redaction vs removal)
- that requires downloading + comparing the bytes, which a human does after
this flags it. This module's job is detection, not adjudication.

State is written to data/integrity-state.json. When a body change is detected,
it emits a GitHub Actions output (integrity_change=true) so the workflow can
open one issue for human review. Alert-once semantics like the CSV poller.

Run locally:
    python -m pipeline.integrity_check
    python -m pipeline.integrity_check --limit 20   # quick partial check

Exit codes:
    0  - checked successfully (whether or not a change was found)
    1  - check error
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "data" / "manifest.json"
STATE_PATH = ROOT / "data" / "integrity-state.json"
LANDING_URL = "https://www.war.gov/UFO/"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"last_checked_at": None, "flagged": [], "history": []}


def _save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _emit_gh_output(**kwargs) -> None:
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if not gh_out:
        return
    with open(gh_out, "a", encoding="utf-8") as f:
        for k, v in kwargs.items():
            f.write(f"{k}={v}\n")


def _head_size(session, url: str) -> int | None:
    for profile in ("chrome131", "chrome120"):
        try:
            r = session.head(url, impersonate=profile, timeout=25,
                             allow_redirects=True,
                             headers={"Referer": LANDING_URL})
            cl = r.headers.get("Content-Length")
            if cl:
                return int(cl)
        except Exception:
            continue
    return None


def run(limit: int | None = None) -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    # Only war.gov-hosted files we have a recorded size for (videos are DVIDS-
    # hosted and tracked separately).
    targets = [f for f in manifest["files"]
               if f.get("type") in ("pdf", "image")
               and f.get("source_url")
               and f.get("size_bytes")]
    if limit:
        targets = targets[:limit]

    state = _load_state()
    prev_flagged = set(state.get("flagged") or [])

    session = requests.Session()
    try:
        session.get(LANDING_URL, impersonate="chrome131", timeout=20)
    except Exception:
        pass

    changed, unreachable = [], []
    for f in targets:
        live = _head_size(session, f["source_url"])
        if live is None:
            unreachable.append(f["id"])
            continue
        recorded = f["size_bytes"]
        if abs(live - recorded) > max(64, recorded * 0.005):  # >0.5% or >64 bytes
            changed.append({
                "id": f["id"],
                "agency": f.get("agency"),
                "url": f["source_url"],
                "recorded_size": recorded,
                "current_size": live,
                "delta_pct": round((live - recorded) / recorded * 100, 1),
            })

    print(f"[{_now_iso()}] integrity check: {len(targets)} files, "
          f"{len(changed)} body-changed, {len(unreachable)} unreachable",
          flush=True)
    for c in changed[:20]:
        print(f"  CHANGED {c['id']}  {c['recorded_size']:,} -> {c['current_size']:,} "
              f"({c['delta_pct']:+.1f}%)", flush=True)

    state["last_checked_at"] = _now_iso()
    state["checked_count"] = len(targets)
    state["unreachable_count"] = len(unreachable)
    new_flag_ids = {c["id"] for c in changed}

    # Alert only when there are NEWLY-changed files not already flagged.
    newly = new_flag_ids - prev_flagged
    if newly:
        state["history"] = (state.get("history") or [])[-49:] + [{
            "at": state["last_checked_at"],
            "newly_changed": sorted(newly),
            "count": len(newly),
        }]
        state["flagged"] = sorted(new_flag_ids)
        _save_state(state)
        print(f"INTEGRITY CHANGE: {len(newly)} newly body-changed files", flush=True)
        _emit_gh_output(integrity_change="true", changed_count=str(len(newly)),
                        changed_ids=",".join(sorted(newly)))
    else:
        # No new changes; keep flagged list in sync (files may have reverted)
        state["flagged"] = sorted(new_flag_ids)
        _save_state(state)
        print("no new body changes since last check", flush=True)

    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    try:
        return run(args.limit)
    except Exception as e:
        print(f"FAIL: integrity check error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
