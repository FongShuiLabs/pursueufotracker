"""Stage X: fetch Plausible Stats API and snapshot results.

Reads PLAUSIBLE_API_KEY and PLAUSIBLE_SITE_ID from .env (gitignored).
Pulls aggregate metrics, top pages, top sources, top countries, and custom
events from the Plausible Stats API for several rolling windows. Writes a
timestamped snapshot to data/analytics/YYYY-MM-DD.json.

Why this exists: lets us track traffic without screenshot-pasting, surfaces
the 10k/mo pageview-cap watch automatically (Business tier on Plausible
caps at 10k; we want a heads-up at 85%), and gives us a long-term local
record outside Plausible's 5-year retention.

Run:
    python -m pipeline.plausible_stats

Output:
    data/analytics/2026-05-21.json
    + console summary with cap-watch warning if >85% of monthly budget used

API docs: https://plausible.io/docs/stats-api
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import urllib.request
import urllib.parse
import urllib.error

from .config import ROOT


ENV_PATH = ROOT / ".env"
SNAPSHOT_DIR = ROOT / "data" / "analytics"
API_BASE = "https://plausible.io/api/v1/stats"
MONTHLY_PAGEVIEW_BUDGET = 10_000  # Business tier cap
CAP_WARN_AT = 0.85  # warn at 85% of monthly budget


def _load_env() -> dict[str, str]:
    """Tiny .env parser. Doesn't pull from os.environ to avoid surprise leaks."""
    if not ENV_PATH.exists():
        sys.exit(f"  .env not found at {ENV_PATH}. Copy .env.example and add your key.")
    env = {}
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def _api_get(path: str, params: dict, api_key: str) -> dict:
    """GET a Plausible API endpoint, return parsed JSON."""
    qs = urllib.parse.urlencode(params)
    url = f"{API_BASE}/{path}?{qs}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        sys.exit(f"  Plausible API error: HTTP {e.code} on {path} - {body[:300]}")
    except urllib.error.URLError as e:
        sys.exit(f"  Plausible API network error on {path}: {e}")


def _aggregate(site_id: str, period: str, api_key: str) -> dict:
    return _api_get("aggregate", {
        "site_id": site_id,
        "period": period,
        "metrics": "visitors,pageviews,bounce_rate,visit_duration,views_per_visit",
    }, api_key).get("results", {})


def _breakdown(site_id: str, period: str, prop: str, api_key: str, limit: int = 10) -> list[dict]:
    return _api_get("breakdown", {
        "site_id": site_id,
        "period": period,
        "property": prop,
        "metrics": "visitors,pageviews",
        "limit": str(limit),
    }, api_key).get("results", [])


def _custom_event_count(site_id: str, period: str, event: str, api_key: str) -> int:
    """Count fires of a specific custom event over the period."""
    results = _api_get("aggregate", {
        "site_id": site_id,
        "period": period,
        "metrics": "events",
        "filters": f"event:name=={event}",
    }, api_key).get("results", {})
    return (results.get("events") or {}).get("value", 0)


def run() -> None:
    env = _load_env()
    api_key = env.get("PLAUSIBLE_API_KEY")
    site_id = env.get("PLAUSIBLE_SITE_ID", "pursueufotracker.com")
    if not api_key or api_key == "your-key-here":
        sys.exit("  PLAUSIBLE_API_KEY missing or unset in .env")

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = SNAPSHOT_DIR / f"{today}.json"

    print(f"  Fetching Plausible stats for {site_id}...")

    snapshot = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "site_id": site_id,
        "periods": {},
    }

    for period in ("day", "7d", "30d", "month"):
        print(f"    period={period}")
        snapshot["periods"][period] = {
            "aggregate": _aggregate(site_id, period, api_key),
            "top_pages": _breakdown(site_id, period, "event:page", api_key, limit=15),
            "top_sources": _breakdown(site_id, period, "visit:source", api_key, limit=10),
            "top_countries": _breakdown(site_id, period, "visit:country", api_key, limit=10),
        }

    # Custom events (configured per .claude/accounts.md)
    print("    custom events (30d)")
    snapshot["custom_events_30d"] = {
        evt: _custom_event_count(site_id, "30d", evt, api_key)
        for evt in ("Top5Click", "Share", "404Recovery", "EmailSubscribe")
    }

    out_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Snapshot written: {out_path}")

    # Summary + cap watch
    month = snapshot["periods"]["month"]["aggregate"]
    pv = (month.get("pageviews") or {}).get("value", 0)
    vis = (month.get("visitors") or {}).get("value", 0)
    pct = pv / MONTHLY_PAGEVIEW_BUDGET if MONTHLY_PAGEVIEW_BUDGET else 0
    print()
    print(f"  Month-to-date: {pv} pageviews, {vis} unique visitors")
    print(f"  Cap budget:    {pv}/{MONTHLY_PAGEVIEW_BUDGET} ({pct:.0%} used)")
    if pct >= CAP_WARN_AT:
        print(f"  WARNING: at {pct:.0%} of monthly pageview budget. Consider next-tier upgrade.")
    else:
        print(f"  (warning threshold: {CAP_WARN_AT:.0%})")

    # Quick traffic snapshot
    day = snapshot["periods"]["day"]["aggregate"]
    print()
    print(f"  Last 24h:      {(day.get('pageviews') or {}).get('value', 0)} pageviews, "
          f"{(day.get('visitors') or {}).get('value', 0)} unique visitors, "
          f"bounce {(day.get('bounce_rate') or {}).get('value', '?')}%")
    print(f"  Top page 24h:  ", end="")
    tp = snapshot["periods"]["day"]["top_pages"][:1]
    if tp:
        print(f"{tp[0].get('page', '?')} ({tp[0].get('visitors', '?')} visitors)")
    else:
        print("(no pages yet)")


if __name__ == "__main__":
    run()
