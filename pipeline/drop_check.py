"""Drop guard: has the poller detected a war.gov change the site hasn't ingested yet?

This exists because on 2026-06-12 a real new drop (Drop 03, 294 rows) landed
mid-session, the poller caught it and committed `[NEW DROP] ...`, but it slid
past unnoticed in a `git pull --rebase` (the [NEW DROP] commit was buried among
"poll: unchanged" commits). Detection was never the gap - SURFACING the
detected-but-not-ingested state was.

Mechanism: the poller writes the current war.gov CSV fingerprint to
`data/poll-state.json` (csv_sha256 + row_count). After a drop is ingested and
the site rebuilt, we stamp that same fingerprint into `data/last-ingest.json`
via `--mark`. If the two diverge, a drop is pending.

Usage:
    python -m pipeline.drop_check          # check + report (wired to a SessionStart hook)
    python -m pipeline.drop_check --mark   # record current poll-state as ingested (run AFTER a drop ingest)

Exit code is always 0 (informational); the loud banner is the signal, not the code.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

from .config import ROOT

POLL_STATE = ROOT / "data" / "poll-state.json"
LAST_INGEST = ROOT / "data" / "last-ingest.json"


def _read(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception as e:  # corrupt file - treat as unknown, don't crash the hook
        print(f"  drop_check: could not read {path.name}: {e}")
        return None


def mark_ingested() -> None:
    """Stamp the current poller fingerprint as the ingested baseline."""
    poll = _read(POLL_STATE)
    if not poll:
        sys.exit("  drop_check --mark: data/poll-state.json missing; cannot mark.")
    marker = {
        "ingested_csv_sha256": poll.get("csv_sha256"),
        "ingested_row_count": poll.get("row_count"),
        "ingested_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "_note": "Written by `python -m pipeline.drop_check --mark` after a drop was ingested + the site rebuilt. drop_check compares poll-state.json against this.",
    }
    LAST_INGEST.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")
    print(f"  drop_check: marked ingested at row_count={marker['ingested_row_count']} "
          f"(csv_sha256 {str(marker['ingested_csv_sha256'])[:12]}...).")


def check() -> None:
    poll = _read(POLL_STATE)
    if not poll:
        print("DROP STATUS: unknown (no data/poll-state.json - poller has not run locally).")
        return
    ingest = _read(LAST_INGEST)
    cur_sha = poll.get("csv_sha256")
    cur_rows = poll.get("row_count")
    changed_at = poll.get("last_change_at")

    if not ingest:
        print("=" * 64)
        print("  DROP STATUS: no ingest baseline recorded yet.")
        print(f"  Poller currently sees {cur_rows} CSV rows (last change {changed_at}).")
        print("  Run `python -m pipeline.drop_check --mark` after confirming the")
        print("  site is current, so future drops are detected automatically.")
        print("=" * 64)
        return

    ing_sha = ingest.get("ingested_csv_sha256")
    ing_rows = ingest.get("ingested_row_count")

    if cur_sha and ing_sha and cur_sha == ing_sha:
        print(f"DROP STATUS: current. Site ingested {ing_rows} rows; poller agrees "
              f"(csv unchanged since {ingest.get('ingested_at')}).")
        return

    # Divergence -> a drop (or a war.gov byte-swap) is pending ingestion.
    delta = (cur_rows - ing_rows) if isinstance(cur_rows, int) and isinstance(ing_rows, int) else "?"
    print("!" * 64)
    print("  >>> UN-INGESTED WAR.GOV CHANGE DETECTED <<<")
    print(f"  Poller sees : {cur_rows} CSV rows  (changed {changed_at})")
    print(f"  Site has    : {ing_rows} rows ingested (at {ingest.get('ingested_at')})")
    print(f"  Delta       : {('+' if isinstance(delta, int) and delta >= 0 else '')}{delta} rows")
    print(f"  csv_sha256  : poller {str(cur_sha)[:12]}...  != ingested {str(ing_sha)[:12]}...")
    print("")
    print("  ACTION: this is the marquee event. Follow DROP02_REACTION.md:")
    print("    1. Ingest:  python -m pipeline.run all")
    print("    2. Verify the new-file diff (Hard Rule #7) before any public claim")
    print("    3. Rebuild + push, curl-verify live")
    print("    4. python -m pipeline.drop_check --mark   (clears this warning)")
    print("!" * 64)


def run() -> None:
    if "--mark" in sys.argv:
        mark_ingested()
    else:
        check()


if __name__ == "__main__":
    run()
