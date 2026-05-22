# Reach playbook

The site's job: be the most-trusted, most-shareable, fastest-loading mirror of the PURSUE release in every major language. Every choice below ladders up to that.

## SEO surface area

- **161 files × 6 languages = ~966 indexed pages.** Every long-tail search ("Apollo 17 UFO", "FBI Roswell memo 1947", "Greece UAP 2023") lands on us.
- **Per-file Schema.org** (`CreativeWork`, `VideoObject`, `Dataset`). Earns rich results.
- **Per-file `hreflang`** for ES / PT / JA / ZH / AR / FR. Google surfaces localized URLs in each market.
- **Sitemap regenerated every build.** Pinged to Google + Bing search consoles on deploy.
- **Per-file canonical URLs.** No duplicate-content penalty.
- **Open-graph + Twitter cards per file.** Every link preview is unique.

## Distribution

| Channel | Move |
|---|---|
| Reddit (r/UFOs 3M+, r/HighStrangeness, r/UAP, r/UFOB) | Top-10 page launch post + per-file deep-link in topic threads |
| Hacker News | "Show HN: Searchable mirror of the Pentagon's PURSUE UAP release" |
| X / Bluesky | Threaded launch with OG cards; per-file shares with copy-link-with-timestamp |
| YouTube | 28 videos re-uploaded with full transcripts + site URL pinned to description |
| TikTok / Reels / Shorts | Auto-generated 9:16 vertical clips with captions burned in (one per video = 28 short-form posts) |
| Wikipedia | Add as primary-source citation on PURSUE / UAP / specific incident pages |
| Newsletter | Email capture; alert on rolling PURSUE additions |
| RSS | Auto-pulled by aggregators (Feedly, Inoreader, NewsBlur) |
| Press kit | `/press/` page: assets, fact sheet, embed code, contact, checksums |
| Journalist outreach | Drafted templates for Coulthart, Knapp, NYT/WaPo UAP beat, Vice, Motherboard |
| Podcasts | Drafted pitches: Weaponized, MysteryWire, Need to Know, Theories of Everything |
| API | `/api/files.json` for devs and researchers (free backlinks) |

## Performance budget

Audience is global, much of it on mobile / 3G. Targets:

- **LCP < 2.0s** on 3G mobile (largest contentful paint)
- **CLS < 0.1** (no layout shift)
- **Total page weight < 200KB** for index/listing pages
- **Per-file pages: lazy-load video, inline critical CSS, defer everything else**
- **Cloudflare Pages + R2 origin: 250+ POPs worldwide, free egress**

## Trust signals (the honest-is-better-marketing payoff)

- **/verdict/ page** answers "do aliens exist" honestly. Quotable. Cite-able.
- **SHA-256 on every file.** Journalists can verify integrity vs. the war.gov original.
- **Source URL displayed** on every file. We never claim the document; we mirror and index it.
- **Methodology transparent.** Rubric is open JSON; anyone can recompute scores.
- **No paywall, no ads, no signup wall.** Free public archive.
- **CC0 metadata, public-domain mirror.** Nothing copyrighted, nothing locked.

## What we measure

Plausible Analytics (privacy-first, GDPR-clean, ~10KB):
- Page views, top files, top countries, referrers
- Search queries inside the on-site search
- Share-button clicks per file
- Top-10 page conversion to deep-file pages

No cookies, no PII, no creep factor. Adds to trust signal.

## Ranking the reach moves by ROI

1. **Per-file detail pages with TL;DR + share buttons** (huge SEO surface, native virality)
2. **/verdict/ page** (the link journalists cite)
3. **/top-10/ page** (the link normies share)
4. **YouTube re-uploads with transcripts** (YouTube SEO is a separate ocean)
5. **Multi-language mirrors** (3-5x audience cap)
6. **TikTok/Reels vertical clips** (highest viral coefficient per minute of effort)
7. **Press kit + journalist outreach drafts** (one good citation = months of organic)
8. **Email capture for rolling drops** (PURSUE adds files; we own the alert channel)
9. **Wikipedia citations** (slow burn, permanent)
10. **API endpoint** (devs build derivative tools, all linking back)
