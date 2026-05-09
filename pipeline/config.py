"""Central paths, constants, and tunables. Import everything from here."""
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Inputs
SCRATCH_DIR = ROOT / "_scratch"

# Data
DATA_DIR = ROOT / "data"
MANIFEST_PATH = DATA_DIR / "manifest.json"
SCHEMA_PATH = DATA_DIR / "manifest.schema.json"
RUBRIC_PATH = DATA_DIR / "scoring-rubric.json"
URL_LIST_PATH = DATA_DIR / "url-list.txt"

# Downloads
DOWNLOADS_DIR = ROOT / "downloads"
DL_PDF = DOWNLOADS_DIR / "pdf"
DL_VIDEO = DOWNLOADS_DIR / "video"
DL_IMAGE = DOWNLOADS_DIR / "image"

# Extracted
EXTRACTED_DIR = ROOT / "extracted"
EX_PDF_TEXT = EXTRACTED_DIR / "pdf-text"
EX_TRANSCRIPTS = EXTRACTED_DIR / "transcripts"
EX_THUMBNAILS = EXTRACTED_DIR / "thumbnails"

# Generated
GENERATED_DIR = ROOT / "generated"
GEN_FILES = GENERATED_DIR / "files"
GEN_OG = GENERATED_DIR / "og-cards"
GEN_SEARCH = GENERATED_DIR / "search-index.json"
GEN_TIMELINE = GENERATED_DIR / "timeline.json"
GEN_MAP = GENERATED_DIR / "map.json"
GEN_FEED = GENERATED_DIR / "feed.xml"

# Templates
TEMPLATES_DIR = ROOT / "templates"

# Site config
SITE_NAME = "PURSUE UFO Tracker"
SITE_URL = "https://pursueufotracker.com"
SITE_DESCRIPTION = (
    "The independent tracker for the Trump administration's PURSUE UAP "
    "disclosure program. Every file from every drop, indexed, scored on "
    "the Anomalousness Index, and verified against war.gov. Rolling release."
)

# Network
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
DOWNLOAD_CONCURRENCY = 6
DOWNLOAD_TIMEOUT_S = 120
DOWNLOAD_CHUNK_BYTES = 1 << 16  # 64KB
RETRY_MAX = 5
RETRY_BASE_DELAY_S = 2.0

# Whisper
WHISPER_MODEL = "base"  # tiny | base | small | medium | large
WHISPER_LANG = "en"

# File-type detection
PDF_EXTS = {".pdf"}
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".m4v", ".mkv"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tiff", ".tif"}

ALL_DIRS = [
    SCRATCH_DIR, DATA_DIR,
    DOWNLOADS_DIR, DL_PDF, DL_VIDEO, DL_IMAGE,
    EXTRACTED_DIR, EX_PDF_TEXT, EX_TRANSCRIPTS, EX_THUMBNAILS,
    GENERATED_DIR, GEN_FILES, GEN_OG,
    TEMPLATES_DIR,
]

def ensure_dirs() -> None:
    """Create all expected directories. Idempotent."""
    for d in ALL_DIRS:
        d.mkdir(parents=True, exist_ok=True)


def file_type_for(ext: str) -> str | None:
    ext = ext.lower()
    if ext in PDF_EXTS: return "pdf"
    if ext in VIDEO_EXTS: return "video"
    if ext in IMAGE_EXTS: return "image"
    return None


def download_dir_for(file_type: str) -> Path:
    return {"pdf": DL_PDF, "video": DL_VIDEO, "image": DL_IMAGE}[file_type]
