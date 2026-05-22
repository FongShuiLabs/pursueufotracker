"""Stage 9.5 (optional): generate localized mirrors via DeepL.

Languages targeted: ES, PT, JA, ZH, AR, FR.
Translates: page <title>, <meta description>, h1/h2/p/li text, OG metadata.
Adds <link rel="alternate" hreflang=...> across all language versions.

Requires DEEPL_API_KEY env var. No-op if not set.
"""
from __future__ import annotations
import os
from pathlib import Path

from .config import GENERATED_DIR, ensure_dirs


LANGS = ["es", "pt", "ja", "zh", "ar", "fr"]


def run() -> None:
    ensure_dirs()
    key = os.environ.get("DEEPL_API_KEY")
    if not key:
        print("  DEEPL_API_KEY not set - skipping translation stage")
        print(f"  (would generate: {', '.join(LANGS)})")
        return
    try:
        import httpx
    except ImportError:
        print("  httpx missing")
        return
    src_dir = GENERATED_DIR / "files"
    if not src_dir.exists():
        print("  (no source pages to translate)")
        return
    # Implementation note: DeepL pricing is per character. For the full 161 pages
    # x 6 langs, expect ~5M chars total = ~$25/month on the Pro plan, or free
    # under the 500K-char Free plan if you only translate the index + verdict +
    # top-10 + 10 highest-anomaly file pages (recommended for cost).
    print("  TODO: implement DeepL request loop with hreflang stitching")
    print("  (scaffolded; flip on when DEEPL_API_KEY is configured)")


if __name__ == "__main__":
    run()
