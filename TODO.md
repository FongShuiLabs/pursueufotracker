# PURSUE UFO Tracker - Action Queue

> ## ✅ DROP 05 IS LIVE (deployed 2026-08-27)
>
> Verified live, not assumed: all **41** new Drop 05 pages return HTTP 200
> (paced check, zero failures), the homepage shows the Release 05 banner and a
> "What's New in Drop 05" section, `llms.txt` advertises **375 files / five
> releases** (it was serving "161 files" that morning), and the new EOP file is
> linked from the intel-and-doe hub. Running `verify-deploy.ps1` returns
> **DEPLOY VERIFIED**.
>
> **62 URLs submitted to IndexNow** (41 new files + 21 changed pages) - Bing,
> Yandex, Naver, Seznam, `200 OK`. Note the `index-now` stage inside
> `pipeline.run all` fired BEFORE the push, when those URLs were still 404, so
> that submission was wasted; this one was done after the deploy. **On the next
> drop, submit to IndexNow AFTER the push, not as part of the build.**
> Google does not support IndexNow and will recrawl on its own schedule.
>
> ### Next action (operator)
> **Post the r/UFOs thread** - `_scratch/reddit-drop05.md`, Option A. The draft is
> marked CLEARED TO POST; all five of its URLs were re-checked live at 200.
> Text post, not a link post, weekday 9am-1pm ET.
>
> ### Then, before Drop 06 (~Sept 4 if the +28 pattern holds)
> 1. **ntfy alerts** - paste `poll-wargov-workflow-READY-TO-PASTE.yml.txt` into
>    `.github/workflows/poll-wargov.yml` via the GitHub web UI, and add repo
>    secret `NTFY_TOPIC`. The workflow currently running has ZERO ntfy
>    references, so a drop will still arrive silently.
> 2. **Email capture** - Drop 05 came and went with no form live. That is two
>    consecutive drops of spike traffic not captured.
>
> Credential note: the push is authenticated as GitHub user **FongShuiLabs**,
> stored in `~/.git-credentials` as PLAINTEXT (`credential.helper=store`).

**Last updated: 2026-07-16** (post-freeze session: verified site health, pulled GSC, re-verified Drop 04 distribution copy. Full strategy in `_scratch/PLAN-2026-07-16.md`.)

---

## Current state (verified 2026-07-16)

- **Drop 04 live and clean.** 334 files (manifest + live API + poll-state all agree), CSV SHA-256 `13e730c1...`, poller current (no change since 2026-07-12). Integrity check clean (216 files, 0 body-changed, 0 unreachable). Homepage 200, deploys healthy.
- **114 old-slug orphans already canonical-remapped** (fix f532c6d holds; Drop 04's `d8`→`d008`, `serial-3`→`serial-003` re-slugs all carry correct canonical tags). No remap work needed - Google is still consolidating.
- **robots.txt /generated/ fix (2026-07-13) is landing.** 28-day GSC shows canonical `/files/` URLs replacing the raw `/generated/` twins; a few `/generated/` URLs still hold 90-day clicks. Monitor deindexing over the next few weeks.

## The strategic read (from the 2026-07-16 GSC pull)

**Traffic is the bottleneck, and organic search is currently a rounding error.**
28-day: 11 clicks / 1.33K impressions / 0.8% CTR / pos 8.5. 90-day: 98 clicks /
6.51K impr / 1.5% CTR / pos 7.5, with the homepage taking ~half the clicks and the
rest a 1-4-click long tail. The May Reddit virality was the only real traffic; it
has decayed. **Priority order: distribution + email capture > SEO micro-opt > AdSense-chasing.**
At this traffic AdSense revenue is ~zero even if approved; get it approved to bank
for later, but it is not a near-term earner.

---

## 🔴 PENDING OPERATOR ACTIONS (Claude can't do these)

1. **Post the Drop 05 r/UFOs thread** - the site is DEPLOYED, links verified live.
   Use `_scratch/reddit-drop05.md` **Option A** (the 1963 White House / NASC paper
   trail). Written timing-neutral on purpose: Drop 05 landed Aug 7 and went live
   Aug 27, so a "just dropped" framing would read stale - that is what killed the
   Drop 04 draft. Do NOT post `_scratch/reddit-drop04.md`; it is two releases old.
   Weekday 9am-1pm ET, text post, replace [SITE] with the domain.
2. **AdSense status** — RESOLVED 2026-07-17 (operator screenshots, Work profile):
   "Getting ready", review requested **12 Jul 2026 09:33** (fresh cycle - not the
   7/1 one; window is "few days to 2-4 weeks"). Ownership verified. DO NOT
   re-request; wait for the decision email at developer@fongshuilabs.com. The
   Sites-list "Ads.txt: Not found" chip is FALSE-stale: file verified live+correct
   2026-07-17 (200, text/plain, correct pub ID, 301 variants fine, not blocked) -
   AdSense's ads.txt crawler just lags; no action. glp1cost.org: also "Getting
   ready" (in review since ~May), its ads.txt reads "Authorized".
3. **Pick an ESP for email capture** — Substack recommended (free, discovery traffic,
   paid tier later). The form is now FULLY PRE-STAGED sitewide (pipeline/subscribe.py,
   2026-07-18): once you create the account and hand over the handle, the flip is
   two config values + `wire-subscribe`/`build`/`build-categories` + push (~10 min).
   Drop 05 has now LANDED (Aug 7) with no capture form live - that spike is spent.
   Get it live before Drop 06 (the gaps have run +14/+21/+28/+28). Full
   revenue sequencing: `_scratch/MONETIZATION_PLAYBOOK.md` (gates 0-5).
4. **Cloudflare Email Routing** — ✅ DONE 2026-08-05 (Claude, operator-authorized).
   Enabled + DNS live (MX/SPF/DKIM verified resolving); catch-all **Active** →
   anthony.fong.esq@gmail.com. All @pursueufotracker.com addresses now deliver.
   ONE CLICK REMAINS for the operator: Cloudflare's verification email for
   developer@fongshuilabs.com is in that inbox — click it, then (optionally)
   switch the catch-all destination to the business inbox.
5. **Install the poller build-skip workflow** — paste `poll-wargov-workflow-UPDATED.yml.txt`
   into `.github/workflows/poll-wargov.yml` via GitHub web UI (PAT lacks workflow
   scope). Kills ~40/day of no-op Cloudflare builds.
6. **Amazon Associates application** (developer@fongshuilabs.com, payee Fong Shui Labs
   LLC EIN, TD business 714). Until a real tag exists, zero affiliate framing (Hard Rule #8).

## 🟡 OPEN — Claude autonomous (SEO is background, not headline)

- **`/revisions` CTR leak** — GSC drilled 2026-08-08: 28d window shows 0 clicks /
  18 impressions / position 5.4, queries all below threshold. The Jul-17 download-led
  retitle CANNOT be scored on 18 impressions; position improved (5.4), so it is not
  hurting. HOLD until Drop 05 spikes the URL-shaped family, then score. Do not edit.
- **URL-shaped query capture** — drilled 2026-08-08, and the lane has structurally
  changed: for exact file-ID queries (e.g. "dow-uap-pr053") the live SERP is DVIDS
  with a video thumbnail at #1 + a Google AI Overview answering the query inline +
  official .mil pages + YouTube; pursueufotracker is not on page 1 organically. GSC
  "position 2.3, 74 impr/28d, 0 clicks" on the dow-uap-pr05x family reflects rare
  sub-threshold queries, not winnable head IDs. **Read: meta rewrites cannot win
  clicks an AI Overview absorbs. The play is machine citability** — being the source
  AI answers quote. Shipped 2026-08-08: `llms.txt` fully rebuilt (it was frozen at
  Drop 01: "161 files", 171-URL sitemap, "single highest-scoring file" now an 8-way
  tie, no CIA/videos/deep-dives sections, stale .html URL) with every claim verified
  against the manifest, and wired into `preflight.py check-counts` so it hard-fails
  pre-push if any of its 16 numeric claims drifts from live data. See
  [[gsc-url-shaped-queries]].
- ~~**Count drift (minor)**~~ — ✅ **DONE 2026-08-06**, and it was worse than this entry
  described (the entry's own numbers were wrong: the homepage said 33 *and* 36 in two
  places, not 30, and the hub sums to 35, not 31). Four surfaces each claimed a
  different number - homepage 33 + 36, file-page sidebar 36, category sidebar 30 -
  against a hub that has always been self-consistent at **35 analyses + 1 primer card**.
  All 392 pages now read 35. The hub's JSON-LD `numberOfItems: 36` is correct as-is and
  was deliberately left alone: it enumerates all 36 `ListItem`s including the primer.
  Guarded so it can't drift a fifth time: `pipeline/preflight.py` now derives the count
  from the hub and hard-fails pre-push on any mismatch, on the hub disagreeing with
  itself, or on a claim being reworded out of pattern range (that last mode is why the
  51 hand-authored statics went unnoticed - no builder owns them, so a rebuild does NOT
  fix them). See [[homepage-hand-authored-drifts]].
- **Next deep-dive** — the Robertson Panel standalone this entry used to recommend
  ALREADY SHIPPED (`/robertson-panel`, verified live in the deep-dives hub 2026-08-08;
  this entry was stale). Apollo 14 (d026/d027) remains covered by
  /astronaut-light-flashes-explained - do not duplicate. No new candidate ranked;
  re-rank from GSC after Drop 05. Every claim verified from CSV/manifest (Hard Rule
  #7), no % aliens (Hard Rule #2).

## 🛰️ Drop 05 - what shipped (2026-08-18)

- **375 files** (was 334): +41 = DoD 19, FBI 17, CIA 2, State 2, EOP 1.
  22 documents / 16 videos / 3 images, 14 redacted, zero removed.
- **New agency: `EOP`** (Executive Office of the President), war.gov's own
  `EOP-UAP-D001` prefix. Required three wirings - `AGENCY_MAP`, the agency prose
  maps in `build_site.py`, and the `intel-and-doe-uap-files` hub match list,
  which had a hardcoded agency tuple that would have **orphaned the new file from
  all category navigation**.
- The parse-time `!! UNMAPPED AGENCY LABELS` warning added on 2026-08-17 fired on
  its first real drop, exactly as rehearsed - instead of post-ingest
  misdiagnosing it as "placeholder junk ... Do not commit".
- Count reconciliation touched ~460 files: cluster sizes (FBI-modern 30→47,
  CIA 21→23, diplomatic 7→9), score bands (66-band 92→96, 70-band 6→7), and a
  sitewide 334→375 pass done with context-matching so historical decomposition
  ("Release 04 brought the archive to 334") stayed true.
- Also fixed en route: `/top-10` said "Positions 5 through 10 are tied at 70"
  (stale even before this drop - eight files sit at 72), and a `drops.json`
  claim I wrote that Bahia was documented "across three separate arms of
  government" - it is **two** (EOP + State), and Colorado Springs and Western US
  already spanned two each. Removed before it reached a page.

## 🔗 Internal-link audit (2026-08-18) - 3 defects found and fixed

Ran a sitewide audit of every `href="/files/<id>"` against the manifest. Found
by accident while adding the Drop 05 homepage section, which is the point: these
had been live for an unknown period and nothing was checking.

- **`index.html` linked to a 404** - `nasa-uap-d007-skylab-tech**inc**al-...`
  (transposed letters). On the highest-traffic page on the site. Fixed to the
  canonical `...technical...` id.
- **`/pursue-release-02-pentagon-videos`** linked to the `...fast-sh**e**rical...`
  old-slug orphan instead of the canonical `...spherical...` id. Fixed.
- **`/random`** linked to the `nasa-uap-d3a-...` orphan instead of
  `nasa-uap-d003a-...`. Fixed.

**Remaining (deliberately not fixed): 1 dead link**, `dow-uap-pr20-...-kuwait-may-2022-2`,
which appears ONLY on the orphan page `dow-uap-pr20-...-kuwait-may-2022.html`. War.gov
retired the Kuwait slug entirely and no replacement file exists. The orphan is kept for
URL stability (Hard Rule #1) and its own canonical already points at a live page, so the
dead sibling link is cosmetic and invisible to canonical navigation.

**Worth automating:** this audit is ~20 lines (walk every `*.html`, regex the
`/files/` hrefs, diff against manifest ids and the orphan set) and would fit
naturally in `preflight pre-push`. Not added yet - flagging rather than
silently expanding the guard surface mid-drop.

## 🔎 SEO audit 2026-08-17 (evidence pulled, deliberately zero on-page edits)

**Verdict: the site is technically healthy and demand is the only constraint.
No on-page work is justified. Editing now would be churn against noise.**

GSC 28d (Jul 19 - Aug 15): **1 click / 216 impressions / 0.5% CTR / position 12**.
3-month: 64 clicks / 5.22K / 1.2% / position 8.1. Impressions are down ~78% vs
July's 1.33K. The position 6.0 -> 12 move is **not a ranking loss**: with only
216 impressions the mix is random long-tail ("apollo 17 alien", "the central
intelligence agency and overhead reconnaissance"), while the brand/head queries
that used to anchor position 6 have fallen below GSC's visibility threshold.
This is the inter-drop trough at 38 days, exactly what the standing rule predicts.

Technical layer verified clean (this part does NOT depend on demand):
- **Indexing healthy and RISING** - 346 indexed, stepped up in late July. Not deindexed.
- **Sitemap 100% clean** - all 401 URLs curled live, every one 200. Zero dead URLs published.
- All 7 category hubs + /deep-dives return 200 live; `_redirects` at 82/100 rules,
  under the cutoff that broke them before.
- GSC's "Not found (404): 10" is historical URLs Google remembers, NOT our defect
  (proven by the clean sitemap sweep).
- "Blocked by robots.txt: 88" and "Alternate page with proper canonical: 54" are
  both intentional and working as designed.
- "Duplicate, Google chose different canonical: 9" - still improving on its own
  (14 -> 11 -> 9). Leave it.

**The one SEO action that would actually help is deploying what is already built.**
Verified live 2026-08-17: `https://pursueufotracker.com/llms.txt` still serves
**"161 files"** and **"171 indexed URLs"** - the Drop-01 numbers, 173 files and
three drops stale. The rebuilt version (334 files, verified, guarded) is sitting
undeployed in the working tree. Every AI assistant fetching the site today gets
the stale manifest, which is precisely the machine-citability lane the Aug-8 GSC
work identified as the remaining winnable play. See [[gsc-url-shaped-queries]].

## ⏳ Standing refresh hooks

- ~~**FAQ "When will more UFO files be released?" + /drops cadence claims**~~ -
  ✅ **DONE 2026-08-17**, triggered exactly as this hook specified (mid-August
  passed with no drop). The +14/+21/+28 pattern is now stated as **broken**: 33
  days since Release 04, longer than any prior gap, and the site no longer
  publishes a predicted date anywhere. Updated: `/faq` visible copy AND its
  JSON-LD twin (both carried byte-identical text - JSON-LD re-validated, 2 blocks
  / 16 entities intact), `data/drops.json` `expected_next.note` (the "NEXT DROP -
  Monitoring" block, the site's most prominent when-is-it surface) plus a new
  `as_of` stamp, and a latent "Subscribers get an alert within minutes" overclaim
  in the `drops_index.html.j2` fallback that the 2026-08-10 cadence sweep missed
  because it only renders when `expected_next.note` is empty.
  **Re-arm on the next drop:** all four surfaces need the new release added, and
  the 33-day figure re-stated or removed.
- **/aaro-unresolved-uap "latest annual report" section** (added 2026-07-17, targets
  the "latest aaro uap report 2025 2026" GSC query family at pos 17-20): the status
  is date-stamped "as of July 17, 2026". When AARO publishes its FY2025 annual (or
  Historical Record Vol. 2), update the section + meta description same-day - being
  current on that news cycle is the whole play. Verify from aaro.mil/war.gov, not memory.

## 🔵 DECISION NEEDED: make the poller cadence real, or leave it honest?

Found 2026-08-10 from the GitHub Actions API (all 696 runs): the poller's cron asks
for every-30-min weekday / hourly off-hours, but **GitHub throttles scheduled
workflows so hard that cadence has never once been delivered** - really ~9-11
runs/day, median gap 107 min, worst observed 11.9 h. Reliability is otherwise
excellent (0.6% failures) and detection is state-based, so a skipped cycle only
DELAYS a drop, never misses it.

The site had been promising the undelivered number on 12 public surfaces; all are
now rewritten to "several times a day" (true at the historical floor). That closes
the Hard Rule #7 exposure. **Remaining choice is yours:**

- **(a) Leave it.** Copy is honest, detection still guaranteed. Drop-day latency
  stays ~2 h typical. Zero work. ← recommended unless drop-day speed matters
- **(b) Make it real.** Cron alone cannot; needs an external pinger hitting
  `workflow_dispatch` on a real schedule (cron-job.org free tier, or a Cloudflare
  Worker cron - you already run CF). ~20 min setup, then the 30-min claim could be
  restored truthfully. Worth it only if being first to post a drop is the goal.

See [[poller-cadence-never-as-documented]] for the full measurement.

## 🛰️ Drop 05 readiness (~early August)

- When the poller fires `[NEW DROP]`: follow `DROP_REACTION.md` (release-agnostic,
  rewritten 2026-07-17 with the count-drift + drops.json-append steps). Run the
  preflight guards each stage: `python -m pipeline.preflight pre-ingest|post-ingest|pre-push`
  (post-ingest/pre-push now also check count drift; reconcile before the push gate).
- Fetch fresh CSV via `poll_wargov._fetch_csv()` + SHA-256 match BEFORE ingest
  (parse-csv reads stale `_scratch` otherwise). Use `download-manifest`, never legacy
  `download`. Diff manifest ids vs `git show HEAD:data/manifest.json` before trusting the ingest.
- Have email capture LIVE before this drop (see operator action #3).

---

## Reference

- Full session strategy + execution order: `_scratch/PLAN-2026-07-16.md`
- Distribution copy (verified): `_scratch/READY-TO-FIRE.md` + `_scratch/reddit-drop04.md`
- Account inventory: `.claude/accounts.md`
- Pipeline shortcut: `python -m pipeline.run --from build` then commit + push (CF auto-deploys ~30s). Full run incl. IndexNow: `python -m pipeline.run all`.
