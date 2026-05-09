# Outreach Kit

Pre-drafted launch material. Use as-is or edit. Honesty over hype on every channel - that's the position that compounds.

---

## X / Bluesky launch thread

> 1/ The Trump administration is releasing declassified UFO files on a rolling basis under PURSUE. Drop 1 on May 8 was 162 files: FBI, DoD, NASA, State.
>
> I built the tracker that indexes every one. Searchable, scored, transcripts. Free.
>
> [yourdomain.com]
>
> 2/ It is not a "% chance aliens" site. Nobody can honestly produce that number.
>
> Each file gets an Anomalousness Index (0-100) - evidentiary weight that the encounter remains unexplained after conventional analysis. Methodology is open JSON. Recompute it yourself.
>
> [yourdomain.com/verdict.html]
>
> 3/ The most striking files in Drop 1 aren't the famous ones. The Greece 2023 90-degree-turn at 80mph is a maneuver no known aircraft can survive. Score 84.
>
> Top 10 most anomalous: [yourdomain.com/top-10.html]
>
> 4/ Every video has a Whisper-generated transcript. Every PDF is full-text searchable. Every file has a SHA-256 hash you can verify against the war.gov original.
>
> If you're a journalist or researcher, the press kit + verification manifest is at [yourdomain.com/press.html]
>
> 5/ The Trump administration says more drops are coming on a rolling basis. The site polls war.gov/UFO daily.
>
> Subscribe and you'll know within minutes of the next drop landing.
>
> [yourdomain.com] (subscribe form on the homepage)

---

## Reddit r/UFOs launch post

> **Title:** I built a free, searchable mirror of the entire Trump PURSUE UFO release - every file scored on evidentiary weight
>
> **Body:**
>
> All 162 files from the May 8 drop are indexed at [yourdomain.com]. Every video has a Whisper transcript. Every PDF is full-text searchable. Every file links back to war.gov with a SHA-256 hash for verification.
>
> I scored each file on what I'm calling the **Anomalousness Index** - 0-100 reflecting evidentiary weight that the encounter remains unexplained after conventional analysis. **It is not a "% chance aliens"** - nobody can honestly produce that number. The rubric is open JSON; you can recompute every score yourself.
>
> The Greece 2023 (90-degree turn at 80 mph) and Western US "Eye of Sauron" orb files scored highest. Top 10 here: [yourdomain.com/top-10.html]
>
> The Trump administration says more files come on a rolling basis. The site auto-rebuilds when new drops land. Subscribe on the homepage if you want next-drop alerts.
>
> Free, no ads, no signup wall, no paywall. Public domain documents deserve to be accessible.
>
> Feedback welcome.

**Note:** r/UFOs is aggressive about self-promo. Read their rules before posting and engage in comments authentically. Don't post and ghost.

---

## Hacker News launch (Show HN)

> **Title:** Show HN: Searchable mirror of the Trump administration's PURSUE UFO release
>
> **Body (first comment):**
>
> Hi HN - I built this over the weekend after the Pentagon launched war.gov/UFO with 162 declassified UAP files.
>
> The official site has no search, no transcripts, no per-file context. This mirror adds:
>
> - Full-text search across all PDFs (pdfplumber + Lunr.js client-side)
> - Whisper-generated transcripts for all 28 videos with VTT subtitle tracks
> - SHA-256 verification manifest for journalists
> - JSON API at /api/files.json
> - An "Anomalousness Index" 0-100 per file, with open methodology - explicitly NOT a "probability of alien origin" because no honest analyst can produce that number
> - Drop tracker for the rolling-release cadence
>
> Stack: Python pipeline (httpx + pdfplumber + Whisper + Pillow + Jinja2) → static HTML → Cloudflare Pages + R2.
>
> Curious what HN thinks of the score methodology. Rubric is at /data/scoring-rubric.json on the site.

---

## UAP-beat journalist email template

```
Subject: Built the Trump PURSUE files mirror - searchable, transcribed, verifiable

Hi [Journalist],

Saw your [SPECIFIC piece - e.g., "Greece 2023 piece in The Debrief"]. Wanted to share something I built that should make Drop 1 (and every drop after) easier to cover:

[yourdomain.com]

What's there:
- All 162 files from the May 8 PURSUE release, indexed and ranked
- Whisper transcripts on every video (full-text searchable)
- SHA-256 hash on every file - your fact-checker can verify integrity vs. war.gov
- JSON API + verification manifest at /press.html
- Per-file detail pages with embed code if you want to drop a player into your story

Free, no paywall, no signup. CC0 metadata. Cite freely.

The Trump administration is signaling rolling releases. The tracker auto-indexes within hours of each new drop. Happy to add you to the press list for advance notification when Drop 2 lands - reply with "add me" if useful.

Best,
[Anthony]
```

**Targets (research recent bylines on each before sending):**
- Ross Coulthart (NewsNation)
- George Knapp (KLAS / Mystery Wire)
- Bryan Bender (Politico defense reporter)
- Marik von Rennenkampff (The Hill)
- Tim McMillan (The Debrief)
- Ralph Blumenthal (NYT freelance, broke 2017 story)
- Leslie Kean (NYT freelance, same)
- Jeremy Corbell (independent / Need To Know)
- George Knapp + Jeremy Corbell - Weaponized podcast (highest-leverage one-shot)

---

## YouTube creator pitch (UAP space)

```
Subject: Free transcripts + HD downloads for your PURSUE coverage

Hi [Creator],

Loved your [SPECIFIC video]. Quick offer: I built a tracker for the Trump PURSUE UFO releases at [yourdomain.com] and want to make your covering it easier.

For every video in the war.gov release, the site has:
- Full Whisper transcript (txt + VTT - drop straight into your editor)
- HD download link
- SHA-256 hash for verification
- Embed code if you want a player on your channel page
- Free OG cards per file for thumbnail inspiration

JSON API at /api/files.json if you want to script anything.

Drop 2 is expected on a rolling basis - happy to give you advance notice when it lands. Reply "add me" to be on the early-notification list.

No reciprocal ask. Public-domain docs should be accessible. If the tracker saves you 20 minutes editing one video, that's worth it.

Best,
[Anthony]
```

**Targets:**
- Need To Know (Knapp + Corbell)
- That UFO Podcast
- 7 News Spotlight (Ross Coulthart's channel)
- Theories of Everything (Curt Jaimungal)
- Project Unity
- The Why Files
- Joe Rogan booking (long shot but possible if Coulthart references it)

---

## Wikipedia citations (slow burn, permanent)

After the site has been live for 30+ days and is being cited by mainstream press:

1. Edit the existing Wikipedia article on **Unidentified anomalous phenomena** - add a citation under "Government investigations" linking to the Trump PURSUE tracker as a primary-source archive.
2. Edit **Pentagon UAP** related articles - add references to specific files (e.g., the Greece 2023 file).
3. Create a stub article on **PURSUE (program)** if one doesn't exist; cite the tracker as primary source.

Wikipedia is hard - editors will revert anything that smells promotional. The play is: cite to specific factual claims (not "this site is cool"), use neutral tone, and only after enough independent press coverage exists to establish notability. Six months in, this is one of the highest-permanence backlinks possible.

---

## Subreddit map (target audiences)

| Subreddit       | Subs   | Tone          | Post type that wins |
|-----------------|--------|---------------|----------------------|
| r/UFOs          | 3.0M   | Tribal, hot   | Top-10 listicle, specific-file deep dive |
| r/UFOB          | 200k   | Skeptical     | Verification manifest, SHA hashes, "you can fact-check us" |
| r/HighStrangeness | 350k | Open          | Eye-of-Sauron orb file, weird kinematics |
| r/UAP           | 100k   | Quiet, mature | Methodology post, Anomalousness Index discussion |
| r/aliens        | 1.2M   | Casual        | Top-10, headline-grabber files |
| r/conspiracy    | 2.0M   | Hot, partisan | Stay neutral; "here are the documents themselves" |
| r/space         | 25M    | Skeptical     | Apollo files, NASA-specific deep dive |
| r/Documentaries | 23M    | Curious       | Top-10 + transcripts as "self-watch documentary" |

Stagger posts across 7-10 days. Same site, different angle on each. Engage in every comment thread for the first 24h - reply rate is what determines whether mods promote or shadowban.

---

## Press release (for /press/ page)

A formatted version of this lives in [generated/press.html](generated/press.html). Key talking points:

> **For immediate release - May 9, 2026**
>
> **Independent tracker indexes Trump administration's first PURSUE UFO drop, 162 files searchable in minutes**
>
> An independent project has launched a free, searchable mirror of the Department of War's PURSUE (Presidential Unsealings and Reporting System for UAP Encounters) UFO disclosure program. Every file from the May 8 release is now categorized, transcribed, scored on a transparent evidentiary-weight rubric, and verified by SHA-256 hash against the war.gov original.
>
> "The Pentagon's interface is a flat list," said the site's founder. "162 declassified files deserve search, transcripts, and per-file context. Public-domain documents should be as accessible as possible."
>
> The tracker uses an Anomalousness Index - a 0-100 score reflecting evidentiary weight that an encounter remains unexplained after conventional analysis. "It is explicitly not a probability of extraterrestrial origin," the founder added. "Nobody can honestly produce that number, and any site claiming to is selling something. We score evidentiary weight; readers draw their own conclusions."
>
> The Trump administration has stated additional files will be released on a rolling basis. The tracker indexes new files within hours of each release.
>
> [yourdomain.com]
>
> Press contact: [your email]

---

## Operator's notes

- **Don't oversell.** The strongest position is "we mirror, we score, we don't editorialize the underlying files." Hype shortens the audience's lifecycle.
- **Reply to everyone for the first 72 hours.** This is when retention compounds.
- **Don't argue with disbelievers.** Honest framing already concedes the right things; show them the methodology and let it breathe.
- **Save every press mention.** Build a `/in-the-news/` page from the second mention onward. Social proof multiplies inbound.
- **The SECOND drop is more important than the first.** First drop = curiosity spike. Second drop = test of whether you're a one-time Reddit post or the durable canonical tracker. Pre-stage the Drop 2 outreach now.
