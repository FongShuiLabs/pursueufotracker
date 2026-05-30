# pursueufotracker.com — Claude session primer

> Project-level instructions that load automatically at session start.

## Always read first

1. **`.claude/accounts.md`** (local-only, gitignored). Account inventory: which email / account / key owns which service (GitHub, Bing Webmaster, Cloudflare, IndexNow, Plausible, GSC, etc.) so you don't ask the operator the same questions twice.
2. **`INCOME_PLAN.md` top section** — locked launch deadlines (as of 2026-05-15). If any deadline has slipped >24 hours without explicit reschedule, surface it to the operator at session start.

If `.claude/accounts.md` doesn't exist on this machine, ask the operator to recreate it from the most recent session that had it.

## Project quick facts

- **Live URL**: https://pursueufotracker.com
- **Repo**: https://github.com/FongShuiLabs/pursueufotracker (auto-deploys on push to `main` via Cloudflare Pages)
- **Stack**: Python pipeline → static HTML → Cloudflare Pages
- **Source of record**: https://www.war.gov/UFO/ (PURSUE program landing page)
- **Pipeline orchestrator**: `python -m pipeline.run all` (or a specific stage like `build`, `build-categories`, `index-now`)
- **Auto-poller**: GitHub Action at `.github/workflows/poll-wargov.yml` polls war.gov every 30 min weekday business hours, hourly off-hours. Opens an issue on real CSV change.

## High-leverage docs

- [`DISTRIBUTION.md`](DISTRIBUTION.md) — Reddit / HN / X / journalist launch material, copy-paste ready
- [`DROP02_REACTION.md`](DROP02_REACTION.md) — Real-time playbook for when the auto-poller fires `[NEW DROP]` (pre-flight + Reddit/X/journalist templates, every claim placeholder-driven so nothing posts from memory)
- [`MONETIZE.md`](MONETIZE.md) — Ad / affiliate / sponsor activation guide
- [`PIPELINE.md`](PIPELINE.md) — Pipeline stage docs
- [`DEPLOY.md`](DEPLOY.md) — Deploy mechanics
- [`TODO.md`](TODO.md) — Open work
- [`.claude/accounts.md`](.claude/accounts.md) — Account inventory (local-only)

## Hard rules that apply on this project specifically

These are in addition to the operator's global rules in `~/.claude/CLAUDE.md`:

1. **Never delete a file page** without explicit the operator approval, even if war.gov withdraws the underlying file. URL stability across war.gov revisions is a deliberate editorial position (see `/revisions` page).
2. **Never publish a "% chance aliens" or equivalent probability of extraterrestrial origin number.** The scoring rubric is evidentiary-weight only. This refusal is part of the credibility moat.
3. **Never edit `data/poll-state.json` locally and commit.** That file is owned by the bot. Touching it causes false-positive change detection on the next bot run.
4. **War.gov edge requires curl_cffi `chrome120` impersonation + session warmup** against `/UFO/` before fetching the CSV. Custom user-agents get blacklisted. See `pipeline/poll_wargov.py` for working pattern.
5. **Bot author for GH Actions commits**: `pursueufotracker-bot <bot@pursueufotracker.com>`. Don't change this without updating the workflow file.
6. **Cloudflare Pages strips `.html` extensions and 308-redirects.** Canonical URLs must be extension-less (`/files/X` not `/files/X.html`). All sitemap / RSS / JSON-LD url fields enforce this.
7. **Never publish an unverified claim about war.gov data. HARD RULE.** Every claim that appears on a public page about what the CSV contains, what changed, what was removed, what was added, or how war.gov restructured the data MUST be derived from the current `_scratch/uap-csv.csv` (or a fresh fetch) and verified by direct count or grep before it goes on a page. Inferences about war.gov's intent ("they consolidated X into Y," "they renamed Z," "they switched schemas") are NOT facts and must be flagged as interpretation or omitted. The site's credibility is the entire product; one wrong assertion that a reader can falsify in 30 seconds undoes weeks of trust-building. If a claim is interesting but not verifiable from the raw data, label it "audit in progress" and link the methodology, do not assert. Self-corrections on this page are acceptable; a second wrong assertion in a correction is not. Established 2026-05-20 after two consecutive misreadings of the May 11 revision (the Arabian Gulf "consolidation" framing and the "title reformat" framing both turned out to be inferences, not facts).
8. **No commercial outbound links until the monetization relationship is active. HARD RULE.** Do not add affiliate links, sponsored placements, "as an Associate this site earns" disclaimers, or any other framing that implies a paid commercial relationship UNLESS the underlying contract or program is verified active. Specifically: no Amazon affiliate links until `AMAZON_AFFILIATE_TAG` in `pipeline/config.py` is set to a real tag from an approved Amazon Associates account; no sponsor logos until a signed sponsorship contract exists; no "we earn from this" framing until we actually do. Aspirational affiliate framing ("we'll be an Affiliate once approved") is forbidden because it reads, in screenshot form, identical to an active false claim. The check is binary: are we getting paid for this link right now, today? If no, the link is recommendation-only with no commercial framing, or it does not exist. Established 2026-05-21 after the homepage "Essential UFO Reading" section was discovered to be claiming "Amazon Associate" status with `YOURTAG` placeholder URLs (zero referral fees collectible) and broken ASINs (Elizondo link pointed to a Kenan Thompson book, Coulthart link 404'd) during the r/UFOs viral spike. Credibility cost of a wrong affiliate claim during high traffic >> revenue cost of waiting until approval lands.

## Default voice

- No em dashes (the operator's global rule). Use ` - ` (space-hyphen-space) or restructure.
- Honest framing, not hype. The site's whole position is "we refuse to oversell."
- Direct, file-path-citing answers. Don't infer site state from memory; grep / read the file first (also the operator's global rule).
