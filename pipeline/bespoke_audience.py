"""Kind-specific audience text for records the generic encounter templates would misdescribe.

summarize.py builds every file's TL;DR / what-we-know / what-we-don't from one encounter
template ("... record from a military encounter report documenting a UAP encounter ...",
"No official conclusion has been issued classifying the object as conventional"). For most
of the archive that is fair. Release 06 broke it in two ways:

  1. 45 records report no observation at all: the AAWSAP program file and its 37 technical
     papers (DIRDs), and a Navy personnel record. The template called a paper on metallic
     glasses "a military encounter report".
  2. The Tremonton, Utah file cluster records an OFFICIAL conclusion (Project Blue Book's
     later assessments favored seabirds), so the template's "no official conclusion has
     been issued" bullet would contradict the file's own text on the release's most
     searched pages.

Every sentence below is taken from war.gov's own summary of the record (data/manifest.json
`summary`, i.e. the CSV "Description Blurb") or from the record's title; nothing is inferred.
summarize.py only uses these for EMPTY fields, so a hand edit in manifest.json still wins.
"""
from __future__ import annotations

import re

from .records import is_reference_record

_MONTH = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
_MITIGATION_REDACTED = "Redacted portions may contain identifying or technical detail."
_GENERIC_CORROBORATION = "Independent corroboration from non-government sources has not been confirmed."

_NA_MUNDANE = "Not applicable: this is a reference document, not an encounter report."

_BLUE_BOOK_MUNDANE = (
    "Project Blue Book first considered sunlight reflecting from birds or balloons and a mirage effect, a December 1952 review "
    "found the objects closely resembled pillow balloons in flight, and later Air Force assessments favored seabirds reflecting "
    "sunlight. The film's limited detail prevented a conclusive resolution."
)


def _score_sentence_reference(f: dict) -> str:
    val = (f.get("score") or {}).get("value")
    if val is None:
        return "Not yet scored."
    return (f"Anomalousness Index {val}/100 - the rubric default for a document that reports no encounter, "
            "not a finding about any event.")


def _title_parts(title: str) -> tuple[str, str | None]:
    """'DOW-UAP-D117, AAWSAP DIRD, Metallic Glasses for Aerospace Applications, December 2009'
    -> ('AAWSAP DIRD, Metallic Glasses for Aerospace Applications', 'December 2009')."""
    t = re.sub(r"^[A-Z]+-UAP-[A-Z]*\d+[a-z]?,\s*", "", (title or "").strip())
    m = re.match(rf"^(.+),\s*({_MONTH}\s+\d{{4}})\s*$", t)
    return (m.group(1), m.group(2)) if m else (t, None)


def _dird(f: dict) -> dict:
    head, date = _title_parts(f.get("title", ""))
    topic = re.sub(r"^AAWSAP DIRD,\s*", "", head)
    when = f" ({date})" if date else ""
    what_we_dont = [
        "This is a technical reference paper, not a report of a UAP encounter: it describes no sighting.",
        "War.gov cautions that its summary reflects the paper's scope and framing at the time of writing and does not imply "
        "current validation of the concepts discussed.",
        _MITIGATION_REDACTED if f.get("redacted") else _GENERIC_CORROBORATION,
    ]
    return {
        "tldr": ("Defense Intelligence Reference Document (DIRD) from the Defense Intelligence Agency's AAWSAP program: "
                 f"a technical reference paper, \"{topic}\"{when}."),
        "what_we_know": [
            "Produced under AAWSAP (the Advanced Aerospace Weapon System Applications Program), a Defense Intelligence Agency "
            "program that war.gov says was active from 2008 to 2012.",
            "War.gov describes DIRDs as reference and synthesis products rather than original research, and describes each as "
            "one of 38 DIRDs produced between 2009 and 2011. The CSV contains 37, all released together in Release 06.",
            "War.gov notes that not every DIRD in the series directly concerns aerospace systems or future threat assessment.",
        ],
        "what_we_dont": what_we_dont,
        "mundane_candidate": _NA_MUNDANE,
        "score_sentence": _score_sentence_reference(f),
    }


def _aawsap_admin(f: dict) -> dict:
    head, date = _title_parts(f.get("title", ""))
    when = f", {date}" if date else ""
    return {
        "tldr": f"Administrative record from the Defense Intelligence Agency's AAWSAP program: {head}{when}.",
        "what_we_know": [
            "War.gov describes AAWSAP as a Defense Intelligence Agency-administered program active from 2008 to 2012.",
            "Its official scope of work identified 12 technical research areas relating to potential aerospace threats over a "
            "time horizon of more than 40 years.",
            "As an administrative record, the file documents how AAWSAP was scoped, organized, tasked, funded, or described at "
            "a particular point in time.",
        ],
        "what_we_dont": [
            "This is a contract or programmatic record, not a report of a UAP encounter: it describes no sighting.",
            "It shows how the program was structured, not what its research found; the technical papers (DIRDs) are separate "
            "records in the same release.",
            _MITIGATION_REDACTED if f.get("redacted") else _GENERIC_CORROBORATION,
        ],
        "mundane_candidate": _NA_MUNDANE,
        "score_sentence": _score_sentence_reference(f),
    }


def _newhouse_personnel(f: dict) -> dict:
    return {
        "tldr": ("Final U.S. Navy personnel record of Chief Warrant Officer Delbert C. Newhouse, who filmed the objects near "
                 "Tremonton, Utah in July 1952."),
        "what_we_know": [
            "He left naval service as a Chief Warrant Officer 4, then the highest Warrant Officer grade.",
            "The record shows his career as a Photographer's Mate, a Navy enlisted specialty responsible for photography and "
            "related imaging work.",
            "Project Blue Book investigators characterized him as an expert photographer based on his naval experience.",
        ],
        "what_we_dont": [
            "This is a personnel record, not a report of a sighting: it documents the witness's background, not the objects "
            "he filmed.",
            "Photographic expertise bears on how reliable a witness is, not on what the objects were.",
            _GENERIC_CORROBORATION,
        ],
        "mundane_candidate": _NA_MUNDANE,
        "score_sentence": _score_sentence_reference(f),
    }


def _tremonton_film(f: dict) -> dict:
    return {
        "tldr": ("Digitized 16mm color film of a group of bright objects shot near Tremonton, Utah on July 2, 1952 by U.S. Navy "
                 "Chief Warrant Officer Delbert C. Newhouse, later reviewed by Project Blue Book."),
        "what_we_know": [
            "Shot on a handheld Bell & Howell Auto Master camera near Tremonton, Utah, and submitted to the U.S. Air Force by "
            "Newhouse, who reported observing and filming the objects.",
            "Project Blue Book's later assessments favored seabirds reflecting sunlight (DOW-UAP-D102); the Navy's Photographic "
            "Interpretation Center read the objects differently (DOW-UAP-D098).",
            "War.gov notes that from the 55-second mark the film shows unrelated footage that appears to be a demonstration of "
            "sewing equipment.",
        ],
        "what_we_dont": [
            "The film's limited detail and lack of fixed reference points prevented a conclusive resolution.",
            "How and when the sewing-equipment footage came to be combined with the Tremonton film is not established by the "
            "available record.",
            "Records submitted with the film say it was originally paired with mountain scenery from Idaho, which is not "
            "preserved in this digitization.",
        ],
        "mundane_candidate": _BLUE_BOOK_MUNDANE,
    }


def _tremonton_bluebook_file(f: dict) -> dict:
    return {
        "tldr": ("Project Blue Book's file on the July 2, 1952 Tremonton, Utah film: the Air Force's assessment of the witness and "
                 "its explanations of the objects over several years."),
        "what_we_know": [
            "The Air Force assessed the witness, Navy Warrant Officer Delbert C. Newhouse, a photographer, as honest and "
            "reliable, with more than 1,000 hours of aerial-photography experience.",
            "He reported 12 to 14 reflective objects and filmed them on color film. Early documents considered birds, balloons "
            "and a mirage; later assessments were more confident the objects were seabirds reflecting sunlight.",
            "War.gov's AARO comment notes the file conflicts on the film format (35mm versus 16mm): the original was a 50-foot "
            "roll of 16mm Kodachrome, and the footage in the National Archives (DOW-UAP-PR159) digitizes a 16mm print.",
        ],
        "what_we_dont": [
            "The film's limited detail and lack of fixed reference points prevented reliable determination of the objects' "
            "distance, size, altitude, or speed from the film alone.",
            "The seabird conclusion is an Air Force assessment based on comparison with similar films; the Navy's Photographic "
            "Interpretation Center generally assessed the objects it analyzed (DOW-UAP-D098) as inconsistent with natural "
            "phenomena or commonly known aerospace technologies.",
            "Efforts to identify a pillow-balloon release in the Tremonton area were unsuccessful (DOW-UAP-D103).",
        ],
        "mundane_candidate": _BLUE_BOOK_MUNDANE,
    }


def _tremonton_photo_file(f: dict) -> dict:
    return {
        "tldr": ("Project Blue Book's photo file on the Tremonton film, documenting a December 1952 check of whether the objects "
                 "were General Mills \"pillow balloons.\""),
        "what_we_know": [
            "In December 1952 investigators contacted General Mills, Inc., then the only known manufacturer of pillow balloons, "
            "to ask whether a balloon release could account for the incident.",
            "In late December 1952 Blue Book personnel, balloon specialists and General Mills representatives reviewed the "
            "footage; the consensus was that the objects closely resembled pillow balloons in flight.",
            "One General Mills representative was less convinced, noting the objects appeared somewhat too bright and seemed "
            "to maneuver too rapidly.",
        ],
        "what_we_dont": [
            "Efforts to identify a pillow-balloon release in the Tremonton area were unsuccessful.",
            "The reviewers questioned earlier high-speed calculations because they depended on the unverified assumption that "
            "the camera operator held the camera still.",
            "Later Air Force assessments favored seabirds rather than balloons.",
        ],
        "mundane_candidate": _BLUE_BOOK_MUNDANE,
    }


def _flying_discs_file(f: dict) -> dict:
    return {
        "tldr": ("U.S. Air Force Director of Intelligence collection of \"flying disc\" reporting from September to December "
                 "1952, including pages on the Tremonton, Utah film."),
        "what_we_know": [
            "War.gov describes it as an archival collection of correspondence, memoranda, reporting forms, case summaries and "
            "routing material drawn from multiple governmental and non-governmental sources.",
            "Pages 26-36 refer to the July 1952 Tremonton incident, in which a Navy Warrant Officer filmed unidentified objects "
            "that the Air Force later assessed were likely seabirds.",
            "Overall it reflects how such reports were recorded, circulated, and evaluated in late 1952.",
        ],
        "what_we_dont": [
            "It does not present a single analytical conclusion on the nature or origin of \"flying discs.\"",
            "The collection spans many reports; pages 26-36 are the portion war.gov identifies as relating to Tremonton.",
            _GENERIC_CORROBORATION,
        ],
        "mundane_candidate": ("Not applicable to the collection as a whole. For the Tremonton pages, the Air Force later assessed "
                              "the objects were likely seabirds."),
    }


def _ruppelt(f: dict) -> dict:
    audio = f.get("type") == "video"  # audio recordings are stored as type "video"
    what = "Audio recording" if audio else "Transcript"
    return {
        "tldr": (f"{what} of a March 1952 presentation by Captain Edward J. Ruppelt outlining the U.S. Air Force's reorganized "
                 "investigation into unidentified flying objects."),
        "what_we_know": [
            "War.gov lists Boston, Massachusetts as the location and March 1952 as the date.",
            "Ruppelt previews prospective technical methods, such as diffraction-grating photography and radar-scope "
            "synchronization, that were later incorporated into Project Blue Book, the Air Force program active from 1952 to 1969.",
            ("A transcript of the presentation is released alongside as DOW-UAP-D154." if audio
             else "The audio recording of the presentation is released alongside as DOW-UAP-PR160."),
        ],
        "what_we_dont": [
            "War.gov describes the presentation as an outline of the reorganized investigation and its planned methods, not a "
            "report of a specific sighting.",
            "Whether the previewed methods worked as described is not addressed in war.gov's summary.",
            _GENERIC_CORROBORATION,
        ],
        "mundane_candidate": "Not applicable: this is a briefing about investigation methods, not a report of a sighting.",
    }


# id prefix -> builder. Prefixes are unique in the manifest (checked at build time by the
# post-ingest guard: every listed prefix must match exactly one file).
_BY_PREFIX = {
    "dow-uap-pr159-": _tremonton_film,
    "dow-uap-d102-": _tremonton_bluebook_file,
    "dow-uap-d103-": _tremonton_photo_file,
    "dow-uap-d104-": _newhouse_personnel,
    "dow-uap-d105-": _flying_discs_file,
    "dow-uap-pr160-": _ruppelt,
    "dow-uap-d154-": _ruppelt,
}


def bespoke(f: dict) -> dict | None:
    """Audience fields for this file, or None to use the generic encounter template."""
    i = f.get("id", "")
    for prefix, build in _BY_PREFIX.items():
        if i.startswith(prefix):
            return build(f)
    if "aawsap-dird" in i:
        return _dird(f)
    if "aawsap" in i and is_reference_record(f):
        return _aawsap_admin(f)
    return None
