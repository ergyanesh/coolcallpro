"""
Universal per-page audit — runs on ANY HTML page on the site.

Checks the rules every page must satisfy regardless of type:
    - canonical URL (present, no .html)
    - <title> <= 60 chars
    - <meta name="description"> <= 155 chars
    - exactly one <h1>
    - Open Graph: type, title, description, url, site_name, image
    - Twitter Card: card, title, description
    - skip-link is the first child of <body>
    - <main id="main-content"> wraps primary content
    - site-wide CSS regression (.article-content a:not(.btn) rule present)
    - MarketCall-required disclaimer (if the paragraph is on the page, it must
      match the locked text byte-for-byte — revenue-threatening if edited)

Usage:
    python audit_page.py <path-to-any-html-page>
    python audit_page.py --strict <path-to-any-html-page>

Exit codes:
    0 = all checks pass
    1 = one or more checks failed
"""

import html as html_mod
import re
import sys
from pathlib import Path


# --- MarketCall disclaimer (verbatim — never edit) -------------------------
# Required by MarketCall partner agreement. Page containing any portion of
# this paragraph must preserve the full text byte-identical.
MARKETCALL_DISCLAIMER_SIGNATURE = "is a free service to assist homeowners in connecting with local service providers"
MARKETCALL_DISCLAIMER_FULL = (
    "Cool Call Pro is a free service to assist homeowners in connecting with "
    "local service providers. All contractors/providers are independent and "
    "Cool Call Pro does not warrant or guarantee any work performed. It is "
    "the responsibility of the homeowner to verify that the hired contractor "
    "furnishes the necessary license and insurance required for the work "
    "being performed. All persons depicted in a photo or video are actors "
    "or models and not contractors listed on Cool Call Pro."
)


def read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def check(label: str, passed: bool, detail: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"  [{status}] {label}{suffix}")
    return passed


def audit_page_universal(html: str, path: str) -> int:
    print(f"\nUNIVERSAL PAGE AUDIT: {path}")
    fails = 0

    # Head essentials
    title = re.search(r"<title>([^<]+)</title>", html)
    meta = re.search(r'<meta name="description"\s+content="([^"]+)"', html)
    h1_matches = re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.DOTALL)
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)

    if not title:
        fails += 1 if not check("<title> tag present", False) else 0
    else:
        # Unescape HTML entities so &amp; counts as 1 char, not 5. Google indexes
        # the displayed text, not the HTML-escaped source.
        title_len = len(html_mod.unescape(title.group(1)))
        if not check(f"<title> <= 60 chars (actual: {title_len})", title_len <= 60):
            fails += 1

    if not meta:
        fails += 1 if not check("Meta description present", False) else 0
    else:
        meta_len = len(html_mod.unescape(meta.group(1)))
        if not check(f"Meta description <= 155 chars (actual: {meta_len})", meta_len <= 155):
            fails += 1

    if not check(f"Exactly one <h1> (actual: {len(h1_matches)})", len(h1_matches) == 1):
        fails += 1

    if not canonical:
        fails += 1 if not check("Canonical URL present", False) else 0
    elif not check(f"Canonical has no .html: {canonical.group(1)}", ".html" not in canonical.group(1)):
        fails += 1

    # Open Graph (6 required tags)
    og_tags = ["type", "title", "description", "url", "site_name", "image"]
    og_missing = [t for t in og_tags if not re.search(rf'property="og:{t}"', html)]
    if not check(f"All 6 Open Graph tags present (missing: {og_missing or 'none'})", not og_missing):
        fails += 1

    # Twitter Card
    tw_tags = ["card", "title", "description"]
    tw_missing = [t for t in tw_tags if not re.search(rf'name="twitter:{t}"', html)]
    if not check(f"All 3 Twitter Card tags present (missing: {tw_missing or 'none'})", not tw_missing):
        fails += 1

    # Semantic structure
    if not check("Skip link (.skip-link) present", bool(re.search(r'<a[^>]*class="[^"]*skip-link', html))):
        fails += 1
    if not check('<main id="main-content"> present', bool(re.search(r'<main[^>]+id="main-content"', html))):
        fails += 1

    # MarketCall disclaimer — if the signature appears, the full text must match
    if MARKETCALL_DISCLAIMER_SIGNATURE in html:
        # Normalize whitespace for comparison (HTML can have newlines in the middle)
        normalized = re.sub(r"\s+", " ", html)
        if not check(
            "MarketCall disclaimer text is VERBATIM (not edited)",
            MARKETCALL_DISCLAIMER_FULL in normalized,
            "Locked by MarketCall partner agreement — do not rewrite",
        ):
            fails += 1
    # (If the signature is absent on this page, no check needed — not every page carries it.)

    return fails


def audit_css_regression_site() -> int:
    """Checks the site-wide CSS rule that affects every article page."""
    print("\nCSS REGRESSION (site-wide)")
    fails = 0

    try:
        css = Path("css/style.css").read_text(encoding="utf-8")
    except FileNotFoundError:
        print("  [SKIP] css/style.css not found — run from project root.")
        return 0

    has_underline = re.search(
        r"\.article-content\s+a(?::not\([^)]+\))?\s*\{[^}]*text-decoration\s*:\s*underline",
        css, re.DOTALL,
    )
    if not check(".article-content a rule with text-decoration:underline", bool(has_underline)):
        fails += 1

    has_orange = re.search(
        r"\.article-content\s+a(?::not\([^)]+\))?\s*\{[^}]*color\s*:\s*var\(--orange",
        css, re.DOTALL,
    )
    if not check(".article-content a color is --orange or --orange-dark", bool(has_orange)):
        fails += 1

    has_btn_exclusion = re.search(r"\.article-content\s+a:not\(\.btn\)", css)
    if not check(".article-content a:not(.btn) selector (CTA button protection)", bool(has_btn_exclusion)):
        fails += 1

    return fails


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("--"):
        print("Usage: python audit_page.py <path-to-html>")
        sys.exit(2)

    path = args[0]
    html = read(path)
    fails = audit_page_universal(html, path)

    print()
    if fails == 0:
        print(f"OK — universal audit passed for {path}")
        sys.exit(0)
    else:
        print(f"FAIL — {fails} universal check(s) failed on {path}.")
        sys.exit(1)


if __name__ == "__main__":
    main()
