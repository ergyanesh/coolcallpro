"""Comprehensive QC for city pages — runs every verifiable check needed to
declare a regenerated page batch ship-ready.

Usage:
  python scripts/qc_city_pages.py [--dir locations] [--cities city1.html city2.html ...]
  python scripts/qc_city_pages.py --pilot   # check _pilot_test/ instead

Each city is scored per check; output groups failures by check type so a single
generator bug surfaces as a pattern, not 115 separate noise lines. Exit code is
1 if any city fails any check, 0 otherwise (so it can gate CI / pre-commit).
"""

import os, re, sys, json, argparse, openpyxl

# ============================================================
# Algorithmic truth from CLAUDE.md
# ============================================================
CLIMATE_TYPE_FROM_ZONE = {
    "Zone 1A (Very Hot-Humid)": "tropical",
    "Zone 2A (Hot-Humid)": "hot-humid",
    "Zone 2B (Hot-Dry)": "hot-dry",
    "Zone 3A (Warm-Humid)": "mixed-humid",
    "Zone 3B (Warm-Dry)": "hot-dry",
    "Zone 3C (Warm-Marine)": "coastal",
    "Zone 4A (Mixed-Humid)": None,  # see ZONE_4A_DECISIONS for per-city override
    "Zone 4B (Mixed-Dry)": "mountain",
    "Zone 4C (Mixed-Marine)": "coastal",
    "Zone 5A (Cool-Humid)": "cold",
    "Zone 5B (Cold-Dry)": "mountain",
    "Zone 5B (Cool-Dry)": "mountain",
    "Zone 6A (Cold-Humid)": "cold",
    "Zone 6B (Cold-Dry)": "mountain",
    "Zone 7 (Very Cold)": "subarctic",
    "Zone 8 (Subarctic)": "subarctic",
}

# Zone 4A is climatically borderline — northern Zone 4A cities (Mid-Atlantic +
# upper Midwest + NY/NJ) function as cold-climate from an HVAC perspective
# (winter heating dominates), so emergency cards prioritize NO HEAT + FROZEN
# PIPES. Southern Zone 4A cities (Southeast + Tennessee Valley) function as
# mixed-humid. This table mirrors generate_city_pages_v3.py:177 ZONE_4A_DECISIONS
# verbatim — keep them in sync.
ZONE_4A_OVERRIDES = {
    "Kansas City": "cold", "Philadelphia": "cold", "St. Louis": "mixed-humid",
    "Charlotte": "mixed-humid", "Baltimore": "cold", "Washington": "mixed-humid",
    "Nashville": "mixed-humid", "Louisville": "mixed-humid", "Lexington": "mixed-humid",
    "Raleigh": "mixed-humid", "Winston-Salem": "mixed-humid", "Wichita": "cold",
    "Chattanooga": "mixed-humid", "Knoxville": "mixed-humid", "Newark": "cold",
    "New York City": "cold", "Richmond": "mixed-humid", "Virginia Beach": "mixed-humid",
    "Dayton": "cold", "Fort Wayne": "cold", "Indianapolis": "cold",
    "Omaha": "cold", "Lincoln": "cold", "Des Moines": "cold",
    "Toledo": "cold", "Columbus": "cold", "Cleveland": "cold",
    "Akron": "cold", "Buffalo": "cold", "Syracuse": "cold",
    "Rochester": "cold", "Wilmington": "cold", "Charleston": "mixed-humid",
}

def resolve_climate_type(zone, city_name):
    """Resolve climate type with Zone 4A override fallback. Mirrors generator logic."""
    ct = CLIMATE_TYPE_FROM_ZONE.get(zone)
    if ct is None and "4A" in str(zone):
        ct = ZONE_4A_OVERRIDES.get(city_name, "mixed-humid")
    return ct
EXPECTED_EMERGENCY_CARDS = {
    "tropical":    ("NO AC", "NO HEAT", "WATER LEAK"),
    "hot-humid":   ("NO AC", "NO HEAT", "WATER LEAK"),
    "hot-dry":     ("NO AC", "STRANGE NOISES", "NO HEAT"),
    "mixed-humid": ("NO AC", "NO HEAT", "STRANGE NOISES"),
    "coastal":     ("NO AC", "NO HEAT", "STRANGE NOISES"),
    "mountain":    ("NO HEAT", "NO AC", "STRANGE NOISES"),
    "cold":        ("NO HEAT", "FROZEN PIPES", "NO AC"),
    "subarctic":   ("NO HEAT", "FROZEN PIPES", "NO AC"),
}

STALE_OBBBA_PATTERNS = [
    "Federal tax credits of up to $2,000 for qualifying heat pumps",
    "may also receive up to $3,200/year via the",
    "Federal tax credits may also apply for qualifying high-efficiency",
    "Federal ENERGY STAR tax credits may also apply",
    "All local incentives stack with the federal",
]

REQUIRED_SECTION_MARKERS = [
    "EMERGENCY LANE",
    "TRUST STRIP",
    "CLIMATE",  # CLIMATE + PHOTO
    "LOCAL DATA 2x2",
    "SERVICES + ZIPS",
    "MID-PAGE CTA",
    "FAQs",
    "Nearby Service Areas",
]

CITY_FILE_RE = re.compile(r'^([a-z0-9-]+?)-([a-z]{2})\.html$')

def slug_to_city_name_lookup(xlsx_path='cities_updated.xlsx'):
    """Build a lookup from slug -> (city_name, state, climate_zone, summer_high, winter_low)."""
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    out = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]: continue
        city, state = row[0], row[1]
        slug = re.sub(r'[^a-z0-9]+', '-', f"{city.lower()}-{state.lower()}").strip('-')
        out[slug] = {
            'city': city,
            'state': state,
            'zone': row[14],
            'summer_high': row[9],
            'winter_low': row[10],
            'published': row[15],
        }
    return out

# ============================================================
# Per-city checks
# ============================================================
def check_emergency_cards(html, expected):
    m = re.search(r'EMERGENCY LANE.*?TRUST STRIP', html, re.DOTALL)
    if not m: return ("missing EMERGENCY LANE section",)
    icons = re.findall(r'<div class="precaution-icon"[^>]*>([^<]+?)</div>', m.group(0))
    cards = []
    for icon in icons[:3]:
        cleaned = re.sub(r'^[^A-Z]*', '', icon).strip()
        cards.append(cleaned)
    if len(cards) < 3:
        return (f"only {len(cards)} emergency cards found, expected 3",)
    if tuple(cards) != expected:
        return (f"got {tuple(cards)} expected {expected}",)
    return ()

def check_local_data_cards(html):
    """Each of 4 cards must have: H3 non-empty, body non-empty, ≥1 link, H3 != topic-icon-text."""
    m = re.search(r'LOCAL DATA 2x2.*?SERVICES \+ ZIPS', html, re.DOTALL)
    if not m: return ["missing LOCAL DATA 2x2 section"]
    section = m.group(0)
    # Parse 4 cards: each card has precaution-icon + h3 + body + (optional) link
    cards = re.findall(
        r'<div class="precaution-icon"[^>]*>([^<]+?)</div>\s*'
        r'<h3>([^<]*)</h3>\s*'
        r'<p[^>]*>(.*?)</p>',
        section, re.DOTALL
    )
    failures = []
    if len(cards) != 4:
        failures.append(f"found {len(cards)} Local Data cards, expected 4")
        return failures
    for i, (icon, h3, body) in enumerate(cards):
        # icon may have HTML entities like &#127777;&#65039; — strip to get topic words
        icon_clean = re.sub(r'&#\d+;|&[a-z]+;|\s+', ' ', icon).strip().lower()
        h3_clean = h3.strip().lower()
        body_clean = re.sub(r'<[^>]+>', '', body).strip()
        if not h3.strip():
            failures.append(f"card {i+1}: empty H3")
        if len(body_clean) < 30:
            failures.append(f"card {i+1}: body too short ({len(body_clean)} chars)")
        if 'href=' not in body:
            failures.append(f"card {i+1}: no <a href> in body — missing primary source")
        # Topic-icon vs H3 duplication check: the icon strips down to e.g. "climate profile";
        # H3 should NOT contain the same phrase verbatim
        topic_words = [w for w in icon_clean.split() if len(w) > 3]
        if topic_words and all(w in h3_clean for w in topic_words):
            failures.append(f"card {i+1}: H3 duplicates icon topic ('{icon.strip()}' vs '{h3}')")
    return failures

def check_hero_subhead(html):
    m = re.search(r'<section class="city-hero".*?</section>', html, re.DOTALL)
    if not m: return ["missing city-hero section"]
    section = m.group(0)
    failures = []
    # Extract the subhead paragraph (first <p> after the H1)
    sub = re.search(r'<h1>.*?</h1>\s*<p>(.*?)</p>', section, re.DOTALL)
    if not sub: return ["no hero subhead <p> found"]
    text = re.sub(r'<[^>]+>', '', sub.group(1))
    # Placeholders that should never leak
    if '{summer_high}' in text: failures.append("subhead leaked {summer_high} placeholder")
    if '{winter_low}' in text: failures.append("subhead leaked {winter_low} placeholder")
    if '{city}' in text.lower(): failures.append("subhead leaked {city} placeholder")
    if len(text) < 30: failures.append(f"subhead too short ({len(text)} chars)")
    return failures

def check_obbba_clean(html):
    failures = []
    for pattern in STALE_OBBBA_PATTERNS:
        if pattern in html:
            failures.append(f"stale OBBBA claim: '{pattern[:60]}...'")
    return failures

def check_clean_urls(html):
    failures = []
    # Internal hrefs (relative or coolcallpro.com) must not contain .html
    internal_html = re.findall(r'href="((?:\.\.?/|/)[^"]*?\.html)"', html)
    if internal_html:
        failures.append(f"{len(internal_html)} internal href(s) end in .html — first: {internal_html[0]}")
    # Canonical
    canon = re.search(r'<link rel="canonical"\s+href="([^"]+)"', html)
    if not canon:
        failures.append("missing canonical")
    else:
        url = canon.group(1)
        if not url.startswith('https://coolcallpro.com'):
            failures.append(f"canonical wrong domain: {url}")
        if url.endswith('.html'):
            failures.append(f"canonical ends in .html: {url}")
    return failures

def check_jsonld(html):
    failures = []
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    if not blocks:
        failures.append("no JSON-LD blocks")
        return failures
    for i, raw in enumerate(blocks):
        try:
            json.loads(raw)
        except json.JSONDecodeError as e:
            failures.append(f"JSON-LD block {i+1} invalid: {e}")
    return failures

def check_no_local_business(html):
    failures = []
    if '"@type": "LocalBusiness"' in html or '"@type":"LocalBusiness"' in html:
        failures.append("LocalBusiness schema present (banned for referral site)")
    if '"@type": "LocalService"' in html or '"@type":"LocalService"' in html:
        failures.append("LocalService schema present (banned for referral site)")
    return failures

def check_required_sections(html):
    failures = []
    for marker in REQUIRED_SECTION_MARKERS:
        if marker not in html:
            failures.append(f"section marker missing: '{marker}'")
    return failures

def check_meta_basics(html):
    failures = []
    h1_count = len(re.findall(r'<h1[\s>]', html))
    if h1_count != 1:
        failures.append(f"{h1_count} <h1> tags (expected 1)")
    title = re.search(r'<title>([^<]+)</title>', html)
    if not title:
        failures.append("missing <title>")
    elif len(title.group(1)) > 70:
        failures.append(f"<title> length {len(title.group(1))} > 70")
    desc = re.search(r'<meta name="description"[^>]*content="([^"]+)"', html)
    if not desc:
        failures.append("missing meta description")
    elif len(desc.group(1)) > 160:
        failures.append(f"meta description length {len(desc.group(1))} > 160")
    return failures

def check_mobile_call_bar(html):
    if '<div class="mobile-call-bar">' not in html:
        return ["missing mobile-call-bar"]
    return []

def check_footer_col(html):
    if 'class="footer"' in html and 'class="footer-col"' not in html:
        return ["footer present but missing footer-col wrappers (renders invisibly)"]
    return []

# ============================================================
# Main
# ============================================================
ALL_CHECKS = [
    ('emergency_cards',  check_emergency_cards),  # signature differs — handled separately
    ('local_data_cards', check_local_data_cards),
    ('hero_subhead',     check_hero_subhead),
    ('obbba_clean',      check_obbba_clean),
    ('clean_urls',       check_clean_urls),
    ('jsonld',           check_jsonld),
    ('no_local_biz',     check_no_local_business),
    ('required_sections', check_required_sections),
    ('meta_basics',      check_meta_basics),
    ('mobile_call_bar',  check_mobile_call_bar),
    ('footer_col',       check_footer_col),
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='locations', help='Directory to scan (default: locations)')
    ap.add_argument('--pilot', action='store_true', help='Scan _pilot_test/ instead of locations/')
    ap.add_argument('--cities', nargs='*', help='Specific filenames to check (e.g. atlanta-ga.html)')
    args = ap.parse_args()

    target_dir = '_pilot_test' if args.pilot else args.dir
    if not os.path.isdir(target_dir):
        print(f"ERROR: directory not found: {target_dir}")
        sys.exit(2)

    xlsx_data = slug_to_city_name_lookup()

    if args.cities:
        files = [f for f in args.cities if os.path.exists(os.path.join(target_dir, f))]
    else:
        files = sorted(f for f in os.listdir(target_dir) if CITY_FILE_RE.match(f))

    if not files:
        print(f"No city HTML files found in {target_dir}")
        sys.exit(0)

    print(f"Running QC on {len(files)} city pages in {target_dir}/")
    print("=" * 100)

    failure_pattern = {}  # check_name -> list of (city, failure)
    perfect = []
    failed = []

    for fn in files:
        slug = fn.replace('.html', '')
        path = os.path.join(target_dir, fn)
        with open(path, 'r', encoding='utf-8') as fh:
            html = fh.read()

        city_failures = []
        # Emergency cards — needs xlsx data + Zone 4A override resolution
        meta = xlsx_data.get(slug)
        if meta:
            ctype = resolve_climate_type(meta['zone'], meta['city'])
            if ctype:
                expected = EXPECTED_EMERGENCY_CARDS.get(ctype)
                fails = check_emergency_cards(html, expected)
                for f in fails:
                    city_failures.append(('emergency_cards', f))
            else:
                city_failures.append(('emergency_cards', f"unmapped zone: {meta['zone']}"))
        else:
            city_failures.append(('xlsx_lookup', f"no xlsx row for slug: {slug}"))

        # Other checks
        for check_name, fn_check in ALL_CHECKS[1:]:  # skip emergency_cards (already done)
            fails = fn_check(html)
            for f in fails:
                city_failures.append((check_name, f))

        if not city_failures:
            perfect.append(slug)
        else:
            failed.append(slug)
            for check_name, msg in city_failures:
                failure_pattern.setdefault(check_name, []).append((slug, msg))

    print(f"\n{'='*100}\nRESULT: {len(perfect)} clean / {len(failed)} with failures, out of {len(files)} total\n{'='*100}\n")

    if failure_pattern:
        for check_name, failures in sorted(failure_pattern.items(), key=lambda kv: -len(kv[1])):
            print(f"\n[{check_name}] {len(failures)} cities failed:")
            for slug, msg in failures[:5]:
                print(f"  {slug}: {msg}")
            if len(failures) > 5:
                print(f"  ... and {len(failures)-5} more")

    if failed:
        print(f"\n{len(failed)} cities failed. Exit 1.")
        sys.exit(1)
    else:
        print("\nAll cities pass QC. Exit 0.")
        sys.exit(0)

if __name__ == '__main__':
    main()
