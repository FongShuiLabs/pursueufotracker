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
        "title": "FBI UFO Files: 86 Bureau Records Trump Declassified",
        "h1": "FBI UFO Files",
        "match": lambda f: f.get("category") == "fbi" or f.get("agency") == "FBI",
        "intro": (
            "Eighty-six FBI files have been declassified across the Trump PURSUE releases (May-June 2026). "
            "The largest single "
            "block is the Bureau's central case file <strong>62-HQ-83894</strong> (18 PDFs), which "
            "aggregates UFO and flying-disc investigations from <strong>June 1947 through July 1968</strong> "
            "- 21 years of running investigative records. The release also includes Oak Ridge, "
            "Tennessee incident reporting, eyewitness testimonies and public reports from the period, "
            "technical proposals on propulsion systems engineers thought might explain the reported "
            "objects, and case file pages newly declassified beyond what the FBI Vault has previously "
            "posted. <strong>Release 03 (June 2026) added 29 more FBI records</strong> - modern Unidentified "
            "Anomalous Phenomena reports that extend the Bureau's UFO record from the 1947-1968 vault into "
            "the present, including the 2022 Colorado Springs incident (FD-1057 and a digital rendering), "
            "2026 Northeastern 'orb' sightings (FD-302 reports), and the FBI-UAP-PR003 'Orbs Over the Pond' "
            "video. Most files are partially redacted; we mark redaction status on each. All are public "
            "domain U.S. Government works under 17 U.S.C. § 105. For a file-by-file walkthrough of the "
            "62-HQ-83894 cluster, see <a href='/fbi-62-hq-83894'>our dedicated deep dive</a>."
        ),
        "meta_desc": (
            "All 86 FBI UFO files declassified across the Trump administration's 2026 PURSUE releases. "
            "Central case file 62-HQ-83894, Oak Ridge incidents, 1947-1968 investigations, plus 2022 "
            "Colorado Springs and 2026 Northeastern orb reports. Indexed, searchable, full SHA-256 verification."
        ),
        "keywords": "FBI UFO files, FBI UFO declassified, 62-HQ-83894, FBI flying disc investigation, Oak Ridge UFO, FBI vault UFO, Trump FBI UFO release, PURSUE FBI",
    },
    {
        "slug": "military-uap-files",
        "title": "Pentagon UAP Files: 143 Military Encounter Reports From the Trump UFO Release",
        "h1": "Pentagon UAP & Military Encounter Files",
        "match": lambda f: f.get("agency") == "DoD",
        "intro": (
            "One hundred forty-three Department of War files cover U.S. military Unidentified Anomalous "
            "Phenomena encounters spanning <strong>a 1949 U.S. Army flying-saucer study through 2026</strong>. "
            "These include AARO mission packets and "
            "Mission Reports (MISREPs) from the Mediterranean, Greek airspace, the Arabian Gulf, the "
            "Indo-Pacific, Iraq, Syria, the UAE, and Yemen - plus a multi-document AARO case from the "
            "<strong>Western United States</strong> added in Release 03 (June 2026). Many include "
            "full-motion video from "
            "<strong>infrared (IR), electro-optical (EO), and short-wave infrared (SWIR) sensors</strong>. "
            "These are the files that score highest on the Anomalousness Index, because the encounters "
            "have the strongest sensor and witness chain - trained military operators, multi-sensor "
            "capture, and unresolved official disposition."
        ),
        "meta_desc": (
            "All 143 Pentagon and Department of War UAP files from the Trump 2026 PURSUE releases. "
            "AARO mission reports, MISREPs, Mediterranean, Greece, UAE, Iraq, Syria, Western US, IR/EO/SWIR "
            "sensor captures. Full transcripts, AI-ranked anomalousness."
        ),
        "keywords": "Pentagon UAP files, DoD UFO files, AARO mission report, MISREP UAP, Greece UAP 2024, UAE UAP, Mediterranean UFO, military UFO video, war.gov UAP, Trump Pentagon UFO",
    },
    {
        "slug": "nasa-ufo-photos",
        "title": "NASA UFO Photos: Apollo, Gemini, Mercury & Skylab UAP Records",
        "h1": "NASA UFO & UAP Records",
        "match": lambda f: f.get("category") in ("nasa", "apollo") or f.get("agency") == "NASA",
        "intro": (
            "Thirty-three NASA files have been declassified under PURSUE - fifteen in Release 01 "
            "(May 8, 2026), seven in Release 02 (May 22, 2026), and eleven more in Release 03 "
            "(June 12, 2026). They span the earliest U.S. "
            "crewed spaceflights through the Apollo program: <strong>Mercury-Redstone 4 and Mercury-Atlas "
            "7, 8, and 9 air-to-ground audio</strong> (1961-1963), <strong>Gemini 4, 5, 7, and 9 crew "
            "debriefings and audio</strong> - including the Gemini 7 recording in "
            "which astronaut Frank Borman reports an unidentified object in low Earth orbit - "
            "<strong>Apollo 11, 12, 16, and 17 crew debriefings and transcripts</strong>, <strong>Apollo 12 "
            "and 17 mission photography</strong> with highlighted areas of unidentified phenomena above "
            "the lunar horizon, the <strong>Schmitt-Grimaldi lunar flash</strong> that Apollo 17 LMP "
            "Harrison Schmitt reported north of the crater Grimaldi in December 1972, and a "
            "<strong>Skylab crew debriefing</strong> from 1973. Release 03 (June 2026) added the Gemini 4, "
            "5, 7, and 9 debriefings, the <strong>Apollo 16 scientific debriefing</strong>, an interview "
            "excerpt with astronaut <strong>Gordon Cooper</strong>, and a 1962-63 astronaut scientific "
            "debriefing set. Astronaut-witness corroboration is rare in the UAP record. NASA-UAP-D003A "
            "(Borman / Gemini 7) is tied for the highest score (72) in the entire PURSUE release."
        ),
        "meta_desc": (
            "All 33 NASA UFO files in the Trump 2026 PURSUE releases. Apollo 12, 16, and 17 "
            "records, Gemini 4/5/7/9 crew debriefings, Frank Borman and Gordon Cooper audio, Mercury "
            "program audio (1961-63), Skylab debriefing, Schmitt-Grimaldi lunar flash. Astronaut-witness records."
        ),
        "keywords": "NASA UFO photos, Apollo 12 UAP, Apollo 16 UFO, Apollo 11 UFO, Apollo 17 UFO, Gemini 7 UAP, Gemini 4 UFO, Gemini 9 UAP, Gordon Cooper UFO, Frank Borman UFO, Mercury Atlas UFO, Skylab UFO, Schmitt-Grimaldi lunar flash, astronaut UFO sighting, NASA UAP declassified",
    },
    {
        "slug": "state-department-uap-cables",
        "title": "State Department UAP Cables: 7 Diplomatic Records 1952-2004",
        "h1": "State Department UAP Diplomatic Cables",
        "match": lambda f: f.get("category") == "state" or f.get("agency") == "STATE",
        "intro": (
            "Seven U.S. Department of State files were declassified under PURSUE, spanning "
            "<strong>1952 through 2004</strong>. The set includes 5 numbered embassy cables - the "
            "<strong>1985 Papua New Guinea cable</strong> from the U.S. Embassy in Port Moresby to "
            "USCINCPAC, the <strong>1994 cable from Dushanbe documenting a Tajik pilot and three U.S. "
            "citizens encountering an UAP at 41,000 feet over Kazakhstan in a 747</strong>, plus cables "
            "from Tbilisi (Georgia), Mexico, and Ashgabat (Turkmenistan) - and 2 earlier internal State "
            "memoranda from 1952 and 1963 (the 1963 memo from the Executive Office's National Aeronautics "
            "and Space Council). The cluster is the State Department's running record of what foreign "
            "governments, foreign aviation authorities, and earlier internal policy reviewers communicated "
            "about UAP through official U.S. channels. For a file-by-file walkthrough with diplomatic "
            "context, see <a href='/diplomatic-uap-cables'>our deep dive</a>."
        ),
        "meta_desc": (
            "All 7 State Department UAP files in the Trump May 2026 PURSUE release: 5 embassy cables "
            "(Papua New Guinea 1985, Kazakhstan 1994, Georgia 2001, Mexico 2003, Turkmenistan 2004) "
            "plus 2 earlier internal State memos from 1952 and 1963. Indexed and searchable."
        ),
        "keywords": "State Department UFO, UAP diplomatic cable, Papua New Guinea UFO 1985, Kazakhstan UAP 1994, USCINCPAC UAP, embassy UFO cable, Mexico UAP Congress, declassified State UFO, diplomatic UAP cable",
    },
    {
        "slug": "cia-ufo-files",
        "title": "CIA UFO Files: 19 Declassified CIA UAP Records From the Trump Disclosure",
        "h1": "CIA UFO & UAP Files",
        "match": lambda f: f.get("agency") == "CIA",
        "intro": (
            "Nineteen CIA files have been declassified under PURSUE - eighteen historical Central "
            "Intelligence Agency UAP records added in <strong>Release 03 (June 12, 2026)</strong>, plus "
            "<strong>CIA-UAP-D001</strong>, a 1973 CIA Intelligence Information Report relating to USSR "
            "activity, from Release 02. The Release 03 set reaches back to the agency's earliest UFO work: "
            "the <strong>Scientific Advisory Panel on Unidentified Flying Objects</strong>, a study titled "
            "<strong>'The Central Intelligence Agency and Overhead Reconnaissance'</strong>, the "
            "<strong>CASE 17708 / Dr. Leon Davidson</strong> correspondence, a German scientist's article "
            "on 'flying discs,' and multiple mid-century reports of sightings of unconventional aircraft. "
            "Most are partially redacted; we mark redaction status on each. All are public domain U.S. "
            "Government works under 17 U.S.C. § 105."
        ),
        "meta_desc": (
            "All 19 CIA UFO files declassified in the Trump administration's 2026 PURSUE releases. The "
            "CIA Scientific Advisory Panel on UFOs, 'The CIA and Overhead Reconnaissance,' the Leon "
            "Davidson / CASE 17708 correspondence, mid-century sighting reports, and the 1973 USSR "
            "intelligence report. Indexed, searchable, SHA-256 verified."
        ),
        "keywords": "CIA UFO files, CIA UAP declassified, CIA Scientific Advisory Panel UFO, CIA overhead reconnaissance UFO, Leon Davidson UFO, CASE 17708, CIA flying disc, CIA-UAP-D001, Trump CIA UFO release, PURSUE CIA",
    },
    {
        "slug": "intel-and-doe-uap-files",
        "title": "Intelligence Community, DOE & Government UAP Files: ODNI, Energy Department, and Federal Records",
        "h1": "Intelligence Community, DOE & Government UAP Records",
        "match": lambda f: f.get("agency") in ("ODNI", "DOE", "ICA", "USG"),
        "intro": (
            "Six U.S. intelligence-community, Department of Energy, and federal-government UAP files have "
            "been declassified under PURSUE (the CIA's records now have <a href='/cia-ufo-files'>their own "
            "section</a>). The cluster includes "
            "<strong>ODNI-UAP-D001</strong> (the USPER Narrative from a senior U.S. Intelligence "
            "Community official describing a multi-witness UAP encounter from a military helicopter "
            "in late 2025); three <strong>Department of Energy</strong> records tied to the U.S. nuclear "
            "weapons complex - enhanced PANTEX imagery, James Tuck correspondence from the 1970s, and a "
            "1986 Pajarito astronomers invitation (PANTEX assembly plant, Los Alamos via Tuck, and the "
            "Pajarito Plateau); an <strong>Intelligence Community analysis of the 2022 Colorado Springs "
            "UAP incident</strong> (ICA-UAP-D001, added in Release 03); and a <strong>U.S. Government "
            "compilation of Congressional and White House UFO-related constituent correspondence</strong> "
            "(USG-UAP-D001, Release 03). All files are public domain U.S. Government works under "
            "17 U.S.C. § 105."
        ),
        "meta_desc": (
            "Six ODNI, Department of Energy, and U.S. Government UAP files from the Trump 2026 PURSUE "
            "releases. ODNI-UAP-D001 USPER helicopter narrative, three DOE nuclear-complex files (PANTEX, "
            "Los Alamos, Pajarito), an IC analysis of the 2022 Colorado Springs incident, and "
            "Congressional/White House UFO correspondence. (CIA files are in their own section.)"
        ),
        "keywords": "ODNI UAP report, ODNI-UAP-D001, DOE UAP, Department of Energy UFO, PANTEX UAP, USPER UAP narrative, Colorado Springs UAP 2022, Congressional UFO correspondence, intelligence community UAP, PURSUE intel disclosure",
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
        f'<a class="cat-card" href="/files/{fid}">'
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
            {"@type": "ListItem", "position": 2, "name": cat["h1"], "item": canonical},
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
                "url": f"{SITE_URL}/files/{f['id']}",
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
    # Cross-category + editorial internal links. The hub pages receive a
    # file->hub link from all 161 file-page breadcrumbs; this nav redistributes
    # that equity to the other hubs and the high-value editorial pages, and
    # lifts pageviews per session (more ad impressions).
    other_cats = "".join(
        f'<a class="explore-chip" href="/{c["slug"]}/">{_html.escape(c["h1"])}</a>'
        for c in CATEGORIES if c["slug"] != cat["slug"]
    )
    explore_nav = f"""  <nav class="cat-explore" aria-label="Explore the rest of the archive" style="margin:48px 0 8px;padding:28px;background:rgba(82,180,255,.04);border:1px solid rgba(82,180,255,.15);border-radius:10px">
    <h2 style="color:#fff;font-size:20px;margin-bottom:16px">Explore the rest of the PURSUE archive</h2>
    <div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:18px">{other_cats}</div>
    <p style="color:#a8b8cc;font-size:14px;margin:0;line-height:1.9">
      <a href="/top-10" style="color:#52b4ff;text-decoration:none">Top 10 most anomalous</a> &nbsp;·&nbsp;
      <a href="/methodology" style="color:#52b4ff;text-decoration:none">How the scoring works</a> &nbsp;·&nbsp;
      <a href="/timeline" style="color:#52b4ff;text-decoration:none">Timeline 1947-2026</a> &nbsp;·&nbsp;
      <a href="/verdict" style="color:#52b4ff;text-decoration:none">The honest verdict</a> &nbsp;·&nbsp;
      <a href="/changes" style="color:#52b4ff;text-decoration:none">War.gov revision diff</a> &nbsp;·&nbsp;
      <a href="/faq" style="color:#52b4ff;text-decoration:none">FAQ</a>
    </p>
  </nav>"""
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
<!-- Google AdSense ownership verification + Auto Ads (pub-7264251466939264, activated 2026-05-22) -->
<meta name="google-adsense-account" content="ca-pub-7264251466939264">
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7264251466939264" crossorigin="anonymous"></script>
<!-- Privacy-friendly analytics by Plausible -->
<script async src="https://plausible.io/js/pa-ZDj9MJVwqhPZChU5a2Hhx.js"></script>
<script>
  window.plausible=window.plausible||function(){{(plausible.q=plausible.q||[]).push(arguments)}},plausible.init=plausible.init||function(i){{plausible.o=i||{{}}}};
  plausible.init()
</script>
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
  .explore-chip{{display:inline-block;padding:8px 14px;background:rgba(82,180,255,.08);border:1px solid rgba(82,180,255,.25);border-radius:6px;color:#dfe6ef;text-decoration:none;font-size:13px;font-weight:500}}
  .explore-chip:hover{{border-color:rgba(82,180,255,.5)}}
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

  <h2 class="sr-only">All files in {cat['h1']}</h2>
  <div class="cat-grid">
{cards}
  </div>

{explore_nav}

  <a class="cat-back" href="/">← BACK TO ALL 294 FILES</a>
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
