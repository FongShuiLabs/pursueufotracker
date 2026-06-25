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
from .build_categories import CATEGORIES


CHOICE_EXPLANATIONS = {
    "sensor_quality": {
        "single_sensor_military": "Captured by a single U.S. military sensor platform (typically infrared, occasionally short-wave infrared or dual EO+IR), aboard a mission aircraft or operational platform. Instrumented, time-stamped, and recoverable. Lower than a multi-sensor capture only because cross-modality confirmation is the rubric's higher bar.",
        "photographic": "Captured as a still photograph rather than a time-series sensor capture. The rubric scores still photography below instrumented sensor capture because a still image lacks temporal context and cross-modality confirmation - both of which weight heavily against artifact and noise explanations.",
        "eyewitness_only": "Reported by a witness with no instrumented record. The lowest tier in the rubric's sensor axis. Eyewitness perception in field conditions, even when the witness is highly credentialed, scores below capture by any instrumented modality.",
    },
    "witness_credibility": {
        "astronaut": "Astronaut witness on the official federal record. The highest tier in the rubric and essentially unique in the PURSUE archive - only the Borman/Lovell Gemini 7 file fits this tier, which is the structural reason it is the sole 72 in the archive.",
        "military_personnel": "Trained U.S. military personnel reporting from an operational mission context. The second-highest credibility tier in the rubric. This is the witness profile shared by the entire AARO-submitted infrared-capture cluster that anchors the 66-point score band.",
        "federal_agent": "Federal agency personnel (FBI investigators or equivalent) recording the report into the federal investigative system. Investigative credentials, but typically operating in a reactive rather than mission-active posture.",
        "civilian_credentialed": "Civilian witness whose report entered the federal record through investigative channels. The rubric weights civilian credentialed witnesses below uniformed personnel because the report enters the federal record at a remove rather than directly from a mission context.",
    },
    "corroboration": {
        "single_witness_instrument": "Single-witness or single-instrument capture. Every file in the PURSUE archive scores at this corroboration tier on the released metadata - the rubric records the honest limit of the underlying record rather than inferring multi-witness corroboration that the released summaries do not establish.",
    },
    "kinematic_anomaly": {
        "no_kinematic_data": "No kinematic measurements - speed, acceleration, vector - are published in the released file with sufficient precision to score on the kinematic axis. The rubric does not infer kinematic anomaly from narrative observer estimates. Every file in the archive carries this value, which is itself an observation about the disclosure: kinematic-grade telemetry was not part of what was released.",
    },
    "mundane_explanation_available": {
        "weak_mundane_candidate": "A conventional candidate explanation has been considered but is not dispositive. Every file in the archive scores this way - reflecting that the underlying release metadata systematically caveats strong determinations in either direction. The released summaries warn against reading them as conclusive analytical judgments, and the rubric respects that.",
    },
    "official_disposition": {
        "open_after_review": "Released as open after formal review by the originating agency. The file passed through a review process and was published in that posture - a stronger disposition signal than 'unresolved with no review,' because review has occurred and the open status is the agency's published conclusion.",
        "unresolved_no_review": "Catalogued as unresolved with no formal review process having concluded. This is the AARO baseline disposition for the 27-file score-66 cluster - the reports are logged into the system as unresolved, but no formal review has finalized. The rubric distinguishes this from 'open after review' because the absence of review is itself a status signal.",
    },
}

TOPIC_PAGES = [
    {"match": lambda f: f["id"] == "nasa-uap-d003a-gemini-7-audio-excerpt-1965",
     "slug": "/borman-incident", "name": "The Borman Incident", "size": 1,
     "anchor": "the highest-scoring file in the archive at 72"},
    {"match": lambda f: f["id"].startswith("65-hs1-834228961-62-hq-83894-"),
     "slug": "/fbi-62-hq-83894", "name": "FBI Case 62-HQ-83894", "size": 18,
     "anchor": "the 18-PDF FBI central case file covering 1947-1968"},
    {"match": lambda f: f["id"] in {"nasa-uap-vm001-apollo-12-1969","nasa-uap-vm002-apollo-12-1969","nasa-uap-vm003-apollo-12-1969","nasa-uap-vm004-apollo-12-1969","nasa-uap-vm005-apollo-12-1969","nasa-uap-d001-apollo-12-transcript-1969"},
     "slug": "/apollo-12-ufo-photos", "name": "Apollo 12 UFO Photos", "size": 6,
     "anchor": "the 6-file Apollo 12 PURSUE cluster"},
    {"match": lambda f: f["id"] in {"nasa-uap-d002-apollo-17-transcript-1972","nasa-uap-d005-apollo-17-crew-debriefing-for-science-1973","nasa-uap-d006-apollo-17-technical-crew-debriefing-1973","nasa-uap-vm006-apollo-17-1972"},
     "slug": "/apollo-17-ufo-records", "name": "Apollo 17 UFO Records", "size": 4,
     "anchor": "the 4-file Apollo 17 PURSUE cluster, including the triangular-formation lunar image and Schmitt light-flash debriefing"},
    {"match": lambda f: f["id"] == "nasa-uap-d023-interview-excerpt-with-astronaut-gordon-cooper-1962",
     "slug": "/gordon-cooper-ufo", "name": "Gordon Cooper on UFOs", "size": 1,
     "anchor": "the 1962 Walter Cronkite interview clip, tied for the archive's highest score at 72"},
    {"match": lambda f: f["id"] in {"nasa-uap-d024-apollo-16-scientific-debriefing","nasa-uap-d025-apollo-16-scientific-debriefing"},
     "slug": "/apollo-16-ufo", "name": "Apollo 16 and UFOs", "size": 2,
     "anchor": "the two Apollo 16 scientific debriefings (the orbital flash and the 'alien star base' remark), tied for the archive's highest score at 72"},
    {"match": lambda f: f["id"] in {"nasa-uap-d016-preliminary-gemini-4-crew-debriefing-part-i-1965","nasa-uap-d017-preliminary-gemini-4-crew-debriefing-part-ii-1965","nasa-uap-d018-gemini-4-experiment-debriefing-1967"},
     "slug": "/gemini-4-ufo", "name": "Gemini 4 UFO", "size": 3,
     "anchor": "the three classified Gemini 4 debriefings (D016/D017/D018) documenting McDivitt's 1965 encounter with an unidentified orbiting object near Hawaii"},
    {"match": lambda f: f["id"] in {"nasa-uap-d013-mercury-atlas-7-may-24-1962","nasa-uap-d015-astronaut-scientific-debriefings-1962-1963"},
     "slug": "/mercury-fireflies", "name": "John Glenn's Fireflies", "size": 2,
     "anchor": "the classified NASA scientific investigation of Glenn's 1962 'fireflies' sighting and Carpenter's real-time audio confirmation from Mercury Atlas 7"},
    {"match": lambda f: f["id"] == "nasa-uap-d004-apollo-11-technical-crew-debriefing-1969",
     "slug": "/apollo-11-ufo", "name": "Apollo 11 UFO Sightings", "size": 1,
     "anchor": "the classified Apollo 11 Technical Crew Debriefing describing three unexplained observations including the object Buzz Aldrin tracked with a monocular one day from the Moon"},
    {"match": lambda f: f.get("agency") == "STATE",
     "slug": "/diplomatic-uap-cables", "name": "Diplomatic UAP Cables", "size": 7,
     "anchor": "the 7-file State Department PURSUE cluster spanning 1952-2004 embassy cables and policy memoranda"},
    {"match": lambda f: f["id"] == "cia-uap-002-scientific-advisory-panel-on-unidentified-flying-objects-report-1952",
     "slug": "/robertson-panel", "name": "The Robertson Panel", "size": 1,
     "anchor": "the 1952-53 CIA Scientific Advisory Panel (the Robertson Panel) that recommended an official policy of debunking UFOs"},
    {"match": lambda f: f["id"] == "cia-uap-003-the-central-intelligence-agency-and-overhead-reconnaissance-the-u-2-",
     "slug": "/u-2-ufo-sightings", "name": "U-2 Spy Planes and UFOs", "size": 1,
     "anchor": "the CIA history stating U-2 and OXCART flights accounted for more than half of all UFO reports in the late 1950s and 1960s"},
    {"match": lambda f: f["id"] == "cia-uap-015-project-blue-book-special-report-no-14-analysis-of-reports-of-uniden",
     "slug": "/project-blue-book-special-report-14", "name": "Project Blue Book Special Report No. 14", "size": 1,
     "anchor": "the Air Force's 1955 statistical UFO study (3,201 sightings, 19.7% left unknown)"},
    {"match": lambda f: f["id"] == "cia-uap-d001-intelligence-information-report-ussr-1973",
     "slug": "/cia-uap-d001-1973-ussr", "name": "CIA-UAP-D001 (1973 USSR)", "size": 1,
     "anchor": "the 1973 CIA Intelligence Information Report describing a HUMINT source's observation of a bright green airborne UAP in the Soviet Union"},
    {"match": lambda f: f["id"] == "cia-uap-017-placement-on-high-alert-due-to-perceived-aggressive-foreign-posturin",
     "slug": "/cia-harare-ufo-2008", "name": "CIA Harare Airport UFO (2008)", "size": 1,
     "anchor": "the SECRET/NOFORN CIA report sent to the White House Situation Room in 2008 documenting a disc-shaped object with rotating color-shifting lights over Harare International Airport, Zimbabwe"},
    {"match": lambda f: f["id"] == "cia-uap-016-sightings-of-unidentified-flying-objects-in-ladakh-nepal-sikkim-and-",
     "slug": "/cia-himalayan-ufo-1968", "name": "CIA Himalayan UFO Sightings (1968)", "size": 1,
     "anchor": "the 1968 CIA field intelligence report documenting seven UFO sightings across Ladakh, Nepal, Sikkim and Bhutan, including a field source claim that a metallic disc-shaped object was physically found near Pokhara, Nepal"},
    {"match": lambda f: f.get("agency") == "CIA",
     "slug": "/cia-ufo-files-explained", "name": "CIA UFO Files", "size": 19,
     "anchor": "the 19-file CIA cluster, from the 1953 Robertson Panel to the U-2 history and Cold War sightings"},
    {"match": lambda f: f["id"].startswith("fbi-september-2023-sighting"),
     "slug": "/fbi-2023-uap-investigation", "name": "FBI 2023 UAP Investigation", "size": 4,
     "anchor": "the 4-document FBI investigation cluster from September 2023 - three FD-302 witness interviews and an FBI Lab composite sketch of a bronze metallic cigar-shaped object at a US test site"},
    {"match": lambda f: f["id"].startswith("fbi-uap-"),
     "slug": "/fbi-modern-uap-files", "name": "FBI Modern UAP Files", "size": 29,
     "anchor": "the FBI's modern UAP files: the 2022 Colorado Springs interview and the FBI-authenticated northeastern orb videos"},
    {"match": lambda f: f["id"] == "odni-uap-d001-usper-narrative-senior-usic-official",
     "slug": "/odni-uap-d001-helicopter-encounter", "name": "ODNI-UAP-D001 Helicopter Encounter", "size": 1,
     "anchor": "the senior US intelligence official's first-person helicopter UAP narrative from late 2025, released in PURSUE Release 02"},
    {"match": lambda f: f["id"].startswith("dow-uap-pr"),
     "slug": "/pursue-release-02-pentagon-videos", "name": "Release 02 Pentagon UAP Videos", "size": 51,
     "anchor": "the 51-file DOW-UAP-PR050-PR099 series released in PURSUE Release 02 on May 22, 2026"},
    {"match": lambda f: f.get("agency") == "DOE",
     "slug": "/doe-nuclear-uap-files", "name": "DOE Nuclear UAP Files", "size": 3,
     "anchor": "the 3 Department of Energy files tying the U.S. nuclear weapons complex to UAP (PANTEX, Los Alamos via Tuck, Pajarito Astronomers)"},
    {"match": lambda f: (f.get("score") or {}).get("value") == 66,
     "slug": "/aaro-unresolved-uap", "name": "AARO Unresolved UAP", "size": 27,
     "anchor": "the 27-file AARO unresolved cluster tied at 66"},
]


def _topic_page_for(f: dict) -> dict | None:
    """First-match wins (predicates are mutually exclusive by construction)."""
    for tp in TOPIC_PAGES:
        try:
            if tp["match"](f):
                return {"slug": tp["slug"], "name": tp["name"], "size": tp["size"], "anchor": tp["anchor"]}
        except Exception:
            continue
    return None


def _score_tier_phrase(score: int | None, rank: int, total: int) -> str:
    """One sentence placing this score in the broader archive context."""
    if score is None:
        return ""
    if score >= 72:
        return "That score is the highest in the PURSUE archive - the only file at this tier."
    if score >= 66:
        return f"That places it tied with 26 other files at 66 - the densest single-score cluster in the archive, anchored by AARO-submitted military infrared captures."
    if score >= 65:
        return f"That places it one rubric point below the 27-file AARO 66 cluster and seven below the Gemini 7 audio at 72 - the second tier in the archive."
    if score >= 60:
        return f"That places it in the mid-archive band ({rank} of {total} by score). The score reflects the rubric's read on evidentiary weight, not the underlying event's significance."
    return f"That places it in the lower-scoring band of the archive ({rank} of {total} by score), typical of investigative-record style files where the report is paper-based rather than instrumented."


def _rank_map(all_files: list[dict]) -> dict[str, int]:
    """File id -> rank (1-indexed) by score desc, ties broken by id."""
    ranked = sorted(all_files, key=lambda g: (-((g.get("score") or {}).get("value") or 0), g.get("id", "")))
    return {g["id"]: i + 1 for i, g in enumerate(ranked)}


def _agency_rank_map(all_files: list[dict]) -> dict[str, tuple[int, int]]:
    """File id -> (rank within agency, total files in agency)."""
    from collections import defaultdict
    by_agency: dict[str, list[dict]] = defaultdict(list)
    for f in all_files:
        by_agency[f.get("agency", "")].append(f)
    result: dict[str, tuple[int, int]] = {}
    for agency, files in by_agency.items():
        files.sort(key=lambda g: (-((g.get("score") or {}).get("value") or 0), g.get("id", "")))
        for i, g in enumerate(files):
            result[g["id"]] = (i + 1, len(files))
    return result


def _category_page(f: dict) -> dict | None:
    """Map a file to its category hub page (slug + display name) using the
    same match logic as build_categories, so the breadcrumb can deep-link
    each file page to its category landing page. Returns None if no hub
    page matches (shouldn't happen for current manifest, but stay safe)."""
    for cat in CATEGORIES:
        try:
            if cat["match"](f):
                return {"slug": cat["slug"], "name": cat["h1"]}
        except Exception:
            continue
    return None


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


_SERIES_RE = re.compile(r"^(.+?)[-_]section[-_]?(\d+)$", re.IGNORECASE)


def _series_neighbors(f: dict, all_files: list[dict]) -> tuple[dict | None, dict | None]:
    """If this file is part of a paginated series (e.g. FBI 62-HQ-83894-section-N),
    return (prev, next) file dicts for rel=prev/next link tags. Else (None, None)."""
    m = _SERIES_RE.match(f.get("id", ""))
    if not m:
        return None, None
    base, num_str = m.group(1), m.group(2)
    try:
        num = int(num_str)
    except ValueError:
        return None, None
    by_section = {}
    for g in all_files:
        gm = _SERIES_RE.match(g.get("id", ""))
        if gm and gm.group(1) == base:
            try:
                by_section[int(gm.group(2))] = g
            except ValueError:
                continue
    prev_f = by_section.get(num - 1) if (num - 1) in by_section else None
    next_f = by_section.get(num + 1) if (num + 1) in by_section else None
    return prev_f, next_f


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


def _seo_titles_map(all_files: list[dict]) -> dict[str, str]:
    """Build {file_id: differentiated_title} for SEO uniqueness.

    When multiple files share the same CSV Title (multi-row PDFs where the
    same underlying file gets multiple CSV row representations), all share
    the same title text. That creates duplicate <title> tags across multiple
    URLs, which is a real SEO problem (Google treats duplicate-title pages
    as competing for the same ranking).

    Fix: group files by title; within each duplicate group, append
    "(record N)" where N is the order of appearance in the manifest (1-indexed).
    When a title is unique, leave it alone. This avoids the trap of trying
    to extract a "record number" from the slug (which would mis-extract years
    like 2023, 2024 from slugs that don't actually have a record suffix).
    """
    from collections import defaultdict
    title_groups: dict[str, list[str]] = defaultdict(list)
    for f in all_files:
        title_groups[f.get("title", "")].append(f["id"])

    seo = {}
    for title, ids in title_groups.items():
        if len(ids) <= 1:
            seo[ids[0]] = title
            continue
        # Multi-file group: number by manifest order of appearance
        for n, fid in enumerate(ids, start=1):
            seo[fid] = f"{title} (record {n})"
    return seo


def _render_file_pages(env: Environment, manifest: dict) -> None:
    tpl = env.get_template("file.html.j2")
    all_files = manifest["files"]
    seo_titles = _seo_titles_map(all_files)
    rank_by_id = _rank_map(all_files)
    agency_rank_by_id = _agency_rank_map(all_files)
    total_files = len(all_files)
    for f in all_files:
        out = GEN_FILES / f"{f['id']}.html"
        size_h = _human_size(f.get("size_bytes"))
        prev_f, next_f = _series_neighbors(f, all_files)
        # Build per-file score-component explanations from the rubric choices
        comps = (f.get("score") or {}).get("detail") or {}
        score_explanations = {}
        for cname, c in comps.items():
            choice = c.get("choice") if isinstance(c, dict) else None
            if choice and cname in CHOICE_EXPLANATIONS and choice in CHOICE_EXPLANATIONS[cname]:
                score_explanations[cname] = CHOICE_EXPLANATIONS[cname][choice]
        rank = rank_by_id.get(f["id"])
        ag_rank, ag_total = agency_rank_by_id.get(f["id"], (None, None))
        score_val = (f.get("score") or {}).get("value")
        archive_context = {
            "rank": rank,
            "total": total_files,
            "agency_rank": ag_rank,
            "agency_total": ag_total,
            "tier_phrase": _score_tier_phrase(score_val, rank or 999, total_files),
            "topic_page": _topic_page_for(f),
        }
        ctx = {
            "f": f,
            "seo_title": seo_titles[f["id"]],
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
            "category_page": _category_page(f),
            "series_prev": prev_f,
            "series_next": next_f,
            "archive_context": archive_context,
            "score_explanations": score_explanations,
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
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
             f"<sitemap><loc>{SITE_URL}/sitemap.xml</loc><lastmod>{today}</lastmod></sitemap>",
             f"<sitemap><loc>{SITE_URL}/video-sitemap.xml</loc><lastmod>{today}</lastmod></sitemap>",
             "</sitemapindex>"]
    (ROOT / "sitemap-index.xml").write_text("\n".join(parts), encoding="utf-8")


def _build_sitemap(manifest: dict) -> None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    # Homepage - lastmod = today (rebuilt frequently)
    parts.append(f"<url><loc>{SITE_URL}/</loc><lastmod>{today}</lastmod>"
                 f"<priority>1.0</priority><changefreq>daily</changefreq></url>")
    # High-value editorial pages - lastmod = today (rebuilt with site).
    # ALL URLs are extension-less canonical forms that serve 200 direct
    # (no redirect chains). The /pretty alias and /generated/X both serve
    # the same content; we choose the pretty form in the sitemap.
    for path, prio, freq in [
        ("/verdict", "0.95", "weekly"),
        ("/top-10", "0.95", "weekly"),
        ("/press", "0.85", "monthly"),
        ("/drops", "0.9", "weekly"),
        ("/revisions", "0.9", "weekly"),
        ("/changes", "0.9", "weekly"),
        ("/about", "0.7", "monthly"),
        ("/contact", "0.6", "monthly"),
        ("/privacy", "0.5", "monthly"),
        ("/faq", "0.85", "monthly"),
        ("/glossary", "0.85", "monthly"),
        ("/methodology", "0.9", "monthly"),
        ("/verify", "0.9", "monthly"),
        ("/rubric", "0.9", "monthly"),
        ("/search", "0.85", "weekly"),
        ("/timeline", "0.85", "weekly"),
        ("/borman-incident", "0.9", "monthly"),
        ("/apollo-12-ufo-photos", "0.9", "monthly"),
        ("/fbi-62-hq-83894", "0.9", "monthly"),
        ("/aaro-unresolved-uap", "0.9", "monthly"),
        ("/pursue-program", "0.9", "monthly"),
        ("/apollo-17-ufo-records", "0.9", "monthly"),
        ("/diplomatic-uap-cables", "0.9", "monthly"),
        ("/cia-ufo-files-explained", "0.9", "monthly"),
        ("/fbi-modern-uap-files", "0.9", "monthly"),
        ("/robertson-panel", "0.9", "monthly"),
        ("/project-blue-book-special-report-14", "0.9", "monthly"),
        ("/gordon-cooper-ufo", "0.9", "monthly"),
        ("/u-2-ufo-sightings", "0.9", "monthly"),
        ("/apollo-16-ufo", "0.9", "monthly"),
        ("/gemini-4-ufo", "0.9", "monthly"),
        ("/mercury-fireflies", "0.9", "monthly"),
        ("/apollo-11-ufo", "0.9", "monthly"),
        ("/cia-harare-ufo-2008", "0.9", "monthly"),
        ("/cia-himalayan-ufo-1968", "0.9", "monthly"),
        ("/fbi-2023-uap-investigation", "0.9", "monthly"),
        ("/odni-uap-d001-helicopter-encounter", "0.9", "monthly"),
        ("/pursue-release-02-pentagon-videos", "0.9", "monthly"),
        ("/doe-nuclear-uap-files", "0.9", "monthly"),
        ("/cia-uap-d001-1973-ussr", "0.9", "monthly"),
        ("/api", "0.8", "monthly"),
        ("/fbi-ufo-files/", "0.9", "weekly"),
        ("/military-uap-files/", "0.9", "weekly"),
        ("/nasa-ufo-photos/", "0.9", "weekly"),
        ("/state-department-uap-cables/", "0.9", "weekly"),
        ("/cia-ufo-files/", "0.9", "weekly"),
        ("/intel-and-doe-uap-files/", "0.9", "weekly"),
    ]:
        parts.append(f"<url><loc>{SITE_URL}{path}</loc><lastmod>{today}</lastmod>"
                     f"<priority>{prio}</priority><changefreq>{freq}</changefreq></url>")
    # Drop detail pages - lastmod = drop date. Extension-less canonical.
    drop_dir = ROOT / "generated" / "drops"
    if drop_dir.exists():
        for drop_html in sorted(drop_dir.glob("*.html")):
            if drop_html.name == "index.html":
                continue
            stem = drop_html.stem  # filename without .html
            m = re.match(r"(\d{4}-\d{2}-\d{2})", drop_html.name)
            lastmod = m.group(1) if m else today
            parts.append(
                f"<url><loc>{SITE_URL}/drops/{html.escape(stem)}</loc>"
                f"<lastmod>{lastmod}</lastmod>"
                f"<priority>0.85</priority><changefreq>monthly</changefreq></url>"
            )
    # File detail pages - lastmod = date_released (or today if missing)
    for f in manifest["files"]:
        lastmod = f.get("date_released") or today
        parts.append(
            f"<url><loc>{SITE_URL}/files/{html.escape(f['id'])}</loc>"
            f"<lastmod>{lastmod}</lastmod>"
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
