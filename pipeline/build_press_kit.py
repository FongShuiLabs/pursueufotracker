"""Stage 9.3: render /press/ - press kit for journalists and podcasters.

Includes:
- Fact sheet (counts, agencies, date ranges)
- Embed code snippets (iframe, link previews)
- Brand assets (logo, OG images)
- Contact line (operator fills in)
- SHA-256 manifest for verification
- Suggested questions / talking points
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
    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = manifest["files"]
    by_agency = {}
    for f in files:
        by_agency.setdefault(f["agency"], 0)
        by_agency[f["agency"]] += 1
    high = [f for f in files if (f.get("score") or {}).get("value", 0) >= 80]
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True, lstrip_blocks=True,
    )
    if not (TEMPLATES_DIR / "press.html.j2").exists():
        print("  (templates/press.html.j2 missing)")
        return
    tpl = env.get_template("press.html.j2")
    out = GENERATED_DIR / "press.html"
    out.write_text(tpl.render(
        manifest=manifest,
        total=len(files),
        by_agency=by_agency,
        high_anomaly=high,
        site_name=SITE_NAME,
        site_url=SITE_URL,
    ), encoding="utf-8")
    # Also dump the verification manifest journalists can download
    verify = [{"id": f["id"], "title": f.get("title"), "sha256": f.get("sha256"),
               "size_bytes": f.get("size_bytes"), "source_url": f.get("source_url")}
              for f in files]
    (GENERATED_DIR / "verification-manifest.json").write_text(
        json.dumps(verify, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  press kit -> {out}")


if __name__ == "__main__":
    run()
