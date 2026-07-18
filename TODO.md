# PURSUE UFO Tracker — Action Queue

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

1. **Post the Drop 04 r/UFOs thread** — HIGHEST URGENCY, decaying value. Fully
   re-verified copy in `_scratch/reddit-drop04.md` (Option A). All numbers checked
   vs live manifest, all 3 URLs 200, the "deformed balloon" debrief quote confirmed
   live. Weekday 9am-1pm ET, text post. If the viral two-tiered-video moment has
   cooled, the body still lands (the debrief-vs-video angle is evergreen).
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
   Live BEFORE Drop 05 (~early-mid August) or the spike evaporates again. Full
   revenue sequencing: `_scratch/MONETIZATION_PLAYBOOK.md` (gates 0-5).
4. **Cloudflare Email Routing for pursueufotracker.com** (~5 min) — the `/contact`
   addresses (contact@/press@/tips@/privacy@/legal@) still BOUNCE. CF zone → Email →
   catch-all → developer@fongshuilabs.com. Also a human-reviewer trust signal for AdSense.
5. **Install the poller build-skip workflow** — paste `poll-wargov-workflow-UPDATED.yml.txt`
   into `.github/workflows/poll-wargov.yml` via GitHub web UI (PAT lacks workflow
   scope). Kills ~40/day of no-op Cloudflare builds.
6. **Amazon Associates application** (developer@fongshuilabs.com, payee Fong Shui Labs
   LLC EIN, TD business 714). Until a real tag exists, zero affiliate framing (Hard Rule #8).

## 🟡 OPEN — Claude autonomous (SEO is background, not headline)

- **`/revisions` CTR leak** — 778 impressions / 2 clicks over 90 days (worst CTR on
  the site). Retitle (6/14) didn't fix it. Needs a GSC query-for-this-page drill to
  learn intent BEFORE rewriting the title/meta (searchers may want the file, not the
  changelog) — otherwise we optimize for the wrong intent.
- **URL-shaped query capture** — literal war.gov CSV paths + exact PDF filenames draw
  impressions but ~0 clicks; a new `?release=3` variant appeared. Extend `/uap-data-csv`
  + file-page meta descriptions to win these. See [[gsc-url-shaped-queries]].
- **Count drift (minor)** — homepage says "30 analyses", the deep-dives hub subsections
  sum to 31. Reconcile in the next sitewide count sweep (see [[homepage-hand-authored-drifts]]).
- **Next deep-dive** (ranked by GSC evidence, distribution-first so treat as background):
  Apollo 14 (d026/d027) is ALREADY covered by /astronaut-light-flashes-explained - do not
  duplicate. Top candidate is a Robertson Panel standalone (evergreen). Every claim verified
  from CSV/manifest (Hard Rule #7), no % aliens (Hard Rule #2).

## ⏳ Standing refresh hooks

- **FAQ "When will more UFO files be released?" + /drops title cadence claims**
  (added 2026-07-17): both state "four releases" and extrapolate the next drop to
  early-to-mid August 2026 from the +14/+21/+28-day gaps. When Drop 05 lands (or
  mid-August passes with no drop), update the FAQ answer (visible + JSON-LD twin),
  the /drops meta description (templates/drops_index.html.j2), and re-run build-drops.
- **/aaro-unresolved-uap "latest annual report" section** (added 2026-07-17, targets
  the "latest aaro uap report 2025 2026" GSC query family at pos 17-20): the status
  is date-stamped "as of July 17, 2026". When AARO publishes its FY2025 annual (or
  Historical Record Vol. 2), update the section + meta description same-day - being
  current on that news cycle is the whole play. Verify from aaro.mil/war.gov, not memory.

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
