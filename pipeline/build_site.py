"""Stage 9: render generated/files/<id>.html, RSS, sitemap, timeline.json, map.json.

Uses Jinja2 templates from templates/. Per-file pages embed:
- title, agency, category, dates
- type-specific viewer (PDF iframe, <video> with VTT track, <img>)
- download button with size + sha256
- score breakdown with each component contribution
- transcript or first-page text preview
- Open Graph meta pointing to generated/og-cards/<id>.png
"""
from __future__ import annotations
import html
import json
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import (
    MANIFEST_PATH, ROOT, GEN_FILES, GEN_TIMELINE, GEN_MAP, GEN_FEED,
    TEMPLATES_DIR, SITE_NAME, SITE_URL, SITE_DESCRIPTION, ensure_dirs,
    AMAZON_AFFILIATE_TAG, BUY_ME_COFFEE_USERNAME, PATREON_USERNAME,
    ENABLE_ADS, ADSENSE_CLIENT_ID,
)


def _human_size(n: int | None) -> str:
    if not n:
        return "?"
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}" if isinstance(n, float) else f"{n} {unit}"
        n = n / 1024
    return f"{n:.1f} TB"


def _build_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True, lstrip_blocks=True,
    )


def _render_file_pages(env: Environment, manifest: dict) -> None:
    tpl = env.get_template("file.html.j2")
    for f in manifest["files"]:
        out = GEN_FILES / f"{f['id']}.html"
        size_h = _human_size(f.get("size_bytes"))
        ctx = {
            "f": f,
            "size_human": size_h,
            "site_name": SITE_NAME,
            "site_url": SITE_URL,
            "og_card": f"../og-cards/{f['id']}.png",
            "amazon_tag": AMAZON_AFFILIATE_TAG,
            "buy_me_coffee": BUY_ME_COFFEE_USERNAME,
            "patreon_user": PATREON_USERNAME,
            "enable_ads": ENABLE_ADS,
            "adsense_client_id": ADSENSE_CLIENT_ID,
        }
        out.write_text(tpl.render(**ctx), encoding="utf-8")


def _build_timeline(manifest: dict) -> None:
    items = []
    for f in manifest["files"]:
        items.append({
            "id": f["id"],
            "title": f.get("title"),
            "date": f.get("date_event") or f.get("date_released"),
            "category": f.get("category"),
            "agency": f.get("agency"),
            "score": (f.get("score") or {}).get("value"),
            "url": f"files/{f['id']}.html",
        })
    items.sort(key=lambda x: x["date"] or "")
    GEN_TIMELINE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_map(manifest: dict) -> None:
    pts = []
    for f in manifest["files"]:
        g = f.get("geo") or {}
        if g.get("lat") is not None and g.get("lng") is not None:
            pts.append({
                "id": f["id"],
                "title": f.get("title"),
                "lat": g["lat"], "lng": g["lng"],
                "place": g.get("place"),
                "score": (f.get("score") or {}).get("value"),
                "url": f"files/{f['id']}.html",
            })
    GEN_MAP.write_text(json.dumps(pts, ensure_ascii=False, indent=2), encoding="utf-8")


def _build_feed(manifest: dict) -> None:
    try:
        from feedgen.feed import FeedGenerator
    except ImportError:
        print("  feedgen missing - skipping RSS")
        return
    fg = FeedGenerator()
    fg.id(SITE_URL + "/")
    fg.title(SITE_NAME)
    fg.link(href=SITE_URL, rel="alternate")
    fg.description(SITE_DESCRIPTION)
    fg.language("en")
    for f in sorted(manifest["files"], key=lambda x: x.get("date_released") or "", reverse=True)[:50]:
        fe = fg.add_entry()
        fe.id(f"{SITE_URL}/files/{f['id']}.html")
        fe.title(f.get("title") or f["id"])
        fe.link(href=f"{SITE_URL}/files/{f['id']}.html")
        fe.description(f.get("summary") or f.get("title") or "")
        d = f.get("date_released") or "2026-05-08"
        try:
            dt = datetime.fromisoformat(d).replace(tzinfo=timezone.utc)
        except Exception:
            dt = datetime.now(timezone.utc)
        fe.published(dt)
    fg.rss_file(str(GEN_FEED), pretty=True)


def _build_sitemap(manifest: dict) -> None:
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    parts.append(f"<url><loc>{SITE_URL}/</loc><priority>1.0</priority></url>")
    for f in manifest["files"]:
        parts.append(
            f"<url><loc>{SITE_URL}/files/{html.escape(f['id'])}.html</loc>"
            f"<priority>0.8</priority></url>"
        )
    parts.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(parts), encoding="utf-8")


def run() -> None:
    ensure_dirs()
    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return
    if not (TEMPLATES_DIR / "file.html.j2").exists():
        print("  (no file template; expected templates/file.html.j2)")
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    env = _build_env()
    _render_file_pages(env, manifest)
    _build_timeline(manifest)
    _build_map(manifest)
    _build_feed(manifest)
    _build_sitemap(manifest)
    print(f"  built site: {len(manifest['files'])} pages + RSS + sitemap + timeline + map")


if __name__ == "__main__":
    run()
