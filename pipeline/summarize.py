"""Stage 6.5: generate audience-friendly TL;DR fields per file.

Reads manifest + extracted text. For each file, fills these fields IF EMPTY:
- tldr             : one-sentence plain-English description
- what_we_know     : list of 3 short bullets
- what_we_dont     : list of 3 short bullets
- mundane_candidate: best non-anomalous explanation, or "none offered"
- score_sentence   : plain-English explanation of the score

These fields can be hand-edited in manifest.json; this stage NEVER overwrites
non-empty values. Designed to be safe to rerun.

Approach: deterministic templates from structured data + extracted text.
No LLM call required (keeps the pipeline reproducible and free). For files
where you want bespoke summaries, edit the manifest by hand.
"""
from __future__ import annotations
import json
import re
from collections import Counter
from pathlib import Path

from .config import MANIFEST_PATH, ROOT, ensure_dirs


STOPWORDS = set("""
the a an and or but of to in for on at by with from as is are was were be been being
this that these those it its their there here which who whom whose what why how
not no nor so if then than such also can may might must should would could
i you he she we they me him her us them our your his their my mine ours yours
about into onto upon over under between within without across through during after before
""".split())


def _top_keywords(text: str, n: int = 8) -> list[str]:
    if not text:
        return []
    words = re.findall(r"[a-zA-Z]{4,}", text.lower())
    counts = Counter(w for w in words if w not in STOPWORDS)
    return [w for w, _ in counts.most_common(n)]


def _agency_blurb(agency: str) -> str:
    return {
        "NASA": "NASA mission record",
        "FBI":  "FBI investigative document",
        "DoD":  "Department of Defense record",
        "STATE":"State Department diplomatic cable",
        "OTHER":"Federal record",
    }.get(agency, "Federal record")


def _category_blurb(cat: str) -> str:
    return {
        "apollo":   "from a crewed lunar mission",
        "fbi":      "from a Bureau case file",
        "military": "from a military encounter report",
        "state":    "from an overseas diplomatic post",
        "composite":"based on a witness reconstruction",
        "other":    "",
    }.get(cat, "")


def _type_blurb(t: str) -> str:
    return {"pdf": "documenting", "video": "showing footage of", "image": "depicting"}.get(t, "describing")


def _build_tldr(f: dict) -> str:
    bits = [_agency_blurb(f.get("agency") or "OTHER")]
    cb = _category_blurb(f.get("category") or "other")
    if cb: bits.append(cb)
    bits.append(_type_blurb(f.get("type") or "pdf"))
    bits.append("a UAP encounter")
    if f.get("date_event"):
        bits.append(f"({f['date_event']})")
    if f.get("geo", {}).get("place"):
        bits.append(f"over {f['geo']['place']}")
    s = " ".join(bits) + "."
    return s[0].upper() + s[1:]


def _build_what_we_know(f: dict, kw: list[str]) -> list[str]:
    known = []
    if f.get("agency"):
        known.append(f"Document originates from {f['agency']}.")
    if f.get("date_event"):
        known.append(f"Encounter dated {f['date_event']}.")
    if f.get("geo", {}).get("place"):
        known.append(f"Reported location: {f['geo']['place']}.")
    if f.get("type") == "video":
        known.append("Sensor footage available; transcript provided.")
    elif f.get("type") == "image":
        known.append("Photographic capture preserved in the original release.")
    if f.get("redacted"):
        known.append("Portions of the document are redacted.")
    while len(known) < 3:
        if kw:
            known.append(f"Document references: {', '.join(kw[:5])}.")
            break
        known.append("Released as part of the PURSUE disclosure batch on May 8, 2026.")
    return known[:3]


def _build_what_we_dont(f: dict) -> list[str]:
    unknown = []
    if not f.get("date_event"):
        unknown.append("Exact date of the encounter is not specified in the released file.")
    if not (f.get("geo") or {}).get("place"):
        unknown.append("Specific geographic coordinates are not disclosed.")
    if f.get("redacted"):
        unknown.append("Redacted portions may contain identifying or technical detail.")
    score = f.get("score") or {}
    if score.get("components", {}).get("kinematic_anomaly") in (None, "no_kinematic_data"):
        unknown.append("No kinematic data (speed, altitude, maneuver) is attached.")
    if score.get("components", {}).get("official_disposition") not in ("resolved_conventional",):
        unknown.append("No official conclusion has been issued classifying the object as conventional.")
    while len(unknown) < 3:
        unknown.append("Independent corroboration from non-government sources has not been confirmed.")
    return unknown[:3]


def _build_mundane(f: dict) -> str:
    comp = (f.get("score") or {}).get("components", {})
    m = comp.get("mundane_explanation_available")
    return {
        "no_plausible_mundane": "None has been formally offered.",
        "weak_mundane_candidate": "A conventional explanation is technically possible but has not been demonstrated.",
        "plausible_mundane": "A conventional explanation (drone, balloon, atmospheric, sensor artifact) plausibly fits the description.",
        "strong_mundane_candidate": "A conventional explanation is the leading working hypothesis.",
        "resolved_mundane": "The encounter has been resolved as a conventional object.",
    }.get(m, "Not assessed in the released file.")


def _build_score_sentence(f: dict) -> str:
    s = f.get("score") or {}
    val = s.get("value")
    if val is None:
        return "Not yet scored."
    detail = s.get("detail") or {}
    if not detail:
        return f"Anomalousness Index {val}/100. Components not specified."
    # Top 2 contributing components
    ranked = sorted(detail.items(), key=lambda kv: kv[1].get("contribution", 0), reverse=True)[:2]
    drivers = ", ".join(f"{k.replace('_',' ')} ({v['choice']})" for k, v in ranked)
    return f"Anomalousness Index {val}/100. Top drivers: {drivers}."


def run() -> None:
    ensure_dirs()
    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for f in manifest["files"]:
        # Pull keywords if extracted text exists
        kw = []
        tp = (f.get("extracted") or {}).get("text_path")
        if tp:
            try:
                kw = _top_keywords((ROOT / tp).read_text(encoding="utf-8", errors="ignore"))
            except FileNotFoundError:
                kw = []
        f.setdefault("audience", {})
        a = f["audience"]
        if not a.get("tldr"):              a["tldr"] = _build_tldr(f)
        if not a.get("what_we_know"):      a["what_we_know"] = _build_what_we_know(f, kw)
        if not a.get("what_we_dont"):      a["what_we_dont"] = _build_what_we_dont(f)
        if not a.get("mundane_candidate"): a["mundane_candidate"] = _build_mundane(f)
        if not a.get("score_sentence"):    a["score_sentence"] = _build_score_sentence(f)
        if kw and not a.get("keywords"):   a["keywords"] = kw
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  audience fields filled for {len(manifest['files'])} files")


if __name__ == "__main__":
    run()
