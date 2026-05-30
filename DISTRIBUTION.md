# Distribution Playbook - Copy / Paste Ready

Pre-drafted material for the launch push. Everything is sized to its channel and uses the angle that's already differentiating: open AI scoring + open rubric + public-domain files. The "tens-to-hundreds of thousands per month" revenue target needs traffic; this is the traffic plan.

## NEW ANGLE (updated 5/11/26): war.gov is editing the list in real time

On May 11, 2026, war.gov silently revised the canonical PURSUE file list from 161 to 158: 28 renamed with DOW-UAP-PR## prefixes, 5 removed, 3 added, 6 "Arabian Gulf" entries consolidated under "Middle East". Our automated poller caught it within hours and opened GitHub issues #2 and #3 documenting the deltas.

This is now the LAUNCH STORY:
- "I built an automated tracker that detected war.gov silently editing the PURSUE list - here's the full diff"
- It's a stronger story than "here's another UFO index"
- Journalists especially will pick this up: news.gov editing public records IS the story
- Full change log lives at https://pursueufotracker.com/revisions

Use the revisions URL prominently in EVERY post below.

**Execute in this order** for compounding effect:

1. Day 1 (Tue-Thu, 9am ET): Reddit r/UFOs self-post (single biggest first-week lever)
2. Day 1, evening: Hacker News "Show HN"
3. Day 1-2: X / Twitter thread
4. Day 2: 4 journalist pitch emails
5. Day 3-5: r/aliens, r/HighStrangeness, r/UFOB, r/UFOscience (staggered)
6. Day 7: YouTube video 1 ships
7. Ongoing: HARO / Featured.com / Help A B2B Writer responses (3-5 per day)

---

## 1. Reddit r/UFOs self-post (the big one)

**Subreddit:** r/UFOs (3.4M members)
**Best time:** Tue-Thu, 9-10am ET (catches the daily peak)
**Type:** Text post (NOT a link post - mods auto-remove most link posts; text post with link in comments survives)

### Title (pick one - first one is the strongest now that we have the war.gov-edits angle)
> My automated tracker just caught war.gov silently editing the Trump UFO release. 161 files became 158 overnight. Here's the full diff.

> War.gov quietly revised the PURSUE UFO release on May 11. My auto-poller caught it: the canonical CSV went 161 rows to 158 - zero files added or removed, verified by URL-set diff.

> I had Claude AI score all 161 Trump PURSUE files. Then war.gov restructured the CSV (161 rows to 158, no files removed). Both snapshots are still indexed here.

> All 161 files from the May 8 PURSUE drop, ranked by AI on a transparent rubric (no "% chance aliens" nonsense)

### Body

```
On May 11, war.gov silently restructured the canonical PURSUE CSV. 161 rows became 158 rows. My automated tracker (which polls war.gov every 30 min during weekday business hours via a public GitHub Action) caught it within hours.

What actually changed, verified by URL-set comparison against the May 8 snapshot:
- Zero PDFs added, zero PDFs removed.
- Zero videos added, zero videos removed.
- 9 PDFs that previously had 1 CSV row now have 2-4 CSV rows each (12 extra rows total) - the same PDF cross-referenced from multiple incident-report rows.
- 1 PDF had its storage slug changed (Title unchanged).

The 161 -> 158 row delta is fully explained by those two facts. Full diff and data tables:

https://pursueufotracker.com/changes

For context on what this tracker actually is: I built it for the May 8 PURSUE drop (war.gov/UFO) because the official interface is a flat list of 161 thumbnails with no search, no filtering, no transcripts on the videos. While I was at it, I had Claude AI apply a six-factor rubric to every file and rank them by what I'm calling the Anomalousness Index - NOT "probability of aliens" (anyone publishing that number is selling you something), but evidentiary weight that the encounter remains unexplained after conventional analysis.

The rubric is open JSON, anyone can audit or recompute it:
https://pursueufotracker.com/data/scoring-rubric.json

Six components, weights sum to 1.00:
- Sensor quality (0.25): multi-sensor military > single sensor > photo > eyewitness
- Witness credibility (0.20): astronaut > trained aviator > federal agent > civilian
- Corroboration (0.20): multi-witness multi-instrument > single source
- Kinematic anomaly (0.15): physically impossible > edge of envelope > consistent with known craft
- Mundane explanation availability (0.10): no plausible mundane > strong mundane candidate
- Official disposition (0.10): open after review > resolved conventional

Top 5 by Anomalousness Index (read these first):

1. **NASA-UAP-D3A, Gemini 7 audio, Dec 5 1965** - score 72 (highest in Drop 01)
   Astronaut Frank Borman reports an unidentified object - a "bogey" - to Houston mission control on the Gemini 7 air-to-ground loop, with crewmate Jim Lovell also on the recording. An astronaut eyewitness on the official NASA record is essentially unique in this archive, which is why it tops the rubric. Disposition: open after review.

2. **Unresolved UAP Report, Middle East, May 2022** - score 66
   CENTCOM submitted 5 seconds of infrared footage to AARO. The accompanying mission report (DoW-UAP-D10) called the object a "possible missile" and four other objects "possible birds" - still logged unresolved.

3. **Unresolved UAP Report, Iraq, May 2022** - score 66
   CENTCOM, 10 seconds of infrared footage to AARO. Mission report DoW-UAP-D14 called it a "probable SU-27/35" (a fighter jet), but it was never positively identified, so it stays unresolved.

4. **Unresolved UAP Report, Syria, July 2022** - score 66
   CENTCOM, 14 seconds captured on both an infrared and an electro-optical sensor (DoW-UAP-D16), described as moving north to south. The dual-sensor capture is what edges it into the top tier.

5. **Unresolved UAP Report, Iraq, December 2022** - score 66
   CENTCOM, 10 seconds of infrared footage to AARO (DoW-UAP-D18), object flying west to east before leaving the sensor field of view. Logged unresolved.

A note on the ties: files 2-5 all score 66 because they share the same evidentiary profile - single military platform, military-personnel witness, no published kinematic data, unresolved with no formal review. The rubric reports the honest tie instead of inventing precision to break it. Full ranked list with every score:
https://pursueufotracker.com/top-10

What this tracker does NOT do:
- Claim aliens exist (the files don't prove that)
- Claim aliens don't exist (the files don't prove that either)
- Sell anything (no paywall, no ads currently, no email signup wall)

What it does do:
- Full text search across every PDF
- Whisper-generated transcripts on every video (28 videos, 41 minutes of footage)
- SHA-256 hash on every file so journalists can verify the mirror matches war.gov byte-for-byte
- Public-domain confirmed (17 U.S.C. § 105 - all U.S. Gov works)

Site: https://pursueufotracker.com
Top 10 page: https://pursueufotracker.com/top-10
Methodology (full scoring walkthrough): https://pursueufotracker.com/methodology
The honest verdict on what these files prove: https://pursueufotracker.com/verdict
War.gov revision diff (the story): https://pursueufotracker.com/revisions

Happy to AMA on the methodology, the war.gov diff, or anything else.
```

### After posting
- Reply to top 3-5 comments within the first hour (signals engagement to the algorithm)
- Pin a comment with the methodology link
- Do NOT delete and repost if it doesn't take off - let it ride; mods notice repost behavior

---

## 2. Hacker News "Show HN"

**Submit at:** https://news.ycombinator.com/submit
**Best time:** Mon-Thu, 8-10am ET (off-Pacific peak, fewer competing posts)

### Title (HN charges word penalty for hype - keep it factual)
> Show HN: I scored all 161 Trump PURSUE UFO files with Claude and a public rubric

### URL
> https://pursueufotracker.com

### First comment (post yourself, immediately)

```
Author here. Some quick notes on the build:

- The PURSUE release was 161 files in three formats: PDFs, JPGs, MP4s (videos hosted on DVIDS). The official war.gov interface is a flat list with no search, no filtering, no transcripts on the videos.

- Pipeline is Python: curl_cffi for fetching (war.gov's CF rules reject most non-browser TLS fingerprints), pdfplumber for PDF text extraction, OpenAI Whisper for the video transcripts, Claude (Anthropic SDK) for applying the scoring rubric to each file's description, Jinja2 for rendering, Cloudflare Pages for static hosting.

- The Anomalousness Index is six weighted components, all human-designed, weights sum to 1.00. Rubric lives as open JSON at https://pursueufotracker.com/data/scoring-rubric.json - anyone can recompute every score. I deliberately did NOT publish a "% chance aliens" number; that number is not honestly computable from these files.

- GitHub Action polls the canonical war.gov UAP CSV every 30 minutes during weekday business hours; when the hash changes, it opens an issue. Cloudflare auto-deploys when I push.

- Source is public on GitHub: https://github.com/FongShuiLabs/pursueufotracker

Happy to answer questions on the pipeline, the rubric, or why I made specific scoring choices.
```

### HN behavior
- Reply to ALL top-level comments within 4 hours
- Don't argue. Acknowledge methodology critiques and link to the rubric.
- If "this is hype" comes up, point to the rubric and the explicit "no probability of aliens" stance

---

## 3. X / Twitter thread

**Best time:** 10am-1pm ET weekday

### Tweet 1 (hook)
> I had Claude AI rank all 161 Trump PURSUE UFO files on six evidentiary axes.
>
> The #1 most anomalous file isn't Apollo. It isn't Roswell. It's astronaut Frank Borman's audio from Gemini 7 in 1965.
>
> Open rubric. Public data. No "% chance aliens" nonsense. 🧵
>
> https://pursueufotracker.com

### Tweet 2
> The rubric scores 6 things, weights sum to 1.00:
>
> • Sensor quality (.25)
> • Witness credibility (.20)
> • Corroboration (.20)
> • Kinematic anomaly (.15)
> • Mundane explanation availability (.10)
> • Official disposition (.10)
>
> Open JSON. Anyone can recompute every score: pursueufotracker.com/data/scoring-rubric.json

### Tweet 3
> #1 - NASA-UAP-D3A, Gemini 7 Audio, 1965. Score 72.
>
> Astronaut Frank Borman reports an unidentified object to Houston mission control. On the official NASA voice loop. Astronaut-witness on the federal record is essentially unique in the archive.
>
> [link to the file page]

### Tweet 4
> The next tier all score 66 - four CENTCOM infrared tracks submitted to AARO and logged unresolved:
>
> • Middle East, May 2022 (5 sec)
> • Iraq, May 2022 (10 sec)
> • Syria, July 2022 (14 sec, dual-sensor)
> • Iraq, December 2022 (10 sec)

### Tweet 5
> The standout of that tier: Syria, July 2022.
>
> 14 seconds captured simultaneously on infrared AND electro-optical sensors. Multi-sensor capture is what closes off the easy single-sensor-artifact explanation.
>
> [link]

### Tweet 6
> The most visually striking file in the 66-point tier: Greece, January 2024.
>
> A military operator logged a diamond-shaped object at ~499 mph (434 kn), visible ONLY on the Short-Wave Infrared sensor, over ~2 minutes.
>
> Scores 66 - tied with the rest of the top tier; only Gemini 7's 72 sits above it. [link]

### Tweet 7
> Bonus for the data nerds: war.gov quietly restructured the file list on May 11 (161 CSV rows to 158).
>
> My auto-poller caught it within hours. Zero files added or removed - verified by URL-set diff. Full breakdown:
>
> pursueufotracker.com/changes

### Tweet 8 (close)
> What this site does:
>
> ✅ Full text search across every PDF
> ✅ Whisper transcripts on every video
> ✅ SHA-256 hash verification against war.gov
> ✅ Public domain (17 USC § 105 - U.S. Gov works)
> ✅ No paywall, no email gate
>
> https://pursueufotracker.com
>
> Tag @ross_coulthart @LueElizondo @TheDebrief - methodology feedback welcome.

---

## 4. Journalist pitch emails (send 4 separate emails, NOT a blast)

### Email to Ross Coulthart (NewsNation / Need to Know)

**Subject:** Independent tracker scored all 161 Trump PURSUE files - top 5 + open rubric

```
Hi Ross,

Quick pitch in case useful for a segment or a Need to Know episode.

I built an independent tracker for the PURSUE disclosure that does what war.gov/UFO doesn't: full-text search, video transcripts, SHA-256 verification against the original files, and an AI-applied evidentiary-weight score on every encounter.

The scoring rubric is published as open JSON - six components, weights sum to 1.00. NOT a "probability of aliens" number; that number isn't honestly computable from these files and I refused to publish one. It's evidentiary weight that the encounter remains unexplained after conventional analysis.

Top 5 by score:
1. NASA-UAP-D3A, Gemini 7 Audio, 1965 (Frank Borman) - 72
2. Unresolved UAP Report, Middle East, May 2022 (CENTCOM IR) - 66
3. Unresolved UAP Report, Iraq, May 2022 (CENTCOM IR) - 66
4. Unresolved UAP Report, Syria, July 2022 (dual-sensor IR+EO) - 66
5. Unresolved UAP Report, Iraq, December 2022 (CENTCOM IR) - 66

Site: https://pursueufotracker.com
Press kit (free embed assets, fact sheet, contact): https://pursueufotracker.com/press
Open rubric: https://pursueufotracker.com/data/scoring-rubric.json
Top 10 with full reasoning: https://pursueufotracker.com/top-10

Public domain on all 161 files (17 U.S.C. § 105) so anything is free to embed, quote, or screenshot. Happy to be on a segment to walk through the methodology or just send raw data.

[Your name]
[Your phone]
[Your email]
```

### Email to George Knapp (KLAS / Weaponized)

```
Hi George,

Built an independent index for the PURSUE drop that surfaces what war.gov's flat list hides. Two things you might care about:

1. NASA-UAP-D3A - Frank Borman, Gemini 7, December 1965. Astronaut-on-the-record audio of an unidentified object in low Earth orbit, on the official NASA voice loop. This is the highest-scoring file in the archive on a six-axis rubric I published openly.

2. Greece, January 2024 - SWIR-only diamond-shaped object tracked at ~499 mph, invisible to standard IR and EO. The classified sensor capture pattern is the kind of detail that's hard to spin as a balloon.

Site: https://pursueufotracker.com
Open rubric: https://pursueufotracker.com/data/scoring-rubric.json
Public-domain data, free to use on Weaponized.

Happy to send raw scoring data, talk through methodology, or just be a free factchecker on file claims.

[Your name]
```

### Email to Bryan Bender (Politico) or Tim McMillan (The Debrief)

```
Hi [Bryan/Tim],

For your UAP beat - independent tracker for the May 8 PURSUE drop with full-text search across all 161 files, Whisper-generated video transcripts, and SHA-256 verification against war.gov. Public domain so cite freely.

Two angles that might be reportable:

1. **The scoring story.** I had Claude apply an open six-axis rubric to every file. The math is auditable (rubric weights sum to 1.00 as published JSON). Highest-scoring file is Frank Borman's 1965 Gemini 7 audio - astronaut-on-the-record, which is essentially unique in the archive.

2. **The Greece SWIR file.** January 2024. Military operator tracked a diamond-shaped UAP at ~499 mph (434 kn) visible ONLY on Short-Wave Infrared, over ~2 minutes. Not visible on standard IR or EO. Scored 66 on the rubric (tied with the top tier; only Gemini 7's 72 sits above it). AARO disposition is unresolved, no formal review. The sensor specificity is unusual.

Press kit (fact sheet + embed assets): https://pursueufotracker.com/press
Rubric: https://pursueufotracker.com/data/scoring-rubric.json

Available for background or attribution. No agenda, no claim that aliens exist - just better-indexed government records than war.gov ships natively.

[Your name]
```

### Email to Ryan Sprague (Somewhere in the Skies) - podcast pitch

```
Hi Ryan,

Big fan of Somewhere in the Skies. Built an independent tracker for the PURSUE disclosure that does what war.gov doesn't - full-text search, video transcripts, AI scoring on an open rubric.

I think the methodology might be interesting for a Somewhere segment: I deliberately refused to publish a "probability of aliens" number (because that's not honestly computable from these files) but I DID publish a six-axis evidentiary-weight rubric where the math is fully auditable. It's a different way to talk about UAP evidence without the usual either-or trap.

Would love to come on if it's a fit. 30-45 min, methodology + tour of the highest-scoring files (Gemini 7 Borman, Greece SWIR, Apollo 17).

Site: https://pursueufotracker.com
Rubric: https://pursueufotracker.com/data/scoring-rubric.json

[Your name]
[Phone]
```

---

## 5. r/aliens / r/HighStrangeness / r/UFOB / r/UFOscience (staggered, Day 3-5)

Same body as the r/UFOs post, but DIFFERENT title each time (don't post identical titles or you'll be tagged as spam).

### r/aliens title
> The Trump UFO files, ranked by AI on a transparent six-factor rubric (highest-scoring is from 1965)

### r/HighStrangeness title
> 161 PURSUE files with the most anomalous ones called out - including 1965 astronaut audio of a "bogey" and unresolved CENTCOM infrared tracks

### r/UFOB title
> Indexed every file from the May 8 disclosure with full transcripts + AI scoring on an open rubric

### r/UFOscience title (more sober audience)
> Open six-axis scoring rubric applied to all 161 PURSUE files. Methodology critique welcome.

### r/conspiracy title
> Trump's UFO files ranked by AI - the open methodology and the 5 the government can't explain

---

## 6. YouTube video script (Video 1: the launch)

**Length:** 6-9 min
**Style:** screen recording walkthrough + voiceover, no face

### Outline

```
[0:00-0:20] HOOK
"On May 8, 2026, the Trump administration declassified 161 UFO files. War.gov dropped them as a flat list with no search, no transcripts, no way to compare them. So I had Claude AI score every single one on six evidentiary axes. Here are the five most anomalous, and how the scoring actually works."

[0:20-1:00] CONTEXT
"PURSUE stands for Presidential Unsealings and Reporting System for UAP Encounters. 161 files from FBI, the Department of War, NASA, and the State Department. Spans 80 years - from 1947 FBI investigations of Roswell, to NASA Apollo photography, to military encounter footage as recent as 2024. All files are public domain. I built pursueufotracker.com because the official interface makes it nearly impossible to actually read what's in there."

[1:00-2:00] THE METHODOLOGY (critical - earns credibility)
"The score is what I call the Anomalousness Index. NOT a probability of aliens. Anyone publishing that number is selling you something. The score reflects evidentiary weight that the encounter remains unexplained after conventional analysis. Six components, weights sum to 1.00. [show rubric on screen]. The full rubric is open JSON - anyone can recompute every score."

[2:00-3:30] FILES #2-5: THE 66-POINT TIER
"After Gemini 7's 72, the next tier on the rubric is a four-way tie at 66 - all CENTCOM infrared tracks, submitted to AARO, logged unresolved. Middle East, May 2022: five seconds of IR, the mission report flagged it as a 'possible missile.' Iraq, May 2022: ten seconds of IR, the report flagged it as a 'probable SU-27 or 35' that was never confirmed. Iraq, December 2022: ten seconds of IR, object tracked west-to-east. And the standout of the tier - Syria, July 2022: fourteen seconds captured simultaneously on infrared AND electro-optical sensors. The dual-sensor capture is what closes off the easy single-sensor-artifact explanation."

[3:30-5:00] BONUS: THE MOST VISUALLY STRIKING FILE
"Doesn't make the top five by score - only because roughly fifteen files tie at 66 - but it's the file people remember: Greece, January 2024. A military operator logged a diamond-shaped object at approximately 434 knots, that's about 499 miles per hour, visible ONLY on the Short-Wave Infrared sensor. Invisible on standard IR. Invisible on EO. Over roughly two minutes. The mission report explicitly cautions that its descriptions should not be read as conclusive about the object's actual features - so I'm not telling you what it was. I'm telling you what the sensor recorded."

[5:00-6:30] FILE #1: GEMINI 7 (the twist)
"This is what made me build the site. NASA-UAP-D3A. Gemini 7. December 5, 1965. Astronaut Frank Borman reports an unidentified object - he called it a 'bogey' - to Houston mission control. On the official NASA voice loop, with crewmate Jim Lovell also on the recording. Audio is on the site. Astronaut-witness on the federal record is essentially unique in this archive. The Apollo photos can be explained. The lunar formations can be debated. But trained astronauts reporting an unidentified object to mission control, on the record, is a different category of evidence."

[6:30-7:30] CLOSE
"Site is pursueufotracker.com. All 161 files, full text search, transcripts on every video. The rubric is open. SHA-256 hashes verify against war.gov. Public domain. Subscribe if you want to be alerted when Drop 02 lands - my auto-poller checks war.gov every 30 minutes. Link in description."
```

---

## 7. HARO / Featured.com / Help A B2B Writer (ongoing)

Set up alerts for "UFO", "UAP", "Pentagon disclosure", "AARO", "Trump UFO". Respond to every relevant query within 4 hours.

**Response template:**

```
[Reporter name],

Re: [their question topic]

I run pursueufotracker.com, the independent tracker for the Trump administration's PURSUE UAP disclosure. Happy to provide [data / quote / context].

[1-2 sentence direct answer]

[1 specific file or fact that supports the answer]

If you want raw scoring data, transcripts, or any of the 161 underlying files (all public domain), the API is at https://pursueufotracker.com/api/files.json and the press kit is at https://pursueufotracker.com/press.

[Your name]
Operator, PURSUE UFO Tracker
[Phone if comfortable]
```

---

## Tracking what worked

After two weeks, list:
- Which Reddit post drove the most clicks (Cloudflare analytics under pursueufotracker.com)
- Which journalist replied
- Which podcast pitch booked
- HN thread peak position
- X thread peak engagement

Double down on whatever worked. Drop whatever didn't.
