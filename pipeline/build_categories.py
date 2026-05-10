"""Stage 9.7: SEO category landing pages.

Builds one page per topical cluster: fbi-ufo-files, military-uap-files,
nasa-ufo-photos, state-department-uap-cables. Each targets a distinct search
query, contains 50-100+ internal links to file pages, structured data
(CollectionPage + ItemList + BreadcrumbList), and a unique editorial intro
so they're not duplicate content.

Output: generated/categories/<slug>.html
URL:    /<slug>/  (via _redirects rewrite)
"""
from __future__ import annotations
import html as _html
import json
from pathlib import Path

from .config import MANIFEST_PATH, ROOT, GENERATED_DIR, SITE_NAME, SITE_URL, ensure_dirs


CATEGORIES = [
    {
        "slug": "fbi-ufo-files",
        "title": "FBI UFO Files: 57 Bureau Records Trump Just Declassified",
        "h1": "FBI UFO Files",
        "match": lambda f: f.get("category") == "fbi" or f.get("agency") == "FBI",
        "intro": (
            "Fifty-seven FBI files were declassified in the May 2026 PURSUE release: the bureau's "
            "internal case file <strong>62-HQ-83894</strong>, which aggregates UAP investigations from "
            "<strong>June 1947 through July 1968</strong>. It covers the Roswell field office reporting, "
            "the Oak Ridge incidents, four decades of citizen sighting reports, the FBI photographic "
            "library, and technical proposals on propulsion systems engineers thought might explain the "
            "objects. Most files are partially redacted; we mark redaction status on each. All are public "
            "domain U.S. Government works under 17 U.S.C. § 105."
        ),
        "meta_desc": (
            "All 57 FBI UFO files declassified in the Trump administration's May 2026 PURSUE release. "
            "Case file 62-HQ-83894, Roswell records, Oak Ridge incidents, 1947-1968 investigations. "
            "Indexed, searchable, full SHA-256 verification."
        ),
        "keywords": "FBI UFO files, FBI UFO declassified, 62-HQ-83894, Roswell FBI records, Oak Ridge UFO, FBI vault UFO, Trump FBI UFO release, PURSUE FBI",
    },
    {
        "slug": "military-uap-files",
        "title": "Pentagon UAP Files: 83 Military Encounter Reports From the Trump UFO Release",
        "h1": "Pentagon UAP & Military Encounter Files",
        "match": lambda f: f.get("category") == "military" or f.get("agency") == "DoD",
        "intro": (
            "Eighty-three Department of War files cover U.S. military Unidentified Anomalous Phenomena "
            "encounters from <strong>2020 through 2026</strong>. These include AARO mission packets and "
            "Mission Reports (MISREPs) from the Mediterranean, Greek airspace, the Arabian Gulf, the "
            "Indo-Pacific, Iraq, Syria, the UAE, and Yemen. Many include full-motion video from "
            "<strong>infrared (IR), electro-optical (EO), and short-wave infrared (SWIR) sensors</strong>. "
            "These are the files that score highest on the Anomalousness Index, because the encounters "
            "have the strongest sensor and witness chain - trained military operators, multi-sensor "
            "capture, and unresolved official disposition."
        ),
        "meta_desc": (
            "All 83 Pentagon and Department of War UAP files from the Trump May 2026 PURSUE release. "
            "AARO mission reports, MISREPs, Mediterranean, Greece, UAE, Iraq, Syria, IR/EO/SWIR sensor "
            "captures. Full transcripts, AI-ranked anomalousness."
        ),
        "keywords": "Pentagon UAP files, DoD UFO files, AARO mission report, MISREP UAP, Greece UAP 2024, UAE UAP, Mediterranean UFO, military UFO video, war.gov UAP, Trump Pentagon UFO",
    },
    {
        "slug": "nasa-ufo-photos",
        "title": "NASA UFO Photos: Apollo, Gemini, Skylab UAP Records",
        "h1": "NASA UFO & UAP Records",
        "match": lambda f: f.get("category") in ("nasa", "apollo") or f.get("agency") == "NASA",
        "intro": (
            "Fifteen NASA files were declassified under PURSUE in May 2026. They include <strong>Apollo "
            "12, 16, and 17 mission photography</strong> with highlighted areas of unidentified "
            "phenomena above the lunar horizon, the <strong>Schmitt-Grimaldi lunar flash report from "
            "December 1972</strong>, <strong>Gemini 7 air-to-ground audio</strong> in which astronaut "
            "Frank Borman reports an unidentified object in low Earth orbit, and <strong>Skylab crew "
            "debriefings</strong> from 1973-74. Astronaut-witness corroboration is rare in the UAP "
            "record. NASA-UAP-D3A (Borman / Gemini 7) is the single highest-scored file in Drop 01."
        ),
        "meta_desc": (
            "All NASA UFO files in the Trump May 2026 PURSUE release. Apollo 12/16/17 lunar anomaly "
            "photos, Gemini 7 Frank Borman UAP audio, Skylab debriefing, Schmitt-Grimaldi lunar flash. "
            "Astronaut-witness records."
        ),
        "keywords": "NASA UFO photos, Apollo 12 UFO, Apollo 17 UFO, Gemini 7 UAP, Frank Borman UFO, Skylab UFO, Schmitt-Grimaldi lunar flash, astronaut UFO sighting, NASA UAP declassified",
    },
    {
        "slug": "state-department-uap-cables",
        "title": "State Department UAP Cables: 7 Diplomatic Records 1952-2025",
        "h1": "State Department UAP Diplomatic Cables",
        "match": lambda f: f.get("category") == "state" or f.get("agency") == "STATE",
        "intro": (
            "Seven U.S. Department of State diplomatic cables were declassified under PURSUE, spanning "
            "<strong>1952 through 2025</strong>. They include the <strong>1985 Papua New Guinea cable</strong> "
            "from the U.S. Embassy in Port Moresby to USCINCPAC, the <strong>1994 Tajikistan PanAm crew "
            "sighting at flight level 410</strong>, plus dispatches from Kazakhstan, Turkmenistan, "
            "Georgia, and Mexico. These cables are the State Department's running record of what U.S. "
            "diplomats reported back to Foggy Bottom when foreign governments or aviation authorities "
            "raised UAP encounters through diplomatic channels."
        ),
        "meta_desc": (
            "All 7 State Department UAP diplomatic cables in the Trump May 2026 PURSUE release. "
            "1985 Papua New Guinea, 1994 Tajikistan PanAm, Kazakhstan, Turkmenistan, Georgia, Mexico. "
            "1952-2025 span. Indexed and searchable."
        ),
        "keywords": "State Department UFO, UAP diplomatic cable, Papua New Guinea UFO 1985, Tajikistan PanAm UFO 1994, USCINCPAC UAP, embassy UFO cable, declassified State UFO",
    },
]


def _pick_files(manifest: dict, match) -> list[dict]:
    files = [f for f in manifest["files"] if match(f)]
    files.sort(key=lambda f: (f.get("score") or {}).get("value") or 0, reverse=True)
    return files


def _file_card_html(f: dict) -> str:
    fid = _html.escape(f["id"])
    title = _html.escape(f.get("title") or fid)
    agency = _html.escape(f.get("agency") or "")
    ftype = _html.escape((f.get("type") or "").upper())
    score = (f.get("score") or {}).get("value")
    score_html = (
        f'<span class="score-pill">SCORE {score}</span>' if score is not None else ""
    )
    summary = _html.escape((f.get("summary") or "")[:200])
    return (
        f'<a class="cat-card" href="/files/{fid}.html">'
        f'<div class="cat-card-head"><span class="cat-tag">{agency} · {ftype}</span>{score_html}</div>'
        f'<h3>{title}</h3>'
        f'<p>{summary}</p>'
        f'</a>'
    )


def _page_html(cat: dict, files: list[dict]) -> str:
    canonical = f"{SITE_URL}/{cat['slug']}/"
    title_full = f"{cat['title']} | {SITE_NAME}"
    breadcrumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "PURSUE Tracker", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": cat["h1"]},
        ],
    }
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": cat["h1"],
        "numberOfItems": len(files),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "url": f"{SITE_URL}/files/{f['id']}.html",
                "name": f.get("title") or f["id"],
            }
            for i, f in enumerate(files[:50])
        ],
    }
    collection = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": cat["h1"],
        "description": cat["meta_desc"],
        "url": canonical,
        "isBasedOn": "https://www.war.gov/UFO/",
        "license": "https://www.usa.gov/government-works",
    }
    jsonld = json.dumps([breadcrumbs, item_list, collection], ensure_ascii=False)
    cards = "\n".join(_file_card_html(f) for f in files)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_html.escape(title_full)}</title>
<meta name="description" content="{_html.escape(cat['meta_desc'])}">
<meta name="keywords" content="{_html.escape(cat['keywords'])}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">

<meta property="og:type" content="website">
<meta property="og:title" content="{_html.escape(cat['title'])}">
<meta property="og:description" content="{_html.escape(cat['meta_desc'])}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE_URL}/og-cover.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE_URL}/og-cover.svg">
<meta name="twitter:title" content="{_html.escape(cat['title'])}">
<meta name="twitter:description" content="{_html.escape(cat['meta_desc'])}">

<script type="application/ld+json">{jsonld}</script>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
<style>
  .cat-page{{max-width:1100px;margin:0 auto;padding:60px 24px}}
  .breadcrumb{{font-family:'JetBrains Mono',monospace;font-size:11px;letter-spacing:1.5px;color:#7a92b0;margin-bottom:24px}}
  .breadcrumb a{{color:#52b4ff;text-decoration:none}}
  .cat-page h1{{font-size:clamp(36px,5vw,56px);background:linear-gradient(180deg,#fff,#52b4ff);-webkit-background-clip:text;background-clip:text;color:transparent;letter-spacing:.01em;margin-bottom:14px}}
  .cat-lede{{font-size:18px;color:#dfe6ef;line-height:1.75;margin-bottom:24px;max-width:880px}}
  .cat-meta-row{{display:flex;gap:24px;flex-wrap:wrap;color:#a8b8cc;font-size:13px;font-family:'JetBrains Mono',monospace;letter-spacing:1px;margin-bottom:40px}}
  .cat-meta-row strong{{color:#52ffb4}}
  .cat-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;margin-bottom:60px}}
  .cat-card{{display:block;padding:20px;background:rgba(10,15,28,.6);border:1px solid rgba(82,180,255,.15);border-radius:10px;text-decoration:none;transition:border-color .2s,transform .2s}}
  .cat-card:hover{{border-color:rgba(82,180,255,.4);transform:translateY(-2px)}}
  .cat-card-head{{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;gap:10px}}
  .cat-tag{{font-family:'JetBrains Mono',monospace;font-size:10px;color:#52b4ff;letter-spacing:1.5px}}
  .score-pill{{font-family:'JetBrains Mono',monospace;font-size:10px;color:#52ffb4;background:rgba(82,255,180,.1);padding:3px 8px;border-radius:3px;letter-spacing:1px}}
  .cat-card h3{{color:#fff;font-size:16px;margin:0 0 8px;line-height:1.35;font-weight:600}}
  .cat-card p{{color:#a8b8cc;font-size:13px;margin:0;line-height:1.55}}
  .cat-back{{display:inline-block;margin-top:24px;color:#52b4ff;font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:1px;text-decoration:none}}
</style>
</head>
<body>
<div class="starfield" aria-hidden="true"></div>
<div class="grid-bg" aria-hidden="true"></div>

<main class="cat-page">
  <div class="breadcrumb"><a href="/">PURSUE Tracker</a> &nbsp;/&nbsp; {_html.escape(cat['h1'])}</div>
  <h1>{_html.escape(cat['h1'])}</h1>
  <div class="cat-meta-row">
    <span><strong>{len(files)}</strong> files</span>
    <span>Source: <a href="https://www.war.gov/UFO/" target="_blank" rel="noopener" style="color:#52b4ff;text-decoration:none">war.gov/UFO</a></span>
    <span>Released: May 8, 2026</span>
    <span>License: 17 U.S.C. § 105 (public domain)</span>
  </div>
  <p class="cat-lede">{cat['intro']}</p>
  <p class="cat-lede">Files below are sorted by <a href="/data/scoring-rubric.json" style="color:#52b4ff">Anomalousness Index</a> (highest evidentiary weight first). Each links to a full detail page with viewer, transcript (for videos), SHA-256 verification, and source link to war.gov.</p>

  <div class="cat-grid">
{cards}
  </div>

  <a class="cat-back" href="/">← BACK TO ALL 161 FILES</a>
</main>

<footer style="text-align:center;padding:60px 24px;color:#7a92b0;font-size:13px;border-top:1px solid rgba(82,180,255,.1);margin-top:60px">
  <p>Independent tracker. Not affiliated with the U.S. Department of War. Source of record: <a href="https://www.war.gov/UFO/" target="_blank" rel="noopener" style="color:#52b4ff">war.gov/UFO</a></p>
</footer>
</body>
</html>
"""


def run() -> None:
    ensure_dirs()
    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    out_dir = GENERATED_DIR / "categories"
    out_dir.mkdir(parents=True, exist_ok=True)
    for cat in CATEGORIES:
        files = _pick_files(manifest, cat["match"])
        path = out_dir / f"{cat['slug']}.html"
        path.write_text(_page_html(cat, files), encoding="utf-8")
        print(f"  /{cat['slug']}/ -> {len(files)} files")
