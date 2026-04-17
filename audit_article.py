"""
Per-article pre-deploy audit.

Runs every SEO, safety, YMYL, and pillar-spec check in one pass. The
hvac-article-writer skill MUST call this (in --strict mode) before claiming an
article is done. Failures must be fixed before committing.

Usage:
    python audit_article.py articles/<slug>.html                 # soft audit
    python audit_article.py articles/<slug>.html --strict --browser-verified

    --strict            Adds: Your-Money YMYL checks (tax caveat, APR caveat,
                        brand-defamation warn), CSS regression check, and
                        a blocking browser-verification gate.
    --browser-verified  Required with --strict. Asserts you have opened the
                        article at localhost:8080/articles/<slug> and visually
                        confirmed: (1) body links render underlined/colored,
                        (2) every FAQ expands/collapses on click, (3) TOC
                        jump-links work, (4) hero image renders, (5) no
                        obvious layout or text issues.

Exit codes:
    0 = all checks pass
    1 = one or more checks failed
    2 = --strict specified without --browser-verified (blocking gate)
"""

import re
import sys
from pathlib import Path


# --- Forbidden safety words (per skill's YMYL rules) -----------------------

FORBIDDEN_PHRASES = [
    # The word "licensed" is forbidden — we're a referral service
    r"\blicensed\b",
    # DIY instructions that could injure or kill the reader
    r"relight the pilot",
    r"open the electrical panel",
    r"discharge the capacitor",
    r"test the capacitor yourself",
    r"handle the refrigerant",
    r"recharge the refrigerant yourself",
    r"bypass the safety",
    r"bypass the switch",
    r"cut the wires",
    r"jump the contactor",
]

# --- Cost figures (must match costs.html — single source of truth) ---------

# Any in-article cost drift from these canonical ranges fails the audit.
# Keep this in sync with costs.html.
REQUIRED_COST_RANGES = {
    "diagnostic": {"low": 65, "high": 150, "label": "diagnostic / service call"},
    "compressor_low": 900,     # canonical low for compressor replacement
    "compressor_high": 2800,
    # Capacitor lives inside $90-$450 minor AC repair bucket
    "capacitor_low": 90,
    "capacitor_high": 450,
    "refrigerant_low": 150,
    "refrigerant_high": 600,
}

# Patterns that indicate DRIFT from costs.html
COST_DRIFT_PATTERNS = [
    (r"\$75\s*(?:to|&ndash;|\u2013|-)\s*\$150", "Diagnostic $75-$150 — canonical is $65-$150"),
    (r"\$1,200\s*(?:to|&ndash;|\u2013|-)\s*\$2,800", "Compressor $1,200-$2,800 — canonical is $900-$2,800"),
    (r"\$90\s*(?:to|&ndash;|\u2013|-)\s*\$400", "Capacitor $90-$400 — canonical is $90-$450"),
]


def read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def check(label: str, passed: bool, detail: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"  [{status}] {label}{suffix}")
    return passed


def audit_safety(html: str) -> int:
    print("\nSAFETY AUDIT (YMYL)")
    fails = 0

    for pattern in FORBIDDEN_PHRASES:
        matches = re.findall(pattern, html, re.I)
        passed = not matches
        if not check(f'No forbidden phrase: "{pattern}"', passed, f"{len(matches)} occurrences" if matches else ""):
            fails += 1

    for label, pattern in [
        ("General HVAC safety callout present", r"callout-danger.*?HVAC systems involve high-voltage"),
        ("Topic-specific safety warning (kill the power / breaker)", r"Kill the Power|kill the breaker|flip the breaker"),
        ("Advertising disclosure", r"Advertising Disclosure"),
        ("Professional redirect for refrigerant", r"Section 608|certification is legally required|refrigerant work is federally regulated"),
        ("Professional redirect for gas", r"gas utility|evacuate|natural gas"),
    ]:
        if not check(label, bool(re.search(pattern, html, re.I | re.DOTALL))):
            fails += 1

    return fails


def audit_seo(html: str) -> int:
    print("\nSEO CHECKLIST")
    fails = 0

    title = re.search(r"<title>([^<]+)</title>", html)
    meta = re.search(r'<meta name="description"\s+content="([^"]+)"', html)
    h1 = re.search(r"<h1>([^<]+)</h1>", html)
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)

    if not title or not meta or not h1 or not canonical:
        print("  [FAIL] Missing required head element (title/meta/h1/canonical)")
        return fails + 1

    t, m, h, c = title.group(1), meta.group(1), h1.group(1), canonical.group(1)

    # Rule 1 (SOFT): H1 framing matches search intent.
    # Question form is preferred for symptom/diagnostic/decision articles
    # (how people type "why is my ac blowing warm air"). Declarative is
    # preferred for head-term pillars, cost guides, comparisons, best-of lists
    # (how people type "hvac cost guide 2026", "repair vs replace"). We no
    # longer fail on form — writer picks the form that matches intent.
    is_question = h.rstrip().endswith("?") or "?" in h
    print(f"  [INFO] H1 form: {'question' if is_question else 'declarative'} — \"{h[:70]}...\"")

    if not check(f"<title> <= 60 chars (actual: {len(t)})", len(t) <= 60):
        fails += 1
    if not check(f"Meta description <= 155 chars (actual: {len(m)})", len(m) <= 155):
        fails += 1
    if not check(f"Canonical has no .html: {c}", ".html" not in c):
        fails += 1

    # OG + Twitter
    og_present = all(re.search(rf'property="og:{t}"', html) for t in ["type", "title", "description", "url", "site_name", "image"])
    if not check("All 6 Open Graph tags present", og_present):
        fails += 1
    tw_present = all(re.search(rf'name="twitter:{t}"', html) for t in ["card", "title", "description"])
    if not check("All 3 Twitter Card tags present", tw_present):
        fails += 1

    # Schemas
    if not check("Article schema (JSON-LD)", '"@type": "Article"' in html):
        fails += 1
    bc_list_items = html.count('"@type": "ListItem"')
    if not check(f"Breadcrumb schema has 3 ListItems (actual: {bc_list_items})", bc_list_items == 3):
        fails += 1

    # FAQ schema vs visible FAQ count
    q_count = html.count('"@type": "Question"')
    faq_item_count = len(re.findall(r'class="faq-item"', html))
    if not check(f"FAQ schema count: {q_count} (>=4)", q_count >= 4):
        fails += 1
    if not check(
        f"FAQ visible items match schema and use .faq-item pattern (visible: {faq_item_count}, schema: {q_count})",
        faq_item_count == q_count,
    ):
        fails += 1
    # Hard ban on plain H3+P FAQ pattern inside the FAQ section
    faq_section = re.search(r'<h2 id="faqs">(.*?)(?:<h2|</article>)', html, re.DOTALL)
    if faq_section:
        plain_h3_in_faq = len(re.findall(r"<h3>", faq_section.group(1)))
        # Allow exactly one H3 for the "Local HVAC Service Areas" closing block
        if not check(
            f"FAQ section contains no plain H3/P FAQs (found {plain_h3_in_faq} H3s; expect 0 or 1 for Service Areas)",
            plain_h3_in_faq <= 1,
        ):
            fails += 1

    # Internal + external links
    has_costs_link = '<a href="../costs"' in html or 'href="costs"' in html
    if not check("Links to /costs (canonical cost source)", has_costs_link):
        fails += 1
    has_authority = all(s in html for s in ["energy.gov", "epa.gov"])
    if not check("External authority links (DOE + EPA minimum)", has_authority):
        fails += 1

    # Cost drift from costs.html
    drift_found = []
    for pattern, msg in COST_DRIFT_PATTERNS:
        if re.search(pattern, html):
            drift_found.append(msg)
    if not check(
        f"No cost drift from costs.html ({len(drift_found)} drifts detected)",
        not drift_found,
        "; ".join(drift_found) if drift_found else "",
    ):
        fails += 1

    # Image — lead-img tag with alt text >=40 chars, attribute order agnostic
    lead_img = re.search(r'<img[^>]*class="lead-img"[^>]*>', html)
    alt_ok = False
    if lead_img:
        alt_match = re.search(r'alt="([^"]*)"', lead_img.group(0))
        alt_ok = bool(alt_match and len(alt_match.group(1)) >= 40)
    if not check("Hero image has descriptive alt (40+ chars)", alt_ok):
        fails += 1

    # H4 inside <article> (article body should be clean H1->H2->H3)
    article = re.search(r'<article class="article-content">(.*?)</article>', html, re.DOTALL)
    if article:
        body_h4 = len(re.findall(r"<h4", article.group(1)))
        if not check(
            f"No H4+ inside <article> body (found: {body_h4})",
            body_h4 == 0,
        ):
            fails += 1

    return fails


# --- YMYL "Your-Money" checks (--strict only) -------------------------------
# Triggered by keywords in the article body. If the article makes tax/rebate
# claims, we require a professional-consultation caveat nearby. Same for APR
# claims. Brand-name defamation risk gets a warn, not a fail.

YOUR_MONEY_TAX_TRIGGERS = r"\b(tax credit|25C|HEEHRA|IRA 25C|federal rebate|IRS Section 25C)\b"
YOUR_MONEY_TAX_CAVEAT = r"(not tax.*advice|consult.*tax professional|qualified tax professional|tax professional.*(confirm|verify)|confirm.*tax professional)"

YOUR_MONEY_APR_TRIGGERS = r"\b(APR|annual percentage rate|financing rate)\b"
YOUR_MONEY_APR_CAVEAT = r"(rates vary|APR.*vary|confirm.*rate.*lender|rates change|rates are subject to change|confirm current rates)"

# Brand names that, when within 120 chars of a negative/scam word, suggest
# single-brand defamation risk. We warn (do not fail).
BRAND_NAMES = [
    "EasySeal", "Nu-Calgon", "Carrier", "Trane", "Lennox", "Goodman", "Rheem",
    "York", "Daikin", "Mitsubishi", "Synchrony", "GreenSky", "Service Finance",
    "HomeAdvisor", "Angi", "Thumbtack", "Yelp",
]
NEGATIVE_WORDS = r"\b(scam|upsell|avoid|never use|rip.?off|bait.?and.?switch|predatory|defaults|voids?)\b"


def audit_your_money(html: str, strict: bool) -> int:
    if not strict:
        return 0
    print("\nYOUR-MONEY YMYL (strict mode)")
    fails = 0

    tax_hit = re.search(YOUR_MONEY_TAX_TRIGGERS, html, re.I)
    if tax_hit:
        caveat = re.search(YOUR_MONEY_TAX_CAVEAT, html, re.I)
        if not check("Tax-professional caveat present (article makes tax/rebate claims)", bool(caveat)):
            fails += 1
    else:
        print("  [INFO] No tax/rebate claims detected — tax caveat not required.")

    apr_hit = re.search(YOUR_MONEY_APR_TRIGGERS, html)
    if apr_hit:
        caveat = re.search(YOUR_MONEY_APR_CAVEAT, html, re.I)
        if not check("APR-vary caveat present (article makes APR/financing-rate claims)", bool(caveat)):
            fails += 1
    else:
        print("  [INFO] No APR/financing-rate claims detected — APR caveat not required.")

    # Brand-defamation warn (no fail)
    brand_risks = []
    for brand in BRAND_NAMES:
        for m in re.finditer(re.escape(brand), html):
            ctx_start = max(0, m.start() - 120)
            ctx_end = min(len(html), m.end() + 120)
            ctx = html[ctx_start:ctx_end]
            if re.search(NEGATIVE_WORDS, ctx, re.I):
                brand_risks.append(brand)
                break
    if brand_risks:
        print(f"  [WARN] Brand names appearing near negative language: {', '.join(sorted(set(brand_risks)))}")
        print("         Review these passages. Prefer category language unless the claim is tied to")
        print("         published manufacturer documentation (e.g., warranty terms).")

    return fails


def audit_css_regression(strict: bool) -> int:
    """Checks that site-wide CSS rules required for articles are present.
    Only runs in --strict mode since it reads files outside the article itself."""
    if not strict:
        return 0
    print("\nCSS REGRESSION (strict mode)")
    fails = 0

    try:
        css = Path("css/style.css").read_text(encoding="utf-8")
    except FileNotFoundError:
        print("  [SKIP] css/style.css not found (run from project root for this check).")
        return 0

    # WCAG 1.4.1 — body links must have a visible affordance in article prose.
    has_rule = re.search(r"\.article-content\s+a\s*\{[^}]*text-decoration\s*:\s*underline", css, re.DOTALL)
    if not check(".article-content a rule with text-decoration:underline exists in style.css", bool(has_rule)):
        fails += 1

    return fails


def audit_pillar_spec(html: str, is_pillar: bool) -> int:
    if not is_pillar:
        return 0
    print("\nPILLAR SPEC (Instruction 2B)")
    fails = 0

    main = re.search(r"<main.*?</main>", html, re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", main.group(0) if main else html)
    word_count = len(re.sub(r"\s+", " ", text).split())
    if not check(f"3,000-5,000 words (actual: {word_count})", 3000 <= word_count <= 5000):
        fails += 1
    if not check("Jump-link TOC (class='toc')", 'class="toc"' in html):
        fails += 1
    q_count = html.count('"@type": "Question"')
    if not check(f"15-25 FAQs for pillar (actual: {q_count})", 15 <= q_count <= 25):
        fails += 1

    return fails


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("--"):
        print("Usage: python audit_article.py <path-to-article.html> [--strict] [--browser-verified]")
        sys.exit(2)

    path = args[0]
    strict = "--strict" in args
    browser_verified = "--browser-verified" in args

    # Blocking gate: strict mode requires explicit browser-verification
    # because the script cannot inspect CSS rendering. This codifies the
    # "audit is a floor, not a ceiling" lesson from the 2026-04-17 C4-pillar
    # link-rendering regression.
    if strict and not browser_verified:
        slug = Path(path).stem
        print("=" * 70)
        print("STRICT MODE requires --browser-verified. Before re-running:")
        print()
        print(f"  1. Start the dev server:  python serve.py")
        print(f"  2. Open in browser:       http://localhost:8080/articles/{slug}")
        print("  3. Visually confirm:")
        print("     (a) Body links are UNDERLINED and BLUE (WCAG 1.4.1)")
        print("     (b) Every FAQ expands/collapses on click")
        print("     (c) TOC jump-links scroll to the correct H2")
        print("     (d) Hero image renders correctly above the disclosure")
        print("     (e) No obvious layout, font, or text issues")
        print(f"  4. Re-run: python audit_article.py {path} --strict --browser-verified")
        print("=" * 70)
        sys.exit(2)

    html = read(path)
    is_pillar = "pillar" in Path(path).stem.lower() or "complete-" in Path(path).stem.lower() or "-guide" in Path(path).stem.lower()

    print(f"Auditing: {path}")
    print(f"Type: {'PILLAR' if is_pillar else 'CLUSTER'}")
    print(f"Mode: {'STRICT (browser-verified)' if strict else 'soft'}")

    fails = 0
    fails += audit_safety(html)
    fails += audit_seo(html)
    fails += audit_your_money(html, strict)
    fails += audit_css_regression(strict)
    fails += audit_pillar_spec(html, is_pillar)

    print()
    if fails == 0:
        mode = "strict" if strict else "soft"
        print(f"OK — all {mode} checks passed. Article is safe to commit.")
        sys.exit(0)
    else:
        print(f"FAIL — {fails} check(s) failed. Fix before committing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
