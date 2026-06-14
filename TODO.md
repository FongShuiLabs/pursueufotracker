# PURSUE UFO Tracker — Action Queue

**Last updated: 2026-06-14** (Drop 03 ingested + live; deploy unblocked; CIA deep-dive + /revisions SEO shipped)

---

## ✅ DONE 2026-06-13/14 (PURSUE Release 03 - the marquee event)

**Drop 03 landed 2026-06-12 (war.gov CSV 222 -> 294 rows). Now fully live.** Caught via a CBS News video after the poller's `[NEW DROP]` commit slid past in a rebase - hence the new [[drop-guard-never-miss-a-drop]] (drop_check + SessionStart hook; run `--mark` after each ingest).

- **Ingested 72 new files -> 294 total**, all SHA-256 verified. FBI +29, CIA +18, DoD +12, NASA +11, ICA +1, USG +1. 3 typo re-slugs (skylab/email/cigar), zero withdrawals.
- **war.gov changed the CSV schema** (added a leading "Featured" column) - parse_csv now maps by column NAME, not position. New agency labels mapped: CIA (short), ICA, USG. See [[wargov-csv-schema-evolves-per-drop]]. Ingest uses `download-manifest`, NOT the legacy `download` stage (it collapses videos by source_url).
- **New `/cia-ufo-files/` hub (19)** + Apollo 16 restored (real in Drop 03) + Gemini 4/5/9 + Gordon Cooper. Homepage Top-5, all hub counts, and the **sitewide 222->294 sweep** (homepage, faq, /changes R03 block, pursue-program, all 408 file pages, editorial essays) done. All 114 orphans re-homed from current twins.
- **DEPLOY WAS STUCK ~14h**: not quota/billing - `generated/search-index.json` hit 27.1 MiB, over Cloudflare Pages' 25 MiB/file cap, failing asset validation on every commit. Fixed: `build_search.py` now caps per-doc body at 5000 chars (titles+summaries full) -> 4.58 MiB. **If a deploy ever stalls again, check the CF Pages build log for the oversized-asset error first.**
- **Content/SEO**: new CIA deep-dive `/cia-ufo-files-explained` (Robertson Panel, U-2, Blue Book; "less-redacted than CIA public copies" hook); `/revisions` retitled to the war.gov-CSV intent (was 549 impr @ 0.4% CTR - all "uap-csv.csv" queries); IndexNow ping for Drop-03 + CIA URLs.

## 🔴 PENDING OPERATOR ACTIONS (Drop 03)
1. **Install the poller build-skip workflow**: paste `poll-wargov-workflow-UPDATED.yml.txt` into `.github/workflows/poll-wargov.yml` via GitHub web UI. Adds `[CF-Pages-Skip]` to "unchanged" poll commits so they stop triggering Cloudflare builds (~40/day of noise). PAT lacks workflow scope.

## 🟡 OPEN SEO (next session)
- `/generated/` + `.html` non-canonical URL audit (Hard Rule #6 - equity splitting across URL variants).
- Fresh GSC pull once Drop 03 indexes - new query opportunities around CIA / Apollo 16 / FBI orbs.
- Gordon Cooper: fold into NASA hub or a glossary entry (one file - avoid a thin standalone).

---

## ✅ DONE 2026-06-12 (GSC/Plausible-driven, the traffic-data pass)

Pulled Plausible (steady-state ~3-25 pv/day post-viral; NASA hub = #2 page) + GSC live via Chrome MCP (domain property). Data verdict: **NASA/Apollo is the organic magnet**; `/nasa-ufo-photos/` ranks pos 11.5 / 195 impressions = the clearest page-2 win.

- **NASA hub deepened + corrected** (`build_categories.py` + regenerated): stale "Fifteen NASA files" -> 22 (15 R01 + 7 R02), killed the false "Apollo 16" (0 occurrences in data), added the 5 Mercury files (Atlas 7/8/9 + Redstone 4, 1961-63) the intro had omitted, fixed Schmitt-Grimaldi attribution, D003A now "highest-scored in the entire release" (72). Title/keywords add Mercury + the live `apollo 12 uap` query. Same fixes on `apollo-12-ufo-photos` + `diplomatic-uap-cables`. Homepage "NASA - 15 FILES" left intact (correctly scoped to "What's in Drop 01?").
- **111 orphan duplicate file pages refreshed** - GSC showed Google ranks old-slug orphans (`vm1`/`d3a`/`vm6`/`fbi-photo-a5`) that served stale "NASA's 15 / of 161" because the physical files shadow their own 301s on Cloudflare. Operator chose fix-in-place (no delete): re-homed each from its current canonical twin. 0 stale markers remain on any file page. See memory [[orphan-duplicate-file-pages]].
- All changes pushed + curl-verified live.

### Open opportunities surfaced this pass (operator's call)
1. **Orphan duplicate-content split still exists** (by operator choice). Deleting the 111 orphans would let the existing 301s consolidate ranking onto canonical pages - higher SEO upside, needs explicit approval. Reversible via git.
2. **`/revisions`: 546 impressions, 0.4% CTR, pos 8.2** - the biggest impression-volume page, barely converting. A title/meta-description rewrite is the lever, but GSC query->page intent wasn't drilled (needs another Chrome MCP pass). Lower-confidence until intent is known.
3. **SEO hygiene**: GSC shows `/generated/files/...` and `.html`-extension URLs indexed (non-canonical per Hard Rule #6). Worth a dedicated audit - equity splitting across URL variants.

## ✅ DONE 2026-06-11 (net-new content)

- **New `/verify` page** - the file-integrity story (222/222 SHA-256, how to check any file vs war.gov, the byte-swap case study) as a dedicated, linkable page. Wired into the sitemap, `_redirects`, all 222 file pages, the homepage tools-nav + verification FAQ, and the methodology page. Fills the gap that `/methodology` only covers scoring.
- **Glossary expanded 17 -> 31 terms** - added ODNI, CIA, DOE, IIR, USPER, FLIR, Tic Tac, USO, transmedium, NORTHCOM, EUCOM, USCINCPAC, PANTEX, nap-of-the-earth (visible + DefinedTerm JSON-LD aligned). "Tic Tac" captures a high-volume query without a thin standalone page.
- **Top-5 ranking fix** (PR072/68 inserted at #2) and **51 PR file pages** now honestly label war.gov's shared release note.
- **Editorial audit complete** - CIA/ODNI/DOE/AARO/FBI deep-dives all verified accurate; fixed the Pentagon "29 formations" overstatement and one broken FBI link (sitewide link sweep otherwise clean).

## ✅ DONE 2026-06-11 (sitewide credibility + count sweep)

- **222/222 SHA-256 coverage reached** - hashed the 78 videos + fixed/hashed the 8 NASA audio files (incl. the flagship Gemini 7/Borman audio, which a parse bug had mis-typed as PDF). Source fix: `parse_csv.py` now maps "AUD"->video.
- **Removed reader-falsifiable false claims sitewide** (Hard Rule #7): "1947 Roswell" FBI framing (zero files mention Roswell), a fabricated "1994 Tajikistan PanAm" cable (the real 1994 cable is the Dushanbe-origin / over-Kazakhstan one), a nonexistent "Apollo 16" file, and a "161+64=222" arithmetic error (it's 158+64).
- **Fixed stale "161" counts everywhere** - homepage, timeline, search, about, api, random, borman, diplomatic, faq, press, verdict, top-10, drops, category back-links, and `templates/file.html.j2` (was on all 222 file pages). "161" now appears only in the accurate May-11 row-count history.
- **Regenerated the public API** - it was a full release behind at 161 files; now serves all 222 with current hashes (`/generated/api/files.json`).
- Surfaced the now-true "222/222 SHA-256 verified" milestone in the homepage hero, stat block, and Release-02 banner.

---

## 🔴 PENDING OPERATOR ACTIONS (do these — Claude can't)

1. **Paste the corrected viral r/UFOs post** — body ready in `_scratch/reddit-viral-post-EDITED.md`. Removes 4 false claims ("removed 5/added 3", "28 DOW-UAP-PR renames", "Arabian Gulf consolidation") + fixes stale top-5. Its `/changes` link is live with verified proof. HIGHEST PRIORITY (it's a 487K-view post with false claims). See `_scratch/handoff-2026-06-10-byteswap.md` for full context.
2. **Install the integrity-check workflow** via GitHub web UI — YAML + instructions in `integrity-check-workflow.yml.txt` (repo root). Runs daily, opens an issue if war.gov swaps a file body. (PAT lacks workflow scope, so web-UI install.)
3. **AdSense** — re-review requested 6/10, status "Getting ready." Just wait for the email at developer@fongshuilabs.com.

## ✅ DONE 2026-06-10 (the byte-swap thread)

- Verified war.gov re-processed 62 Release-01 PDFs (smaller + OCR'd, NO content removed) against our archived originals — all 62. Published on `/changes`.
- Evidence preserved: `data/wargov-file-integrity-audit-2026-06-10.json` (old + current sizes/hashes). Old hashes also in git at `6686500`.
- Restored SHA-256 hashes on 136 file pages (Phase B) with honest "verified as of [date]" framing.
- Built `pipeline/integrity_check.py` — per-file body-swap monitor (the durable fix for what the CSV poller misses). Baseline clean.
- Release 02 fully ingested earlier today (222 files, poller URL fixed to uap-data.csv).

## Optional / lower-priority

- Hash the 78 DVIDS videos (manifest sha256 null for them; pages say "pending"). Heavy download. The originals for the 28 Release-01 videos are in `downloads/video/`.
- Gracious reply to the competitor's comment (u/Narrow_Market45) after the post edit.

---

## (Older) 📅 CHECKPOINT — Saturday 2026-06-07 — RESOLVED (Drop 02 landed 5/22, ingested 6/9)

**Step 1 — did Drop 02 actually land?**
- Check `data/poll-state.json` `last_change_at` vs the 6/3 baseline `2026-05-12T23:19:37Z` (row_count was 158)
- Or look for a `[NEW DROP]` auto-poller issue on the repo

**Step 2A — IF Drop 02 landed:** Follow [`DROP02_REACTION.md`](DROP02_REACTION.md) end-to-end. PLUS post a short UPDATE comment on the original r/UFOs viral thread (Aclosmurf account, ~5/20): *"Update — Drop 02 landed [DATE]. [N] new files indexed, scored, SHA-256 verified. Full diff: pursueufotracker.com/changes"* — and drop the homepage banner from DROP02_REACTION.md § 4.

**Step 2B — IF Drop 02 did NOT land:** Skip the full reaction post. Post a short status-check on the original r/UFOs thread: *"Status check [DATE]: war.gov still at 158 rows, no new files since May 11. Auto-poller still active. /changes has the verified diff."*

**Hard Rule #7** — every count/date in the public posts must come from live-pulled `poll-state.json` or the `[NEW DROP]` issue body. No memory, no inference. (The May 11 narrative got mis-told as "5 removed / 3 added / 28 renamed" the first time around — don't repeat.)

Also check on 6/7: r/UFOscience post (was 5/27, draft in DISTRIBUTION.md if still unposted), AdSense site review (~day 16 of the 1-14 window).

---

## 🔥 OPEN ITEMS THAT NEED YOU (operator UI / account actions)

These can't be done by Claude. Most are ~5 min each.

### 1. Reddit pending posts

- **r/UFOscience** — was scheduled Wed 5/27, overdue. Draft is paste-ready in [DISTRIBUTION.md](DISTRIBUTION.md) lines 340-341 (title) + 46-109 (body, verified-corrected). Best window: Tue-Thu 9-10am ET. Friday/weekend posting works but with softer engagement.
- **r/Python pipeline post** — eligible since 5/28. Draft was in the 5/23 chat thread (not yet saved to file). Space ≥48 hrs from r/UFOscience to avoid cross-promo flag on the `Aclosmurf` account.
- **r/datascience** — was scheduled 5/24. Status still unknown to Claude. Confirm whether it posted; if not, decide skip vs ship.

### 2. AdSense (developer@fongshuilabs.com inbox)

- **Site review status** — added 2026-05-22, **day 7** of the 1-14 window today. Approval email may have landed; quick inbox check.
- **Auto Ads UI config** — settings persist through review and activate on approval. Per the 5/22 plan: ad load LOW for pursueufotracker.com, disable Vignette + Anchor + Side rail; ad load Medium for glp1cost.org. AdSense → Ads → By site → pencil icon.

### 3. Cloudflare Email Routing for pursueufotracker.com (~5 min)

The role addresses on `/contact` (`contact@`, `press@`, `privacy@`, `legal@`, `tips@`) currently BOUNCE. CF dashboard → pursueufotracker.com zone → Email → enable → catch-all → developer@fongshuilabs.com.

### 4. Amazon Associates signup (~5 min)

Unlocks the affiliate lever (currently blocked by Hard Rule #8 until approved). Account email developer@fongshuilabs.com, payee Fong Shui Labs LLC EIN, TD business 714. Wait for approval before adding any live links.

---

## 🛰️ UPCOMING REAL-TIME EVENT — Drop 02 (~2026-06-07)

When the auto-poller fires a `[NEW DROP]` GitHub issue: **follow [DROP02_REACTION.md](DROP02_REACTION.md) top-to-bottom**. It has the pre-flight checklist, the verified-data placeholder block, and paste-ready Reddit/X/journalist templates.

Per INCOME_PLAN.md cadence around the drop:
- **Wed 6/3** — pre-Drop-02 reminder post: "Drop 02 expected in ~4 days, here's how we'll catch it."
- **Day of drop** — DROP02_REACTION.md flow.

---

## 🟢 NICE-TO-HAVE / WHEN-YOU-FEEL-LIKE-IT

- **Buttondown email signup** — if email capture matters. Subscribe form is currently a safe-fail RSS/GitHub-Watch placeholder. Welcome email pre-drafted at [data/welcome-email.md](data/welcome-email.md) (already updated to clean drop URL).
- **Video transcripts** — 28 videos still need Whisper transcription. `python -m pipeline.run transcribe` takes hours on CPU.
- **TikTok/Reels clips** — `pipeline.clip_generator` is built but needs ffmpeg in PATH.
- **Methodology page differentiator paragraph** — your call whether to add explicit "why us vs pursueindex.com" framing.
- **Clean /drops/ canonical for Drop 01** — already done this session (commit 7645667). Same pattern applies automatically to Drop 02.

---

## ✅ DONE since 2026-05-09 (the launch + post-launch work)

Most of the items the original TODO listed under "tomorrow" and "this week" have shipped. Highlights of what's been done:

- **Launch shipped** — site live, Reddit r/UFOs went viral 5/20-21 (3.1k pageviews/day spike).
- **War.gov auto-poller** — GitHub Action polling every 30 min weekday business hours (`/`hourly off-hours), `[NEW DROP]` issue on real change. Public repo (Actions minutes free).
- **War.gov May 11 revision** — caught within hours, verified diff published on `/changes` (zero PDFs added/removed; CSV restructured from 161 → 158 rows by adding multi-row representations of 9 PDFs + 1 slug rename).
- **D20 SHA-256 byte-identity verification** — proved the May 8 → May 23 D20 PDF was an identical-bytes storage rename, not a content change.
- **Monetization stack** — Auto Ads script live sitewide (pub-7264251466939264), site review applied 5/22.
- **Analytics** — Plausible Business tier, Stats API enabled (`pipeline/plausible_stats.py`).
- **Google Workspace** activated on fongshuilabs.com (`developer@fongshuilabs.com` is the daily login for AdSense/Plausible).
- **SEO push** (this session, 2026-05-28/29) — Twitter Cards on the 3 static pages that lacked them; clean `/drops/` URLs across template + sitemap + _redirects; file-page breadcrumb deep-links to category hubs (161 new file→hub links concentrating equity); category hubs cross-link each other + 6 editorial pages; homepage hero + JSON-LD corrected to verified top-5 (Hard Rule #7); zero redirect-inducing internal links sitewide.
- **DISTRIBUTION.md cleanup** (this session) — top-5 rewritten to match live data; UAE "4 min 57 sec" → real durations; Apollo "65" removed from top-5; X thread restructured; YouTube script restructured; Bender email Greece disposition corrected; r/conspiracy title softened.
- **DROP02_REACTION.md created** (this session) — real-time playbook for the next drop, every claim placeholder-driven.

---

## Pipeline shortcut

Anything site-content related: `python -m pipeline.run --from build` then commit and push. Cloudflare auto-deploys in ~30 sec, full pipeline including IndexNow ping is `python -m pipeline.run all`.
