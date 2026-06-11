"""Stage 0.5: parse the war.gov uap-csv.csv into a full manifest (~161 entries).

Reads _scratch/uap-csv.csv (downloaded from
https://www.war.gov/Portals/1/Interactive/2026/UFO/uap-csv.csv via curl_cffi).

For each row:
- Slugifies title -> id
- Maps Type column (PDF/VID/IMG) to manifest type
- Maps Agency to FBI/DoD/NASA/STATE
- For VID type: queries DVIDS API to get MP4 URL, captions, thumbnail
- Default-scores using rubric heuristics based on type + agency
- Writes audience.* fields from the CSV description

Replaces the prior hand-curated 13-entry manifest with the real ~161-entry one.
The hand-curated scoring components are PRESERVED for files whose IDs match.
"""
from __future__ import annotations
import csv
import json
import re
import time
from pathlib import Path

from curl_cffi import requests
from tqdm import tqdm

from .config import MANIFEST_PATH, ROOT, ensure_dirs


CSV_PATH = ROOT / "_scratch" / "uap-csv.csv"
DVIDS_KEY = "key-68bb60d16b35e"
DVIDS_HEADERS = {"Referer": "https://www.war.gov/UFO/", "Origin": "https://www.war.gov"}

AGENCY_MAP = {
    "FBI": "FBI",
    "Department of War": "DoD",
    "NASA": "NASA",
    "Department of State": "STATE",
    # Added with PURSUE Release 02 (May 22 2026):
    "Central Intelligence Agency": "CIA",
    "Office of the Director of National Intelligence": "ODNI",
    "Department of Energy": "DOE",
}

TYPE_MAP = {
    "PDF": "pdf",
    "VID": "video",
    "IMG": "image",
    # "AUD" (audio) files are hosted on DVIDS as video MP4s (audio-only stream).
    # Map to "video" so they resolve a DVIDS URL and render in the player.
    # Before this was added (2026-06-10), AUD fell through to "pdf" and lost
    # its DVIDS resolution - which silently broke the flagship Gemini 7 audio.
    "AUD": "video",
}

# Agencies that share the "intel" category (intelligence-community + DOE
# nuclear-program records, distinct from military mission reports). New in
# Release 02 - 5 files in this category for the May 22 disclosure.
INTEL_AGENCIES = {"CIA", "ODNI", "DOE"}


def _slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80]


def _category(agency: str, title: str, vtitle: str) -> str:
    t = (title + " " + (vtitle or "")).lower()
    if "apollo" in t or "nasa" in t:
        return "apollo" if "apollo" in t else "nasa"
    if agency == "FBI":
        return "fbi"
    if agency == "STATE":
        return "state"
    if agency in INTEL_AGENCIES:
        return "intel"
    if "composite" in t or "sketch" in t:
        return "composite"
    return "military"


def _default_score(type_: str, agency: str, redacted: bool) -> dict:
    """Conservative default rubric values when we don't have richer info."""
    sensor = {"pdf": "eyewitness_only", "video": "single_sensor_military",
              "image": "photographic"}.get(type_, "eyewitness_only")
    witness = {"FBI": "federal_agent", "DoD": "military_personnel",
               "NASA": "astronaut", "STATE": "civilian_credentialed",
               "CIA": "federal_agent", "ODNI": "federal_agent",
               "DOE": "federal_agent"}.get(agency, "civilian_credentialed")
    return {
        "components": {
            "sensor_quality": sensor,
            "witness_credibility": witness,
            "corroboration": "single_witness_instrument",
            "kinematic_anomaly": "no_kinematic_data",
            "mundane_explanation_available": "weak_mundane_candidate",
            "official_disposition": "open_after_review" if not redacted else "unresolved_no_review",
        }
    }


def _fetch_dvids(video_id: str) -> dict | None:
    if not video_id or not video_id.strip().isdigit():
        return None
    url = f"https://api.dvidshub.net/asset?api_key={DVIDS_KEY}&id=video:{video_id.strip()}"
    try:
        r = requests.get(url, impersonate="chrome131", headers=DVIDS_HEADERS, timeout=20)
        if r.status_code == 200:
            return json.loads(r.content).get("results") or None
    except Exception as e:
        print(f"  DVIDS fail {video_id}: {e}")
    return None


def _pick_mp4(dvids: dict) -> str | None:
    files = dvids.get("files") or []
    if not files:
        return None
    # Prefer the highest quality 1920x1080
    candidates = [f for f in files if f.get("type") == "video/mp4"]
    if not candidates:
        return None
    candidates.sort(key=lambda f: (f.get("size", 0)), reverse=True)
    return candidates[0].get("src")


def _normalize_type(s: str) -> str:
    return TYPE_MAP.get(s.strip().upper(), "pdf")


def _existing_manifest() -> dict:
    """Preserve curated scores from the previous manifest if IDs match."""
    if not MANIFEST_PATH.exists():
        return {}
    try:
        prev = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        return {f["id"]: f for f in prev.get("files", [])}
    except Exception:
        return {}


def run() -> None:
    ensure_dirs()
    if not CSV_PATH.exists():
        print(f"  CSV not found at {CSV_PATH}")
        return
    text = CSV_PATH.read_text(encoding="utf-8-sig", errors="replace")
    reader = csv.reader(text.splitlines())
    rows = list(reader)
    header = rows[0]
    data = [r for r in rows[1:] if any(r)]
    print(f"  CSV: {len(data)} entries")

    prev_by_id = _existing_manifest()
    files: list[dict] = []
    seen_ids: set[str] = set()

    for row in tqdm(data, desc="parsing", unit="row"):
        # Pad short rows
        row = row + [""] * max(0, 14 - len(row))
        (redaction, release_date, title, type_raw, video_pairing, pdf_pairing,
         description, dvids_id, video_title, agency_raw, incident_date,
         incident_location, pdf_link, modal_image) = row[:14]

        type_ = _normalize_type(type_raw)
        agency = AGENCY_MAP.get(agency_raw.strip(), "OTHER")
        redacted = redaction.strip().upper() == "TRUE"

        # ID: use video title for videos, file title for others
        title_for_id = (video_title or title).strip()
        base_id = _slugify(title_for_id) or _slugify(f"{agency}-{type_}-{len(files)}")
        fid = base_id
        n = 1
        while fid in seen_ids:
            n += 1
            fid = f"{base_id}-{n}"
        seen_ids.add(fid)

        # source_url and local_path candidates
        source_url = pdf_link.strip() or None
        thumb_url = modal_image.strip() or None

        # Default geo
        place = incident_location.strip() if incident_location.strip() not in ("", "N/A") else None
        geo = {"lat": None, "lng": None, "place": place}

        # Default date
        date_event = incident_date.strip() if incident_date.strip() not in ("", "N/A") else None

        # Build entry, preserving curated score if id matches
        prev = prev_by_id.get(fid) or {}
        score = prev.get("score") or _default_score(type_, agency, redacted)

        # Convert the CSV's "Release Date" column ("5/8/26", "5/22/26", ...) to
        # ISO "2026-05-08" / "2026-05-22". Default to Release 01 if missing/malformed
        # so legacy entries do not lose their previously-correct date.
        rd = release_date.strip()
        date_released = "2026-05-08"
        m_rd = re.match(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", rd)
        if m_rd:
            mm, dd, yy = m_rd.groups()
            yyyy = yy if len(yy) == 4 else ("20" + yy)
            date_released = f"{yyyy}-{int(mm):02d}-{int(dd):02d}"

        entry = {
            "id": fid,
            "title": title_for_id or title.strip() or fid,
            "category": _category(agency, title, video_title),
            "agency": agency,
            "type": type_,
            "date_event": date_event,
            "date_released": date_released,
            "source_url": source_url,
            "pending_verification": False,
            "local_path": None,        # set after download stage
            "size_bytes": None,
            "sha256": None,
            "redacted": redacted,
            "summary": description.strip(),
            "score": score,
            "extracted": {"text_path": None, "transcript_path": None, "thumbnail_path": None},
            "geo": geo,
            "thumbnail_url": thumb_url,
            "csv_raw_title": title,
        }

        # Video specifics: hit DVIDS for the MP4 URL + captions + thumbnail
        if type_ == "video" and dvids_id.strip():
            entry["dvids_video_id"] = dvids_id.strip()
            dv = _fetch_dvids(dvids_id)
            if dv:
                mp4 = _pick_mp4(dv)
                if mp4:
                    entry["video_url"] = mp4
                cc = (dv.get("closed_caption_urls") or {})
                if cc.get("webvtt"):
                    entry["caption_vtt_url"] = cc["webvtt"]
                if cc.get("srt"):
                    entry["caption_srt_url"] = cc["srt"]
                if dv.get("thumbnail", {}).get("url"):
                    entry["thumbnail_url"] = dv["thumbnail"]["url"]
                if dv.get("duration"):
                    entry["duration"] = dv["duration"]
                entry["dvids_page_url"] = dv.get("url")
            time.sleep(0.15)  # be polite to DVIDS API

        files.append(entry)

    manifest = {
        "generated_at": "2026-05-09T20:00:00Z",
        "rubric_version": "1.0",
        "_note": "Real manifest parsed from war.gov/Portals/1/Interactive/2026/UFO/uap-csv.csv. Video URLs sourced from DVIDS public API.",
        "files": files,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  wrote manifest: {len(files)} entries -> {MANIFEST_PATH}")
    # Quick stats
    from collections import Counter
    types = Counter(f["type"] for f in files)
    agencies = Counter(f["agency"] for f in files)
    redacted = sum(1 for f in files if f["redacted"])
    videos_with_url = sum(1 for f in files if f.get("video_url"))
    print(f"  types: {dict(types)}")
    print(f"  agencies: {dict(agencies)}")
    print(f"  redacted: {redacted}")
    print(f"  videos with MP4 URL: {videos_with_url}")


if __name__ == "__main__":
    run()
