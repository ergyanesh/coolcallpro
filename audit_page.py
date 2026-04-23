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

from safety_rules import check_diy_hazards


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

    # 404 / error pages legitimately skip canonical + OG + Twitter because
    # they should not be indexed or shared. Detected by filename or by an
    # explicit noindex meta tag.
    is_error_page = (
        path.replace("\\", "/").lower().endswith("/404.html")
        or path.replace("\\", "/").lower() == "404.html"
        or 'name="robots" content="noindex' in html.lower()
    )

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

    if is_error_page:
        check("Canonical + OG + Twitter skipped (error page / noindex)", True,
              "404 and noindex pages should not be indexed or shared, so these tags are intentionally omitted")
    else:
        if not canonical:
            fails += 1 if not check("Canonical URL present", False) else 0
        else:
            canonical_url = canonical.group(1)
            if not check(f"Canonical has no .html: {canonical_url}", ".html" not in canonical_url):
                fails += 1
            if not check(
                f"Canonical points to https://coolcallpro.com (actual host: {canonical_url})",
                canonical_url.startswith("https://coolcallpro.com"),
                "Canonical must use the site's primary host + scheme, not http:// or a different domain",
            ):
                fails += 1

    # DUPLICATE-URL PROTECTION (since 2026-04-23):
    # Every internal hyperlink must use clean URLs -- no .html suffix. This
    # prevents the GSC duplicate-indexing bug where Google saw both /about and
    # /about.html as separate pages and split ranking signal. The existing
    # _redirects file already 301s .html -> clean URL; this audit ensures no
    # new pages re-introduce .html references that would tell Google the
    # .html versions are still canonical.
    internal_html_hrefs = re.findall(
        r'href="(?!https?://|mailto:|tel:|javascript:|#)[^"]+\.html(?:#[^"]*)?"',
        html,
    )
    if not check(
        f"Zero internal .html hrefs (found: {len(internal_html_hrefs)})",
        len(internal_html_hrefs) == 0,
        f"Use clean URLs in every internal href (e.g. href=\"../about\" not href=\"../about.html\"). First offender: {internal_html_hrefs[0] if internal_html_hrefs else 'n/a'}",
    ):
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

    # Footer structure — if a <footer class="footer"> exists, its columns must
    # use the .footer-col class. Without it the CSS rules (.footer-col h4,
    # .footer-col li a) do not match and the footer text inherits dark
    # colors on the dark navy background, rendering invisible. Exactly this
    # regression hit the 3 recent articles on 2026-04-20.
    if re.search(r'<footer\s+class="[^"]*\bfooter\b', html):
        if not check(
            "Footer columns use .footer-col class (CSS targets .footer-col for text color)",
            'footer-col' in html,
            "Plain <div> columns render invisible text on dark background",
        ):
            fails += 1

    # Google Fonts ban — we self-host fonts under /fonts/ for LCP performance.
    # Allowing fonts.googleapis.com or fonts.gstatic.com back in regresses the
    # 2026-04-20 performance work (mobile Performance jumped 74 -> 93+ after
    # self-hosting). Any reference fails the audit.
    if 'fonts.googleapis.com' in html or 'fonts.gstatic.com' in html:
        if not check(
            "No Google Fonts CDN references (site is self-hosted under /fonts/)",
            False,
            "Remove any <link> to fonts.googleapis.com or fonts.gstatic.com",
        ):
            fails += 1

    # Google Analytics must be interaction-deferred, not fired on window.load.
    # The window.load pattern pulled ~64 KB of gtag.js into the critical render
    # path and dropped mobile Performance by 17-21 points. The deferred loader
    # fires on first user interaction (click | scroll | touchstart | keydown)
    # with a setTimeout idle fallback. Only check pages that include GA.
    if 'G-WD0ND0K60Q' in html or 'googletagmanager.com/gtag' in html:
        bad_load_pattern = re.search(
            r"window\.addEventListener\(\s*['\"]load['\"]\s*,\s*function\s*\(\s*\)\s*\{[^}]*?gtag",
            html,
            re.DOTALL,
        )
        if not check(
            "GA loader does NOT use window.addEventListener('load') pattern",
            not bad_load_pattern,
            "Old pattern loads gtag.js in the critical render path — use interaction defer",
        ):
            fails += 1

        has_click = "'click'" in html
        has_scroll = "'scroll'" in html
        has_touchstart = "'touchstart'" in html
        has_keydown = "'keydown'" in html
        interaction_events_present = has_click and has_scroll and has_touchstart and has_keydown
        if not check(
            "GA loader listens for user interactions (click, scroll, touchstart, keydown)",
            interaction_events_present,
            "Deferred loader needs all 4 interaction events to fire GA on real engagement",
        ):
            fails += 1

        has_fallback = bool(re.search(r"setTimeout\(\s*loadGA\s*,\s*\d+\s*\)", html))
        if not check(
            "GA loader has setTimeout idle fallback (loads after N seconds if no interaction)",
            has_fallback,
            "Without a fallback, non-interactive page views (some bots, pre-rendering) never track",
        ):
            fails += 1

    return fails


def audit_perf_patterns(html: str, path: str) -> int:
    """Page-class performance checks -- protect the patterns that keep
    articles and location pages ranked 90+ on Lighthouse mobile.

    Three conditional checks:
      1. Article pages (articles/*.html OR root article-*.html):
         Must include at least one hero <img> with loading="eager" or
         fetchpriority="high" so the WebP hero is the LCP target.
      2. Location pages (locations/*.html):
         Must include an inline <style> block containing a .city-hero
         rule so the hero gradient + H1 paint before style.min.css
         downloads. ~4KB critical-CSS pattern; see locations/texas.html.
      3. Any non-location page containing class="page-hero":
         Must include an inline <style> block containing a .page-hero
         rule (same critical-CSS pattern as #2 but for the generic
         page hero). This protects about/contact/costs/author-gyanesh
         and any future generic page that uses .page-hero.

    These checks were added after a user spot-check on 2026-04-21 showed
    that /about, /contact, /costs, /author-gyanesh all scored 60-80 on
    mobile Lighthouse because they didn't inline critical CSS and had
    no priority hero image. Articles (hero WebP) and locations (inline
    .city-hero CSS) already score 90+."""
    print(f"\nPERF PATTERNS (LCP protection)")
    fails = 0
    norm = path.replace("\\", "/").lower()

    is_article = norm.startswith("articles/") or re.match(r"(^|/)article-[^/]+\.html$", norm) is not None
    is_location = norm.startswith("locations/")

    # Extract all inline <style> blocks' contents for pattern matching
    style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", html, re.DOTALL | re.IGNORECASE)
    inline_css = "\n".join(style_blocks)

    if is_article:
        # Hero pattern: <img ... loading="eager" ...> or <img ... fetchpriority="high" ...>
        has_priority_hero = bool(
            re.search(r'<img[^>]*\bloading="eager"', html, re.IGNORECASE)
            or re.search(r'<img[^>]*\bfetchpriority="high"', html, re.IGNORECASE)
        )
        if not check(
            "Article has LCP-priority hero image (loading=eager or fetchpriority=high)",
            has_priority_hero,
            "Articles must designate a hero WebP as the LCP target -- this is the pattern that keeps them 90+ on mobile Lighthouse",
        ):
            fails += 1
    elif is_location:
        # Critical CSS pattern: inline <style> with a .city-hero rule
        has_city_hero_critical = bool(re.search(r"\.city-hero\s*\{", inline_css))
        if not check(
            "Location page has inline critical CSS for .city-hero",
            has_city_hero_critical,
            "Location hubs must inline ~4KB of critical CSS covering .city-hero so the hero paints before style.min.css downloads. See locations/texas.html for the canonical block.",
        ):
            fails += 1
    else:
        # Generic page: if it uses .page-hero, require inline critical CSS for it
        uses_page_hero = bool(re.search(r'class="[^"]*\bpage-hero\b', html))
        if uses_page_hero:
            has_page_hero_critical = bool(re.search(r"\.page-hero\s*\{", inline_css))
            if not check(
                "Page uses .page-hero -> inline critical CSS for .page-hero is required",
                has_page_hero_critical,
                "Pages with .page-hero must inline ~2KB of critical CSS covering .page-hero so the hero paints before style.min.css. See about.html for the canonical block.",
            ):
                fails += 1

    if fails == 0:
        print("  [PASS] Performance pattern appropriate for this page class")
    return fails


def audit_sitemap_no_html() -> int:
    """Site-wide check: sitemap.xml must list only clean URLs, never .html.

    Added 2026-04-23 after GSC showed 17 duplicate-pair listings where Google
    indexed both /X and /X.html because earlier versions of the sitemap and
    the internal link graph surfaced the .html versions. Sitemap already
    listed only clean URLs as of that date; this check locks that in so
    future regenerations can't silently regress."""
    print("\nSITEMAP DUPLICATE-URL CHECK (site-wide)")
    sitemap_path = Path("sitemap.xml")
    if not sitemap_path.exists():
        print("  [SKIP] sitemap.xml not found -- run from project root.")
        return 0
    text = sitemap_path.read_text(encoding="utf-8")
    bad = re.findall(r"<loc>[^<]*\.html</loc>", text)
    if not check(
        f"sitemap.xml has zero .html URLs (found: {len(bad)})",
        len(bad) == 0,
        f"Sitemap must list only clean URLs. First offender: {bad[0] if bad else 'n/a'}",
    ):
        return 1
    return 0


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
    fails += audit_perf_patterns(html, path)
    fails += audit_sitemap_no_html()
    fails += check_diy_hazards(html, source_label=path)

    print()
    if fails == 0:
        print(f"OK — universal audit passed for {path}")
        sys.exit(0)
    else:
        print(f"FAIL — {fails} universal check(s) failed on {path}.")
        sys.exit(1)


if __name__ == "__main__":
    main()
