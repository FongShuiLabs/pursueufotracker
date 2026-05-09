"""Stage 0: parse _scratch/* (saved HTML, HAR, raw text) -> data/url-list.txt.

Accepts whatever Anthony drops in _scratch/:
- *.html, *.htm, *.mhtml         -> BeautifulSoup link extraction
- *.har                          -> JSON parse, pull request URLs
- *.txt                          -> regex extract URLs

Outputs deduplicated, file-type-filtered URL list to data/url-list.txt.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup

from .config import SCRATCH_DIR, URL_LIST_PATH, file_type_for, ensure_dirs

URL_REGEX = re.compile(r"https?://[^\s\"'<>)\]]+", re.IGNORECASE)


def _is_target_url(url: str) -> bool:
    """Keep only URLs that point to a downloadable file we care about."""
    try:
        path = urlparse(url).path
    except Exception:
        return False
    ext = Path(path).suffix.lower()
    return file_type_for(ext) is not None


def _from_html(html: str, base: str | None = None) -> set[str]:
    soup = BeautifulSoup(html, "lxml")
    out: set[str] = set()
    for tag in soup.find_all(["a", "video", "source", "img", "iframe"]):
        for attr in ("href", "src", "data-src", "data-href", "data-url"):
            v = tag.get(attr)
            if not v:
                continue
            full = urljoin(base, v) if base else v
            if full.startswith(("http://", "https://")) and _is_target_url(full):
                out.add(full)
    # Also catch URLs embedded in inline JSON / scripts
    for m in URL_REGEX.findall(html):
        if _is_target_url(m):
            out.add(m)
    return out


def _from_har(har_text: str) -> set[str]:
    out: set[str] = set()
    try:
        har = json.loads(har_text)
    except json.JSONDecodeError:
        return out
    entries = har.get("log", {}).get("entries", [])
    for e in entries:
        url = e.get("request", {}).get("url")
        if url and _is_target_url(url):
            out.add(url)
    return out


def _from_text(text: str) -> set[str]:
    return {m for m in URL_REGEX.findall(text) if _is_target_url(m)}


def parse_all() -> list[str]:
    ensure_dirs()
    if not SCRATCH_DIR.exists():
        return []
    urls: set[str] = set()
    for p in SCRATCH_DIR.iterdir():
        if not p.is_file():
            continue
        suffix = p.suffix.lower()
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"  ! could not read {p.name}: {e}")
            continue

        if suffix in (".html", ".htm", ".mhtml"):
            found = _from_html(content, base="https://www.war.gov/UFO/")
        elif suffix == ".har":
            found = _from_har(content)
        else:
            found = _from_text(content)

        print(f"  {p.name}: {len(found)} target URLs")
        urls.update(found)

    sorted_urls = sorted(urls)
    URL_LIST_PATH.write_text("\n".join(sorted_urls) + "\n", encoding="utf-8")
    print(f"\n  -> {len(sorted_urls)} unique URLs written to {URL_LIST_PATH}")
    return sorted_urls


if __name__ == "__main__":
    parse_all()
