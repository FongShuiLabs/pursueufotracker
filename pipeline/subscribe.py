"""Sitewide subscribe component - single source of truth + stamper stage.

The email-capture form is pre-staged: every surface renders whatever
``subscribe_html()`` returns, driven by two values in ``pipeline/config.py``:

    ESP_PROVIDER = ""            # "" | "buttondown" | "substack"
    ESP_HANDLE   = ""            # the Buttondown username / Substack subdomain

While ESP_PROVIDER is empty every surface shows the safe-fail placeholder
(RSS + GitHub Watch, "email signup launching soon") - byte-for-byte the block
the site has carried since launch. The moment the operator picks an ESP:

    1. Set ESP_PROVIDER + ESP_HANDLE in pipeline/config.py
    2. python -m pipeline.run wire-subscribe   (stamps homepage + statics)
    3. python -m pipeline.run build            (file pages, via build_site ctx)
    4. python -m pipeline.run build-categories (category hubs)
    5. Verify locally, commit, push. Live in ~2 minutes.

Surfaces and how each one gets the block:
    - index.html ................. stamped in place by this stage ("homepage" variant)
    - generated/<essay>.html ..... 51 hand-authored statics, stamped in place
    - templates/file.html.j2 ..... renders {{ subscribe_html|safe }} (build_site ctx)
    - pipeline/build_categories .. calls subscribe_html("page") directly

Stamping is marker-based and idempotent. On first contact a legacy
``<div class="subscribe-bar">...</div>`` block is converted to a marker-wrapped
managed block; after that only the region between markers is ever replaced.
Files without a subscribe-bar are left alone (scope stays deliberately fixed).

Provider notes (verified against each ESP's documented embed patterns):
    - Buttondown exposes a plain-HTML POST endpoint at
      buttondown.com/api/emails/embed-subscribe/<handle> - a native <form>
      works with no JS and degrades cleanly.
    - Substack has NO supported cross-origin POST endpoint; the supported
      no-backend embed is the <handle>.substack.com/embed iframe. We render
      that plus a plain link fallback underneath for iframe-blocked contexts.

Plausible: the placeholder links keep their existing Subscribe events
(channel: rss/github). Live forms fire Subscribe with channel:'email' and an
esp prop, so conversion shows up in the same event view the site already uses.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from .config import ROOT, GENERATED_DIR

try:  # both optional so the site keeps building before the ESP decision
    from .config import ESP_PROVIDER  # type: ignore
except ImportError:  # pragma: no cover
    ESP_PROVIDER = ""
try:
    from .config import ESP_HANDLE  # type: ignore
except ImportError:  # pragma: no cover
    ESP_HANDLE = ""

MARK_START = "<!-- subscribe:start (managed by pipeline/subscribe.py - do not hand-edit; run `python -m pipeline.run wire-subscribe`) -->"
MARK_END = "<!-- subscribe:end -->"

# Legacy block: opens with the bar div and always closes with the fineprint
# paragraph followed by the bar's closing </div> (verified uniform sitewide).
_LEGACY_RE = re.compile(
    r'<div class="subscribe-bar">.*?subscribe-fineprint[^>]*>.*?</p>\s*</div>',
    re.DOTALL,
)
_MANAGED_RE = re.compile(
    re.escape(MARK_START) + r".*?" + re.escape(MARK_END), re.DOTALL
)

_INPUT_STYLE = (
    "padding:12px 16px;border-radius:6px;border:1px solid rgba(82,180,255,.35);"
    "background:rgba(4,6,13,.6);color:#dfe6ef;font-size:15px;min-width:230px"
)

_RSS_LINK = (
    '<a href="/generated/feed.xml" '
    "onclick=\"window.plausible&&plausible('Subscribe',{props:{channel:'rss'}})\" "
    'class="btn btn-primary" style="display:inline-block">📡 Subscribe via RSS</a>'
)
_GH_LINK = (
    '<a href="https://github.com/FongShuiLabs/pursueufotracker/subscription" '
    'target="_blank" rel="noopener" '
    "onclick=\"window.plausible&&plausible('Subscribe',{props:{channel:'github'}})\" "
    'class="btn btn-ghost" style="display:inline-block">🔔 Watch on GitHub</a>'
)
_ALT_ROW_SMALL = (
    '<p style="margin-top:12px;font-size:13px;color:#7a92b0">Prefer no email? '
    '<a href="/generated/feed.xml" style="color:#52b4ff" '
    "onclick=\"window.plausible&&plausible('Subscribe',{props:{channel:'rss'}})\">RSS feed</a> · "
    '<a href="https://github.com/FongShuiLabs/pursueufotracker/subscription" target="_blank" '
    'rel="noopener" style="color:#52b4ff" '
    "onclick=\"window.plausible&&plausible('Subscribe',{props:{channel:'github'}})\">Watch on GitHub</a></p>"
)


def _fineprint(variant: str, live: bool) -> str:
    tail = "Unsubscribe anytime." if live else "Email signup launching soon."
    if variant == "homepage":
        return (
            f'<p class="subscribe-fineprint" style="margin-top:14px">No spam. {tail} '
            '<a href="/verdict">The honest verdict</a> · '
            '<a href="/top-10">Top 10 most anomalous</a> · '
            '<a href="/press">Press kit</a></p>'
        )
    return f'<p class="subscribe-fineprint" style="margin-top:14px">No spam, ever. {tail}</p>'


def _prompt(variant: str) -> str:
    if variant == "homepage":
        return (
            '<p class="subscribe-prompt"><strong>Get alerted the moment '
            "Trump's next UFO drop lands.</strong></p>"
        )
    return (
        '<p class="subscribe-prompt"><strong>Get alerted the moment the next '
        "PURSUE drop lands.</strong></p>"
    )


def subscribe_html(variant: str = "page") -> str:
    """The complete .subscribe-bar block for the given surface variant."""
    prompt = _prompt(variant)
    provider = (ESP_PROVIDER or "").strip().lower()
    handle = (ESP_HANDLE or "").strip()

    if provider and not handle:
        print(f"  WARNING: ESP_PROVIDER={provider!r} but ESP_HANDLE is empty - "
              "rendering placeholder until a handle is set.")
        provider = ""

    if provider == "buttondown":
        body = (
            '<form action="https://buttondown.com/api/emails/embed-subscribe/'
            f'{handle}" method="post" '
            "onsubmit=\"window.plausible&&plausible('Subscribe',"
            "{props:{channel:'email',esp:'buttondown'}})\" "
            'style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center;'
            'align-items:center;margin:0 0 4px">'
            '<label for="bd-email" style="position:absolute;left:-9999px">Email address</label>'
            f'<input type="email" name="email" id="bd-email" required '
            f'placeholder="you@example.com" style="{_INPUT_STYLE}">'
            '<button type="submit" class="btn btn-primary" '
            'style="display:inline-block;cursor:pointer">📩 Get drop alerts</button>'
            "</form>" + _ALT_ROW_SMALL
        )
    elif provider == "substack":
        body = (
            f'<iframe src="https://{handle}.substack.com/embed" width="100%" '
            'height="150" style="max-width:480px;border:1px solid '
            'rgba(82,180,255,.3);border-radius:8px;background:transparent" '
            'frameborder="0" scrolling="no" title="Email signup"></iframe>'
            f'<p style="margin-top:8px;font-size:13px"><a '
            f'href="https://{handle}.substack.com/subscribe" target="_blank" '
            'rel="noopener" style="color:#52b4ff" '
            "onclick=\"window.plausible&&plausible('Subscribe',"
            "{props:{channel:'email',esp:'substack'}})\">Form not loading? "
            "Subscribe directly →</a></p>" + _ALT_ROW_SMALL
        )
    else:  # placeholder - byte-equivalent to the launch-era block
        body = (
            ('<p style="color:#dfe6ef;margin:8px 0 16px;font-size:15px">Two free '
             "options - both update within hours of any new war.gov release:</p>"
             if variant == "homepage" else "")
            + '<div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center;align-items:center">'
            + _RSS_LINK + "\n      " + _GH_LINK + "</div>"
        )

    live = provider in ("buttondown", "substack")
    return (
        '<div class="subscribe-bar">\n    '
        + prompt + "\n    "
        + body + "\n    "
        + _fineprint(variant, live) + "\n  </div>"
    )


def _stamp_file(path: Path, variant: str) -> str:
    """Replace the managed (or legacy) block in one file. Returns a status."""
    text = path.read_text(encoding="utf-8")
    block = f"{MARK_START}\n  {subscribe_html(variant)}\n  {MARK_END}"

    if _MANAGED_RE.search(text):
        new = _MANAGED_RE.sub(lambda _: block, text, count=1)
        status = "refreshed"
    else:
        matches = _LEGACY_RE.findall(text)
        if not matches:
            return "no-bar"
        if len(matches) > 1:
            return "SKIP-multiple-bars"
        new = _LEGACY_RE.sub(lambda _: block, text, count=1)
        status = "migrated"

    if new != text:
        path.write_text(new, encoding="utf-8")
        return status
    return "unchanged"


def run() -> None:
    provider = (ESP_PROVIDER or "").strip().lower() or "placeholder"
    print(f"  subscribe: provider={provider}"
          + (f" handle={ESP_HANDLE}" if ESP_HANDLE else ""))

    counts: dict[str, int] = {}
    homepage = ROOT / "index.html"
    result = _stamp_file(homepage, "homepage")
    counts[result] = counts.get(result, 0) + 1
    if result.startswith("SKIP"):
        print(f"  WARNING: {homepage.name}: {result}")

    for path in sorted(GENERATED_DIR.glob("*.html")):
        result = _stamp_file(path, "page")
        counts[result] = counts.get(result, 0) + 1
        if result.startswith("SKIP"):
            print(f"  WARNING: {path.name}: {result}")

    summary = ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
    print(f"  subscribe: homepage + {len(list(GENERATED_DIR.glob('*.html')))} "
          f"statics scanned ({summary})")
    print("  note: file pages + category hubs pick the block up on the next "
          "`build` / `build-categories` run.")


if __name__ == "__main__":  # pragma: no cover
    run()
    sys.exit(0)
