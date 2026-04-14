"""
State Hub Page Generator — Programmatic SEO
Reads states.xlsx + cities.xlsx and generates template-driven HTML pages.
Every factual claim comes from the spreadsheet data. No improvised prose.
"""

import openpyxl
from collections import defaultdict
from datetime import date
import os
import sys

# Cities with generated pages (xlsx may not be updated yet if file was locked)
GENERATED_CITIES = {
    # Batch 1
    "Los Angeles", "New York City", "San Jose", "Austin", "Jacksonville",
    "Fort Worth", "San Diego", "San Francisco", "Columbus", "Indianapolis",
    "Nashville", "Washington", "Seattle", "El Paso", "Louisville",
    # Batch 2
    "Portland", "Memphis", "Baltimore", "Albuquerque", "Tucson",
    "Fresno", "Sacramento", "Mesa", "Omaha", "Miami",
    "Colorado Springs", "Raleigh", "Virginia Beach", "Oakland",
    "Tulsa", "Cleveland", "Wichita",
    # Batch 3
    "Allentown", "Anchorage", "Augusta", "Baton Rouge", "Boise",
    "Bridgeport", "Brownsville", "Buffalo", "Chattanooga", "Dayton",
    "Des Moines", "Eugene", "Fayetteville", "Fort Wayne", "Glendale",
    "Grand Rapids", "Hartford", "Huntsville", "Irvine", "Knoxville",
    "Laredo", "Lexington", "Lincoln", "Little Rock", "Lubbock",
    "Madison", "Mobile", "Modesto", "Newark", "Peoria",
    "Pittsburgh", "Providence", "Reno", "Richmond", "Salt Lake City",
    "Shreveport", "Spokane", "Springfield", "Syracuse", "Tallahassee",
    "Toledo", "Winston-Salem", "Worcester",
    # Batch 4 — 12 remaining states (9 April 2026)
    "Honolulu", "Charleston", "Columbia", "Greenville", "Jackson",
    "Gulfport", "Portland", "Bangor", "Morgantown",
    "Billings", "Missoula", "Fargo", "Bismarck", "Sioux Falls",
    "Rapid City", "Wilmington", "Burlington", "Cheyenne", "Manchester",
}

# ─── Data Loading ───────────────────────────────────────────────────────

def load_states(path='states.xlsx'):
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    states = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        data = dict(zip(headers, row))
        abbr = data['State Abbreviation']
        states[abbr] = data
    return states

def load_cities(path='cities_updated.xlsx'):
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    headers = [cell.value for cell in ws[1]]
    by_state = defaultdict(list)
    for row in ws.iter_rows(min_row=2, values_only=True):
        data = dict(zip(headers, row))
        by_state[data['State']].append(data)
    return by_state

# ─── Helper Functions ───────────────────────────────────────────────────

def slug(name):
    """State name to URL slug: 'New York' -> 'new-york'"""
    return name.lower().replace(' ', '-')

def city_file(city_name, abbr):
    """City name + abbr to filename: 'Birmingham', 'AL' -> 'birmingham-al'"""
    return city_name.lower().replace(' ', '-').replace('.', '').replace("'", '') + '-' + abbr.lower()

def fmt_pop_short(pop):
    """5237750 -> '5.2M'"""
    if not pop: return 'N/A'
    m = int(pop) / 1_000_000
    return f"{m:.1f}M" if m >= 1 else f"{int(pop):,}"

def fmt_pop_long(pop):
    """5237750 -> '5.2 million'"""
    if not pop: return 'N/A'
    m = int(pop) / 1_000_000
    return f"{m:.1f} million"

def fmt_zones(zones_str):
    """'2A, 3A' -> 'Zones 2A and 3A'"""
    if not zones_str: return ''
    zones = [z.strip() for z in zones_str.split(',')]
    if len(zones) == 1: return f"Zone {zones[0]}"
    if len(zones) == 2: return f"Zones {zones[0]} and {zones[1]}"
    return f"Zones {', '.join(zones[:-1])}, and {zones[-1]}"

def peak_description(peak, summer_high, winter_low):
    """Generate climate demand sentence from peak season + temps."""
    p = (peak or '').lower()
    sh = int(summer_high) if summer_high else '?'
    wl = int(winter_low) if winter_low else '?'
    if 'dual' in p:
        return (f"With summer highs averaging {sh}&deg;F and winter lows dropping to "
                f"{wl}&deg;F, your HVAC system handles heavy demand in both seasons.")
    elif 'winter' in p:
        return (f"With winter lows dropping to {wl}&deg;F, heating is the primary demand "
                f"on your HVAC system. Summer highs near {sh}&deg;F still require reliable cooling.")
    else:
        return (f"With summer highs averaging {sh}&deg;F, cooling is the primary demand "
                f"on your HVAC system. Winter lows near {wl}&deg;F mean heating needs are "
                f"moderate but still important.")

def system_desc(system_type, state_name):
    """Generate system type sentence from data."""
    if not system_type: return ''
    s = system_type.lower()
    if 'mini-split' in s or 'ductless' in s:
        return (f"Most homes across {state_name} rely on mini-split and ductless systems "
                f"for year-round cooling, with heat pumps providing efficient climate control.")
    if '/' in s:
        return (f"Homes across {state_name} typically use either heat pumps or a central "
                f"AC and gas furnace combination, depending on local climate and energy costs.")
    if 'heat pump' in s and 'central ac' not in s:
        return (f"Most homes across {state_name} rely on heat pumps for year-round comfort, "
                f"providing both efficient cooling and heating.")
    if 'central ac + gas furnace' in s:
        return (f"Most homes across {state_name} use a central AC and gas furnace combination "
                f"to handle both cooling and heating demands.")
    return f"Common HVAC systems across {state_name} include {system_type.lower()}."

def article_link(system_type):
    """Pick relevant article link based on dominant system."""
    s = (system_type or '').lower()
    if 'heat pump' in s:
        return '../article-heat-pump.html', 'heat pump options'
    if 'furnace' in s or 'gas' in s:
        return '../article-furnace.html', 'furnace options'
    return '../article-heat-pump.html', 'heat pump options'


def get_state_climate_profile(peak, system, zones):
    """Determine state climate profile from data fields for conditional text."""
    p = (peak or '').lower()
    s = (system or '').lower()
    z = str(zones or '').lower()

    # Tropical: Hawaii (mini-split dominant or Zone 1A only)
    if 'mini-split' in s or ('1a' in z and '2a' not in z):
        return {
            "meta_service": "AC repair, heat pump service, and cooling installation",
            "og_service": "Emergency AC and cooling service available 24/7.",
            "hero_service": "Emergency AC repair, heat pump service, and cooling system installation available 24/7.",
            "cost_type": "ac_tropical",
            "cost_faq_q": "How much does AC replacement cost",
            "services": [
                f"Emergency AC Repair in {{name}}",
                "Central Air Conditioning Installation &amp; Replacement",
                "Heat Pump &amp; Mini-Split Installation &amp; Service",
                "Ductwork Inspection, Cleaning &amp; Mold Prevention",
                "HVAC System Maintenance &amp; Tune-Ups",
                "Indoor Air Quality &amp; Ventilation Solutions",
            ],
        }

    # Subarctic/Heavy winter: Peak=Winter + zones 7 or 8
    if 'winter' in p and ('7' in z or '8' in z):
        return {
            "meta_service": "furnace repair, heating service, and HVAC installation",
            "og_service": "Emergency furnace repair and heating service available 24/7.",
            "hero_service": "Emergency furnace repair, heating service, and HVAC installation available 24/7.",
            "cost_type": "furnace_first",
            "cost_faq_q": "How much does HVAC replacement cost",
            "services": [
                f"Emergency Furnace Repair in {{name}}",
                "High-Efficiency Furnace Installation &amp; Replacement",
                "Boiler Service &amp; Radiant Heating Systems",
                "HVAC System Maintenance &amp; Tune-Ups",
                "Ductwork Inspection, Insulation &amp; Sealing",
                "Indoor Air Quality &amp; Ventilation Solutions",
            ],
        }

    # Winter-dominant: Peak=Winter (but not subarctic)
    if 'winter' in p:
        return {
            "meta_service": "furnace repair, AC service, and HVAC installation",
            "og_service": "Emergency furnace repair and HVAC service available 24/7.",
            "hero_service": "Emergency furnace repair, AC service, and HVAC installation available 24/7.",
            "cost_type": "furnace_first",
            "cost_faq_q": "How much does HVAC replacement cost",
            "services": [
                f"Emergency Furnace Repair in {{name}}",
                "High-Efficiency Furnace Installation &amp; Replacement",
                "Central Air Conditioning Repair &amp; Replacement",
                "Heat Pump Installation &amp; Service",
                "HVAC System Maintenance &amp; Tune-Ups",
                "Ductwork Inspection, Cleaning &amp; Sealing",
                "Indoor Air Quality &amp; Ventilation Solutions",
            ],
        }

    # Summer-dominant: Peak=Summer
    if 'summer' in p:
        return {
            "meta_service": "AC repair, HVAC service, and cooling installation",
            "og_service": "Emergency AC repair and HVAC service available 24/7.",
            "hero_service": "Emergency AC repair, heat pump service, and HVAC installation available 24/7.",
            "cost_type": "ac_first",
            "cost_faq_q": "How much does HVAC replacement cost",
            "services": [
                f"Emergency AC Repair in {{name}}",
                "Central Air Conditioning Installation &amp; Replacement",
                "Heat Pump Installation &amp; Service",
                "Furnace Repair &amp; Heating Service",
                "HVAC System Maintenance &amp; Tune-Ups",
                "Ductwork Inspection, Cleaning &amp; Sealing",
                "Indoor Air Quality &amp; Ventilation Solutions",
            ],
        }

    # Balanced (default): Peak=Both or Dual
    return {
        "meta_service": "AC repair, furnace service, and heat pump installation",
        "og_service": "Emergency AC and furnace service available 24/7.",
        "hero_service": "Emergency AC repair, furnace service, and heat pump installation available 24/7.",
        "cost_type": "both",
        "cost_faq_q": "How much does HVAC replacement cost",
        "services": [
            f"Emergency AC &amp; Furnace Repair in {{name}}",
            "Central Air Conditioning Installation &amp; Replacement",
            "Heat Pump Installation &amp; Service",
            "Furnace Installation &amp; Replacement",
            "HVAC System Maintenance &amp; Tune-Ups",
            "Ductwork Inspection, Cleaning &amp; Sealing",
            "Indoor Air Quality &amp; Ventilation Solutions",
        ],
    }


def state_cost_text(name, ac_cost, furnace_cost, cost_type, html=True):
    """Generate cost paragraph text for state hubs. html=False for schema."""
    b = lambda t: f"<strong>{t}</strong>" if html else t
    base = "Costs vary by city, system size, efficiency rating, and installation complexity."
    if cost_type == "ac_tropical":
        return (f"A standard central AC replacement in {name} typically costs "
                f"{b(ac_cost)}, and mini-split/heat pump installations run "
                f"{b(furnace_cost)}. {base}")
    elif cost_type == "furnace_first":
        return (f"A furnace replacement in {name} typically costs "
                f"{b(furnace_cost)}, and AC replacements run "
                f"{b(ac_cost)}. {base}")
    elif cost_type == "ac_first":
        return (f"A standard central AC replacement in {name} typically costs "
                f"{b(ac_cost)}, and furnace installations run "
                f"{b(furnace_cost)}. {base}")
    else:  # both
        return (f"A standard central AC replacement in {name} typically costs "
                f"{b(ac_cost)}, while furnace installations run "
                f"{b(furnace_cost)}. {base}")

def license_html(d):
    """Generate licensing section paragraph."""
    req = str(d.get('State HVAC License Requirement', '') or '')
    body = d.get('Licensing Body/Agency', '') or ''
    url = d.get('License Lookup URL', '') or ''
    name = d['State Name']

    link_tag = (f'<a href="{url}" style="color: var(--orange-dark); font-weight: 600;" '
                f'target="_blank" rel="noopener">license lookup tool</a>') if url and url != 'N/A' else 'their website'

    safety = (' See our <a href="../safety.html" style="color: var(--orange-dark); '
              'font-weight: 600;">safety tips</a> for more on what to verify before hiring.')

    if req.lower().startswith('no'):
        detail = req.replace('No state HVAC license; ', '').replace('No state HVAC license;', '').strip()
        if detail and detail[0].isupper():
            detail = detail[0].lower() + detail[1:]
        return (f"{name} does not require a statewide HVAC license. However, {detail}. "
                f"Always verify your contractor carries proper insurance and pulls necessary "
                f"permits with your local building department.{safety}")
    else:
        return (f"{name} requires HVAC contractors to hold a license issued by the "
                f"<strong>{body}</strong>. Before hiring, verify your contractor's credentials "
                f"through the board's {link_tag}. Licensed contractors carry insurance, pull "
                f"permits correctly, and stand behind their work.{safety}")

def license_faq(d):
    """FAQ answer for licensing question."""
    req = str(d.get('State HVAC License Requirement', '') or '')
    body = d.get('Licensing Body/Agency', '') or ''
    url = d.get('License Lookup URL', '') or ''
    name = d['State Name']

    if req.lower().startswith('no'):
        detail = req.replace('No state HVAC license; ', '').replace('No state HVAC license;', '').strip()
        if detail and detail[0].isupper():
            detail = detail[0].lower() + detail[1:]
        return (f"{name} does not require a statewide HVAC license. However, {detail}. "
                f"Always verify your contractor carries proper insurance and pulls necessary permits.")
    else:
        link = (f'<a href="{url}" style="color: var(--orange-dark); font-weight: 600;" '
                f'target="_blank" rel="noopener">online license lookup</a>') if url and url != 'N/A' else 'their website'
        return (f"{name} requires all HVAC contractors to hold a license issued by the "
                f"<strong>{body}</strong>. You can verify any contractor's credentials through "
                f"the board's {link}.")

def system_faq(d):
    """FAQ answer for system type question."""
    system = d.get('Dominant HVAC System Type', '') or ''
    name = d['State Name']
    art_url, art_text = article_link(system)
    art_tag = f'<a href="{art_url}" style="color: var(--orange-dark); font-weight: 600;">{art_text} guide</a>'

    s = system.lower()
    if 'mini-split' in s or 'ductless' in s:
        return (f"<strong>Mini-split and ductless systems</strong> are the most common across {name}. "
                f"The state's tropical climate means cooling is the primary need year-round, and "
                f"heat pumps provide efficient climate control. Explore our {art_tag} to learn more.")
    if '/' in s:
        return (f"Homes across {name} commonly use either <strong>heat pumps</strong> or "
                f"<strong>central AC with gas furnace</strong> systems, depending on the local "
                f"climate zone and energy costs. Explore our {art_tag} to learn more.")
    if 'heat pump' in s and 'central ac' not in s:
        return (f"<strong>Heat pumps</strong> are the most common system type across {name}. "
                f"The state's climate makes heat pumps ideal &#8212; they provide both cooling "
                f"and heating efficiently. Explore our {art_tag} to learn more.")
    if 'central ac + gas furnace' in s:
        return (f"<strong>Central AC paired with a gas furnace</strong> is the most common "
                f"system type across {name}. This combination handles both cooling and heating "
                f"demands efficiently. Explore our {art_tag} to learn more.")
    return (f"Common HVAC systems across {name} include <strong>{system}</strong>. "
            f"Explore our {art_tag} to learn more.")

def rebate_list_html(rebates_str):
    """Generate rebate <li> items from comma-separated rebate programs."""
    items = []
    if rebates_str:
        for prog in str(rebates_str).split(','):
            prog = prog.strip()
            if prog:
                items.append(f'            <li><strong>{prog}</strong></li>')
    items.append(
        '            <li><strong>Federal Tax Credits</strong> &#8212; may apply for qualifying '
        'high-efficiency installations; check <a href="https://www.energystar.gov/about/'
        'federal-tax-credits" target="_blank" rel="noopener" style="color: var(--orange-dark); '
        'font-weight: 600;">energystar.gov</a> for current amounts and eligibility</li>')
    return '\n'.join(items)

def cities_grid_html(city_list, abbr):
    """Generate city grid cards. Only show cities that have (or will have) their own page."""
    parts = []
    for city in sorted(city_list, key=lambda c: c['City']):
        name = city['City']
        cf = city_file(name, abbr)
        if city.get('City Page Published') == 'Yes' or name in GENERATED_CITIES:
            parts.append(f'''          <a href="{cf}.html" class="city-grid-card">
            <span class="card-icon">&#128205;</span> {name}, {abbr}
          </a>''')
        # Skip absorbed/removed cities — no Coming Soon entries
    return '\n'.join(parts)

def neighbor_links_html(neighbors_str, hub_abbrs, all_states):
    """Generate neighboring state link elements."""
    if not neighbors_str or 'none' in str(neighbors_str).lower(): return ''
    name_to_abbr = {d['State Name']: a for a, d in all_states.items()}
    parts = []
    for name in str(neighbors_str).split(','):
        name = name.strip()
        if not name: continue
        s = slug(name)
        abbr = name_to_abbr.get(name)
        cls = 'neighbor-link' if abbr in hub_abbrs else 'neighbor-link coming-soon'
        parts.append(f'          <a href="{s}.html" class="{cls}">&#127758; {name}</a>')
    return '\n'.join(parts)

# ─── HTML Template ──────────────────────────────────────────────────────

def generate_html(d, city_list, hub_abbrs, all_states):
    """Generate complete state hub HTML from state data dict."""

    name = d['State Name']
    abbr = d['State Abbreviation']
    s = slug(name)
    pop_short = fmt_pop_short(d.get('State Population'))
    pop_long = fmt_pop_long(d.get('State Population'))
    homeown = d.get('Homeownership Rate %', '')
    zones = d.get('Climate Zones Present', '')
    zones_fmt = fmt_zones(zones)
    sh = int(d['Avg Summer High (F)']) if d.get('Avg Summer High (F)') else ''
    wl = int(d['Avg Winter Low (F)']) if d.get('Avg Winter Low (F)') else ''
    elec = d.get('Avg Electricity Rate (cents/kWh)', '')
    gas = d.get('Avg Natural Gas Rate (dollars/therm)', '')
    seer_region = d.get('SEER2 Region', '')
    seer_min = d.get('SEER2 Minimum', '')
    ac_cost = d.get('Avg AC Install Cost', '')
    furnace_cost = d.get('Avg Furnace Install Cost', '')
    utilities = d.get('Top 3 Utility Companies', '')
    rebates = d.get('State/Utility Rebate Programs', '')
    system = d.get('Dominant HVAC System Type', '')
    peak = d.get('Peak HVAC Demand Season', '')
    neighbors = d.get('Neighboring States', '')

    state_profile = get_state_climate_profile(peak, system, zones)
    peak_desc = peak_description(peak, sh, wl)
    sys_desc = system_desc(system, name)
    art_url, art_text = article_link(system)
    lic_html = license_html(d)
    lic_faq = license_faq(d)
    sys_faq = system_faq(d)
    # Strip HTML for schema (JSON-LD can't have unescaped quotes from HTML tags)
    import re as _re
    lic_faq_schema = _re.sub(r'<[^>]+>', '', lic_faq).replace('"', '\\"')
    sys_faq_schema = _re.sub(r'<[^>]+>', '', sys_faq).replace('"', '\\"').replace('&#8212;', '—')
    rebate_items = rebate_list_html(rebates)
    city_grid = cities_grid_html(city_list, abbr)
    neighbor_html = neighbor_links_html(neighbors, hub_abbrs, all_states)
    neighbor_section = f'''
    <!-- Neighboring States -->
    <section class="section" style="padding: 32px 0 48px;">
      <div class="container" style="max-width: 800px;">
        <div class="city-services" style="margin-bottom: 16px;">
          <h2>Neighboring State HVAC Guides</h2>
          <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">Also serving homeowners in states bordering {name}. HVAC licensing, SEER2 requirements, and rebate programs differ by state.</p>
        </div>
        <div class="neighbor-links">
{neighbor_html}
        </div>
      </div>
    </section>''' if neighbor_html.strip() else ''

    # Byline + Last reviewed (E-E-A-T)
    today = date.today()
    reviewed_iso = today.isoformat()
    reviewed_readable = today.strftime("%B %#d, %Y") if os.name == 'nt' else today.strftime("%B %-d, %Y")
    meta_block = (
        f'<div class="page-meta">'
        f'<span class="byline">By <a href="../author-gyanesh.html">Gyanesh Gulshan</a>, Founder &mdash; B.Tech Mechanical Engineering</span>'
        f'<span class="reviewed">Last reviewed <time datetime="{reviewed_iso}">{reviewed_readable}</time></span>'
        f'</div>'
    )

    # Sources & References footer (E-E-A-T)
    sources_block = '''
    <!-- Sources & References -->
    <section class="section" style="padding: 0 0 48px;">
      <div class="container" style="max-width: 800px;">
        <div class="city-sources">
          <h3>Sources &amp; References</h3>
          <ul>
            <li><a href="https://www.energy.gov/energysaver/heat-and-cool" target="_blank" rel="nofollow noopener">U.S. Department of Energy &mdash; Home Heating &amp; Cooling</a></li>
            <li><a href="https://www.energystar.gov/" target="_blank" rel="nofollow noopener">U.S. ENERGY STAR (EPA)</a></li>
            <li><a href="https://www.dsireusa.org/" target="_blank" rel="nofollow noopener">DSIRE Database of State Incentives</a></li>
            <li><a href="https://www.irs.gov/credits-deductions/energy-efficient-home-improvement-credit" target="_blank" rel="nofollow noopener">IRS &sect;25C Energy Efficient Home Improvement Credit</a></li>
          </ul>
        </div>
      </div>
    </section>'''

    # Climate-aware cost and services strings
    cost_para = state_cost_text(name, ac_cost, furnace_cost, state_profile['cost_type'], html=True)
    cost_para += (f" Higher-efficiency units cost more upfront but lower monthly bills, "
                  f"especially given {name}'s electricity rates. See our "
                  f'<a href="../costs.html" style="color: var(--orange-dark); font-weight: 600;">'
                  f"full HVAC cost guide</a> for detailed pricing breakdowns.")
    schema_cost_plain = state_cost_text(name, ac_cost, furnace_cost, state_profile['cost_type'], html=False)
    faq_cost_para = state_cost_text(name, ac_cost, furnace_cost, state_profile['cost_type'], html=True)
    faq_cost_para += f" All new AC units must meet a minimum <strong>SEER2 {seer_min}</strong> rating."
    svc_items = '\n'.join(f'            <li>{svc.format(name=name)}</li>' for svc in state_profile['services'])

    # Utility names for display
    util_parts = [u.strip() for u in str(utilities).split(',')] if utilities else []
    util_bold = ', '.join(f'<strong>{u}</strong>' for u in util_parts)

    return f'''<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>HVAC Service &amp; Repair in {name} | Cool Call Pro</title>
  <meta name="description"
    content="Looking for HVAC contractors in {name}? Cool Call Pro connects homeowners with 24/7 {state_profile['meta_service']} across {name}. Call (844) 582-1795." />
  <link rel="canonical" href="https://coolcallpro.com/locations/{s}" />

  <!-- Open Graph -->
  <meta property="og:type" content="website" />
  <meta property="og:title" content="HVAC Service &amp; Repair in {name} | Cool Call Pro" />
  <meta property="og:description" content="Connect with independent HVAC professionals across {name}. {state_profile['og_service']}" />
  <meta property="og:url" content="https://coolcallpro.com/locations/{s}" />
  <meta property="og:site_name" content="Cool Call Pro" />
  <meta property="og:image" content="https://coolcallpro.com/images/og-homepage.webp" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="HVAC Service &amp; Repair in {name}" />
  <meta name="twitter:description" content="Connect with independent HVAC professionals across {name}." />
  <meta name="twitter:image" content="https://coolcallpro.com/images/og-homepage.webp" />

  <!-- Favicon -->
  <link rel="icon" href="/favicon.ico" type="image/x-icon" />
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />

  <link rel="stylesheet" href="../css/style.min.css" />
  <link rel="preconnect" href="https://fonts.googleapis.com" crossorigin="anonymous">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preload" as="style"
    href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Outfit:wght@400;600;700;800&display=swap"
    onload="this.onload=null;this.rel='stylesheet'">
  <noscript>
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Outfit:wght@400;600;700;800&display=swap"
      rel="stylesheet">
  </noscript>

  <!-- Google tag (gtag.js) - GA4 deferred for performance -->
  <script>
    window.addEventListener('load', function() {{
      var s = document.createElement('script');
      s.src = 'https://www.googletagmanager.com/gtag/js?id=G-WD0ND0K60Q';
      s.async = true;
      document.head.appendChild(s);
      s.onload = function() {{
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        window.gtag = gtag;
        gtag('js', new Date());
        gtag('config', 'G-WD0ND0K60Q');
      }};
    }});
  </script>

  <!-- Structured Data: BreadcrumbList + FAQPage + Organization -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "BreadcrumbList",
        "itemListElement": [
          {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://coolcallpro.com/"}},
          {{"@type": "ListItem", "position": 2, "name": "Locations", "item": "https://coolcallpro.com/locations"}},
          {{"@type": "ListItem", "position": 3, "name": "{name}", "item": "https://coolcallpro.com/locations/{s}"}}
        ]
      }},
      {{
        "@type": "FAQPage",
        "mainEntity": [
          {{
            "@type": "Question",
            "name": "What HVAC license is required in {name}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "{lic_faq_schema}"
            }}
          }},
          {{
            "@type": "Question",
            "name": "What SEER2 rating is required for new AC units in {name}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "{name} falls in the {seer_region} SEER2 region. All new central air conditioning systems must meet a minimum SEER2 rating of {seer_min} as of January 2023."
            }}
          }},
          {{
            "@type": "Question",
            "name": "{state_profile['cost_faq_q']} in {name}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "{schema_cost_plain}"
            }}
          }},
          {{
            "@type": "Question",
            "name": "Are there HVAC rebates available in {name}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Yes. Check with your local utility provider for current energy efficiency rebates. Federal tax credits may also apply for qualifying high-efficiency installations. Visit energystar.gov for current amounts and eligibility."
            }}
          }},
          {{
            "@type": "Question",
            "name": "What type of HVAC system is most common in {name}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "{sys_faq_schema}"
            }}
          }}
        ]
      }},
      {{
        "@type": "Organization",
        "name": "Cool Call Pro",
        "url": "https://coolcallpro.com",
        "telephone": "+1-844-582-1795",
        "description": "24/7 referral service connecting homeowners with independent HVAC professionals across {name}.",
        "areaServed": {{
          "@type": "State",
          "name": "{name}"
        }}
      }}
    ]
  }}
  </script>

  <style>
    .city-hero {{
      background: linear-gradient(rgba(10, 22, 40, 0.88), rgba(10, 22, 40, 0.88)), url('../images/mixed-humid-climate-hvac-atlanta-hero.webp');
      background-size: cover;
      background-position: center;
      color: white;
      padding: 100px 0 80px;
      text-align: center;
    }}
    .city-hero h1 {{
      font-family: var(--font-display);
      font-size: 2.6rem;
      font-weight: 800;
      line-height: 1.2;
      margin-bottom: 20px;
      letter-spacing: -0.02em;
    }}
    .city-hero p {{
      font-size: 1.15rem;
      max-width: 620px;
      margin: 0 auto;
      opacity: 0.9;
      line-height: 1.7;
    }}
    .city-context {{
      font-size: 1.1rem;
      line-height: 1.85;
      color: var(--gray-700);
      max-width: 760px;
      margin: 0 auto 40px;
    }}
    .city-services {{
      max-width: 760px;
      margin: 0 auto 48px;
    }}
    .city-services h2 {{
      font-size: 1.6rem;
      margin-bottom: 16px;
      color: var(--navy);
    }}
    .city-services ul {{
      list-style: none;
      padding: 0;
    }}
    .city-services ul li {{
      padding: 12px 0 12px 28px;
      position: relative;
      font-size: 1.05rem;
      color: var(--gray-700);
      border-bottom: 1px solid var(--gray-100);
    }}
    .city-services ul li::before {{
      content: "\\2714";
      color: var(--orange-dark);
      font-weight: 700;
      position: absolute;
      left: 0;
      top: 12px;
    }}
    .city-services ul li a {{
      color: var(--orange-dark);
      font-weight: 600;
      text-decoration: none;
    }}
    .city-services ul li a:hover {{
      text-decoration: underline;
    }}
    .city-faq {{
      max-width: 760px;
      margin: 0 auto 48px;
    }}
    .city-faq h2 {{
      font-size: 1.6rem;
      margin-bottom: 20px;
      color: var(--navy);
    }}
    .state-info-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      max-width: 760px;
      margin: 0 auto 48px;
    }}
    .state-info-card {{
      background: var(--gray-50, #f8f9fa);
      border-radius: 12px;
      padding: 24px;
      text-align: center;
    }}
    .state-info-card .info-label {{
      font-size: 0.85rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--gray-500, #6b7280);
      margin-bottom: 8px;
    }}
    .state-info-card .info-value {{
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--navy);
    }}
    .state-info-card .info-value small {{
      font-size: 0.75rem;
      font-weight: 400;
      color: var(--gray-500, #6b7280);
      display: block;
      margin-top: 4px;
    }}
    .city-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      max-width: 760px;
      margin: 0 auto;
    }}
    .city-grid-card {{
      background: var(--gray-50, #f8f9fa);
      border: 1px solid var(--gray-100, #e5e7eb);
      border-radius: 12px;
      padding: 20px 24px;
      text-decoration: none;
      color: var(--navy);
      font-weight: 600;
      font-size: 1.05rem;
      transition: border-color 0.2s, box-shadow 0.2s;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .city-grid-card:hover {{
      border-color: var(--orange-dark);
      box-shadow: 0 2px 8px rgba(255, 165, 0, 0.15);
    }}
    .city-grid-card.coming-soon {{
      opacity: 0.72;
      pointer-events: none;
    }}
    .city-grid-card .card-icon {{
      font-size: 1.2rem;
    }}
    .neighbor-links {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      max-width: 760px;
      margin: 16px auto 0;
    }}
    .neighbor-link {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 10px 18px;
      background: var(--gray-50, #f8f9fa);
      border: 1px solid var(--gray-100, #e5e7eb);
      border-radius: 8px;
      text-decoration: none;
      color: var(--navy);
      font-weight: 600;
      font-size: 0.95rem;
      transition: border-color 0.2s;
    }}
    .neighbor-link:hover {{
      border-color: var(--orange-dark);
    }}
    .neighbor-link.coming-soon {{
      opacity: 0.72;
      pointer-events: none;
    }}
    @media (max-width: 768px) {{
      .city-hero {{
        padding: 80px 0 60px;
      }}
      .city-hero h1 {{
        font-size: 1.8rem;
      }}
      .state-info-grid {{
        grid-template-columns: repeat(2, 1fr);
      }}
    }}
  </style>
</head>

<body>

  <!-- Skip to Content -->
  <a href="#main-content" class="skip-link">Skip to main content</a>

  <!-- Top Bar -->
  <div class="topbar">
    <div class="container topbar-inner" style="justify-content: center; padding: 10px; font-weight: 600;">
      <span class="topbar-text">24/7 Referral Service &#8212; Connecting Homeowners with Independent HVAC Professionals</span>
    </div>
  </div>

  <!-- Header -->
  <header class="header" id="header">
    <nav class="nav container" role="navigation" aria-label="Main navigation">
      <a href="../index.html" class="logo">
        <span class="logo-icon">&#10052;&#65039;</span>
        <span class="logo-text">CoolCall<span class="logo-accent">Pro</span></span>
      </a>
      <ul class="nav-links" id="navLinks">
        <li><a href="../emergency.html" class="nav-link emergency-link">&#128680; Emergency Service</a></li>
        <li><a href="../costs.html" class="nav-link">Cost Guide</a></li>
        <li><a href="../safety.html" class="nav-link">Safety Tips</a></li>
        <li><a href="../locations.html" class="nav-link active">&#128205; Locations</a></li>
        <li><a href="../articles.html" class="nav-link">Articles</a></li>
        <li><a href="../about.html" class="nav-link">About</a></li>
        <li><a href="../contact.html" class="nav-link">Contact</a></li>
      </ul>
      <a href="tel:+18445821795" class="btn btn-cta nav-cta btn-vibrate" id="headerNavCta" aria-hidden="true"
        tabindex="-1" style="opacity: 0; pointer-events: none; transition: opacity 0.3s ease;"><span
          class="phone-icon">&#128222;</span>
        <span class="hide-on-mobile">(844) 582-1795</span></a>
      <button class="hamburger" id="hamburger" aria-label="Menu">&#9776;</button>
    </nav>
  </header>

  <!-- Main Content -->
  <main id="main-content">

    <!-- Hero Section -->
    <section class="city-hero" id="hero">
      <div class="container">
        <span class="section-tag" style="background: rgba(255,255,255,0.1); color: #fff;">&#128205; {name}</span>
        <h1>HVAC Service &amp; Repair in {name}</h1>
        <p>Connect with independent local HVAC professionals across every city and ZIP code in {name}. {state_profile['hero_service']}</p>
        <div style="margin-top: 28px;">
          <a href="tel:+18445821795" class="btn btn-primary btn-lg btn-vibrate"><span class="phone-icon">&#128222;</span> Call Now &#8212; (844) 582-1795</a>
        </div>
        <div class="jump-links" style="margin-top: 16px;">
          <a href="#services" class="jump-link" style="color: rgba(255,255,255,0.8);">Services</a>
          <span class="jump-link-dot" style="color: rgba(255,255,255,0.5);">&#8226;</span>
          <a href="#climate" class="jump-link" style="color: rgba(255,255,255,0.8);">Climate</a>
          <span class="jump-link-dot" style="color: rgba(255,255,255,0.5);">&#8226;</span>
          <a href="#licensing" class="jump-link" style="color: rgba(255,255,255,0.8);">Licensing</a>
          <span class="jump-link-dot" style="color: rgba(255,255,255,0.5);">&#8226;</span>
          <a href="#costs" class="jump-link" style="color: rgba(255,255,255,0.8);">Costs</a>
          <span class="jump-link-dot" style="color: rgba(255,255,255,0.5);">&#8226;</span>
          <a href="#cities" class="jump-link" style="color: rgba(255,255,255,0.8);">Service Areas</a>
          <span class="jump-link-dot" style="color: rgba(255,255,255,0.5);">&#8226;</span>
          <a href="#faqs" class="jump-link" style="color: rgba(255,255,255,0.8);">FAQs</a>
        </div>
      </div>
    </section>

    <!-- Breadcrumb -->
    <div class="breadcrumb-nav">
      <div class="container">
        <nav aria-label="Breadcrumb">
          <ol class="breadcrumb-list">
            <li><a href="../index.html">Home</a></li>
            <li><a href="../locations.html">Locations</a></li>
            <li aria-current="page">{name}</li>
          </ol>
        </nav>
      </div>
    </div>

    <!-- State Overview -->
    <section class="section" style="padding: 48px 0 0;">
      <div class="container">
        <div class="city-context">
          {meta_block}
          <p>{name} is home to over <strong>{pop_long} residents</strong> with a <strong>{homeown}% homeownership rate</strong>. The state spans IECC <strong>{zones_fmt}</strong>, and {peak_desc} {sys_desc} Cool Call Pro connects you with independent local HVAC professionals serving every corner of the state.</p>
        </div>

        <!-- State At-a-Glance -->
        <div class="state-info-grid">
          <div class="state-info-card">
            <div class="info-label">Population</div>
            <div class="info-value">{pop_short}</div>
          </div>
          <div class="state-info-card">
            <div class="info-label">Homeownership</div>
            <div class="info-value">{homeown}%</div>
          </div>
          <div class="state-info-card">
            <div class="info-label">Climate Zones</div>
            <div class="info-value">{zones}</div>
          </div>
          <div class="state-info-card">
            <div class="info-label">SEER2 Minimum</div>
            <div class="info-value">{seer_min} <small>{seer_region} Region</small></div>
          </div>
          <div class="state-info-card">
            <div class="info-label">Summer High</div>
            <div class="info-value">{sh}&deg;F</div>
          </div>
          <div class="state-info-card">
            <div class="info-label">Winter Low</div>
            <div class="info-value">{wl}&deg;F</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Climate & HVAC Demands -->
    <section class="section" style="padding: 0;" id="climate">
      <div class="container">
        <div class="city-services" style="margin-bottom: 40px;">
          <h2>Climate &amp; HVAC Demands in {name}</h2>
          <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">{name} spans IECC {zones_fmt}. {peak_desc} Average electricity rates sit at <strong>{elec}&cent;/kWh</strong>, making system efficiency an important factor in your monthly energy costs. Learn more about <a href="{art_url}" style="color: var(--orange-dark); font-weight: 600;">{art_text}</a> for your home.</p>
        </div>
      </div>
    </section>

    <!-- SEER2 & Efficiency -->
    <section class="section" style="padding: 0;">
      <div class="container">
        <div class="city-services" style="margin-bottom: 40px;">
          <h2>SEER2 Efficiency Requirements in {name}</h2>
          <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">{name} falls within the <strong>{seer_region} SEER2 region</strong>. As of January 2023, all new central air conditioning systems installed in {name} must meet a minimum <strong>SEER2 rating of {seer_min}</strong>. When replacing your AC or heat pump, ensure your contractor installs a unit that meets or exceeds this minimum &#8212; upgrading to a higher-efficiency system can significantly reduce your energy bills. See our <a href="../article-ac-summer.html" style="color: var(--orange-dark); font-weight: 600;">summer AC guide</a> for more on efficiency ratings.</p>
        </div>
      </div>
    </section>

    <!-- Services List -->
    <section class="section" style="padding: 0;" id="services">
      <div class="container">
        <div class="city-services">
          <h2>HVAC Services in {name}</h2>
          <ul>
{svc_items}
          </ul>
        </div>
      </div>
    </section>

    <!-- Licensing -->
    <section class="section" style="padding: 0;" id="licensing">
      <div class="container">
        <div class="city-services" style="margin-bottom: 40px;">
          <h2>HVAC Licensing Requirements in {name}</h2>
          <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">{lic_html}</p>
        </div>
      </div>
    </section>

    <!-- Utilities & Rebates -->
    <section class="section" style="padding: 0;">
      <div class="container">
        <div class="city-services" style="margin-bottom: 40px;">
          <h2>Utility Companies &amp; HVAC Rebates in {name}</h2>
          <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">The major utility providers in {name} include {util_bold}.</p>
          <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700); margin-top: 16px;"><strong>Available rebate programs:</strong></p>
          <ul>
{rebate_items}
          </ul>
          <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700); margin-top: 16px;">Contact your utility provider or HVAC contractor to confirm current eligibility and amounts. Learn about <a href="../article-hvac-financing.html" style="color: var(--orange-dark); font-weight: 600;">HVAC financing options</a>.</p>
        </div>
      </div>
    </section>

    <!-- Cost Overview -->
    <section class="section" style="padding: 0;" id="costs">
      <div class="container">
        <div class="city-services" style="margin-bottom: 40px;">
          <h2>HVAC Installation Costs in {name}</h2>
          <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">{cost_para}</p>
        </div>
      </div>
    </section>

    <!-- Service Areas -->
    <section class="section" style="padding: 0 0 48px;" id="cities">
      <div class="container">
        <div class="city-services" style="margin-bottom: 24px;">
          <h2>Service Areas in {name}</h2>
          <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">Cool Call Pro connects homeowners with HVAC professionals across {name}. Browse our local service pages for city-specific costs, permit offices, and contractor information.</p>
        </div>
        <div class="city-grid">
{city_grid}
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="section section-dark" id="how-it-works">
      <div class="container">
        <div class="section-header">
          <span class="section-tag"
            style="background: rgba(255,165,0,0.15); color: var(--orange-light); border-color: rgba(255,165,0,0.3);">&#9889;
            Simple Process</span>
          <h2 class="section-title">How It Works</h2>
          <p class="section-sub">From your first call to getting connected with an independent HVAC provider in <strong>{name}</strong> &#8212; here's exactly what happens.</p>
        </div>

        <div class="steps-grid">

          <div class="step-card">
            <div class="step-number">01</div>
            <div class="step-icon"><span class="phone-icon">&#128222;</span></div>
            <h3>Call and Tell Us Your Issue</h3>
            <p>Call our 24/7 service line and tell us your HVAC issue. Your request will be routed to an independent professional serving your area in <strong>{name}</strong>.</p>
          </div>

          <div class="step-card">
            <div class="step-number">02</div>
            <div class="step-icon">&#128269;</div>
            <h3>Connect with an HVAC Provider</h3>
            <p>We connect you with an independent HVAC professional serving your ZIP code in <strong>{name}</strong>. Licensing, insurance, and availability vary by provider.</p>
          </div>

          <div class="step-card">
            <div class="step-number">03</div>
            <div class="step-icon">&#128736;&#65039;</div>
            <h3>Review Options &amp; Schedule</h3>
            <p>Your local provider will confirm availability and discuss options. Service options and dispatch times vary by area.</p>
          </div>

        </div>

        <div style="text-align: center; margin-top: 48px;">
          <a href="tel:+18445821795" class="btn btn-primary btn-lg btn-vibrate"><span class="phone-icon">&#128222;</span> Call Now &#8212; (844) 582-1795</a>
        </div>
      </div>
    </section>

    <!-- FAQs -->
    <section class="section" id="faqs">
      <div class="container" style="max-width: 800px;">
        <div class="city-faq">
          <h2>Frequently Asked Questions &#8212; {name} HVAC</h2>
          <div class="faq-list" style="margin-top: 24px;">
            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>What HVAC license is required in {name}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>{lic_faq}</p>
                </div>
              </div>
            </div>

            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>What SEER2 rating is required for new AC units in {name}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>{name} is in the <strong>{seer_region} SEER2 region</strong>, requiring a minimum <strong>SEER2 {seer_min}</strong> for all new central AC systems as of January 2023.</p>
                </div>
              </div>
            </div>

            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>{state_profile['cost_faq_q']} in {name}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>{faq_cost_para}</p>
                </div>
              </div>
            </div>

            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>Are there HVAC rebates available in {name}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>Yes. Check with your local utility provider for current energy efficiency rebates on qualifying high-efficiency equipment. Federal tax credits may also apply for qualifying installations &#8212; visit <a href="https://www.energystar.gov/about/federal-tax-credits" style="color: var(--orange-dark); font-weight: 600;" target="_blank" rel="noopener">energystar.gov</a> for current amounts and eligibility.</p>
                </div>
              </div>
            </div>

            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>What type of HVAC system is most common in {name}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>{sys_faq}</p>
                </div>
              </div>
            </div>
          </div>

          <div style="text-align: center; margin-top: 32px;">
            <a href="tel:+18445821795" class="btn btn-primary btn-lg btn-vibrate"><span class="phone-icon">&#128222;</span> Call Now &#8212; (844) 582-1795</a>
          </div>
        </div>
      </div>
    </section>

{neighbor_section}
{sources_block}

  </main>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <a href="../index.html" class="logo"><span class="logo-icon">&#10052;&#65039;</span><span
              class="logo-text">CoolCall<span class="logo-accent">Pro</span></span></a>
          <p>Connecting homeowners with independent HVAC professionals across the US. Available 24/7 in many areas.</p>
          <div class="footer-contact">
            <a href="tel:+18445821795" class="footer-phone">(844) 582-1795</a>
            <span>24/7 Service Line</span>
          </div>
        </div>
        <div class="footer-col">
          <h3 class="footer-heading">Resources</h3>
          <ul>
            <li><a href="../costs.html">Cost Guide</a></li>
            <li><a href="../emergency.html">Emergency Service</a></li>
            <li><a href="../safety.html">Safety Tips</a></li>
            <li><a href="../articles.html">All Articles</a></li>
            <li><a href="../locations.html">Locations</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3 class="footer-heading">Company</h3>
          <ul>
            <li><a href="../about.html">About Us</a></li>
            <li><a href="../contact.html">Contact</a></li>
            <li><a href="../author-gyanesh.html">Author</a></li>
            <li><a href="../privacy.html">Privacy Policy</a></li>
            <li><a href="../advertising-disclosure.html">Advertising Disclosure</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3 class="footer-heading">Service Areas</h3>
          <ul class="service-areas">
            <li><a href="atlanta-ga.html">Atlanta, GA</a></li>
            <li><a href="chicago-il.html">Chicago, IL</a></li>
            <li><a href="dallas-tx.html">Dallas, TX</a></li>
            <li><a href="houston-tx.html">Houston, TX</a></li>
            <li><a href="phoenix-az.html">Phoenix, AZ</a></li>
            <li><a href="../locations.html">All 50 states &#8594;</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p><strong style="color: rgba(255,255,255,0.82);">How this site works:</strong> We publish HVAC cost and
          troubleshooting information and may connect callers to independent service providers. We do not perform HVAC
          services ourselves. Pricing, availability, and response times vary by provider and location.</p>
        <p><strong style="color: rgba(255,255,255,0.82);">Editorial standards:</strong> Our content focuses on helpful
          troubleshooting tips and realistic pricing information. We avoid guarantees; actual pricing depends on the
          provider and situation. We clearly disclose compensation for referrals. We update content for clarity and
          accuracy when needed.</p>
        <p><strong style="color: rgba(255,255,255,0.82);">Disclaimer:</strong> Cool Call Pro is a free service to assist homeowners in connecting with local service providers. All contractors/providers are independent and Cool Call Pro does not warrant or guarantee any work performed. It is the responsibility of the homeowner to verify that the hired contractor furnishes the necessary license and insurance required for the work being performed. All persons depicted in a photo or video are actors or models and not contractors listed on Cool Call Pro.</p>
        <p>&copy; <span class="copyright-year">2026</span> Cool Call Pro. All rights reserved. &nbsp;&#183;&nbsp; <a href="../privacy.html">Privacy
            Policy</a> &nbsp;&#183;&nbsp; <a href="../terms.html">Terms of Use</a> &nbsp;&#183;&nbsp; <a
            href="../disclaimer.html">Disclaimer</a> &nbsp;&#183;&nbsp; <a href="../advertising-disclosure.html">Advertising
            Disclosure</a></p>
      </div>
    </div>
  </footer>

  <script src="../js/main.min.js" defer></script>

  <!-- Mobile Call Bar -->
  <div class="mobile-call-bar">
    <a href="tel:+18445821795"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width: 1.25em; height: 1.25em; position: relative; top: 0.15em;"><path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56-.35-.12-.74-.03-1.01.24l-1.57 1.97c-2.83-1.35-5.48-3.9-6.89-6.83l1.95-1.66c.27-.28.35-.67.24-1.02-.37-1.11-.56-2.3-.56-3.53 0-.54-.45-.99-.99-.99H4.19C3.65 3 3 3.24 3 3.99 3 13.28 10.73 21 20.01 21c.71 0 1.01-.63 1.01-1.18v-3.45c0-.54-.45-.99-.99-.99z"/></svg> Call Now &#8212; (844) 582-1795</a>
  </div>
<script>document.querySelectorAll(".copyright-year").forEach(function(el){{el.textContent=new Date().getFullYear()}});</script>
</body>

</html>'''

# ─── Main ───────────────────────────────────────────────────────────────

def main():
    states = load_states()
    cities = load_cities()

    # Determine which states have at least 1 published city page
    hub_abbrs = set()
    for abbr, city_list in cities.items():
        for c in city_list:
            if c.get('City Page Published') == 'Yes' or c.get('City') in GENERATED_CITIES:
                hub_abbrs.add(abbr)
                break

    # Accept CLI args: specific state abbreviations, or 'all' for all hub states
    targets = sys.argv[1:] if len(sys.argv) > 1 else []
    if not targets:
        print("Usage: python generate_state_hubs.py AL  (or: AL TX FL  or: all)")
        print(f"\nStates with published cities (eligible for hubs): {sorted(hub_abbrs)}")
        return

    if targets == ['all']:
        targets = sorted(hub_abbrs)

    out_dir = 'locations'
    os.makedirs(out_dir, exist_ok=True)

    for abbr in targets:
        abbr = abbr.upper()
        if abbr not in states:
            print(f"  SKIP: {abbr} not found in states.xlsx")
            continue
        if abbr not in hub_abbrs:
            print(f"  SKIP: {abbr} has no published city pages")
            continue

        d = states[abbr]
        city_list = cities.get(abbr, [])
        html = generate_html(d, city_list, hub_abbrs, states)

        filename = slug(d['State Name']) + '.html'
        filepath = os.path.join(out_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  DONE: {filepath} ({d['State Name']})")

    print(f"\nGenerated {len(targets)} state hub page(s).")

if __name__ == '__main__':
    main()
