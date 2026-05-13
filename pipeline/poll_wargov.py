"""War.gov PURSUE poller (durable, CSV-only authority).

Architecture:
  PRIMARY signal: the canonical uap-csv.csv at war.gov.
  Fetch path 1: curl_cffi with TLS-impersonated Chrome (fast, cheap).
  Fetch path 2: Playwright with real headless Chromium (slower but bypasses
                Akamai bot detection that sometimes blocks path 1).
  If either path succeeds, the CSV is authoritative.

  NO HTML-envelope fallback. The /UFO/ HTML page is a JS shell whose hash
  changes constantly (CSRF tokens, CDN edge variation) without any actual
  data change. Using it as a change-detection signal causes false-positive
  NEW DROP alerts every few hours.

  When CSV is unreachable on BOTH paths, the poll exits success-no-change.
  A "consecutive_csv_failures" counter in state tracks this. After 12
  consecutive failures (~6 hours of cron coverage), the workflow opens
  ONE "csv-unreachable" issue for human intervention. Subsequent failures
  do not spam more issues until a successful poll resets the counter.

Behavior:
  - Fetches CSV via curl_cffi (5 impersonation profiles, session warmup
    against /UFO/ first).
  - If all curl_cffi attempts fail, falls back to Playwright (headless
    Chromium, real Chrome fingerprint, real DOM rendering).
  - If CSV obtained: hash + row-count, diff against state, decide.
  - If CSV not obtained: increment failure counter, set new_drop=false,
    return 0. After 12 failures, set csv_stuck=true (workflow opens a
    one-time stuck issue).

Run locally:
    python -m pipeline.poll_wargov

Exit codes:
    0  - polled successfully, no NEW DROP fired (whether CSV reached or not)
    10 - NEW DROP detected (CSV hash changed)
    1  - poll script error (network, parse, etc.)
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
CSV_URL = "https://www.war.gov/Portals/1/Interactive/2026/UFO/uap-csv.csv"
STATE_PATH = ROOT / "data" / "poll-state.json"
CSV_OUT = ROOT / "_scratch" / "uap-csv.csv"

# After this many consecutive failed CSV fetches, surface a stuck-state issue.
# Bot fires roughly every 30 min weekdays / hourly off-hours, so 12 ~= 6 hours.
STUCK_THRESHOLD = 12

HEADERS = {
    "Referer": "https://www.google.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
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
        "consecutive_csv_failures": 0,
        "csv_stuck_alerted": False,
        "history": [],
    }


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _csv_row_count(csv_text: str) -> int:
    """Count records (not lines - descriptions have embedded newlines in quoted cells)."""
    import csv as _csv, io as _io
    reader = _csv.reader(_io.StringIO(csv_text))
    return max(0, sum(1 for _ in reader) - 1)


def _fetch_csv_curlcffi() -> tuple[bytes, str] | None:
    """Fetch CSV via curl_cffi with TLS-impersonated Chrome. Returns (bytes, profile)
    on success, None if all profiles blocked."""
    for profile in ("chrome120", "chrome119", "chrome116", "edge101"):
        try:
            s = requests.Session()
            warm = s.get(LANDING_URL, impersonate=profile, timeout=20)
            if warm.status_code != 200:
                continue
            r = s.get(CSV_URL, headers={"Referer": LANDING_URL},
                      impersonate=profile, timeout=25)
            if r.status_code == 200 and len(r.content) > 1000:
                return r.content, f"curl_cffi:{profile}"
        except Exception:
            continue
    return None


def _fetch_csv_playwright() -> tuple[bytes, str] | None:
    """Fetch CSV via headless Chromium. Uses real Chrome fingerprint and same-context
    cookie warmup so Akamai's bot detection sees a 'real' browser session. Slower
    (~10-15s per attempt) but bypasses the regimes that block curl_cffi."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )
            ctx = browser.new_context(
                user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36"),
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
                timezone_id="America/New_York",
            )
            ctx.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', "
                "{get: () => undefined})"
            )
            page = ctx.new_page()
            try:
                page.goto(LANDING_URL, wait_until="domcontentloaded", timeout=45000)
            except Exception:
                pass  # tolerate timeout; we just want cookies set
            # Now fetch the CSV in the same browser context, which carries cookies
            # and shares the realistic-Chrome TLS handshake.
            resp = page.request.get(CSV_URL, headers={"Referer": LANDING_URL})
            body = resp.body() if resp.ok else None
            browser.close()
            if body and len(body) > 1000:
                return body, "playwright:chromium"
    except Exception as e:
        print(f"  playwright path failed: {str(e)[:140]}", file=sys.stderr)
    return None


def _fetch_csv() -> tuple[bytes, str] | None:
    """Try curl_cffi first (fast), fall back to Playwright (slow but resilient).
    Returns (csv_bytes, source_label) on success, None if both fail."""
    print(f"[{_now_iso()}] fetching {CSV_URL}")
    result = _fetch_csv_curlcffi()
    if result:
        print(f"  obtained via {result[1]} ({len(result[0])} bytes)")
        return result
    print("  curl_cffi paths all blocked, trying Playwright headless Chromium...")
    result = _fetch_csv_playwright()
    if result:
        print(f"  obtained via {result[1]} ({len(result[0])} bytes)")
        return result
    print("  ALL FETCH PATHS BLOCKED")
    return None


def _emit_gh_output(**kwargs) -> None:
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if not gh_out:
        return
    with open(gh_out, "a", encoding="utf-8") as f:
        for k, v in kwargs.items():
            f.write(f"{k}={v}\n")


def main() -> int:
    state = _load_state()
    state["last_polled_at"] = _now_iso()
    prev_failures = state.get("consecutive_csv_failures", 0)
    already_alerted = state.get("csv_stuck_alerted", False)

    result = _fetch_csv()

    if result is None:
        # CSV unreachable on all paths. Increment failure counter, do not fire
        # NEW DROP. If we cross the threshold and haven't alerted yet, signal
        # the workflow to open a one-time 'csv unreachable' issue.
        new_failures = prev_failures + 1
        state["consecutive_csv_failures"] = new_failures
        should_alert = (not already_alerted) and new_failures >= STUCK_THRESHOLD
        if should_alert:
            state["csv_stuck_alerted"] = True
            print(f"CSV STUCK: {new_failures} consecutive failures - emitting alert")
            _emit_gh_output(
                csv_stuck="true",
                consecutive_failures=str(new_failures),
            )
        else:
            print(f"csv unreachable; consecutive_failures={new_failures} "
                  f"(threshold {STUCK_THRESHOLD}, already_alerted={already_alerted})")
        _save_state(state)
        return 0

    csv_bytes, source = result
    new_hash = hashlib.sha256(csv_bytes).hexdigest()

    try:
        new_count = _csv_row_count(csv_bytes.decode("utf-8-sig", errors="replace"))
    except Exception as e:
        print(f"FAIL: csv parse error: {e}", file=sys.stderr)
        return 1

    prev_hash = state.get("csv_sha256")
    prev_count = state.get("row_count", 0)

    # Successful fetch resets the failure counter and clears any prior alert
    if prev_failures or already_alerted:
        print(f"  csv reachable again - resetting failure counter "
              f"(was {prev_failures}, alerted={already_alerted})")
    state["consecutive_csv_failures"] = 0
    state["csv_stuck_alerted"] = False

    if prev_hash == new_hash:
        print(f"NO CHANGE: rows={new_count} hash={new_hash[:12]}")
        _save_state(state)
        return 0

    # NEW DROP - CSV content has actually changed
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    CSV_OUT.write_bytes(csv_bytes)
    delta = new_count - (prev_count or 0)
    state["csv_sha256"] = new_hash
    state["row_count"] = new_count
    state["last_change_at"] = _now_iso()
    state["history"] = (state.get("history") or [])[-19:] + [{
        "at": state["last_change_at"],
        "csv_sha256": new_hash,
        "row_count": new_count,
        "delta": delta,
        "trigger": "csv",
        "source": source,
    }]
    _save_state(state)
    print(f"NEW DROP via {source}: rows={new_count} delta={delta:+d} hash={new_hash[:12]}")
    _emit_gh_output(
        new_drop="true",
        row_count=str(new_count),
        delta=str(delta),
        sha256=new_hash,
        source=source,
    )
    return 10


if __name__ == "__main__":
    sys.exit(main())
