"""Stage 9.1: render /verdict/ - the honest answer page.

Reads data/verdict-stance.md (Anthony-editable Q&A markdown) and renders to
generated/verdict.html. Auto-injects a few stats from the manifest (file
counts, redaction count) so numbers stay in sync.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .config import (
    MANIFEST_PATH, ROOT, GENERATED_DIR, TEMPLATES_DIR,
    SITE_NAME, SITE_URL, ensure_dirs,
)


def _md_to_qa(md: str) -> list[dict]:
    """Parse the stance markdown into a list of {q, body_html} blocks."""
    blocks = []
    cur = None
    body: list[str] = []
    for line in md.splitlines():
        m = re.match(r"^##\s*Q:\s*(.+)$", line.strip())
        if m:
            if cur:
                blocks.append({"q": cur, "body": "\n".join(body).strip()})
            cur = m.group(1).strip()
            body = []
        else:
            if cur is not None:
                body.append(line)
    if cur:
        blocks.append({"q": cur, "body": "\n".join(body).strip()})
    # Light markdown -> html: paragraphs, bold, lists
    for b in blocks:
        b["body_html"] = _mini_md(b["body"])
    return blocks


def _mini_md(text: str) -> str:
    # bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # bullets
    out = []
    in_list = False
    for line in text.splitlines():
        if re.match(r"^\s*-\s+", line):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>" + re.sub(r"^\s*-\s+", "", line) + "</li>")
        else:
            if in_list:
                out.append("</ul>")
                in_list = False
            if line.strip():
                out.append(f"<p>{line.strip()}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def run() -> None:
    ensure_dirs()
    stance_path = ROOT / "data" / "verdict-stance.md"
    if not stance_path.exists():
        print("  (no verdict-stance.md)")
        return
    if not MANIFEST_PATH.exists():
        print("  (no manifest)")
        return
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = manifest["files"]
    stats = {
        "total":    len(files),
        "pdfs":     sum(1 for f in files if f["type"] == "pdf"),
        "videos":   sum(1 for f in files if f["type"] == "video"),
        "images":   sum(1 for f in files if f["type"] == "image"),
        "redacted": sum(1 for f in files if f.get("redacted")),
        "high_score": sum(1 for f in files if (f.get("score") or {}).get("value", 0) >= 75),
    }
    qa = _md_to_qa(stance_path.read_text(encoding="utf-8"))
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
        trim_blocks=True, lstrip_blocks=True,
    )
    if not (TEMPLATES_DIR / "verdict.html.j2").exists():
        print("  (templates/verdict.html.j2 missing)")
        return
    tpl = env.get_template("verdict.html.j2")
    out = GENERATED_DIR / "verdict.html"
    out.write_text(
        tpl.render(qa=qa, stats=stats, site_name=SITE_NAME, site_url=SITE_URL),
        encoding="utf-8",
    )
    print(f"  verdict page -> {out}")


if __name__ == "__main__":
    run()
