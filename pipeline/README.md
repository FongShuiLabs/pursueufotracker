# pipeline/ - quick reference

```bash
# one-time setup
python -m venv .venv
.venv\Scripts\activate            # PowerShell:  .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# install ffmpeg (for video thumbnails)
# Windows: winget install Gyan.FFmpeg

# the moment you have URLs
python -m pipeline.run all        # runs all 10 stages

# or one stage at a time
python -m pipeline.run parse-inputs   # _scratch/* -> data/url-list.txt
python -m pipeline.run download       # url-list -> downloads/, manifest.json
python -m pipeline.run hash           # SHA-256 every file
python -m pipeline.run extract-pdf    # PDFs -> searchable text
python -m pipeline.run thumbnails     # videos -> poster frames
python -m pipeline.run transcribe     # videos -> Whisper VTT + JSON + TXT
python -m pipeline.run score          # apply Anomalousness Index rubric
python -m pipeline.run search-index   # build Lunr index
python -m pipeline.run og-cards       # per-file social share PNGs
python -m pipeline.run build          # render HTML pages, RSS, sitemap

# resume from a specific stage onward
python -m pipeline.run --from transcribe

# read-only sanity check
python -m pipeline.run validate
```
