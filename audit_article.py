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

import html as html_mod
import re
import sys
from datetime import date, datetime
from pathlib import Path

from safety_rules import check_diy_hazards


# --- YMYL claim triggers (used by audit_ymyl_log + link-proximity check) ----
# Any article body containing one of these terms (outside HTML comments) makes
# YMYL claims and is therefore subject to the verification-log + primary-source-
# proximity gates. Tax / regulatory / refrigerant / dollar-cap / federal-program
# territory.
YMYL_CLAIM_TRIGGERS = [
    r"\bSection 25C\b", r"\bSection 25D\b", r"\bOBBBA\b", r"\bPublic Law 119-21\b",
    r"\bForm 5695\b", r"\bHEAR\b", r"\bHEEHRA\b", r"\bInflation Reduction Act\b",
    r"\bAIM Act\b", r"\bSection 608\b", r"\bR-454B\b", r"\bR-410A\b",
    r"\bGWP\s+\d", r"\bCFPB\b", r"\bR-PACE\b", r"\bSEER2\b", r"\bHSPF2\b",
    r"federal tax credit", r"federal rebate", r"federally regulated",
]
YMYL_TRIGGER_REGEX = re.compile("|".join(YMYL_CLAIM_TRIGGERS), re.IGNORECASE)

# Primary-source domains accepted for link-proximity proof. .gov / .edu /
# energystar.gov / dsireusa.org. Industry sites (acca.org, ahri.org) also
# count for refrigerant / standards claims.
PRIMARY_SOURCE_DOMAINS = [
    "irs.gov", "epa.gov", "energy.gov", "energystar.gov", "dsireusa.org",
    "cdc.gov", "cfpb.gov", "consumerfinance.gov", "noaa.gov", "census.gov",
    "ftc.gov", "doe.gov", "bls.gov", "congress.gov", "govinfo.gov",
    "osha.gov", "nfpa.org",
    ".edu", "acca.org", "ahri.org", "ashrae.org",
]

# YMYL log staleness — re-verification cadence.
YMYL_LOG_MAX_AGE_DAYS = 90


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

    # Unescape HTML entities so &amp; counts as 1 char, not 5. Google indexes
    # the displayed text, not the HTML-escaped source.
    t_len = len(html_mod.unescape(t))
    m_len = len(html_mod.unescape(m))
    if not check(f"<title> <= 60 chars (actual: {t_len})", t_len <= 60):
        fails += 1
    if not check(f"Meta description <= 155 chars (actual: {m_len})", m_len <= 155):
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


def audit_geo_aeo(html: str, strict: bool) -> int:
    """Generative-engine + answer-engine optimization checks.
    Enforces SEO/AEO/GEO schemas that Google and LLM citation engines reward:
      - Speakable schema (voice search + accessibility)
      - about[] with sameAs entity URIs (knowledge-graph linking for GEO)
      - HowTo schema MUST BE ABSENT. Google deprecated HowTo rich results in
        September 2023 — it no longer triggers rich snippets and some
        crawlers treat it as a quality-regression signal. Per FULL-AUDIT-
        REPORT.md finding C1 (2026-04-26), all 12 articles that previously
        carried HowTo schema were stripped via scripts/remove_howto_schema.py.
        This audit check now blocks any future commit that re-introduces it.
    """
    if not strict:
        return 0
    print("\nGEO / AEO (strict mode)")
    fails = 0

    # Speakable schema — any page with FAQ or TLDR should flag it for voice
    has_speakable = '"@type": "SpeakableSpecification"' in html or '"SpeakableSpecification"' in html
    if not check("Speakable schema present (voice search + AEO)", has_speakable):
        fails += 1

    # Entity linking via about[] with sameAs
    has_entity = bool(re.search(r'"about"\s*:\s*\[[^\]]*"sameAs"', html, re.DOTALL))
    if not check("Article 'about' array includes at least one sameAs entity URI (GEO)", has_entity):
        fails += 1

    # HowTo schema must be ABSENT. Deprecated by Google September 2023.
    # Numbered-step procedures still render fine as plain HTML <ol> — only
    # the structured-data schema is forbidden. Replace HowTo's role with
    # Article + FAQPage schema (which the rest of the site already uses).
    has_howto = '"@type": "HowTo"' in html or '"@type":"HowTo"' in html
    if not check(
        "HowTo schema is ABSENT (Google deprecated rich results Sept 2023)",
        not has_howto,
        "Remove the <script type=\"application/ld+json\"> block whose @type is HowTo. "
        "Run scripts/remove_howto_schema.py if the article still has it. "
        "Visible step-by-step content stays as plain HTML — only the schema goes.",
    ):
        fails += 1

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
    # The rule may use :not(.btn) or similar exclusions; accept any selector
    # that targets .article-content descendants of type <a> and applies underline.
    has_underline_rule = re.search(
        r"\.article-content\s+a(?::not\([^)]+\))?\s*\{[^}]*text-decoration\s*:\s*underline",
        css, re.DOTALL,
    )
    if not check(".article-content a rule with text-decoration:underline exists in style.css", bool(has_underline_rule)):
        fails += 1

    # Body link color must be orange-dark (site design convention), not blue.
    # Using blue breaks visual consistency with existing body links in
    # index.html's About Our HVAC Network section and other content sections.
    has_orange_color = re.search(
        r"\.article-content\s+a(?::not\([^)]+\))?\s*\{[^}]*color\s*:\s*var\(--orange",
        css, re.DOTALL,
    )
    if not check(".article-content a color is --orange or --orange-dark (body link convention)", bool(has_orange_color)):
        fails += 1

    # Button protection: the selector must exclude .btn to avoid overriding
    # CTA button styling when a button anchor is inside .article-content.
    has_btn_exclusion = re.search(
        r"\.article-content\s+a:not\(\.btn\)", css
    )
    if not check(".article-content a selector excludes .btn (CTA button protection)", bool(has_btn_exclusion)):
        fails += 1

    return fails


def audit_font_loading(html: str) -> int:
    """Articles must NOT have <link rel="preload" ... .woff2 ...> tags.

    Articles' LCP target is the hero WebP image. Preloading fonts there
    steals connection bandwidth from the LCP and triggers Chrome's
    "preloaded font not used within a few seconds from the window's
    load event" console warning. Fonts still load via style.min.css's
    @font-face with font-display: swap — fast enough since the LCP
    is image-driven, not text-driven.

    Deployed 24 April 2026 across all 23 articles. Migration script:
    scripts/inline_fontface.py (idempotent).
    """
    print("\nFONT LOADING (Chrome 'preloaded font not used' protection)")
    has_font_preload = bool(
        re.search(
            r'<link\s+rel=["\']preload["\'][^>]*\.woff2',
            html,
            re.IGNORECASE,
        )
    )
    if not check(
        "Article has NO font preload tags (LCP is hero image, not text)",
        not has_font_preload,
        "Remove <link rel=\"preload\" ... .woff2 ...>. Articles' LCP target is the hero WebP — preloading fonts steals bandwidth from the LCP and triggers Chrome's 'preloaded font not used' console warning. Fonts still load via style.min.css's @font-face with font-display: swap.",
    ):
        return 1
    return 0


def _strip_html_comments(html: str) -> str:
    """Return body HTML with all <!-- ... --> comments removed.

    Used by YMYL audits so that the verification-log header (which itself
    contains 25C/OBBBA/AIM-Act mentions for documentation purposes) is not
    treated as YMYL claims that need primary-source proximity links.
    """
    return re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)


def _extract_ymyl_log(html: str):
    """Return (log_text, last_verified, next_due) or (None, None, None).

    The canonical block lives inside an HTML comment near <head> and starts
    with the literal "YMYL VERIFICATION LOG". Dates parse as YYYY-MM-DD.
    """
    m = re.search(r"YMYL VERIFICATION LOG.*?-->", html, re.DOTALL)
    if not m:
        return (None, None, None)
    block = m.group(0)
    last = re.search(r"last verified\s+(\d{4}-\d{2}-\d{2})", block, re.IGNORECASE)
    nxt = re.search(r"next due\s+(\d{4}-\d{2}-\d{2})", block, re.IGNORECASE)
    return (
        block,
        datetime.strptime(last.group(1), "%Y-%m-%d").date() if last else None,
        datetime.strptime(nxt.group(1), "%Y-%m-%d").date() if nxt else None,
    )


def audit_ymyl_log(html: str, strict: bool) -> int:
    """Layer 1 of the YMYL verification system (added 2026-05-08).

    Three gates fire only on articles that actually make YMYL claims:

    A. Verification-log presence. If the article body (HTML-comments stripped)
       contains any YMYL trigger term, the inline log block is REQUIRED.
    B. Log-entry format. Each CLAIM block must cite a URL on a primary-source
       domain. "last verified" and "next due" dates must parse.
    C. Staleness gate. If today >= next-due-date, the article is OUT OF DATE
       — block the commit so the writer must re-verify before editing.

    Rationale: the audit was a phrasing linter. It caught "tax credit" without
    a "consult a tax professional" caveat, but never caught a tax-credit claim
    whose primary source had quietly changed under us. These three gates close
    that loop. See CLAUDE.md "Live Verification Discipline" (2026-05-04).
    """
    if not strict:
        return 0
    print("\nYMYL VERIFICATION-LOG AUDIT (Layer 1)")
    fails = 0

    body = _strip_html_comments(html)
    has_claims = bool(YMYL_TRIGGER_REGEX.search(body))

    if not has_claims:
        print("  [INFO] No YMYL trigger terms in body — verification log not required.")
        return 0

    log_block, last_verified, next_due = _extract_ymyl_log(html)

    # Gate A — log present
    if not check(
        "YMYL VERIFICATION LOG block present in <head>",
        log_block is not None,
        "Article makes YMYL claims (25C/OBBBA/HEAR/AIM Act/Section 608/etc.) "
        "but has no inline verification log. See any 2026-05-04 article for the "
        "canonical format.",
    ):
        return fails + 1

    # Gate B — required fields parse
    if not check(
        f"Log has parseable 'last verified' date (got: {last_verified})",
        last_verified is not None,
    ):
        fails += 1
    if not check(
        f"Log has parseable 'next due' date (got: {next_due})",
        next_due is not None,
    ):
        fails += 1

    # Each CLAIM block must cite either a primary-source URL or a known
    # project-internal source of truth (costs.html, cluster_map.json).
    # Split the log on CLAIM markers so we can check each block individually.
    claim_blocks = re.split(r"(?=CLAIM\s+\d+:)", log_block)
    claim_blocks = [b for b in claim_blocks if re.match(r"CLAIM\s+\d+:", b)]
    INTERNAL_SOURCES = ("costs.html", "cluster_map.json", "states.xlsx", "cities_updated.xlsx")
    if not claim_blocks:
        if not check(
            "Log contains at least one CLAIM N: entry",
            False,
            "Log block exists but has no 'CLAIM N: ...' entries.",
        ):
            fails += 1
    else:
        unsourced = []
        for cb in claim_blocks:
            urls = re.findall(r"https?://\S+", cb)
            has_primary = any(any(d in u for d in PRIMARY_SOURCE_DOMAINS) for u in urls)
            has_internal = any(s in cb for s in INTERNAL_SOURCES)
            if not (has_primary or has_internal):
                num_match = re.match(r"CLAIM\s+(\d+):", cb)
                unsourced.append(num_match.group(1) if num_match else "?")
        if not check(
            f"Each CLAIM cites a primary-source URL or internal canonical "
            f"({len(claim_blocks) - len(unsourced)}/{len(claim_blocks)} sourced)",
            not unsourced,
            (
                f"CLAIM(s) {', '.join(unsourced)} have no primary-source URL "
                f"(.gov / .edu / dsireusa.org / energystar.gov / acca.org / ahri.org / "
                f"ashrae.org) and no internal canonical reference (costs.html / "
                f"cluster_map.json / states.xlsx / cities_updated.xlsx). Add a "
                f"'URL: <primary-source-url>' line to each."
            ) if unsourced else "",
        ):
            fails += 1

    # Gate C — staleness
    if next_due is not None:
        today = date.today()
        days_overdue = (today - next_due).days
        if days_overdue > 0:
            if not check(
                f"YMYL log freshness (overdue by {days_overdue} days; next-due was {next_due})",
                False,
                f"Re-verify each CLAIM against its primary source via WebFetch, then bump "
                f"'last verified' to today ({today}) and 'next due' to "
                f"{date.fromordinal(today.toordinal() + YMYL_LOG_MAX_AGE_DAYS)}.",
            ):
                fails += 1
        else:
            days_left = -days_overdue
            print(f"  [PASS] YMYL log freshness ({days_left} days until next due {next_due})")

    return fails


# Per-topic primary-source matrix. For every YMYL claim TYPE that appears in
# the article body, at least one anchor href on a matching domain must also
# appear in the body. Catches "article cites OBBBA but never links to IRS"
# without flagging every TLDR mention.
YMYL_TOPIC_SOURCE_MATRIX = [
    # (topic regex, list of acceptable primary-source domains, human label)
    (r"\bSection 25C\b|\bSection 25D\b|\bForm 5695\b|federal tax credit",
     ["irs.gov", "energystar.gov"], "tax-credit / 25C / 25D / Form 5695"),
    (r"\bOBBBA\b|\bPublic Law 119-21\b",
     ["irs.gov", "congress.gov", "govinfo.gov"], "OBBBA / Public Law 119-21"),
    (r"\bAIM Act\b|\bR-454B\b|\bR-410A\b|\bGWP\s+\d",
     ["epa.gov"], "AIM Act / refrigerant transition"),
    (r"\bSection 608\b|federally regulated",
     ["epa.gov"], "EPA Section 608 refrigerant certification"),
    (r"\bHEAR\b|\bHEEHRA\b|\bInflation Reduction Act\b|federal rebate",
     ["energy.gov", "dsireusa.org"], "HEAR / IRA rebate program"),
    (r"\bCFPB\b|\bR-PACE\b",
     ["consumerfinance.gov", "cfpb.gov"], "CFPB / R-PACE"),
    (r"\bSEER2\b|\bHSPF2\b",
     ["energy.gov", "energystar.gov", "ahri.org"], "SEER2 / HSPF2 efficiency standards"),
]


def audit_ymyl_link_proximity(html: str, strict: bool) -> int:
    """Per-topic primary-source matrix check. For every YMYL claim TYPE
    (25C, OBBBA, AIM Act, HEAR, Section 608, CFPB, SEER2/HSPF2) that appears
    in the article body, the body must include at least one <a href> to a
    matching primary-source domain. Catches "article uses term X but cites
    no primary source for X anywhere."

    This is the article-level discipline — not paragraph-level. A single
    well-placed inline <a href="https://www.irs.gov/...">IRS Section 25C
    page</a> covers every 25C mention in the article. The audit cares that
    the source is present and pointable, not that every paragraph repeats
    the citation.

    Scope: <article class="article-content"> body only. Schema, head meta,
    and the verification log are excluded.
    """
    if not strict:
        return 0
    print("\nYMYL TOPIC -> SOURCE MATRIX (per-topic primary-source link required)")

    article_match = re.search(
        r'<article class="article-content">(.*?)</article>', html, re.DOTALL
    )
    if not article_match:
        print("  [INFO] No <article class=\"article-content\"> body found — skipping.")
        return 0
    body = _strip_html_comments(article_match.group(1))

    hrefs = [hm.group(1) for hm in re.finditer(r'href="([^"]+)"', body)]
    fails = 0
    for topic_pat, accepted_domains, label in YMYL_TOPIC_SOURCE_MATRIX:
        if not re.search(topic_pat, body, re.IGNORECASE):
            continue
        has_source = any(any(d in h for d in accepted_domains) for h in hrefs)
        if not check(
            f"Topic '{label}' has primary-source link in body "
            f"(accepted: {', '.join(accepted_domains)})",
            has_source,
            f"Article makes claims under '{label}' but the body has NO link to "
            f"{' or '.join(accepted_domains)}. Add an inline <a href> to one of "
            f"those domains in the section discussing this topic.",
        ):
            fails += 1
    if fails == 0:
        print("  [PASS] Every YMYL topic in the body has a matching primary-source link")
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
    ci_mode = "--ci" in args
    strict = "--strict" in args or ci_mode
    browser_verified = "--browser-verified" in args or ci_mode

    # Blocking gate: strict mode requires explicit browser-verification
    # because the script cannot inspect CSS rendering. This codifies the
    # "audit is a floor, not a ceiling" lesson from the 2026-04-17 C4-pillar
    # link-rendering regression.
    # --ci mode (used by the git pre-commit hook) runs all strict text checks
    # unattended; the browser-verification gate stays as agent discipline.
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
    if ci_mode:
        mode_label = "STRICT (ci / pre-commit — browser check is agent discipline)"
    elif strict:
        mode_label = "STRICT (browser-verified)"
    else:
        mode_label = "soft"
    print(f"Mode: {mode_label}")

    fails = 0
    fails += audit_safety(html)
    fails += check_diy_hazards(html, source_label=path)
    fails += audit_seo(html)
    fails += audit_your_money(html, strict)
    fails += audit_ymyl_log(html, strict)
    fails += audit_ymyl_link_proximity(html, strict)
    fails += audit_geo_aeo(html, strict)
    fails += audit_css_regression(strict)
    fails += audit_font_loading(html)
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
