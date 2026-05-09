"""Stage 8: generate per-file Open Graph share cards (1200x630 PNG).

Pillow-based. One card per file -> generated/og-cards/<id>.png.
"""
from __future__ import annotations
import json
from pathlib import Path

from .config import MANIFEST_PATH, GEN_OG, ensure_dirs


W, H = 1200, 630
BG = (4, 6, 13)
BLUE = (82, 180, 255)
GRAY = (168, 184, 204)
WHITE = (255, 255, 255)


def _font(size: int):
    from PIL import ImageFont
    candidates = [
        "C:/Windows/Fonts/seguibl.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for c in candidates:
        if Path(c).exists():
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap(draw, text: str, font, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _make_card(out: Path, title: str, agency: str, score: int) -> None:
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Top strip
    d.rectangle([0, 0, W, 6], fill=BLUE)
    d.text((48, 32), "PURSUE FILES INDEX", font=_font(22), fill=BLUE)
    d.text((48, 64), agency.upper(), font=_font(18), fill=GRAY)

    # Title
    title_font = _font(64)
    lines = _wrap(d, title, title_font, max_w=W - 360)
    y = 180
    for line in lines[:3]:
        d.text((48, y), line, font=title_font, fill=WHITE)
        y += 78

    # Score circle
    cx, cy, r = 1020, H // 2, 130
    # ring
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=BLUE, width=8)
    # value
    s_font = _font(96)
    bbox = d.textbbox((0, 0), str(score), font=s_font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((cx - tw // 2, cy - th // 2 - 8), str(score), font=s_font, fill=WHITE)
    d.text((cx - 80, cy + r + 16), "ANOMALOUSNESS", font=_font(16), fill=BLUE)

    # Footer
    d.text((48, H - 60), "war.gov/UFO   |   Independent index", font=_font(20), fill=GRAY)

    img.save(out, "PNG", optimize=True)


def run() -> None:
    ensure_dirs()
    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return
    try:
        import PIL  # noqa: F401
    except ImportError:
        print("  Pillow missing. pip install -r requirements.txt")
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    for f in manifest["files"]:
        out = GEN_OG / f"{f['id']}.png"
        if out.exists():
            continue
        score = (f.get("score") or {}).get("value", 50)
        _make_card(out, f.get("title") or f["id"], f.get("agency") or "OTHER", score)
    print(f"  og cards: {len(manifest['files'])}")


if __name__ == "__main__":
    run()
