# /verdict/ stance file

Operator-editable. Drives the `/verdict/` page. Honest answer to the question
the audience is actually asking. Tone: direct, confident, no hedging-padding,
no sensationalism. Cites into specific files where possible.

---

## Q: Do these files prove aliens exist?

No. None of the 294 files in this release contains a body, a craft, biological
material, or any artifact whose origin can only be extraterrestrial. Anyone
telling you otherwise is selling you something.

## Q: Do they prove aliens don't exist?

Also no. Several files document encounters that the U.S. government has not
been able to explain after review. "Unexplained" is not the same as "alien" -
but it is also not the same as "nothing happened."

## Q: What do they actually prove?

Three things, with file-level evidence:

1. **The U.S. government has been collecting UAP encounter reports continuously
   for at least 80 years**, across the FBI, DoD, NASA, and State Department.
   FBI case file 62-HQ-83894 alone covers 1947-1968.

2. **Trained military and government personnel have observed objects whose
   flight characteristics do not match any known aircraft.** The Greece 2023
   90-degree-turn-at-80mph file documents a maneuver that no known fixed-wing
   or rotary platform can survive without disintegrating.

3. **At least some encounters involve multi-sensor capture, not just eyewitness
   testimony.** The Mediterranean triangular-object file at 25,000 feet is
   military sensor data, not a civilian phone camera.

## Q: What would change the answer?

Any one of these would move the needle from "unexplained" to "extraterrestrial":

- Recovered physical material with isotope ratios outside known terrestrial
  ranges, independently verified by multiple labs
- Biological samples whose genetic structure doesn't match any known Earth
  taxonomy
- Continuous multi-instrument tracking (radar + infrared + visual + telemetry)
  of an object performing maneuvers physically impossible for any known craft,
  released with raw data
- A craft, intact, examined by an international scientific consortium

None of these is in the current PURSUE release.

## Q: Why should I trust this index over war.gov directly?

You shouldn't have to. Every file links back to the war.gov source URL.
Every file has a SHA-256 hash you can independently verify. We mirror;
we don't editorialize the documents themselves. The Anomalousness Index
is our editorial scoring of evidentiary weight, with transparent methodology
- not a claim on the underlying files.

## Q: Did you use AI for the analysis?

Yes, and we want to be specific about what the AI did and didn't do.

**What the AI did:**
- Applied our human-designed scoring rubric to each file's metadata. The rubric defines six components (sensor quality, witness credibility, corroboration, kinematic anomaly, mundane-explanation availability, official disposition) with human-set weights. The AI picked which rubric value best matched each file based on publicly reported descriptions of the file.
- Generated audience-friendly summaries (TL;DR / What we know / What we don't know) from the structured metadata.
- For videos: generated transcripts using OpenAI's Whisper model.
- For PDFs: extracted searchable text using pdfplumber.

**What the AI did NOT do:**
- Did not analyze the underlying files for "alien content" or extraterrestrial markers. That's not what these scores measure and not what AI is capable of.
- Did not editorialize the documents. The files are mirrored as the U.S. government released them.
- Did not generate the rubric weights or the editorial position. Those are human-set and visible at /data/scoring-rubric.json.
- Did not produce a "% chance aliens exist" number. No AI can do that honestly. We refuse to publish one.

**Why disclose this:** other AI-analysis sites don't disclose, then get caught and lose credibility. We tell you upfront. The rubric is open JSON. Every score is reproducible. If you disagree with how a specific file was scored, edit the rubric and recompute - the math is identical.

**Models used:** Claude (Anthropic) for rubric application and summaries. OpenAI Whisper for video transcription. pdfplumber (open-source) for PDF text extraction.

## Q: Why is this site here?

Because war.gov's interface is a flat list, and 294 files deserve search,
categorization, transcripts, and per-file context. Public-domain government
documents should be as accessible as possible. That's the whole pitch.

## Q: Will this site be updated as PURSUE adds more files?

Yes. The Department of War has stated that files will be added to war.gov/UFO
"on a rolling basis." This index re-runs its pipeline on a weekly schedule.
Subscribe to the RSS feed or email list for alerts on new releases.
