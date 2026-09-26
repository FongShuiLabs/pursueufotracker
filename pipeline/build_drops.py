"""Stage 9.7: render the drops tracker.

Reads data/drops.json. Renders:
- generated/drops/index.html         (all drops, newest first)
- generated/drops/<drop-id>.html     (per-drop detail page)

Each drop page: summary, headline files, press coverage, file list.
The index page is the canonical "Trump PURSUE Tracker" landing for journalists
and YouTube creators following the rolling release cadence.
"""
from __future__ import annotations
import calendar
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .records import AGENCY_DISPLAY

from .config import (
    MANIFEST_PATH, ROOT, GENERATED_DIR, TEMPLATES_DIR,
    SITE_NAME, SITE_URL, ensure_dirs,
)

_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven",
          "eight", "nine", "ten", "eleven", "twelve"]


def _long_date(iso: str) -> str:
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{calendar.month_name[m]} {d}, {y}"


def release_facts(drops: list[dict]) -> dict:
    """Release-count wording derived from drops.json, so no template hard-codes it.

    2026-09-20: /drops and /press still said "five drops" and "Latest release:
    June 12 (Drop 03)" after Release 06, and every per-drop page said "All 375
    indexed files" - the same stale-number class as the hero tiles. Templates now
    read these values instead of carrying their own copy.
    """
    ordered = sorted(drops, key=lambda d: d["date"])
    if not ordered:
        return {"n_drops": 0, "n_drops_word": "zero", "dates_phrase": "",
                "first_drop": None, "latest_drop": None}
    years = {d["date"][:4] for d in ordered}
    parts = []
    for d in ordered:
        y, m, day = d["date"].split("-")
        label = f"{calendar.month_name[int(m)]} {int(day)}"
        parts.append(label if len(years) == 1 else f"{label}, {y}")
    phrase = ", ".join(parts[:-1]) + ", and " + parts[-1] if len(parts) > 2 else " and ".join(parts)
    if len(years) == 1:
        phrase += f", {next(iter(years))}"
    n = len(ordered)
    return {
        "n_drops": n,
        "n_drops_word": _WORDS[n] if n < len(_WORDS) else str(n),
        "dates_phrase": phrase,
        "first_drop": {**ordered[0], "date_long": _long_date(ordered[0]["date"])},
        "latest_drop": {**ordered[-1], "date_long": _long_date(ordered[-1]["date"])},
    }


def run() -> None:
    ensure_dirs()
    drops_path = ROOT / "data" / "drops.json"
    if not drops_path.exists():
        print("  (no drops.json)")
        return
    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return
    drops_data = json.loads(drops_path.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files_by_id = {f["id"]: f for f in manifest["files"]}

    out_dir = GENERATED_DIR / "drops"
    out_dir.mkdir(parents=True, exist_ok=True)
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True, lstrip_blocks=True,
    )
    if not (TEMPLATES_DIR / "drop.html.j2").exists():
        print("  (templates/drop.html.j2 missing)")
        return
    if not (TEMPLATES_DIR / "drops_index.html.j2").exists():
        print("  (templates/drops_index.html.j2 missing)")
        return

    drop_tpl = env.get_template("drop.html.j2")
    idx_tpl = env.get_template("drops_index.html.j2")

    drops_sorted = sorted(drops_data.get("drops", []), key=lambda d: d["date"], reverse=True)
    facts = release_facts(drops_sorted)
    total_files = len(manifest["files"])

    # Per-drop pages
    for drop in drops_sorted:
        headline = [files_by_id[fid] for fid in drop.get("headline_files", []) if fid in files_by_id]
        out_path = out_dir / f"{drop['date']}-drop-{drop['number']:02d}.html"
        out_path.write_text(
            drop_tpl.render(
                drop=drop, headline=headline, total_files=total_files, agency_labels=AGENCY_DISPLAY,
                site_name=SITE_NAME, site_url=SITE_URL,
            ),
            encoding="utf-8",
        )

    # Index page
    (out_dir / "index.html").write_text(
        idx_tpl.render(
            drops=drops_sorted, total_files=total_files, **facts, agency_labels=AGENCY_DISPLAY,
            expected_next=drops_data.get("expected_next") or {},
            site_name=SITE_NAME, site_url=SITE_URL,
        ),
        encoding="utf-8",
    )
    print(f"  drops: 1 index + {len(drops_sorted)} per-drop pages")


if __name__ == "__main__":
    run()
