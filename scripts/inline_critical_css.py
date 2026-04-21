"""
One-off: inline critical above-the-fold CSS on every root HTML page that
uses .page-hero but doesn't yet have the critical-CSS block.

This is the same ~2KB <style> block that was hand-applied to about.html /
contact.html / costs.html / author-gyanesh.html / safety.html / emergency.html
on 2026-04-21. The block covers .page-hero, .container, .breadcrumb-nav,
.section-tag, and CSS variables so the hero + breadcrumbs paint before
style.min.css downloads.

Targets any root HTML file that:
  - Contains a `.page-hero` class reference in the body
  - Does NOT already have `.page-hero` rule in an inline <style> block
  - Has exactly one `<link rel="stylesheet" href="css/style.min.css" />`
    line (the inline block is inserted right before it)

Excludes:
  - index.html (already has its full CSS inlined)
  - locations/*.html (use a DIFFERENT critical CSS block for .city-hero)
  - articles/*.html (use the hero-image LCP pattern instead)
  - article-*.html (same as above)

Byte-preserving: reads/writes with newline="" to keep CRLF. Idempotent.
"""

import re
from pathlib import Path

ROOT = Path(__file__).parent.parent

# The canonical critical-CSS block. Mirrors what's already in about.html,
# contact.html, costs.html, author-gyanesh.html, safety.html, emergency.html.
CRITICAL_CSS_BLOCK = (
    "<!-- Critical above-the-fold CSS (inlined for LCP; ~2KB). Paints hero + breadcrumb before style.min.css downloads. -->\n"
    "    <style>"
    ":root{--navy:#0a1628;--navy-deep:#060e1c;--navy-mid:#112040;--blue-light:#4fa3ff;--orange:#d84315;--orange-dark:#b53610;--gray-50:#f7fafc;--gray-200:#e2e8f0;--gray-300:#cbd5e0;--gray-500:#5a6778;--gray-700:#2d3748;--gray-900:#1a202c;--white:#fff;--font-main:'Inter',sans-serif;--font-display:'Outfit',sans-serif}"
    "*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}"
    "html{scroll-behavior:smooth;font-size:16px}"
    "body{font-family:var(--font-main);background:var(--white);color:var(--gray-900);line-height:1.65;max-width:100%;overflow-x:hidden}"
    ".container{max-width:1200px;margin:0 auto;padding:0 24px}"
    ".breadcrumb-nav{background:var(--gray-50);border-bottom:1px solid var(--gray-200);padding:10px 0;font-size:.82rem}"
    ".breadcrumb-list{display:flex;align-items:center;gap:6px;list-style:none;flex-wrap:wrap}"
    ".breadcrumb-list li{display:flex;align-items:center;color:var(--gray-500)}"
    '.breadcrumb-list li:not(:last-child)::after{content:"\\203A";margin-left:6px;color:var(--gray-300)}'
    ".breadcrumb-list a{color:#0d5dc9;text-decoration:none;font-weight:500}"
    ".breadcrumb-list li:last-child{color:var(--gray-700);font-weight:500}"
    ".page-hero{background:var(--navy);padding:80px 0 60px;text-align:center}"
    ".page-hero .container{display:flex;flex-direction:column;align-items:center}"
    ".page-hero h1{font-family:var(--font-display);font-size:clamp(1.6rem,3.2vw,2.5rem);font-weight:900;color:var(--white);margin:0 auto 20px;max-width:760px;line-height:1.18;letter-spacing:-.02em;order:2}"
    ".page-hero p{font-size:1.05rem;color:rgba(255,255,255,.65);max-width:760px;margin:0 auto;order:3}"
    ".section-tag{display:inline-block;background:rgba(26,115,232,.1);color:#0d5dc9;border:1px solid rgba(26,115,232,.25);font-size:.8rem;font-weight:700;padding:6px 14px;border-radius:100px;letter-spacing:.05em;text-transform:uppercase;margin-bottom:16px}"
    ".page-hero .section-tag{color:var(--blue-light);background:rgba(79,163,255,.15);border-color:rgba(79,163,255,.3)}"
    "</style>\n    "
)

STYLESHEET_LINK = '<link rel="stylesheet" href="css/style.min.css" />'
# Sentinel: already patched if the inline <style> contains a .page-hero rule.
SENTINEL = "<style>:root{--navy:"


def should_patch(path: Path, text: str) -> tuple[bool, str]:
    name = path.name
    # Exclude files that use a different perf pattern
    if name == "index.html":
        return False, "index.html has full CSS inlined"
    if name.startswith("article-"):
        return False, "article-*.html uses the hero-image LCP pattern"
    if "class=\"page-hero" not in text:
        return False, "does not use .page-hero"
    if SENTINEL in text:
        return False, "already has critical CSS inlined"
    if STYLESHEET_LINK not in text:
        return False, "no `<link rel=\"stylesheet\" href=\"css/style.min.css\" />` anchor"
    return True, ""


def patch_file(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as fh:
        text = fh.read()
    ok, reason = should_patch(path, text)
    if not ok:
        return f"skip ({reason})"

    is_crlf = "\r\n" in text
    block = CRITICAL_CSS_BLOCK
    if is_crlf:
        block = block.replace("\n", "\r\n")
    new_text = text.replace(STYLESHEET_LINK, block + STYLESHEET_LINK, 1)
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(new_text)
    return "patched"


def main() -> int:
    counts = {"patched": 0, "skipped": 0}
    for path in sorted(ROOT.glob("*.html")):
        result = patch_file(path)
        tag = "PATCHED" if result == "patched" else "skip"
        print(f"  {tag:8s} {path.name:40s} -- {result}")
        if result == "patched":
            counts["patched"] += 1
        else:
            counts["skipped"] += 1
    print(f"\nTotals: {counts['patched']} patched, {counts['skipped']} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
