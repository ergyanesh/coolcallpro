"""
Fix SEO issues identified from GSC data (8 April 2026):
1. Update city page titles to include "Emergency" keyword
2. Update city page meta descriptions with emergency language
3. Fix H1 tags on city pages missing emergency language
4. Generate _redirects file for .html -> clean URL 301 redirects
"""

import os
import re
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))
LOCATIONS_DIR = os.path.join(ROOT, "locations")

# =============================================================================
# 1. TITLE UPDATES — Add "Emergency" to city page titles
# =============================================================================

TITLE_REPLACEMENTS = [
    # Most common pattern: "24/7 AC & HVAC Repair in"
    ("24/7 AC &amp; HVAC Repair in", "Emergency HVAC Repair in"),
    # Cold-climate cities: "Furnace & Heating Repair in"
    ("Furnace &amp; Heating Repair in", "Emergency Heating Repair in"),
    # Some larger cities: "HVAC & AC Service in"
    ("HVAC &amp; AC Service in", "Emergency HVAC Service in"),
    # Denver: "HVAC Repair & Service in"
    ("HVAC Repair &amp; Service in", "Emergency HVAC Repair in"),
    # DC: "HVAC Service & Repair in"  (state pages use this too — only fix city pages)
    ("HVAC Service &amp; Repair in District of Columbia", "Emergency HVAC Service in Washington, DC"),
]

# H1 REPLACEMENTS — Fix the 7 city pages with non-emergency H1s
H1_REPLACEMENTS = [
    ("Year-Round HVAC Repair &amp; AC Service in", "Emergency HVAC Repair &amp; AC Service in"),
    ("High-Altitude HVAC Repair &amp; Service in", "Emergency HVAC Repair &amp; Service in"),
]

def is_city_page(filepath):
    """Return True if this is a city page, not a state hub page."""
    basename = os.path.basename(filepath)
    # State pages are single-word names like texas.html, california.html
    # City pages have hyphens with state abbreviation like houston-tx.html
    # Exception: district-of-columbia.html is a state-level page
    if basename == "district-of-columbia.html":
        return True  # Treat DC as city for title purposes
    # State pages: no state abbreviation suffix
    name = basename.replace(".html", "")
    # City pages typically end with -XX (state abbreviation)
    return bool(re.search(r'-[a-z]{2}$', name))


def fix_city_page(filepath):
    """Apply title, meta description, and H1 fixes to a city page."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    basename = os.path.basename(filepath)
    changes = []

    # --- Title fixes ---
    for old, new in TITLE_REPLACEMENTS:
        if old in content:
            # Only replace within <title> tags
            title_match = re.search(r'<title>.*?</title>', content)
            if title_match and old in title_match.group():
                content = content.replace(
                    title_match.group(),
                    title_match.group().replace(old, new)
                )
                changes.append(f"  Title: '{old}' -> '{new}'")
                break

    # --- Meta description fix: add "emergency" ---
    meta_match = re.search(
        r'(<meta\s+name="description"\s+content=")(Need HVAC repair in)',
        content
    )
    if meta_match:
        content = content.replace(
            meta_match.group(),
            meta_match.group(1) + "Need emergency HVAC repair in"
        )
        changes.append("  Meta: Added 'emergency' to description")

    # --- H1 fixes ---
    for old, new in H1_REPLACEMENTS:
        if old in content:
            content = content.replace(old, new)
            changes.append(f"  H1: '{old}' -> '{new}'")
            break

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] {basename}")
        for c in changes:
            print(c)
        return True
    else:
        return False


# =============================================================================
# 2. GENERATE _redirects FILE
# =============================================================================

def generate_redirects():
    """Generate _redirects file for Cloudflare Pages to 301 redirect .html -> clean URLs."""
    redirects = []

    # Root-level HTML pages
    root_html = glob.glob(os.path.join(ROOT, "*.html"))
    for f in sorted(root_html):
        basename = os.path.basename(f)
        if basename == "404.html":
            continue  # Cloudflare uses 404.html specially
        name = basename.replace(".html", "")
        redirects.append(f"/{basename} /{name} 301")

    # Location pages
    loc_html = glob.glob(os.path.join(LOCATIONS_DIR, "*.html"))
    for f in sorted(loc_html):
        basename = os.path.basename(f)
        name = basename.replace(".html", "")
        redirects.append(f"/locations/{basename} /locations/{name} 301")

    # Article pages in articles/ directory
    articles_dir = os.path.join(ROOT, "articles")
    if os.path.isdir(articles_dir):
        art_html = glob.glob(os.path.join(articles_dir, "*.html"))
        for f in sorted(art_html):
            basename = os.path.basename(f)
            name = basename.replace(".html", "")
            redirects.append(f"/articles/{basename} /articles/{name} 301")

    redirect_path = os.path.join(ROOT, "_redirects")
    with open(redirect_path, 'w', encoding='utf-8') as f:
        f.write("# 301 redirects: .html URLs -> clean URLs (SEO canonicalization)\n")
        f.write("# Generated 8 April 2026 to fix duplicate URL indexing in Google\n\n")
        f.write("\n".join(redirects) + "\n")

    print(f"\n[OK] _redirects file created with {len(redirects)} redirect rules")
    return len(redirects)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SEO FIX: Updating city page titles, metas, and H1s")
    print("=" * 60)

    city_pages = [f for f in glob.glob(os.path.join(LOCATIONS_DIR, "*.html"))
                  if is_city_page(f)]

    updated = 0
    skipped = 0
    for page in sorted(city_pages):
        if fix_city_page(page):
            updated += 1
        else:
            skipped += 1

    print(f"\nUpdated: {updated} city pages")
    print(f"Skipped (already had Emergency or no match): {skipped}")

    print("\n" + "=" * 60)
    print("SEO FIX: Generating _redirects file")
    print("=" * 60)
    generate_redirects()

    print("\nDone! Next steps:")
    print("  1. Minify CSS/JS")
    print("  2. Create deploy folder")
    print("  3. Run QC audit")
