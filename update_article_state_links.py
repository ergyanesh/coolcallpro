"""
Step 5: Update 16 articles with state hub links.
Adds state hub links to two sections in each article:
1. "Local HVAC Service Areas" paragraph — adds a second sentence with state hub links
2. "Find a Pro Near You" sidebar widget — adds state hub links before "All Locations"
"""

import re
import os

# City slug → (state slug, state name)
CITY_TO_STATE = {
    'atlanta-ga': ('georgia', 'Georgia'),
    'birmingham-al': ('alabama', 'Alabama'),
    'boston-ma': ('massachusetts', 'Massachusetts'),
    'charlotte-nc': ('north-carolina', 'North Carolina'),
    'chicago-il': ('illinois', 'Illinois'),
    'dallas-tx': ('texas', 'Texas'),
    'denver-co': ('colorado', 'Colorado'),
    'detroit-mi': ('michigan', 'Michigan'),
    'houston-tx': ('texas', 'Texas'),
    'kansas-city-mo': ('missouri', 'Missouri'),
    'las-vegas-nv': ('nevada', 'Nevada'),
    'milwaukee-wi': ('wisconsin', 'Wisconsin'),
    'minneapolis-mn': ('minnesota', 'Minnesota'),
    'new-orleans-la': ('louisiana', 'Louisiana'),
    'oklahoma-city-ok': ('oklahoma', 'Oklahoma'),
    'philadelphia-pa': ('pennsylvania', 'Pennsylvania'),
    'phoenix-az': ('arizona', 'Arizona'),
    'san-antonio-tx': ('texas', 'Texas'),
    'st-louis-mo': ('missouri', 'Missouri'),
    'tampa-fl': ('florida', 'Florida'),
}

# Root articles (in project root)
ROOT_ARTICLES = [
    'article-ac-summer.html',
    'article-carbon-monoxide.html',
    'article-emergency.html',
    'article-fall-prep.html',
    'article-furnace.html',
    'article-heat-pump.html',
    'article-hvac-financing.html',
    'article-maintenance.html',
    'article-refrigerant.html',
    'article-repair-vs-replace.html',
    'article-spring-ac.html',
    'article-winter-storm.html',
]

# Subfolder articles (in articles/)
SUBFOLDER_ARTICLES = [
    'articles/ac-compressor-buzzing-fan-not-spinning.html',
    'articles/furnace-blowing-cold-air-winter.html',
    'articles/hvac-leaking-water-inside-house.html',
    'articles/why-is-my-ac-blowing-warm-air.html',
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def extract_city_slugs(html):
    """Extract city slugs from the Find a Pro Near You sidebar widget only."""
    # Find the sidebar widget section
    sidebar_match = re.search(r'Find a Pro Near You</h4>\s*<ul>(.*?)</ul>', html, re.DOTALL)
    if not sidebar_match:
        return []
    sidebar_html = sidebar_match.group(1)
    # Match city page links like locations/phoenix-az.html or ../locations/phoenix-az.html
    pattern = r'(?:\.\./)?locations/([\w-]+)\.html'
    slugs = re.findall(pattern, sidebar_html)
    # Filter to only known city slugs (exclude state slugs and locations.html)
    return [s for s in slugs if s in CITY_TO_STATE]


def get_unique_states(city_slugs):
    """Map city slugs to unique states, preserving order."""
    seen = set()
    states = []
    for slug in city_slugs:
        state_slug, state_name = CITY_TO_STATE[slug]
        if state_slug not in seen:
            seen.add(state_slug)
            states.append((state_slug, state_name))
    return states


def update_article(filepath, is_subfolder=False):
    """Update a single article with state hub links."""
    full_path = os.path.join(BASE_DIR, filepath)

    if not os.path.exists(full_path):
        print(f"  SKIP: {filepath} not found")
        return False

    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract city slugs
    city_slugs = extract_city_slugs(content)
    if not city_slugs:
        print(f"  SKIP: {filepath} — no city links found")
        return False

    states = get_unique_states(city_slugs)
    if not states:
        print(f"  SKIP: {filepath} — no states mapped")
        return False

    prefix = '../locations' if is_subfolder else 'locations'
    loc_prefix = '../locations.html' if is_subfolder else 'locations.html'

    print(f"  Cities: {city_slugs}")
    print(f"  States: {[s[1] for s in states]}")

    changes = 0

    # === UPDATE 1: "Local HVAC Service Areas" paragraph ===
    # Find the paragraph and add state links sentence
    # Pattern: ends with "or <a href="...">your city</a>.</p>"
    # We'll add a state sentence before the closing </p>

    para_pattern = r'(or <a href="' + re.escape(loc_prefix) + r'"[^>]*>your city</a>\.)(</p>)'

    state_links = []
    for state_slug, state_name in states:
        state_links.append(
            f'<a href="{prefix}/{state_slug}.html" style="color: var(--orange); font-weight: 600;">{state_name}</a>'
        )

    if len(state_links) == 1:
        state_text = state_links[0]
    elif len(state_links) == 2:
        state_text = f'{state_links[0]} and {state_links[1]}'
    else:
        state_text = ', '.join(state_links[:-1]) + ', and ' + state_links[-1]

    new_sentence = f' Browse state HVAC guides: {state_text}.'

    replacement = r'\1' + new_sentence + r'\2'

    new_content, count = re.subn(para_pattern, replacement, content, count=1)
    if count > 0:
        content = new_content
        changes += 1
        print(f"  OK: Updated 'Local HVAC Service Areas' paragraph")
    else:
        print(f"  FAIL: Could not find paragraph pattern")

    # === UPDATE 2: "Find a Pro Near You" sidebar widget ===
    # Add state hub links before "All Locations →"
    # Pattern: line with "All Locations &rarr;"

    all_loc_pattern = r'(\s*<li><a href="' + re.escape(loc_prefix) + r'" style="font-weight: 600;">All Locations &rarr;</a></li>)'

    state_li_lines = []
    for state_slug, state_name in states:
        state_li_lines.append(
            f'                                <li><a href="{prefix}/{state_slug}.html" style="font-weight: 600;">{state_name} HVAC Guide</a></li>'
        )

    state_li_block = '\n'.join(state_li_lines)

    def sidebar_replacer(match):
        return '\n' + state_li_block + match.group(0)

    new_content, count = re.subn(all_loc_pattern, sidebar_replacer, content, count=1)
    if count > 0:
        content = new_content
        changes += 1
        print(f"  OK: Updated 'Find a Pro Near You' sidebar")
    else:
        print(f"  FAIL: Could not find sidebar 'All Locations' pattern")

    if changes > 0:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  SAVED: {filepath} ({changes} sections updated)")
        return True
    else:
        print(f"  NO CHANGES: {filepath}")
        return False


def main():
    updated = 0
    failed = 0

    print("=" * 60)
    print("Step 5: Adding state hub links to articles")
    print("=" * 60)

    print("\n--- Root Articles ---")
    for article in ROOT_ARTICLES:
        print(f"\n{article}:")
        if update_article(article, is_subfolder=False):
            updated += 1
        else:
            failed += 1

    print("\n--- Subfolder Articles ---")
    for article in SUBFOLDER_ARTICLES:
        print(f"\n{article}:")
        if update_article(article, is_subfolder=True):
            updated += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"DONE: {updated} articles updated, {failed} failed/skipped")
    print("=" * 60)


if __name__ == '__main__':
    main()
