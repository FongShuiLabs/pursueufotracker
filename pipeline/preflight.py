"""Drop-ingest and pre-push guards. Encodes the 2026-07-11/12 Drop 04 lessons
so the next drop cannot silently repeat them.

Three subcommands, run at three moments:

  python -m pipeline.preflight pre-ingest
      BEFORE `pipeline.run all` on a real drop. Fetches a verified-fresh CSV
      via poll_wargov's tested curl_cffi path, writes it to _scratch/uap-csv.csv,
      and confirms its SHA-256 matches what the poller recorded in
      data/poll-state.json. Guards against: parse-csv silently ingesting a
      stale/wrong-schema local scratch file (the "294 entries" incident).

  python -m pipeline.preflight post-ingest
      AFTER the pipeline finishes, BEFORE trusting/committing the result.
      Diffs data/manifest.json against the last committed version. Hard-fails
      on: previously-live file ids missing (the 196-renamed-ids incident),
      OTHER-agency junk entries (the 166-junk-pages incident), or a video
      count that shrank (the 118->10 dict-collision incident).

  python -m pipeline.preflight pre-push
      BEFORE `git push`. Hard-fails if any file staged/committed at HEAD
      exceeds Cloudflare Pages' 25 MiB limit (the "No deployment available"
      incident), warns if _redirects is near the ~100-rule effective ceiling,
      re-verifies the served CSV mirror blob is byte-exact vs poll-state, and
      hard-fails on cluster/score-band count drift (see check-counts).

  python -m pipeline.preflight check-counts
      Recomputes every TOPIC_PAGES cluster size (vs its live match lambda) and
      the score-band totals in EXPECTED_SCORE_BANDS (vs the manifest), and fails
      on any drift, naming the prose to update. Guards against the 2026-07-16
      Drop 04 incident: "four files tied at 72" (really eight), "78 at 66"
      (really 92), and five stale cluster sizes. Also cross-checks every
      hardcoded deep-dive count against generated/deep-dives.html (the
      2026-08-06 incident: the homepage claimed both 33 and 36 in two places,
      the file-page sidebar 36 and the category sidebar 30, against a real 35).
      Also validates 17 llms.txt claims against the manifest, the built
      sitemaps and drops.json (the 2026-08-08 incident: llms.txt was still
      describing the Drop-01 archive three drops later). A drop breaks all
      of them at once - see DROP_REACTION.md step 7b.
      Runs as a warning in post-ingest and a hard gate in pre-push.

Exit code 0 = safe to proceed. Non-zero = stop and read the output.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data" / "manifest.json"
POLL_STATE = ROOT / "data" / "poll-state.json"
REDIRECTS = ROOT / "_redirects"
CF_LIMIT = 25 * 1024 * 1024  # Cloudflare Pages per-file hard limit
REDIRECT_CEILING = 100       # observed effective rule cutoff (see memory notes)

# Score-band totals that render as prose across the site. A drop that adds files
# at one of these scores silently drifts every page that hardcodes the count (the
# 2026-07-16 Drop 04 incident: "four files tied at 72" was really eight, "78 at 66"
# was really 92). When check-counts fails on a band, update BOTH the prose in the
# files below AND the number here, together.
EXPECTED_SCORE_BANDS = {72: 8, 70: 7, 66: 96, 65: 9}  # 70/66 grew in Drop 05
_SCORE_BAND_PROSE = (
    "pipeline/build_site.py (_score_tier_phrase + _explain_witness_astronaut), "
    "generated/faq.html, generated/top-10.html, generated/glossary.html, "
    "generated/aaro-unresolved-uap.html, templates/top10.html.j2"
)


def _fail(msg: str) -> None:
    print(f"  FAIL: {msg}")
    sys.exit(1)


def _ok(msg: str) -> None:
    print(f"  ok: {msg}")


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       encoding="utf-8", cwd=ROOT)
    return r.stdout


def pre_ingest() -> None:
    """Fetch a verified-fresh CSV and confirm it matches the poller's record."""
    from .poll_wargov import _fetch_csv, CSV_OUT, _csv_row_count

    state = json.loads(POLL_STATE.read_text(encoding="utf-8"))
    expected = state.get("csv_sha256")
    print(f"pre-ingest: poller expects sha256 {expected[:16]}..., "
          f"{state.get('row_count')} rows")

    result = _fetch_csv()
    if result is None:
        _fail("live CSV fetch failed on all paths (curl_cffi + playwright). "
              "Do NOT run the pipeline on the stale scratch file.")
    csv_bytes, source = result
    got = hashlib.sha256(csv_bytes).hexdigest()
    rows = _csv_row_count(csv_bytes.decode("utf-8-sig", errors="replace"))

    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    CSV_OUT.write_bytes(csv_bytes)
    _ok(f"fetched {rows} rows via {source}, wrote {CSV_OUT.name}")

    if got != expected:
        _fail(f"fresh fetch sha256 {got[:16]}... != poll-state {expected[:16]}... "
              "war.gov changed since the last poll. Re-check poll-state / wait "
              "for the poller before ingesting, so counts you publish match "
              "what the drop announcement will say.")
    _ok("fresh CSV sha256 matches data/poll-state.json - safe to run "
        "`python -m pipeline.run all`")


def _unmapped_agency_labels() -> set[str]:
    """Agency labels in the freshly-fetched CSV that AGENCY_MAP does not know.

    Lets post-ingest tell "war.gov added an agency" apart from "the scrape
    produced junk" - the two share an agency=OTHER symptom but need opposite
    responses, and conflating them would stall a drop on a false corruption
    alarm."""
    try:
        import csv as _csv
        import io as _io
        from .parse_csv import AGENCY_MAP
        raw = (ROOT / "_scratch" / "uap-csv.csv").read_text(
            encoding="utf-8-sig", errors="replace")
        seen = {(r.get("Agency") or "").strip()
                for r in _csv.DictReader(_io.StringIO(raw))}
        return {a for a in seen if a and a not in AGENCY_MAP}
    except Exception:
        return set()  # never let the diagnostic itself break the guard


def post_ingest() -> None:
    """Diff the new manifest against HEAD's committed manifest."""
    old_raw = _git("show", "HEAD:data/manifest.json")
    if not old_raw.strip():
        _fail("could not read HEAD:data/manifest.json")
    old = {f["id"]: f for f in json.loads(old_raw)["files"]}
    new_files = json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]
    new = {f["id"]: f for f in new_files}

    print(f"post-ingest: HEAD manifest {len(old)} files -> new manifest {len(new)}")

    missing = sorted(set(old) - set(new))
    if missing:
        print(f"  first missing ids: {missing[:8]}")
        _fail(f"{len(missing)} previously-live file ids are GONE from the new "
              "manifest. Live URLs would break (never delete/rename a file "
              "page - project Hard Rule #1). This is the download.py "
              "id-corruption signature: do not commit; revert data/ and "
              "generated/ and investigate.")
    _ok("zero previously-live ids lost")

    junk = [f["id"] for f in new_files if f.get("agency") in (None, "", "OTHER")]
    if junk:
        print(f"  first affected ids: {junk[:8]}")
        # Two very different causes produce agency=OTHER, and calling both
        # "junk" sent the operator hunting a corruption that wasn't there.
        # War.gov adds new agency labels between drops; an unmapped-but-real
        # label is a one-line AGENCY_MAP fix, not a poisoned ingest.
        unmapped = _unmapped_agency_labels()
        if unmapped:
            _fail(f"{len(junk)} entries have agency OTHER because war.gov used "
                  f"agency label(s) not in AGENCY_MAP: {sorted(unmapped)}. This "
                  "is NOT the junk-scrape signature - it is a new agency. Add "
                  "the label(s) to AGENCY_MAP in pipeline/parse_csv.py, then re-run "
                  "`python -m pipeline.run all` (NOT parse-csv alone - see "
                  "DROP_REACTION.md; a standalone re-parse used to wipe "
                  "transcripts/mirror_urls) and re-run this guard.")
        _fail(f"{len(junk)} entries have agency OTHER/empty and the live CSV "
              "contains no unmapped agency label - this IS the placeholder-junk "
              "signature from the legacy URL-scrape path. Do not commit.")
    _ok("zero OTHER-agency junk entries")

    old_types = Counter(f.get("type") for f in json.loads(old_raw)["files"])
    new_types = Counter(f.get("type") for f in new_files)
    for t in ("video", "pdf", "image"):
        if new_types[t] < old_types[t]:
            _fail(f"{t} count SHRANK {old_types[t]} -> {new_types[t]}. Files "
                  "of an existing type never disappear in a drop (the "
                  "video-collapse signature). Do not commit.")
    _ok(f"type counts sane: {dict(new_types)} (was {dict(old_types)})")

    incomplete = [f["id"] for f in new_files
                  if f["id"] not in old and (
                      not f.get("title") or not f.get("sha256")
                      or not (f.get("score") or {}).get("value"))]
    if incomplete:
        print(f"  first incomplete: {incomplete[:8]}")
        _fail(f"{len(incomplete)} NEW files are missing title/sha256/score - "
              "the pipeline did not finish enriching them. Re-run the "
              "remaining stages before building pages.")
    _ok(f"all {len(new) - len(set(old) & set(new))} new files fully enriched")

    # A drop that grows a cluster or a score band silently drifts every page that
    # hardcodes the count. Surface it here as a to-do (pre-push hard-blocks it).
    check_counts(warn_only=True)
    print("post-ingest: manifest diff is clean - safe to build/commit")


def pre_push() -> None:
    """Catch deploy-killers before they reach Cloudflare."""
    oversize = []
    for line in _git("ls-tree", "-r", "-l", "HEAD").splitlines():
        parts = line.split(None, 4)
        if len(parts) == 5 and parts[3].isdigit() and int(parts[3]) > CF_LIMIT:
            oversize.append(f"{int(parts[3]) / 1048576:.1f} MiB  {parts[4]}")
    if oversize:
        print("\n".join("  " + o for o in oversize))
        _fail(f"{len(oversize)} committed files exceed Cloudflare Pages' "
              "25 MiB limit - the deploy will silently show 'No deployment "
              "available'. Untrack them (git rm --cached) and gitignore.")
    _ok("no committed file exceeds 25 MiB")

    rules = [l for l in REDIRECTS.read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.strip().startswith("#")]
    if len(rules) > REDIRECT_CEILING:
        _fail(f"_redirects has {len(rules)} rules - past the ~{REDIRECT_CEILING} "
              "effective ceiling; rules beyond it are silently dropped.")
    margin = REDIRECT_CEILING - len(rules)
    (_ok if margin > 10 else print)(
        f"_redirects at {len(rules)}/{REDIRECT_CEILING} rules"
        + ("" if margin > 10 else f"  WARNING: only {margin} rules of headroom"))

    state = json.loads(POLL_STATE.read_text(encoding="utf-8"))
    blob = subprocess.run(["git", "cat-file", "blob", "HEAD:data/uap-data.csv"],
                          capture_output=True, cwd=ROOT).stdout
    if blob:
        got = hashlib.sha256(blob).hexdigest()
        if got != state.get("csv_sha256"):
            _fail(f"committed data/uap-data.csv blob sha256 {got[:16]}... != "
                  f"poll-state {state.get('csv_sha256', '')[:16]}... - the "
                  "served mirror is not byte-exact (check .gitattributes "
                  "-text rule, or the mirror is stale vs the latest drop).")
        _ok("served CSV mirror blob is byte-exact vs poll-state")

    # Hard gate: never push cluster/score-band counts that drifted from the manifest.
    check_counts()
    print("pre-push: safe to push")


def _match(fn, f) -> bool:
    try:
        return bool(fn(f))
    except Exception:
        return False


# Every place the site hardcodes "how many deep dives are there". The hub page
# itself (generated/deep-dives.html) is the source of truth; these four just
# restate it, and by 2026-08-06 all four disagreed with it AND with each other
# (30 / 33 / 36 / 36 against a real 35). Patterns are shape-anchored, not
# line-anchored, so they survive edits - and a pattern that stops matching is a
# hard failure, because a claim silently dropping out of range is exactly how
# this drifted unnoticed in the first place.
DEEP_DIVE_HUB = ROOT / "generated" / "deep-dives.html"
_DEEP_DIVE_CLAIMS = [
    ("index.html", r"see all (\d+) &rarr;|see all (\d+) →",
     'homepage LONG-READ ANALYSIS strip ("see all N")'),
    ("index.html", r"Deep dives</strong> (\d+) analyses",
     'homepage nav pill ("Deep dives N analyses")'),
    ("templates/file.html.j2", r"Deep-Dive Analysis \((\d+)\)",
     "file-page sidebar nav"),
    ("pipeline/build_categories.py", r"Deep-Dive Analysis \((\d+)\)",
     "category-hub sidebar nav"),
    # The 51 hand-authored statics + essay pages each carry their own copy of
    # the sidebar. No builder owns them, so a rebuild will NOT fix them - they
    # have to be edited in place, and they were the last holdouts on 36.
    ("generated/*.html", r"Deep-Dive Analysis \((\d+)\)",
     "hand-authored static/essay sidebar nav"),
]


def _deep_dive_truth() -> tuple[int, list[str]]:
    """Count deep-dive analyses from the hub, and verify the hub agrees with
    itself. Each section declares a count ("13 analyses") next to its actual
    cards; the primer section declares "the primer" and is deliberately NOT an
    analysis, so it is excluded from the total."""
    problems: list[str] = []
    html = DEEP_DIVE_HUB.read_text(encoding="utf-8")
    total = 0
    sections = re.split(r'<section class="grp">', html)[1:]
    if not sections:
        problems.append(
            f"{DEEP_DIVE_HUB.name}: no '<section class=\"grp\">' blocks found - "
            "the hub markup changed; update _deep_dive_truth() in preflight.py")
        return 0, problems
    for sec in sections:
        head = re.search(r"<h2>(.*?)</h2>.*?<span class=\"count\">(.*?)</span>",
                         sec, re.S)
        if not head:
            continue
        name, declared = head.group(1), head.group(2)
        cards = len(re.findall(r'class="dd-card"', sec))
        m = re.match(r"(\d+) analyses", declared.strip())
        if not m:  # the primer section - counted as a card, never as an analysis
            continue
        if int(m.group(1)) != cards:
            problems.append(
                f'{DEEP_DIVE_HUB.name} section "{name}": header declares '
                f"{m.group(1)} analyses but {cards} cards are present")
        total += cards
    return total, problems


def check_deep_dive_counts() -> list[str]:
    """Cross-check every hardcoded deep-dive count against the hub."""
    truth, problems = _deep_dive_truth()
    if problems:
        return problems
    for rel, pattern, where in _DEEP_DIVE_CLAIMS:
        paths = sorted(ROOT.glob(rel)) if "*" in rel else [ROOT / rel]
        if not paths:
            problems.append(f"{rel}: matched no files - check the path in "
                            "_DEEP_DIVE_CLAIMS (preflight.py)")
            continue
        # A glob fans out over many files; only some carry the claim. Requiring
        # every single one to match would be wrong, but requiring *at least one*
        # across the whole glob still catches the claim vanishing wholesale.
        hits = 0
        for path in paths:
            text = path.read_text(encoding="utf-8")
            found = [int(n) for m in re.finditer(pattern, text)
                     for n in m.groups() if n]
            hits += len(found)
            for n in found:
                if n != truth:
                    problems.append(
                        f"{path.relative_to(ROOT).as_posix()}: {where} says {n} "
                        f"deep dives, hub has {truth} - update it to {truth}")
        if not hits:
            problems.append(
                f"{rel}: the {where} count claim no longer matches its pattern - "
                "it was moved, reworded, or deleted. Re-anchor the pattern in "
                "_DEEP_DIVE_CLAIMS (preflight.py) rather than dropping the check")
    return problems


def _pretty_date(iso: str) -> str:
    """2026-07-10 -> 'July 10, 2026', the form llms.txt prose uses."""
    y, m, d = (int(x) for x in iso.split("-"))
    months = ("January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December")
    return f"{months[m - 1]} {d}, {y}"


_WORD_NUMS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
              "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
_WORD_NUMS_INV = {v: k.capitalize() for k, v in _WORD_NUMS.items()}


def check_llms_txt() -> list[str]:
    """Cross-check every load-bearing number in llms.txt against the manifest
    and built artifacts. The 2026-08-08 incident: llms.txt still described the
    Drop-01 archive (161 files, 171 sitemap URLs, 15 NASA files, a 'single
    highest-scoring file' that is now an 8-way tie) three drops and 173 files
    later - the Drop 04 sweep updated exactly one line of it and missed the
    rest. A file whose entire audience is AI assistants quoting it is the
    worst possible place to hold stale numbers. Same contract as the
    deep-dive checks: a pattern that stops matching is itself a failure."""
    path = ROOT / "llms.txt"
    if not path.exists():
        return ["llms.txt: missing - AI assistants fall back to scraping"]
    text = path.read_text(encoding="utf-8")
    files = json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]

    by_type = Counter(f.get("type") for f in files)
    by_agency = Counter(f.get("agency") for f in files)
    big_five = {"FBI", "DoD", "NASA", "CIA", "STATE"}
    intel_doe = sum(n for a, n in by_agency.items() if a not in big_five)
    transcripts = sum(1 for f in files if f.get("type") == "video"
                      and (f.get("extracted") or {}).get("transcript_path"))

    def score(f):
        s = f.get("score") or {}
        return s.get("value") if isinstance(s, dict) else s

    drops_raw = json.loads((ROOT / "data" / "drops.json").read_text(encoding="utf-8"))
    drops = drops_raw["drops"] if isinstance(drops_raw, dict) else drops_raw
    drops = sorted(drops, key=lambda d: d["date"])

    scores = [score(f) for f in files if score(f) is not None]
    top = max(scores)
    top_ties = scores.count(top)
    sitemap_urls = (ROOT / "sitemap.xml").read_text(encoding="utf-8").count("<url>")
    dd_total, dd_problems = _deep_dive_truth()

    checks = [
        # NOT "across four releases" - hardcoding the release word made this
        # check break on Drop 05 instead of validating it.
        (r"(\d+) files across \w+ releases", len(files), "header total"),
        (r"(\d+) files total: (\d+) PDF documents, (\d+) videos, (\d+) images",
         (len(files), by_type["pdf"], by_type["video"], by_type["image"]),
         "archive-state type breakdown"),
        (r"All (\d+) indexed URLs", sitemap_urls, "sitemap URL count"),
        (r"All (\d+) video pages", by_type["video"], "video sitemap count"),
        (r"structured data for all (\d+) files", len(files), "files API total"),
        (r"fbi-ufo-files/\): (\d+) files", by_agency["FBI"], "FBI category"),
        (r"military-uap-files/\): (\d+) files", by_agency["DoD"], "Pentagon category"),
        (r"nasa-ufo-photos/\): (\d+) files", by_agency["NASA"], "NASA category"),
        (r"cia-ufo-files/\): (\d+) files", by_agency["CIA"], "CIA category"),
        (r"state-department-uap-cables/\): (\d+) diplomatic cables",
         by_agency["STATE"], "State category"),
        (r"intel-and-doe-uap-files/\): (\d+) files", intel_doe, "intel/DOE category"),
        (r"videos/\): (\d+) DVIDS-hosted videos", by_type["video"], "videos category"),
        (r"deep-dives\): (\d+) long-form", dd_total, "deep-dive count"),
        (r"(\w+) files are tied at the top score of (\d+)/100",
         (top_ties, top), "top-score tie"),
        (r"(\d+) of the (\d+) videos have transcripts",
         (transcripts, by_type["video"]), "transcript honesty note"),
        (r"What these (\d+) files do and do not prove", len(files), "verdict line"),
        # The release enumeration and its "as of" anchors. These go stale on
        # EVERY drop and are prose, not stat-block numbers, so they are the
        # easiest to miss - the 2026-08-08 rebuild found llms.txt still
        # describing the Drop-01 archive three drops later.
        (r"(\d+) files across (\w+) releases as of ([A-Z][a-z]+ \d+, \d+)",
         (len(files), _WORD_NUMS_INV.get(len(drops), str(len(drops))),
          _pretty_date(drops[-1]["date"])), "header blockquote 'as of' line"),
        (r"(\w+) releases: Drop 01",
         (_WORD_NUMS_INV.get(len(drops), str(len(drops))),), "release-list heading"),
        (r"brought the total to (\d+) as of Drop (\d+)",
         (len(files), len(drops)), "file-count clarification"),
    ]

    problems = list(dd_problems)
    for pattern, expected, where in checks:
        m = re.search(pattern, text)
        if not m:
            problems.append(
                f"llms.txt: the {where} claim no longer matches its pattern - "
                "it was moved, reworded, or deleted. Re-anchor the pattern in "
                "check_llms_txt (preflight.py) rather than dropping the check")
            continue
        want = expected if isinstance(expected, tuple) else (expected,)
        # Compare each group in the KIND its expected value is: numeric groups
        # accept digits or number-words, string groups (dates, "Four") compare
        # case-insensitively. Coercing everything to int silently produced None
        # for date captures and made the check unfalsifiable.
        got = []
        for g, w in zip(m.groups(), want):
            if isinstance(w, int):
                got.append(int(g) if g.isdigit() else _WORD_NUMS.get(g.lower()))
            else:
                got.append(g)
        got = tuple(got)
        if not all(isinstance(w, int) or str(g).casefold() == str(w).casefold()
                   for g, w in zip(got, want)) or any(
                       isinstance(w, int) and g != w for g, w in zip(got, want)):
            problems.append(
                f"llms.txt: {where} says {got} but live data says {want} - "
                "update the claim (and re-verify its surrounding prose)")

    # Every drop in drops.json must appear in llms.txt's release list with its
    # real date and file count. A numeric spot-check cannot catch a whole
    # missing release line, which is exactly what a new drop introduces.
    for d in drops:
        want = f"{_pretty_date(d['date'])}, {d['file_count']} files"
        if want not in text:
            problems.append(
                f"llms.txt: release list is missing or wrong for "
                f"{d['id']} - expected the substring \"{want}\". Add/fix that "
                "drop in the 'Current archive state' release list")
    return problems


def check_counts(warn_only: bool = False) -> None:
    """Recompute cluster + score-band counts from the manifest and flag drift vs
    the counts the site hardcodes in prose. Catches the 2026-07-16 Drop 04 class:
    TOPIC_PAGES cluster sizes and score-band totals that render across file pages,
    /faq, /top-10, /glossary, and the cluster essays.

    warn_only=True (post-ingest) prints drift without exiting, so a drop's expected
    count changes surface as a to-do. Strict (the `check-counts` subcommand and
    pre-push) hard-fails, so drifted counts can never be pushed live."""
    from . import build_site as bs
    files = json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]

    def score(f):
        s = f.get("score") or {}
        return s.get("value") if isinstance(s, dict) else s

    problems: list[str] = []

    # 1. Every TOPIC_PAGES cluster: declared size vs actual lambda match count.
    #    Self-checking - imports the real match predicates, so a cluster that a
    #    drop grows (agency==CIA, score==66, dow-uap-pr, agency==DOE, ...) is caught.
    for tp in bs.TOPIC_PAGES:
        n = sum(1 for f in files if _match(tp["match"], f))
        if n != tp["size"]:
            problems.append(
                f'cluster {tp["slug"]}: declared size={tp["size"]} but {n} files '
                'match its lambda - update size + the "anchor" prose in build_site.py '
                "(and the cluster essay page if it prints the count)")

    # 2. Score-band totals referenced in prose (golden-value guard).
    counts = Counter(score(f) for f in files if score(f) is not None)
    for band, expected in sorted(EXPECTED_SCORE_BANDS.items(), reverse=True):
        actual = counts.get(band, 0)
        if actual != expected:
            problems.append(
                f"score band {band}: EXPECTED_SCORE_BANDS says {expected}, manifest "
                f"has {actual} - update the prose ({_SCORE_BAND_PROSE}) AND "
                "EXPECTED_SCORE_BANDS in preflight.py, together")

    # 3. Deep-dive counts hardcoded across the site vs the hub page itself.
    problems.extend(check_deep_dive_counts())

    # 4. llms.txt (the AI-assistant manifest) vs manifest + built artifacts.
    problems.extend(check_llms_txt())

    if problems:
        for p in problems:
            print(f"  {'WARN' if warn_only else 'FAIL'}: {p}")
        if warn_only:
            print("  ^ count drift detected - fix the prose before pushing "
                  "(pre-push hard-blocks otherwise)")
            return
        sys.exit(1)
    _ok(f"{len(bs.TOPIC_PAGES)} cluster sizes + {len(EXPECTED_SCORE_BANDS)} "
        "score-band totals all match the manifest, "
        f"{len(_DEEP_DIVE_CLAIMS)} deep-dive count claims match the hub, "
        "and all llms.txt claims match live data")


def main() -> int:
    cmds = {"pre-ingest": pre_ingest, "post-ingest": post_ingest,
            "pre-push": pre_push, "check-counts": check_counts}
    if len(sys.argv) != 2 or sys.argv[1] not in cmds:
        print(f"usage: python -m pipeline.preflight [{'|'.join(cmds)}]")
        return 2
    cmds[sys.argv[1]]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
