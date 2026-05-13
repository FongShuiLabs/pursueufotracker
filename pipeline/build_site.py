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
import re
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


def _related_files(f: dict, all_files: list[dict], limit: int = 6) -> list[dict]:
    """Pick files in the same category as f, ranked by score desc, excluding self.
    Falls back to same agency if category is too small."""
    cat = f.get("category")
    agency = f.get("agency")
    fid = f.get("id")
    same_cat = [g for g in all_files if g.get("category") == cat and g.get("id") != fid]
    if len(same_cat) < limit:
        same_agency = [g for g in all_files
                       if g.get("agency") == agency
                       and g.get("id") != fid
                       and g.get("id") not in {x["id"] for x in same_cat}]
        same_cat += same_agency
    same_cat.sort(key=lambda g: (g.get("score") or {}).get("value") or 0, reverse=True)
    return [
        {
            "id": g["id"],
            "title": g.get("title") or g["id"],
            "agency": g.get("agency"),
            "type": g.get("type"),
            "score": g.get("score"),
        }
        for g in same_cat[:limit]
    ]


_YEAR_RE = re.compile(r'\b(19|20)\d{2}\b')


def _event_year(f: dict) -> str:
    """Extract the encounter year for SEO keywords. Order:
    1. 4-digit year in title (e.g. '..., 1965' or 'October 2023')
    2. 4-digit year in id slug
    3. date_event if it parses as YYYY-MM-DD
    4. Empty string
    """
    for s in (f.get("title", ""), f.get("id", "")):
        m = _YEAR_RE.search(s or "")
        if m:
            return m.group(0)
    de = f.get("date_event") or ""
    if len(de) >= 4 and de[:4].isdigit():
        return de[:4]
    return ""


def _render_file_pages(env: Environment, manifest: dict) -> None:
    tpl = env.get_template("file.html.j2")
    all_files = manifest["files"]
    for f in all_files:
        out = GEN_FILES / f"{f['id']}.html"
        size_h = _human_size(f.get("size_bytes"))
        ctx = {
            "f": f,
            "size_human": size_h,
            "event_year": _event_year(f),
            "site_name": SITE_NAME,
            "site_url": SITE_URL,
            "og_card": f"../og-cards/{f['id']}.png",
            "amazon_tag": AMAZON_AFFILIATE_TAG,
            "buy_me_coffee": BUY_ME_COFFEE_USERNAME,
            "patreon_user": PATREON_USERNAME,
            "enable_ads": ENABLE_ADS,
            "adsense_client_id": ADSENSE_CLIENT_ID,
            "related_files": _related_files(f, all_files),
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
            "url": f"/files/{f['id']}",
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
                "url": f"/files/{f['id']}",
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
        fe.id(f"{SITE_URL}/files/{f['id']}")
        fe.title(f.get("title") or f["id"])
        fe.link(href=f"{SITE_URL}/files/{f['id']}")
        fe.description(f.get("summary") or f.get("title") or "")
        d = f.get("date_released") or "2026-05-08"
        try:
            dt = datetime.fromisoformat(d).replace(tzinfo=timezone.utc)
        except Exception:
            dt = datetime.now(timezone.utc)
        fe.published(dt)
    fg.rss_file(str(GEN_FEED), pretty=True)
    # Inject the XSL stylesheet PI so browsers render the feed as a friendly
    # subscribe page. RSS readers ignore the PI and parse the XML normally.
    feed_text = GEN_FEED.read_text(encoding="utf-8")
    if "<?xml-stylesheet" not in feed_text:
        feed_text = feed_text.replace(
            "<?xml version='1.0' encoding='UTF-8'?>",
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<?xml-stylesheet type="text/xsl" href="/generated/feed.xsl"?>',
            1,
        )
        # feedgen sometimes uses double quotes already
        feed_text = feed_text.replace(
            '<?xml version="1.0" encoding="UTF-8"?>\n<?xml-stylesheet'
            ' type="text/xsl" href="/generated/feed.xsl"?>'
            '\n<?xml-stylesheet type="text/xsl" href="/generated/feed.xsl"?>',
            '<?xml version="1.0" encoding="UTF-8"?>\n<?xml-stylesheet type="text/xsl" href="/generated/feed.xsl"?>',
        )
        GEN_FEED.write_text(feed_text, encoding="utf-8")


def _build_video_sitemap(manifest: dict) -> None:
    """Google Video Search ingests video sitemaps separately. Each <video>
    block needs: thumbnail, title, description, content_loc OR player_loc,
    duration optional. Files are submitted alongside the main sitemap.
    """
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
             'xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">']
    n = 0
    for f in manifest["files"]:
        if f.get("type") != "video":
            continue
        fid = f["id"]
        page = f"{SITE_URL}/files/{html.escape(fid)}"
        thumb = f"{SITE_URL}/generated/og-cards/{html.escape(fid)}.png"
        title = html.escape((f.get("title") or fid)[:100])
        # Video description must be 5-2048 chars
        desc = (f.get("summary") or f.get("title") or fid)
        desc = html.escape(desc[:2000])
        if len(desc) < 5:
            desc = title
        content_loc = f.get("video_url") or f.get("mirror_url") or f.get("source_url") or ""
        pub_date = (f.get("date_released") or "2026-05-08") + "T00:00:00Z"
        parts.append(f"<url><loc>{page}</loc>")
        parts.append("<video:video>")
        parts.append(f"<video:thumbnail_loc>{thumb}</video:thumbnail_loc>")
        parts.append(f"<video:title>{title}</video:title>")
        parts.append(f"<video:description>{desc}</video:description>")
        if content_loc:
            parts.append(f"<video:content_loc>{html.escape(content_loc)}</video:content_loc>")
        parts.append(f"<video:player_loc>{page}</video:player_loc>")
        parts.append(f"<video:publication_date>{pub_date}</video:publication_date>")
        parts.append(f"<video:family_friendly>yes</video:family_friendly>")
        parts.append(f"<video:requires_subscription>no</video:requires_subscription>")
        parts.append("</video:video>")
        parts.append("</url>")
        n += 1
    parts.append("</urlset>")
    (ROOT / "video-sitemap.xml").write_text("\n".join(parts), encoding="utf-8")
    print(f"  video sitemap: {n} video entries")


def _build_sitemap_index() -> None:
    """Sitemap index lets us submit one URL that points to both sitemaps."""
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
             f"<sitemap><loc>{SITE_URL}/sitemap.xml</loc></sitemap>",
             f"<sitemap><loc>{SITE_URL}/video-sitemap.xml</loc></sitemap>",
             "</sitemapindex>"]
    (ROOT / "sitemap-index.xml").write_text("\n".join(parts), encoding="utf-8")


def _build_sitemap(manifest: dict) -> None:
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    # Homepage
    parts.append(f"<url><loc>{SITE_URL}/</loc><priority>1.0</priority><changefreq>daily</changefreq></url>")
    # High-value editorial pages
    for path, prio, freq in [
        ("/generated/verdict.html", "0.95", "weekly"),
        ("/generated/top-10.html", "0.95", "weekly"),
        ("/generated/press.html", "0.85", "monthly"),
        ("/generated/drops/index.html", "0.9", "weekly"),
        ("/revisions", "0.9", "weekly"),
        ("/faq", "0.85", "monthly"),
        ("/glossary", "0.85", "monthly"),
        ("/methodology", "0.9", "monthly"),
        ("/fbi-ufo-files/", "0.9", "weekly"),
        ("/military-uap-files/", "0.9", "weekly"),
        ("/nasa-ufo-photos/", "0.9", "weekly"),
        ("/state-department-uap-cables/", "0.9", "weekly"),
    ]:
        parts.append(f"<url><loc>{SITE_URL}{path}</loc><priority>{prio}</priority><changefreq>{freq}</changefreq></url>")
    # Drop detail pages
    drop_dir = ROOT / "generated" / "drops"
    if drop_dir.exists():
        for drop_html in sorted(drop_dir.glob("*.html")):
            if drop_html.name == "index.html":
                continue
            parts.append(
                f"<url><loc>{SITE_URL}/generated/drops/{html.escape(drop_html.name)}</loc>"
                f"<priority>0.85</priority><changefreq>monthly</changefreq></url>"
            )
    # File detail pages
    for f in manifest["files"]:
        parts.append(
            f"<url><loc>{SITE_URL}/files/{html.escape(f['id'])}</loc>"
            f"<priority>0.8</priority><changefreq>monthly</changefreq></url>"
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
    _build_video_sitemap(manifest)
    _build_sitemap_index()
    print(f"  built site: {len(manifest['files'])} pages + RSS + sitemap + timeline + map")


if __name__ == "__main__":
    run()
