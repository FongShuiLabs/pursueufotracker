# pursueufotracker.com — Claude session primer

> Project-level instructions that load automatically at session start.

## Always read first

**Before doing anything on this project, read `.claude/accounts.md`** (local-only, gitignored). It lists which email / account / key owns which service (GitHub, Bing Webmaster, Cloudflare, IndexNow, AdSense, etc.) so you don't ask Anthony the same questions twice.

If `.claude/accounts.md` doesn't exist on this machine, ask Anthony to recreate it from the most recent session that had it.

## Project quick facts

- **Live URL**: https://pursueufotracker.com
- **Repo**: https://github.com/FongShuiLabs/pursueufotracker (auto-deploys on push to `main` via Cloudflare Pages)
- **Stack**: Python pipeline → static HTML → Cloudflare Pages
- **Source of record**: https://www.war.gov/UFO/ (PURSUE program landing page)
- **Pipeline orchestrator**: `python -m pipeline.run all` (or a specific stage like `build`, `build-categories`, `index-now`)
- **Auto-poller**: GitHub Action at `.github/workflows/poll-wargov.yml` polls war.gov every 30 min weekday business hours, hourly off-hours. Opens an issue on real CSV change.

## High-leverage docs

- [`DISTRIBUTION.md`](DISTRIBUTION.md) — Reddit / HN / X / journalist launch material, copy-paste ready
- [`MONETIZE.md`](MONETIZE.md) — Ad / affiliate / sponsor activation guide
- [`PIPELINE.md`](PIPELINE.md) — Pipeline stage docs
- [`DEPLOY.md`](DEPLOY.md) — Deploy mechanics
- [`TODO.md`](TODO.md) — Open work
- [`.claude/accounts.md`](.claude/accounts.md) — Account inventory (local-only)

## Hard rules that apply on this project specifically

These are in addition to Anthony's global rules in `~/.claude/CLAUDE.md`:

1. **Never delete a file page** without explicit Anthony approval, even if war.gov withdraws the underlying file. URL stability across war.gov revisions is a deliberate editorial position (see `/revisions` page).
2. **Never publish a "% chance aliens" or equivalent probability of extraterrestrial origin number.** The scoring rubric is evidentiary-weight only. This refusal is part of the credibility moat.
3. **Never edit `data/poll-state.json` locally and commit.** That file is owned by the bot. Touching it causes false-positive change detection on the next bot run.
4. **War.gov edge requires curl_cffi `chrome120` impersonation + session warmup** against `/UFO/` before fetching the CSV. Custom user-agents get blacklisted. See `pipeline/poll_wargov.py` for working pattern.
5. **Bot author for GH Actions commits**: `pursueufotracker-bot <bot@pursueufotracker.com>`. Don't change this without updating the workflow file.
6. **Cloudflare Pages strips `.html` extensions and 308-redirects.** Canonical URLs must be extension-less (`/files/X` not `/files/X.html`). All sitemap / RSS / JSON-LD url fields enforce this.

## Default voice

- No em dashes (Anthony's global rule). Use ` - ` (space-hyphen-space) or restructure.
- Honest framing, not hype. The site's whole position is "we refuse to oversell."
- Direct, file-path-citing answers. Don't infer site state from memory; grep / read the file first (also Anthony's global rule).
