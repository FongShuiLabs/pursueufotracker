"""Stage 9.2: render /top-10/ - listicle for share-driven entry traffic.

Default: top 10 files by Anomalousness Index (ties broken by sensor + witness).
Override: data/top10-override.json (optional list of file IDs in order).
"""
from __future__ import annotations
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import (
    MANIFEST_PATH, ROOT, GENERATED_DIR, TEMPLATES_DIR,
    SITE_NAME, SITE_URL, ensure_dirs,
)


def _pick_top(manifest: dict, n: int = 10) -> list[dict]:
    override_path = ROOT / "data" / "top10-override.json"
    files_by_id = {f["id"]: f for f in manifest["files"]}
    if override_path.exists():
        ids = json.loads(override_path.read_text(encoding="utf-8"))
        return [files_by_id[i] for i in ids if i in files_by_id][:n]
    scored = [f for f in manifest["files"] if (f.get("score") or {}).get("value") is not None]
    scored.sort(key=lambda f: f["score"]["value"], reverse=True)
    return scored[:n]


def run() -> None:
    ensure_dirs()
    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    top = _pick_top(manifest)
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True, lstrip_blocks=True,
    )
    if not (TEMPLATES_DIR / "top10.html.j2").exists():
        print("  (templates/top10.html.j2 missing)")
        return
    tpl = env.get_template("top10.html.j2")
    out = GENERATED_DIR / "top-10.html"
    out.write_text(
        tpl.render(items=top, site_name=SITE_NAME, site_url=SITE_URL),
        encoding="utf-8",
    )
    print(f"  top-10 page -> {out}")


if __name__ == "__main__":
    run()
