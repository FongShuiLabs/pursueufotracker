# PURSUE Pipeline Architecture

Static-site pipeline for the Pentagon UAP disclosure mirror. Designed to be:

- **Idempotent** - rerun any stage without re-doing finished work
- **Resumable** - downloads and transcriptions resume on crash
- **Hash-verified** - every downloaded file gets SHA-256 stored in manifest
- **Static-output** - everything ends up as flat HTML/JSON/media that any CDN can serve

## Directory layout

```
ufo-disclosure-site/
├── index.html, styles.css, filter.js     # the homepage (already built)
├── _scratch/                             # raw inputs you save (HTML, HAR, etc.)
├── data/
│   ├── manifest.schema.json              # JSON shape contract
│   ├── manifest.json                     # generated source-of-truth catalog
│   ├── url-list.txt                      # extracted from _scratch
│   └── scoring-rubric.json               # editable Anomalousness weights
├── downloads/{pdf,video,image}/          # raw mirrored files
├── extracted/
│   ├── pdf-text/                         # one .txt per PDF (search corpus)
│   ├── transcripts/                      # .vtt + .json per video (Whisper)
│   └── thumbnails/                       # poster frame per video
├── generated/
│   ├── files/                            # per-file detail HTML pages (162x)
│   ├── og-cards/                         # social share images per file
│   ├── search-index.json                 # Lunr.js index
│   ├── timeline.json                     # for timeline visualization
│   ├── map.json                          # for map visualization
│   └── feed.xml                          # RSS
├── templates/                            # Jinja2 templates
└── pipeline/                             # all Python modules
    ├── config.py
    ├── parse_inputs.py     # _scratch -> data/url-list.txt
    ├── download.py         # url-list.txt -> downloads/ + manifest.json
    ├── hash_files.py
    ├── extract_pdf.py      # downloads/pdf/ -> extracted/pdf-text/
    ├── transcribe.py       # downloads/video/ -> extracted/transcripts/
    ├── thumbnail.py        # downloads/video/ -> extracted/thumbnails/
    ├── score.py            # manifest -> Anomalousness Index per file
    ├── build_search.py     # extracted/* -> generated/search-index.json
    ├── build_site.py       # manifest + extracted -> generated/files/*.html
    ├── gen_og.py           # manifest -> generated/og-cards/*.png
    ├── validate.py         # sanity checks + reports
    └── run.py              # orchestrator: pipeline run [stage]
```

## Stages

| # | Stage          | Module             | Inputs                 | Outputs                           |
|---|----------------|--------------------|------------------------|-----------------------------------|
| 0 | parse-inputs   | parse_inputs.py    | _scratch/*.html, *.har | data/url-list.txt                 |
| 1 | download       | download.py        | data/url-list.txt      | downloads/*, data/manifest.json   |
| 2 | hash           | hash_files.py      | downloads/*            | manifest.json (SHA-256 added)     |
| 3 | extract-pdf    | extract_pdf.py     | downloads/pdf/         | extracted/pdf-text/               |
| 4 | thumbnails     | thumbnail.py       | downloads/video/       | extracted/thumbnails/             |
| 5 | transcribe     | transcribe.py      | downloads/video/       | extracted/transcripts/            |
| 6 | score          | score.py           | manifest + extracted   | manifest.json (scores added)      |
| 7 | search-index   | build_search.py    | extracted/*            | generated/search-index.json       |
| 8 | og-cards       | gen_og.py          | manifest               | generated/og-cards/               |
| 9 | build          | build_site.py      | manifest + extracted   | generated/files/*.html, RSS, etc. |
| - | validate       | validate.py        | everything             | report (no writes)                |

## Runner

```
python -m pipeline.run all                # run every stage in order
python -m pipeline.run download           # just one stage
python -m pipeline.run download --resume  # resume from last partial
python -m pipeline.run --from extract-pdf # everything from stage onward
python -m pipeline.run validate           # sanity-check current state
```

## Manifest schema

Single source of truth. Every stage reads and/or augments it. See `data/manifest.schema.json` for the full contract; key fields:

```json
{
  "id": "apollo-17-triangular-formation",
  "title": "Apollo 17 - Triangular Formation",
  "category": "apollo",
  "agency": "NASA",
  "type": "image",
  "date_event": "1972-12",
  "date_released": "2026-05-08",
  "source_url": "https://www.war.gov/UFO/...",
  "local_path": "downloads/image/apollo-17-triangular-formation.jpg",
  "size_bytes": 4827392,
  "sha256": "...",
  "redacted": false,
  "summary": "...",
  "score": {
    "value": 68,
    "components": {...},
    "rubric_version": "1.0"
  },
  "extracted": {
    "text_path": null,
    "transcript_path": null,
    "thumbnail_path": null
  },
  "geo": { "lat": null, "lng": null, "place": "Lunar sky" }
}
```

## Hosting target

- Static site: Cloudflare Pages (free, fast)
- HD media: Cloudflare R2 (free egress, $0.015/GB storage)
- Search: Lunr.js client-side (no server needed)
- RSS / sitemap: static files

## Dependencies

See `requirements.txt`. Key ones:
- `httpx` for parallel resumable downloads
- `pdfplumber` for PDF text extraction
- `openai-whisper` for video transcription (CPU or CUDA)
- `Pillow` for OG card generation
- `Jinja2` for HTML templating
- `lunr` for search index
- `feedgen` for RSS

`ffmpeg` required on PATH for thumbnails.
