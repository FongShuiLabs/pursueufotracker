"""Stamp the archive's headline numbers into the hand-authored pages that show them.

Why this exists: a few hand-authored pages state archive totals as BARE NUMBERS
in stat tiles and headings, not in sentences. Three consecutive drop sweeps
searched for phrases ("334 files") and missed them, so these went stale:

  index.html            hero tiles: 334 / 189 / 118 / 27 / 190 - still the Drop 04
                        values a full release after the archive reached 375
  /pursue-program       stat row and agency headings: "334 total files" beside agency
                        counts that summed to 294 (DoD 143, FBI 86 ... Drop 03 values)
  /timeline             "334 total files"

The builders never touch these files, so nothing rebuilt them. This stage rewrites
just those numbers from data/manifest.json on every run (idempotent), and
`preflight check-counts` fails the pre-push gate if any of them is stale or its
markup was reworded out from under the pattern.

Prose that narrates a release ("Release 06 added ...") is NOT stamped here: that is
editorial and stays hand-written. Only totals derived from the manifest are, plus the
homepage's release list (the hero sentence, the newest-release banners, the latest-release
chip, the footer and the release-history FAQ answer), which is generated from
data/drops.json. That list had to be hand-edited every drop and was still showing
"DROP 04" and "334 files now indexed" two releases later (found 2026-09-26).

Runs AFTER the page builders (see pipeline/run.py), so it also corrects any count a
builder wrote and sees the final state of every page it checks.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter

from .config import MANIFEST_PATH, ROOT

DROPS_PATH = ROOT / "data" / "drops.json"
MIRROR_PATH = ROOT / "data" / "uap-data.csv"

# (page, [ (description, regex, builder(values) -> replacement) ])
# Each regex must match EXACTLY once; anything else is reported as a miss.


def _mirror() -> tuple[int | None, str | None]:
    """Row count and SHA-256 of the mirrored data/uap-data.csv, or (None, None)."""
    if not MIRROR_PATH.exists():
        return None, None
    raw = MIRROR_PATH.read_bytes()
    rows = sum(1 for _ in csv.DictReader(io.StringIO(raw.decode("utf-8-sig", errors="replace"))))
    return rows, hashlib.sha256(raw).hexdigest()


def _hub_counts(files: list[dict]) -> dict[str, int]:
    """File count per category hub, using the hubs' own match rules."""
    from .build_categories import CATEGORIES
    out = {}
    for c in CATEGORIES:
        n = 0
        for f in files:
            try:
                n += bool(c["match"](f))
            except Exception:
                pass
        out[c["slug"]] = n
    return out


def _drops_list() -> list[dict]:
    try:
        d = json.loads(DROPS_PATH.read_text(encoding="utf-8"))
        return sorted(d["drops"] if isinstance(d, dict) else d, key=lambda x: x["date"])
    except Exception:
        return []


def _values(files: list[dict], n_drops: int) -> dict:
    by_type = Counter(f.get("type") for f in files)
    by_ag = Counter(f.get("agency") for f in files)
    total = len(files)
    named = sum(by_ag[a] for a in ("DoD", "FBI", "NASA", "CIA", "STATE"))
    mirror_rows, mirror_sha = _mirror()
    return {
        "mirror_rows": mirror_rows, "mirror_sha": mirror_sha,
        "total": total,
        "pdf": by_type["pdf"], "video": by_type["video"], "image": by_type["image"],
        "redacted": sum(1 for f in files if f.get("redacted")),
        "sha": sum(1 for f in files if f.get("sha256")),
        "DoD": by_ag["DoD"], "FBI": by_ag["FBI"], "NASA": by_ag["NASA"],
        "CIA": by_ag["CIA"], "STATE": by_ag["STATE"],
        "other": total - named,
        "drops": n_drops,
        "drops_list": _drops_list(),
        "hubs": _hub_counts(files),
    }


def _tile(label: str, key):
    """index.html hero tile: <span class="stat-num">N</span><span class="stat-label">LABEL</span>"""
    pat = (r'(<span class="stat-num">)[^<]*(?:<small>[^<]*</small>)?'
           r'(</span><span class="stat-label">' + re.escape(label) + r'</span>)')

    def build(v):
        inner = key(v) if callable(key) else str(v[key])
        return lambda m: f"{m.group(1)}{inner}{m.group(2)}"
    return (f"hero tile '{label}'", pat, build)


def _stat_row(label_regex: str, key, new_label=None):
    """/pursue-program stat row: <span class="n">N</span><span class="l">LABEL</span>"""
    pat = r'(<span class="n">)\d+(</span><span class="l">)(' + label_regex + r')(</span>)'

    def build(v):
        val = str(v[key])
        return lambda m: f"{m.group(1)}{val}{m.group(2)}{new_label(v) if new_label else m.group(3)}{m.group(4)}"
    return (f"stat row '{label_regex}'", pat, build)


def _heading(text_before: str, key):
    """<h3>Department of State (7 files)</h3> -> the count in parentheses."""
    pat = r'(<h3>' + re.escape(text_before) + r' \()\d+( files\)</h3>)'

    def build(v):
        return lambda m: f"{m.group(1)}{v[key]}{m.group(2)}"
    return (f"heading '{text_before}'", pat, build)


def _strong(suffix: str, key):
    """<strong>189 PDFs</strong>"""
    pat = r'(<strong>)\d+( ' + re.escape(suffix) + r'</strong>)'

    def build(v):
        return lambda m: f"{m.group(1)}{v[key]}{m.group(2)}"
    return (f"inline '{suffix}'", pat, build)


_MON = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
_MONTH = ("January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December")
_WORD = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
         "ten", "eleven", "twelve")
_AG_LABEL = {"DoD": "DoD", "FBI": "FBI", "NASA": "NASA", "CIA": "CIA", "STATE": "State Dept",
             "EOP": "Executive Office of the President", "LLE": "local law enforcement",
             "DOE": "DOE", "ODNI": "ODNI", "ICA": "Intelligence Community", "USG": "U.S. Government"}
RELEASES_START = ("<!-- releases:start (managed by pipeline/stamp_counts.py from data/drops.json "
                  "- do not hand-edit) -->")
RELEASES_END = "<!-- releases:end -->"


def _ymd(iso: str) -> tuple[int, int, int]:
    y, m, d = (int(x) for x in iso.split("-"))
    return y, m, d


def _long(iso: str, year: bool = True) -> str:
    y, m, d = _ymd(iso)
    return f"{_MONTH[m - 1]} {d}, {y}" if year else f"{_MONTH[m - 1]} {d}"


def _slug(dr: dict) -> str:
    return f"/drops/{dr['date']}-drop-{dr['number']:02d}"


def _releases_block(v: dict) -> str | None:
    """Hero sentence + the three newest release banners + links to the older ones."""
    drops = v["drops_list"]
    if not drops:
        return None
    first, last, n = drops[0], drops[-1], len(drops)
    word = _WORD[n] if n < len(_WORD) else str(n)
    same_year = first["date"][:4] == last["date"][:4]
    span = (f"from {_long(first['date'], year=False)} to {_long(last['date'])}" if same_year
            else f"from {_long(first['date'])} to {_long(last['date'])}")
    verified = ("indexed, scored, and SHA-256 verified" if v["sha"] == v["total"]
                else f"indexed and scored ({v['sha']} SHA-256 verified so far)")
    out = [RELEASES_START,
           f'  <p class="hero-lede">The independent tracker of every UFO file the Trump administration '
           f'declassifies through PURSUE: {word} releases so far, {span}. '
           f'<strong style="color:#ffffff">{v["total"]} files now {verified}</strong>. Each new release '
           f'is added here once its files are downloaded and verified.</p>',
           ""]
    newest = list(reversed(drops))
    for i, dr in enumerate(newest[:3]):
        ags = ", ".join(_AG_LABEL.get(a, a) for a in dr.get("agencies", []))
        if i == 0:
            style = ("border-color:rgba(82,180,255,.5);background:linear-gradient(120deg,"
                     "rgba(255,87,87,.08),rgba(82,180,255,.14))")
            files, status = f"{dr['file_count']} new files", "NEWEST · Indexed"
        else:
            style = ("margin-top:12px;border-color:rgba(82,180,255,.3);background:linear-gradient(120deg,"
                     "rgba(82,180,255,.08),rgba(82,180,255,.03))")
            files, status = f"{dr['file_count']} files", "LIVE · Indexed"
        out += [f'  <div class="drop-banner" style="{style}">',
                f'    <div class="drop-tag" style="background:#52b4ff">DROP {dr["number"]:02d}</div>',
                '    <div class="drop-info">',
                f'      <strong>{_long(dr["date"])}</strong> · {files} · {ags}',
                f'      <span class="drop-status">{status}</span>',
                '    </div>',
                f'    <a href="{_slug(dr)}" class="drop-link">View drop →</a>',
                '  </div>']
    older = newest[3:]
    if older:
        links = " · ".join(
            f'<a href="{_slug(dr)}" style="color:#52b4ff;text-decoration:none">Drop {dr["number"]:02d} '
            f'({_long(dr["date"])}, {dr["file_count"]} files)</a>' for dr in older)
        out.append(f'  <p style="max-width:900px;margin:12px auto 0;text-align:center;font-size:13px;'
                   f'color:#a8b8cc">Earlier releases: {links} · <a href="/drops" style="color:#52b4ff;'
                   f'text-decoration:none">All releases →</a></p>')
    out.append("  " + RELEASES_END)
    return "\n".join(out)


def _history_answer(v: dict) -> str | None:
    """Plain-text release history for the homepage FAQPage JSON-LD (contains no double quotes)."""
    drops = v["drops_list"]
    if not drops:
        return None
    parts, running = [], 0
    for i, dr in enumerate(drops):
        running += dr["file_count"]
        if i == 0:
            parts.append(f"Release {dr['number']:02d} went live on {_long(dr['date'])}, with "
                         f"{dr['file_count']} files at war.gov/UFO.")
        elif i < len(drops) - 1:
            parts.append(f"Release {dr['number']:02d} followed on {_long(dr['date'])}, adding "
                         f"{dr['file_count']} more ({running} total).")
        else:
            parts.append(f"Release {dr['number']:02d} followed on {_long(dr['date'])}, adding "
                         f"{dr['file_count']} more, for {running} files total.")
    parts.append("Additional files release on a rolling basis.")
    return " ".join(parts)


def _keep_or(fn):
    """TARGETS builder whose replacement text comes from fn(vals); leaves the match as-is
    when fn has nothing to say (no drops.json)."""
    def build(v):
        val = fn(v)
        return lambda m: m.group(0) if val is None else f"{m.group(1)}{val}{m.group(2)}"
    return build


def _chip(v):
    if not v["drops_list"]:
        return None
    last = v["drops_list"][-1]
    y, mo, d = _ymd(last["date"])
    return f"LATEST RELEASE: DROP {last['number']:02d} · {d} {_MON[mo - 1]} {y}"


def _footer(v):
    if not v["drops_list"]:
        return None
    last = v["drops_list"][-1]
    return f"Last new release: {_long(last['date'])} (Drop {last['number']:02d})"


def _block_repl(v):
    block = _releases_block(v)
    return lambda m: m.group(0) if block is None else block


def _hub_link(slug: str):
    """Homepage 'Browse by agency' button: <a href="/SLUG/" ...>... <span ...>(N)</span></a>.
    They sat at Drop 03-04 values ("Intel + DOE (6)" beside a 17-file hub) until 2026-09-26."""
    pat = (r'(<a href="/' + re.escape(slug) + r'/"[^>]*>(?:(?!</a>).)*?<span style="color:#7a92b0">\()\d+'
           r'(\)</span></a>)')
    return (f"homepage hub button '{slug}'", pat,
            lambda v: (lambda m: f"{m.group(1)}{v['hubs'][slug]}{m.group(2)}"))


def _hub_links() -> list:
    from .build_categories import CATEGORIES
    return [_hub_link(c["slug"]) for c in CATEGORIES]


TARGETS = {
    "index.html": [
        ("homepage release block (hero sentence + banners)",
         r"(?s)" + re.escape(RELEASES_START) + r".*?" + re.escape("  " + RELEASES_END), _block_repl),
        ("latest-release chip", r'(<span class="date-stamp" id="latest-release"[^>]*>)[^<]*(</span>)',
         _keep_or(_chip)),
        ("footer last-new-release", r'(<span id="last-new-release">)[^<]*(</span>)', _keep_or(_footer)),
        ("FAQPage JSON-LD release history",
         r'("name":"When did the Trump administration release the UFO files\?","acceptedAnswer":'
         r'\{"@type":"Answer","text":")[^"]*(")', _keep_or(_history_answer)),
        ("videos FAQ count", r"(\(28 in Drop 01; )\d+( in the archive today\))",
         lambda v: (lambda m: f"{m.group(1)}{v['video']}{m.group(2)}")),
        ("release box verified count", r"(SHA-256 verified against war\.gov \()\d+ of \d+(\))",
         lambda v: (lambda m: f"{m.group(1)}{v['sha']} of {v['total']}{m.group(2)}")),
        _tile("Files indexed", "total"),
        _tile("Documents", "pdf"),
        _tile("Videos", "video"),
        _tile("Images", "image"),
        _tile("Redacted", "redacted"),
        _tile("SHA-256 verified", lambda v: f"{v['sha']}<small>/{v['total']}</small>"),
    ],
    "generated/pursue-program.html": [
        ("files released so far", r"(<strong>Files released so far:</strong> )\d+ across \w+( releases)",
         lambda v: (lambda m: f"{m.group(1)}{v['total']} across "
                              f"{_WORD[len(v['drops_list'])] if len(v['drops_list']) < len(_WORD) else len(v['drops_list'])}"
                              f"{m.group(2)}")),
        _stat_row(r"Total files \(R01-R0\d\)", "total",
                  new_label=lambda v: f"Total files (R01-R{v['drops']:02d})"),
        _stat_row("DoD", "DoD"),
        _stat_row("FBI", "FBI"),
        _stat_row("NASA", "NASA"),
        _stat_row("CIA", "CIA"),
        _stat_row("State Dept", "STATE"),
        _stat_row(r"ODNI \+ DOE \+ other", "other"),
        _strong("PDFs", "pdf"),
        _strong("videos", "video"),
        _strong("image files", "image"),
        _heading("Department of War / DoD", "DoD"),
        _heading("Central Intelligence Agency", "CIA"),
        _heading("ODNI, DOE, and other federal records", "other"),
        _heading("Federal Bureau of Investigation", "FBI"),
        _heading("National Aeronautics and Space Administration", "NASA"),
        _heading("Department of State", "STATE"),
    ],
    "generated/api.html": [
        ("files.json count", r"(All )\d+( files with title, agency)",
         lambda v: (lambda m: f"{m.group(1)}{v['total']}{m.group(2)}")),
        ("per-file endpoint count", r"(<strong>Count:</strong> )\d+( endpoints)",
         lambda v: (lambda m: f"{m.group(1)}{v['total']}{m.group(2)}")),
        ("timeline count", r"(Chronological ordering of all )\d+( files)",
         lambda v: (lambda m: f"{m.group(1)}{v['total']}{m.group(2)}")),
        ("video sitemap count", r"(the video sitemap \()\d+( video files)",
         lambda v: (lambda m: f"{m.group(1)}{v['video']}{m.group(2)}")),
    ],
    "generated/verify.html": [
        ("verify page composition",
         r"(Every one of the )\d+( files in this archive - all )\d+( documents, )\d+( videos, and )\d+( images)",
         lambda v: (lambda m: f"{m.group(1)}{v['total']}{m.group(2)}{v['pdf']}{m.group(3)}{v['video']}{m.group(4)}{v['image']}{m.group(5)}")),
    ],
    "generated/timeline.html": [
        ("timeline total", r'(<span><strong>)\d+(</strong> total files</span>)',
         lambda v: (lambda m: f"{m.group(1)}{v['total']}{m.group(2)}")),
    ],
    # The mirror page's row count and hash come from data/uap-data.csv itself, so the
    # page can never advertise a hash the mirror does not have (2026-09-20: it still
    # showed the Release 04 hash beside "375 rows" after the mirror moved on).
    "generated/uap-data-csv.html": [
        ("mirror row count", r'(<strong>)\d+( rows</strong> · text/csv)',
         lambda v: (lambda m: m.group(0) if v['mirror_rows'] is None
                            else f"{m.group(1)}{v['mirror_rows']}{m.group(2)}")),
        ("mirror sha256", r'(SHA-256: <span style="word-break:break-all">)[0-9a-f]{64}(</span>)',
         lambda v: (lambda m: m.group(0) if v['mirror_sha'] is None
                            else f"{m.group(1)}{v['mirror_sha']}{m.group(2)}")),
    ],
}


# Recurring nav/CTA phrases that state the archive total. ~50 hand-authored essays
# carry the footer link "Search All 375 Files" and ~110 orphaned old-slug file pages
# still said "BROWSE ALL 294 FILES" (Release 03) two releases later: every drop's
# hand sweep missed some of them. These are pure counts inside fixed phrases, so they
# are stamped everywhere they occur (any number of times per page, unlike TARGETS).
# Historical statements ("all 161 files" of Release 01) deliberately do NOT match.
GLOBAL_RULES = [
    ("footer 'Search All N Files'", r"(Search All )\d{3}( Files)", "total"),
    ("'BROWSE ALL N FILES'", r"(BROWSE ALL )\d{3}( FILES)", "total"),
    ("'All N indexed files'", r"(All )\d{3}( indexed files)", "total"),
    ("'Browse all N indexed Trump UFO files'", r"(Browse all )\d{3}( indexed Trump UFO files)", "total"),
    ("homepage 'Search all N files'", r"(<strong[^>]*>Search</strong> all )\d{3}( files)", "total"),
    ("'across all N Trump PURSUE UAP files'", r"(across all )\d{3}( Trump PURSUE UAP files)", "total"),
    ("'across all N PURSUE files'", r"(across all )\d{3}( PURSUE files)", "total"),
    ("'browse all N files'", r"(browse all )\d{3}( files)", "total"),
    ("'Every one of the N Trump PURSUE UFO files'", r"(Every one of the )\d{3}( Trump PURSUE UFO files)", "total"),
    ("'It lists all N files'", r"(It lists all )\d{3}( files)", "total"),
    ("'the N-file combined archive'", r"(the )\d{3}(-file combined archive)", "total"),
    ("'All N released files are searchable'", r"(All )\d{3}( released files are searchable)", "total"),
    ("'None of the N files'", r"(None of the )\d{3}( files)", "total"),
    ("'ALL N FILES SHA-256 VERIFIED'", r"(ALL )\d{3}( FILES SHA-256 VERIFIED)", "total"),
    ("'All N files as JSON'", r"(All )\d{3}( files as JSON)", "total"),
    ("'any of the N mirrored files'", r"(any of the )\d{3}( mirrored files)", "total"),
    ("'What all N files do and do not prove'", r"(What all )\d{3}( files do and do not prove)", "total"),
    ("'Of the N files the Trump administration has released'",
     r"(Of the )\d{3}( files the Trump administration has released)", "total"),
    # Per-agency "see all N X files" links on the essays (the CIA ones sat at 21 after CIA reached 23).
    ("'all N CIA files'", r"([Aa]ll )\d{2,3}( CIA files)", "CIA"),
    ("'all N FBI files'", r"([Aa]ll )\d{2,3}( FBI files)", "FBI"),
]
GLOBAL_DIRS = [
    ROOT,
    ROOT / "generated",
    ROOT / "generated" / "files",
    ROOT / "generated" / "categories",
    ROOT / "generated" / "drops",
]


def _sweep_global(vals: dict, write: bool) -> list[str]:
    """Apply GLOBAL_RULES to every *.html in GLOBAL_DIRS. Returns the changed paths
    (relative to ROOT). With write=False nothing is modified (used by the guard)."""
    changed: list[str] = []
    for d in GLOBAL_DIRS:
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.html")):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue  # never rewrite a page we cannot decode losslessly
            new = text
            for _desc, pat, key in GLOBAL_RULES:
                n = vals[key]
                new = re.sub(pat, lambda m, n=n: f"{m.group(1)}{n}{m.group(2)}", new)
            if new != text:
                changed.append(str(path.relative_to(ROOT)).replace("\\", "/"))
                if write:
                    path.write_text(new, encoding="utf-8")
    return changed


TARGETS["index.html"] += _hub_links()


def _load() -> tuple[list[dict], int]:
    files = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["files"]
    try:
        d = json.loads(DROPS_PATH.read_text(encoding="utf-8"))
        n = len(d["drops"] if isinstance(d, dict) else d)
    except Exception:
        n = 0
    return files, n


def _apply(text: str, rules, vals: dict) -> tuple[str, list[str]]:
    misses = []
    for desc, pat, build in rules:
        new, n = re.subn(pat, build(vals), text, count=0)
        if n != 1:
            misses.append(f"{desc}: pattern matched {n}x (want exactly 1)")
            continue
        text = new
    return text, misses


def stale(files: list[dict] | None = None, n_drops: int | None = None) -> list[str]:
    """Problems that `run()` would fix or cannot fix. Empty list = all current.
    Used by preflight so a stale or reworded tile hard-fails the pre-push gate."""
    if files is None:
        files, n = _load()
        n_drops = n if n_drops is None else n_drops
    vals = _values(files, n_drops or 0)
    out: list[str] = []
    for rel, rules in TARGETS.items():
        path = ROOT / rel
        if not path.exists():
            out.append(f"{rel}: file missing")
            continue
        text = path.read_text(encoding="utf-8")
        new, misses = _apply(text, rules, vals)
        out += [f"{rel}: {m} - the markup changed; re-anchor it in stamp_counts.TARGETS"
                for m in misses]
        if new != text:
            out.append(f"{rel}: headline numbers are stale vs the manifest "
                       f"(run `python -m pipeline.run stamp-counts`)")
    lagging = _sweep_global(vals, write=False)
    if lagging:
        out.append(f"{len(lagging)} page(s) carry a stale archive-total nav phrase "
                   f"(e.g. 'Search All N Files'; first: {', '.join(lagging[:3])}) - "
                   f"run `python -m pipeline.run stamp-counts`")
    return out


def run() -> None:
    files, n_drops = _load()
    vals = _values(files, n_drops)
    print(f"  manifest: total={vals['total']} pdf={vals['pdf']} video={vals['video']} "
          f"image={vals['image']} redacted={vals['redacted']} sha256={vals['sha']} "
          f"| DoD={vals['DoD']} FBI={vals['FBI']} NASA={vals['NASA']} CIA={vals['CIA']} "
          f"STATE={vals['STATE']} other={vals['other']} | releases={n_drops}")
    for rel, rules in TARGETS.items():
        path = ROOT / rel
        if not path.exists():
            print(f"  WARN {rel}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        new, misses = _apply(text, rules, vals)
        for m in misses:
            # Loud but non-fatal here: a hard stop mid-ingest would strand a drop.
            # The pre-push guard (check-counts) is the hard gate.
            print(f"  WARN {rel}: {m}")
        if new != text:
            path.write_text(new, encoding="utf-8")
            print(f"  stamped {rel}")
        else:
            print(f"  ok      {rel} (already current)")
    changed = _sweep_global(vals, write=True)
    print(f"  nav-phrase sweep: {len(changed)} page(s) updated to {vals['total']} files")


if __name__ == "__main__":
    run()
