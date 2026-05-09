"""Stage 6: compute the Anomalousness Index for every file.

Reads data/scoring-rubric.json. If a manifest entry has a `score.components`
dict referencing rubric keys, computes the weighted sum. If not, attempts
to use a preset matching the file id; falls back to a neutral score with
explicit `unscored: true` flag.
"""
from __future__ import annotations
import json
from pathlib import Path

from .config import MANIFEST_PATH, RUBRIC_PATH, ensure_dirs


def _load_rubric() -> dict:
    return json.loads(RUBRIC_PATH.read_text(encoding="utf-8"))


def _score_from_components(components: dict[str, str], rubric: dict) -> tuple[int, dict]:
    total = 0.0
    detail = {}
    for cname, cdef in rubric["components"].items():
        chosen = components.get(cname)
        if chosen and chosen in cdef["scale"]:
            v = cdef["scale"][chosen]
        else:
            v = 50  # neutral default if unspecified
            chosen = chosen or "(unspecified)"
        contribution = v * cdef["weight"]
        total += contribution
        detail[cname] = {"choice": chosen, "value": v, "weight": cdef["weight"], "contribution": round(contribution, 2)}
    return max(0, min(100, round(total))), detail


def run() -> None:
    ensure_dirs()
    if not MANIFEST_PATH.exists() or not RUBRIC_PATH.exists():
        print("  (need manifest + rubric)")
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    rubric = _load_rubric()
    presets = rubric.get("presets", {})
    manifest["rubric_version"] = rubric["version"]

    for f in manifest["files"]:
        existing = f.get("score") or {}
        components = existing.get("components")
        if not components:
            preset = presets.get(f["id"])
            if preset:
                components = preset
            else:
                f["score"] = {
                    "value": 50,
                    "components": {},
                    "rubric_version": rubric["version"],
                    "unscored": True,
                    "note": "no rubric components or preset; neutral placeholder",
                }
                continue
        value, detail = _score_from_components(components, rubric)
        f["score"] = {
            "value": value,
            "components": components,
            "detail": detail,
            "rubric_version": rubric["version"],
        }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  scored {len(manifest['files'])} files")


if __name__ == "__main__":
    run()
