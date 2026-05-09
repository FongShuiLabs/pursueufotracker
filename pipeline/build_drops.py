"""Stage 9.7: render the drops tracker.

Reads data/drops.json. Renders:
- generated/drops/index.html         (all drops, newest first)
- generated/drops/<drop-id>.html     (per-drop detail page)

Each drop page: summary, headline files, press coverage, file list.
The index page is the canonical "Trump PURSUE Tracker" landing for journalists
and YouTube creators following the rolling release cadence.
"""
from __future__ import annotations
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import (
    MANIFEST_PATH, ROOT, GENERATED_DIR, TEMPLATES_DIR,
    SITE_NAME, SITE_URL, ensure_dirs,
)


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

    # Per-drop pages
    for drop in drops_sorted:
        headline = [files_by_id[fid] for fid in drop.get("headline_files", []) if fid in files_by_id]
        out_path = out_dir / f"{drop['date']}-drop-{drop['number']:02d}.html"
        out_path.write_text(
            drop_tpl.render(
                drop=drop, headline=headline,
                site_name=SITE_NAME, site_url=SITE_URL,
            ),
            encoding="utf-8",
        )

    # Index page
    (out_dir / "index.html").write_text(
        idx_tpl.render(
            drops=drops_sorted,
            expected_next=drops_data.get("expected_next") or {},
            site_name=SITE_NAME, site_url=SITE_URL,
        ),
        encoding="utf-8",
    )
    print(f"  drops: 1 index + {len(drops_sorted)} per-drop pages")


if __name__ == "__main__":
    run()
