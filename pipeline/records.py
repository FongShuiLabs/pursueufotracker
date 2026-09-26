"""Record-kind helpers shared by summarize (audience text) and build_site (score copy).

Most of the archive is encounter reports, and the generic per-file text describes an
encounter ("testimony relayed through...", "reported by trained personnel during an
operational mission"). A few record kinds report no observation at all, and that text is
simply false for them. Release 06 was the first to ship them in bulk:

  - the AAWSAP program file (a statement of objectives, a solicitation, five contract
    modifications) and its 37 Defense Intelligence Reference Documents, technical papers
    on topics such as metallic glasses and biosensors
  - the final Navy personnel record of the Tremonton, Utah cameraman

Those get their own honest copy instead of the encounter templates.
"""
from __future__ import annotations


def is_reference_record(f: dict) -> bool:
    """True for program / administrative / reference documents that describe no event."""
    i = f.get("id", "")
    return "aawsap" in i or i.startswith("dow-uap-d104-")


# Display names for the agency codes a reader cannot decode ("LLE", "EOP", "STATE" ...).
# Codes readers already know (DoD, FBI, NASA, CIA, ODNI) are shown as-is, so existing
# pages keep their labels and keywords.
AGENCY_DISPLAY = {
    "STATE": "State Department", "DOE": "Department of Energy", "ICA": "Intelligence Community",
    "USG": "U.S. Government", "EOP": "Executive Office of the President", "LLE": "Local Law Enforcement",
}


def agency_display(code: str) -> str:
    return AGENCY_DISPLAY.get(code or "", code or "")
