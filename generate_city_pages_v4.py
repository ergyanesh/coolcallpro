#!/usr/bin/env python3
"""
City Page Generator v4 — 25 April 2026
Card-driven layout port. Emits the new Houston/Phoenix-pilot canonical
layout: alternating white/gray-50 sections, climate-aware emergency
cards, tag pills, callout banners, OBBBA-aware tax-credit copy.

Reuses helpers from generate_city_pages_v3 where possible (climate
profiles, services list, licensing, rebates, neighborhoods raw data,
local context, sources, image figure).

Usage:
    python generate_city_pages_v4.py --city "Phoenix"
    python generate_city_pages_v4.py --city "Phoenix" --output-path _pilot_test/phoenix-az.html
    python generate_city_pages_v4.py --batch 1
    python generate_city_pages_v4.py --dry-run
    python generate_city_pages_v4.py --force --output-dir _pilot_test
"""

import os
import re
import sys
from datetime import date
from html import escape

# Reuse v3 helpers wholesale -- this v4 only refactors generate_page().
from generate_city_pages_v3 import (
    XLSX_FILE, STATES_XLSX, OUTPUT_DIR,
    PUBLISHED_CITIES, REMOVED_CITIES, ABSORBED, ANCHOR_ABSORBS,
    BATCH_1, BATCH_2,
    CLIMATE_MAP, ZONE_4A_DECISIONS, CLIMATE_PROFILES, CLIMATE_ARTICLE_LINKS,
    STATE_FULL,
    state_slug, city_slug, get_climate_type,
    get_nearby_cities,
    services_list,
    license_faq_sentence,
    page_meta_html,
    location_figure_html,
    schema_cost_faq_text,
    load_states, load_cities,
)


# ============================================================
# CARD-DRIVEN LAYOUT HELPERS
# ============================================================

# Tag pill HTML helpers — keep contexts consistent across sections.
def tag_pill(label, color_var, bg, border, icon_html=""):
    """Render a section-tag pill with the canonical inline style."""
    icon = f"{icon_html} " if icon_html else ""
    return (
        f'<span style="display:inline-block; font-size:0.78rem; font-weight:800; '
        f'letter-spacing:0.12em; text-transform:uppercase; color:{color_var}; '
        f'padding:6px 14px; background:{bg}; border:1px solid {border}; '
        f'border-radius:999px; margin-bottom:16px;">{icon}{label}</span>'
    )


def emergency_pill():
    return tag_pill(
        "What's wrong right now?",
        "var(--red)", "#fef2f2", "#fed7d7",
        icon_html="&#128680;",
    )


def trust_pill(city_e):
    return tag_pill(
        f"The {city_e} Network",
        "var(--navy)", "#fff", "var(--gray-200)",
        icon_html="&#128205;",
    )


def climate_pill():
    return tag_pill(
        "Climate Profile",
        "var(--blue)", "#ebf8ff", "#bee3f8",
        icon_html="&#127777;&#65039;",
    )


def localdata_pill():
    # Local data sits on var(--gray-50) → use #fff bg for the pill.
    return tag_pill(
        "Primary Sources",
        "var(--blue)", "#fff", "#bee3f8",
        icon_html="&#128202;",
    )


def services_pill():
    # Services sits on white → use var(--gray-50) bg.
    return tag_pill(
        "Coverage",
        "var(--navy)", "var(--gray-50)", "var(--gray-200)",
        icon_html="&#128295;",
    )


def faq_pill():
    return tag_pill(
        "Common Questions",
        "var(--navy)", "var(--gray-50)", "var(--gray-200)",
        icon_html="&#10067;",
    )


def metro_pill():
    return tag_pill(
        "Metro Area",
        "var(--navy)", "var(--gray-50)", "var(--gray-200)",
        icon_html="&#127961;&#65039;",
    )


# Reusable inline white-box style for plain .precaution-card cards (so they
# don't appear "boxless"). Per CLAUDE.md City Page Design System.
PLAIN_CARD_STYLE = (
    "display:flex; flex-direction:column; background:#fff; "
    "border:1px solid var(--gray-200); box-shadow: 0 4px 16px rgba(10,22,40,0.04);"
)


# ============================================================
# CLIMATE-AWARE EMERGENCY CARDS
# ============================================================

# Each emergency card returns a fully-rendered <div class="precaution-card ..."> string.
# Card #1 is always .precaution-danger (red); #2 / #3 vary by climate.

def card_no_ac(climate_type, city_e, summer_high):
    """NO AC danger card — Card #1 for hot-humid, hot-dry, mixed-humid, coastal, tropical."""
    if climate_type == "hot-dry":
        body = (
            f"Outdoor unit silent &middot; indoor blower running but warm air &middot; "
            f"system short-cycling on/off in 100&deg;F+ heat. In {city_e}'s extreme heat, "
            f"an AC failure becomes a habitability issue within hours &mdash; the most "
            f"common culprits are electrical (capacitor, contactor, low refrigerant) and "
            f"require a technician."
        )
    else:
        body = (
            "Outdoor unit silent &middot; indoor blower running but warm air &middot; "
            "ice on the refrigerant lines &middot; short-cycling on/off. The most common "
            "cause is electrical (capacitor, contactor) or refrigerant &mdash; both "
            "require a technician."
        )
    return (
        '<div class="precaution-card precaution-danger">\n'
        '            <div class="precaution-icon">&#10052;&#65039; NO AC</div>\n'
        '            <h3>AC out, blowing warm, or iced over</h3>\n'
        f'            <p style="margin-bottom: 0;">{body}</p>\n'
        '          </div>'
    )


def card_no_heat(climate_type, city_e, winter_low, danger=True):
    """NO HEAT card — danger by default; some climates downgrade to plain."""
    klass = "precaution-card precaution-danger" if danger else "precaution-card"
    style_attr = "" if danger else f' style="{PLAIN_CARD_STYLE}"'
    if climate_type in ("hot-dry",):
        body = (
            f"Furnace won't ignite &middot; heat pump blowing cold air on a "
            f"{winter_low}&deg;F desert night &middot; short-cycling. {city_e}'s "
            f"heating season is short but cold snaps still happen. "
            f"<strong>If you smell gas, leave the building immediately and call 911 first.</strong>"
        )
    elif climate_type in ("cold", "subarctic", "mountain"):
        body = (
            f"Furnace won't ignite &middot; blowing cold air &middot; short-cycling "
            f"&middot; burning smell on first startup. In {city_e}, a furnace failure "
            f"in deep winter can lead to frozen pipes within hours. "
            f"<strong>If you smell gas, leave the building immediately and call 911 first.</strong>"
        )
    else:
        body = (
            "Furnace won't ignite &middot; blowing cold air &middot; short-cycling "
            "&middot; burning smell on first startup. "
            "<strong>If you smell gas, leave the building immediately and call 911 first.</strong>"
        )
    return (
        f'<div class="{klass}"{style_attr}>\n'
        '            <div class="precaution-icon">&#128293; NO HEAT</div>\n'
        '            <h3>Furnace not igniting or blowing cold</h3>\n'
        f'            <p style="margin-bottom: 0;">{body}</p>\n'
        '          </div>'
    )


def card_water_leak(city_e):
    """WATER LEAK warning card — hot-humid / tropical."""
    return (
        '<div class="precaution-card precaution-warning">\n'
        '            <div class="precaution-icon">&#128167; WATER LEAK</div>\n'
        '            <h3>Water dripping from vent or air handler</h3>\n'
        f'            <p style="margin-bottom: 0;">Water from a ceiling vent &middot; pooling near the indoor air handler &middot; drain pan overflowing. The #1 cause in humid {city_e} summers is a clogged condensate drain line &mdash; clearing it requires working around the evaporator coil and is a technician task.</p>\n'
        '          </div>'
    )


def card_frozen_pipes(city_e):
    """FROZEN PIPES warning card — cold / subarctic."""
    return (
        '<div class="precaution-card precaution-warning">\n'
        '            <div class="precaution-icon">&#10052;&#65039; FROZEN PIPES</div>\n'
        '            <h3>Pipes freezing while heat is out</h3>\n'
        f'            <p style="margin-bottom: 0;">Once {city_e} indoor temps drop below 55&deg;F, pipes in exterior walls and unheated basements are at risk. If your heat is out and the forecast is below freezing, this is an emergency &mdash; restoring heat fast prevents thousands in burst-pipe damage.</p>\n'
        '          </div>'
    )


def card_strange_noises(climate_type, city_e):
    """STRANGE NOISES warning card — hot-dry, mixed-humid, coastal, mountain."""
    if climate_type == "hot-dry":
        body = (
            f"Loud bangs &middot; metal-on-metal screaming &middot; grinding from the "
            f"condenser. In {city_e} summers your outdoor unit runs at near-100% capacity "
            f"for hours &mdash; failing fan motors, compressor bearings, and warped fan "
            f"blades are common. Turn the system off and call before damage spreads to the "
            f"compressor itself."
        )
    else:
        body = (
            "Loud bangs &middot; metal-on-metal screaming &middot; grinding or rattling "
            "from the outdoor unit. Failing fan motors, loose blower wheels, and worn "
            "compressor bearings are the usual causes. Turn the system off and call &mdash; "
            "running through these noises spreads the damage."
        )
    return (
        '<div class="precaution-card precaution-warning">\n'
        '            <div class="precaution-icon">&#9888;&#65039; STRANGE NOISES</div>\n'
        '            <h3>Banging, screaming, or grinding outdoor unit</h3>\n'
        f'            <p style="margin-bottom: 0;">{body}</p>\n'
        '          </div>'
    )


def emergency_cards_for_climate(climate_type, city_e, summer_high, winter_low):
    """Return list of 3 fully-rendered card HTML strings, climate-aware."""
    if climate_type in ("hot-humid", "tropical"):
        return [
            card_no_ac(climate_type, city_e, summer_high),
            card_no_heat(climate_type, city_e, winter_low, danger=True),
            card_water_leak(city_e),
        ]
    if climate_type == "hot-dry":
        return [
            card_no_ac(climate_type, city_e, summer_high),
            card_strange_noises(climate_type, city_e),
            card_no_heat(climate_type, city_e, winter_low, danger=True),
        ]
    if climate_type in ("cold", "subarctic"):
        return [
            card_no_heat(climate_type, city_e, winter_low, danger=True),
            card_frozen_pipes(city_e),
            # Card #3 NO AC — keep plain (non-danger) since AC is secondary in cold climates
            (
                '<div class="precaution-card" style="' + PLAIN_CARD_STYLE + '">\n'
                '            <div class="precaution-icon">&#10052;&#65039; NO AC</div>\n'
                '            <h3>AC out during a summer heat wave</h3>\n'
                f'            <p style="margin-bottom: 0;">Outdoor unit silent &middot; warm air at vents &middot; short-cycling. Even short {city_e} summers bring stretches of 90&deg;F+ days &mdash; an AC failure during a heat wave is a real-comfort emergency. Most causes are electrical and require a technician.</p>\n'
                '          </div>'
            ),
        ]
    if climate_type == "mountain":
        return [
            card_no_heat(climate_type, city_e, winter_low, danger=True),
            card_no_ac(climate_type, city_e, summer_high),
            card_strange_noises(climate_type, city_e),
        ]
    # mixed-humid / coastal / fallback
    return [
        card_no_ac(climate_type, city_e, summer_high),
        card_no_heat(climate_type, city_e, winter_low, danger=True),
        card_strange_noises(climate_type, city_e),
    ]


# ============================================================
# HERO SUBHEAD CLIMATE VARIANTS
# ============================================================

def hero_subhead(climate_type, summer_high, winter_low):
    """Return climate-aware hero subhead. Falls back to standard line if temps missing."""
    sh = (summer_high or "").strip()
    wl = (winter_low or "").strip()
    standard = "Connect with an independent local HVAC pro now &mdash; 24/7 dispatch nationwide."
    if climate_type in ("hot-humid", "tropical"):
        return "When summer humidity hits and your AC quits, every hour matters. " + standard
    if climate_type == "hot-dry" and sh:
        return (
            f"When the desert heat surges past {escape(sh)}&deg;F, your AC can't afford "
            f"downtime. {standard}"
        )
    if climate_type in ("cold", "subarctic") and wl:
        return (
            f"When the temperature drops to {escape(wl)}&deg;F and your heat fails, every "
            f"hour counts. {standard}"
        )
    if climate_type == "mountain":
        return (
            "When mountain weather swings 40&deg;F in a day and your HVAC quits, you need "
            f"help fast. {standard}"
        )
    # mixed-humid / coastal / anything missing data
    return f"When your AC or heat fails on the worst day of the year, every hour matters. {standard}"


# ============================================================
# CLIMATE PROFILE HELPERS (intro + stat cards)
# ============================================================

def climate_profile_descriptor(climate_type, climate_zone):
    """Short adjective-style label inserted in the H2: 'hot-humid', 'desert', 'cold', etc."""
    return {
        "hot-humid": "hot-humid",
        "tropical": "tropical, year-round cooling",
        "hot-dry": "hot-dry desert",
        "mixed-humid": "mixed-humid",
        "coastal": "marine coastal",
        "cold": "cold-winter",
        "subarctic": "extreme-cold",
        "mountain": "high-altitude",
    }.get(climate_type, "regional")


def climate_profile_intro(c, climate_type):
    """Intro paragraph beneath the Climate Profile H2 — climate-aware, references SEER."""
    seer_e = escape(c['seer'])
    climate_zone_e = escape(c['climate'])
    if climate_type in ("hot-humid", "tropical"):
        return (
            f"This is a strongly cooling-dominated {climate_zone_e} climate &mdash; AC runs "
            f"8&ndash;10 months of the year and humidity management is a year-round design "
            f"consideration. Federal {seer_e} minimum applies to new equipment."
        )
    if climate_type == "hot-dry":
        return (
            f"This is among the most cooling-dominated U.S. climates &mdash; very high "
            f"cooling-degree-day totals and many days at or above 100&deg;F. Federal "
            f"{seer_e} minimum applies. Proper sizing is critical &mdash; an undersized "
            f"unit will run nonstop and fail prematurely."
        )
    if climate_type in ("cold", "subarctic"):
        return (
            f"This is a heating-dominated {climate_zone_e} climate &mdash; the furnace is "
            f"the most-used appliance in the home for 5&ndash;7 months a year. Federal "
            f"{seer_e} minimum applies to new AC equipment, and AFUE 90+ is the de-facto "
            f"baseline for new gas furnaces in cold-winter regions."
        )
    if climate_type == "mountain":
        return (
            f"At elevation, the {climate_zone_e} climate combines cold winters with high "
            f"cooling needs in summer &mdash; thin air reduces equipment efficiency about "
            f"4&ndash;5% per 1,000 feet. Federal {seer_e} minimum applies."
        )
    # mixed-humid / coastal / fallback
    return (
        f"This {climate_zone_e} climate splits the year between heating and cooling load. "
        f"Federal {seer_e} minimum applies to new AC equipment. Heat pumps that handle both "
        f"heating and cooling from one outdoor unit are an increasingly popular choice."
    )


def climate_stat_cards(c, climate_type):
    """4 stat cards: summer high · climate zone · cooling/heating proxy · electric heat share.

    For cells the xlsx doesn't carry verbatim (CDD, electric-heat %), we
    fall back to the winter low as the second proxy — keeps the layout
    consistent without inventing data.
    """
    summer_e = escape(c['summer_high'] or "")
    winter_e = escape(c['winter_low'] or "")
    # IECC zone short label, e.g. "2A" out of "Zone 2A (Hot-Humid)"
    zone_short = c['climate']
    if zone_short.startswith("Zone "):
        zone_short = zone_short.replace("Zone ", "").split(" ")[0]
    zone_short_e = escape(zone_short)
    zone_label = climate_profile_descriptor(climate_type, c['climate'])
    zone_label_e = escape(zone_label)

    cards = []
    # Card 1: summer high
    if summer_e:
        cards.append((f"{summer_e}&deg;F", "Avg summer high"))
    else:
        cards.append(("--", "Avg summer high"))
    # Card 2: IECC zone short
    cards.append((zone_short_e, f"IECC zone ({zone_label_e})"))
    # Card 3: winter low (substituted for CDD which we don't have for every city)
    if winter_e:
        cards.append((f"{winter_e}&deg;F", "Avg winter low"))
    else:
        cards.append(("--", "Avg winter low"))
    # Card 4: state SEER label (number-only proxy works visually)
    seer_text = c['seer'] or ""
    seer_short = seer_text.replace("SEER2 ", "").replace("SEER ", "")
    # Take just the first numeric token (e.g. "14.3") for the big stat
    parts = seer_short.split()
    big = parts[0] if parts else "--"
    cards.append((escape(big), "Federal SEER2 minimum"))

    out = []
    for big_val, label in cards:
        out.append(
            '<div class="precaution-card" style="text-align:center; padding: 24px 16px; '
            'background:#fff; border:1px solid var(--gray-200); '
            'box-shadow: 0 4px 16px rgba(10,22,40,0.04);">\n'
            '              <div style="font-size: 2.4rem; font-weight: 800; '
            'color: var(--orange-dark); line-height: 1; font-family: var(--font-display);">'
            f'{big_val}</div>\n'
            f'              <p style="font-size: 0.95rem; color: var(--gray-700); margin: 8px 0 0;">{label}</p>\n'
            '            </div>'
        )
    return "\n            ".join(out)


def climate_h2_text(c, climate_type):
    """H2 text for the Climate Profile section — uniform 'Citys descriptor climate & your HVAC' shape."""
    descriptor = climate_profile_descriptor(climate_type, c['climate'])
    return f"{escape(c['city'])}'s {descriptor} climate &amp; your HVAC"


# ============================================================
# CITY-RELATIVE FIGURE BLOCK (for inline placement in Climate section)
# ============================================================

def inline_location_figure(slug, city, st):
    """Render the per-city Wikimedia figure inline. Returns "" when image is missing."""
    return location_figure_html("city", slug, f"{city}, {st}", in_subdir=True).strip()


# ============================================================
# LOCAL DATA 2x2 CARD GRID (4 cards + intro + warning callout)
# ============================================================

def local_data_intro_callout(c):
    """Info banner above the 2x2 grid."""
    state_full = escape(STATE_FULL.get(c['state'], c['state']))
    return (
        '<div style="margin: 0 auto 32px; background: linear-gradient(135deg, #f7fafc, #edf2f7); '
        'border: 1px solid var(--gray-200); border-left: 5px solid var(--blue); '
        'border-radius: var(--radius); padding: 20px 24px;">\n'
        '            <div style="display: flex; align-items: flex-start; gap: 16px;">\n'
        '              <div style="font-size: 1.6rem; line-height: 1; flex-shrink: 0;" aria-hidden="true">&#128202;</div>\n'
        '              <div>\n'
        '                <div style="font-family: var(--font-display); font-weight: 800; '
        'font-size: 1.05rem; color: var(--navy); margin-bottom: 6px;">About these primary sources</div>\n'
        '                <p style="margin: 0; color: var(--gray-700); line-height: 1.65;">'
        f'Every numerical claim below references a federal, state, or municipal primary source &mdash; '
        f'NOAA climate normals, U.S. Census ACS, the {state_full} licensing authority, and your local '
        f'utility\'s published rebate program.</p>\n'
        '              </div>\n'
        '            </div>\n'
        '          </div>'
    )


def local_data_warning_callout():
    """Bottom warning banner — OBBBA-aware tax-credit notice."""
    return (
        '<div style="max-width: 1100px; margin: 32px auto 0; '
        'background: linear-gradient(135deg, #fffbeb, #fef3c7); '
        'border: 1px solid var(--yellow); border-left: 5px solid var(--orange-dark); '
        'border-radius: var(--radius); padding: 20px 24px;">\n'
        '            <div style="display: flex; align-items: flex-start; gap: 16px;">\n'
        '              <div style="font-size: 1.6rem; line-height: 1; flex-shrink: 0;" aria-hidden="true">&#128203;</div>\n'
        '              <div>\n'
        '                <div style="font-family: var(--font-display); font-weight: 800; '
        'font-size: 1.05rem; color: var(--navy); margin-bottom: 6px;">'
        'Federal tax credits &mdash; important update for 2026</div>\n'
        '                <p style="margin: 0; color: var(--gray-700); line-height: 1.65;">'
        'The federal <strong>Section 25C Energy Efficient Home Improvement Credit</strong> '
        'was terminated for installations placed in service after Dec 31, 2025 by the One Big '
        'Beautiful Bill Act (Public Law 119-21). <strong>State HEAR rebates and utility '
        'programs remain in effect.</strong> See our <a href="../article-hvac-financing" '
        'style="color: var(--orange-dark); font-weight: 600;">HVAC financing options</a> '
        'for what\'s still available.</p>\n'
        '              </div>\n'
        '            </div>\n'
        '          </div>'
    )


def local_data_card(icon_html, h3, body_html, link_html):
    """Render one of the 2x2 data cards with .precaution-card white-box style + auto-pinned link."""
    return (
        f'<div class="precaution-card" style="{PLAIN_CARD_STYLE}">\n'
        f'              <div class="precaution-icon" style="color: var(--blue);">{icon_html}</div>\n'
        f'              <h3>{h3}</h3>\n'
        f'              <p>{body_html}</p>\n'
        f'              <p style="margin-top: auto; padding-top: 8px; margin-bottom: 0;">{link_html}</p>\n'
        f'            </div>'
    )


# ============================================================
# v5 Local-Data parser: pull primary-source claims from xlsx col 17
# ============================================================

# Regex: capture an <h3 ...>...</h3> block followed by the immediately-next
# <p ...>...</p> block. Tolerates whitespace + interleaved tags.
_H3_P_PAIR_RE = re.compile(
    r'<h3[^>]*>(?P<h3>.*?)</h3>\s*(?:<p[^>]*>(?P<p>.*?)</p>)?',
    re.IGNORECASE | re.DOTALL,
)
_TAG_STRIP_RE = re.compile(r'<[^>]+>')
_FIRST_HREF_RE = re.compile(r'<a\s+[^>]*href="([^"]+)"', re.IGNORECASE)


def _strip_tags(s):
    return _TAG_STRIP_RE.sub('', s or '').strip()


def parse_local_context_blocks(html):
    """Parse local_context_html into a list of (h3_text, paragraph_inner_html) tuples.

    h3_text has tags stripped (plain text). paragraph_inner_html is the raw
    inner HTML of the <p> that immediately follows the <h3> — tags preserved
    so primary-source <a href> + <strong> survive.
    """
    if not html:
        return []
    out = []
    for m in _H3_P_PAIR_RE.finditer(html):
        h3 = _strip_tags(m.group('h3'))
        p_inner = (m.group('p') or '').strip()
        if not h3 or not p_inner:
            continue
        out.append((h3, p_inner))
    return out


def categorize_block(h3_text):
    """Map an H3 heading to one of: CLIMATE / HOUSING / LICENSE / REBATES / OVERFLOW."""
    h = h3_text.lower()
    # LICENSE first (catches "Licensing, Permits & Rebates" before REBATES does)
    # Includes city-permitting-authority phrasings so "Pikes Peak Regional Building"
    # type blocks land here instead of OVERFLOW.
    license_kw = (
        'license', 'licensing', 'contractor', 'roc ', ' roc', 'registrar',
        ' board', 'department of labor', 'workforce', 'mechanical administrator',
        'tdlr', 'cslb', 'dbpr', 'pahic', 'lslbc', 'ocilb', 'hacr',
        'qualifier', 'building department', 'regional building',
    )
    if any(k in h for k in license_kw):
        return 'LICENSE'
    # HOUSING
    housing_kw = ('housing', 'census', 'acs', 'heating fuel', 'heating-fuel', 'stock', 'fuel-oil', 'fuel oil')
    if any(k in h for k in housing_kw):
        return 'HOUSING'
    # CLIMATE
    climate_kw = ('climate', 'noaa', 'weather', 'temperature', 'snow', 'precipitation')
    # avoid 'heating' false-positive caught above by HOUSING
    if any(k in h for k in climate_kw):
        return 'CLIMATE'
    # REBATES — keyword-bucketed so "Cooling Ordinance" / "Heating Fuel"
    # (a city-distinctive block / a housing block) don't preempt the actual
    # rebates+permits content. We deliberately exclude the lone words
    # "energy" and "ordinance" — a proper rebates block always also mentions
    # rebate/permit/fee/utility-name explicitly.
    rebates_kw = (
        'rebate', 'permit', 'fee', 'utility', 'utilities', 'incentive',
        'tax credit', 'federal credit',
        'ppl ', 'bge ', 'duke ', 'apc ', 'aps ', 'aps,', 'aps &',
        'srp', 'pud', 'pge', 'mass save', 'masssave', 'mdu', 'enstar',
        'chugach', 'austin energy', 'georgia power', 'alabama power',
        'idaho power', 'eversource', 'puget', 'entergy', 'focus on energy',
    )
    if any(k in h for k in rebates_kw):
        return 'REBATES'
    return 'OVERFLOW'


# Heuristic anchor labels for the "→" link based on the URL host/path.
def _anchor_label_for(url, state_full):
    if not url:
        return 'View source'
    u = url.lower()
    if 'ncei.noaa.gov' in u or 'noaa.gov' in u:
        return 'NOAA NCEI Climate Normals'
    if 'census.gov' in u:
        return 'Census ACS Data'
    if 'energystar.gov' in u:
        return 'ENERGY STAR'
    if 'dsireusa.org' in u:
        return f'DSIRE {escape(state_full)}'
    if 'irs.gov' in u:
        return 'IRS Section 25C'
    if 'energy.gov' in u:
        return 'U.S. DOE'
    # State licensing regulator URLs → "{State} License Lookup"
    license_hosts = (
        'tdlr.', 'cslb.ca.gov', 'roc.az.gov', 'myfloridalicense.com',
        'hpc.state.', 'oplc.', 'pahic.', 'state.', '.gov/license',
        'dpor.', 'dca.ca.gov', 'dllr.', 'lirc.', 'ctlcic.',
    )
    if any(h in u for h in license_hosts):
        return f'{escape(state_full)} License Lookup'
    # City permit / fee schedule URLs
    if 'permit' in u or 'fee-schedule' in u or 'pddsite' in u or 'planning' in u:
        return 'City Fee Schedule'
    # Generic .gov city sites → "City Resource"
    if '.gov' in u:
        return 'Municipal Source'
    return 'View primary source'


# ============================================================
# URL -> primary-source institution name (Card H3 derivation)
# Used to keep the card's H3 distinct from the icon-label topic word.
# Phoenix-pilot reference: H3s read like "NOAA NCEI 1991-2020 Normals",
# "U.S. Census ACS 2022 5-Year", "Arizona Registrar of Contractors",
# "APS, SRP, Phoenix Permitting" - i.e. the institution(s), never
# the topic word that the icon already shows.
# ============================================================

# Topic words owned by the icon labels per category. We must NEVER let
# any of these words appear in a card's H3 - that's the duplication trap.
_TOPIC_WORDS_BY_CAT = {
    'CLIMATE': ('climate', 'climate profile'),
    'HOUSING': ('housing', 'housing stock'),
    'LICENSE': ('license', 'licensing', 'contractor licensing'),
    'REBATES': ('rebates', 'rebate', 'permits & rebates', 'local rebates'),
}


def _h3_from_url(url, category, state_full, city_name):
    """Map a primary-source URL to a card H3 string (institution name).

    Returns None if no mapping fits - caller falls back to host-derived
    title-case or the original H3 text.
    """
    if not url:
        return None
    u = url.lower()

    # Federal data / agencies
    if 'ncei.noaa.gov' in u or 'weather.gov' in u or 'noaa.gov' in u:
        return 'NOAA NCEI 1991&ndash;2020 Normals'
    if 'census.gov' in u:
        return 'U.S. Census ACS 2022 5-Year'
    if 'energystar.gov' in u:
        return 'ENERGY STAR (EPA)'
    if 'dsireusa.org' in u:
        return 'DSIRE Database (NCSU + DOE)'
    if 'irs.gov' in u:
        return 'IRS Section 25C Guidance'
    if 'energy.gov' in u:
        return 'U.S. Department of Energy'
    if 'basc.pnnl.gov' in u:
        return 'DOE Building Science Corp.'

    # State licensing boards / departments
    if 'roc.az.gov' in u:
        return 'Arizona Registrar of Contractors'
    if 'cslb.ca.gov' in u:
        return 'California Contractors State License Board'
    if 'dca.ca.gov' in u:
        return 'California Dept. of Consumer Affairs'
    if 'myfloridalicense.com' in u or 'dbpr.state.fl.us' in u:
        return 'Florida DBPR / CILB'
    if 'tdlr.texas.gov' in u:
        return 'Texas Dept. of Licensing &amp; Regulation'
    if 'dol.wa.gov' in u or 'lni.wa.gov' in u:
        return 'Washington Dept. of Labor &amp; Industries'
    if 'dpor.virginia.gov' in u:
        return 'Virginia DPOR'
    if 'dol.ny.gov' in u or 'dol.state.ny.us' in u:
        return 'New York Dept. of State'
    if 'mass.gov' in u:
        return 'Massachusetts Board of State Examiners'
    if 'hacr.alabama.gov' in u:
        return 'Alabama HACR Board'
    if 'lslbc.gov' in u or 'lslbc.louisiana.gov' in u:
        return 'Louisiana State Licensing Board'
    if 'nscb.nv.gov' in u or 'nvcontractorsboard.com' in u:
        return 'Nevada State Contractors Board'
    if 'commerce.alaska.gov' in u:
        return 'Alaska Mechanical Administrators'
    if 'srca.nm.gov' in u:
        return 'New Mexico Construction Industries Div.'
    if 'nclicensing.org' in u:
        return 'NC Licensing Board for Contractors'
    if 'dsps.wi.gov' in u:
        return 'Wisconsin DSPS'
    if 'com.ohio.gov' in u:
        return 'Ohio Construction Industry Examining Board'
    if 'oplc.' in u:
        return 'NH Office of Professional Licensure'
    if 'pahic.' in u:
        return 'PA Home Improvement Contractor Registry'
    if 'cca.hawaii.gov' in u:
        return 'Hawaii DCCA'
    if 'njconsumeraffairs.gov' in u:
        return 'NJ Division of Consumer Affairs'
    if 'dllr.state.md.us' in u or 'dllr.maryland.gov' in u:
        return 'Maryland DLLR'
    if 'dli.mn.gov' in u:
        return 'Minnesota Dept. of Labor &amp; Industry'
    if 'oklahoma.gov' in u and ('cib' in u or 'license' in u or 'contractor' in u):
        return 'Oklahoma Construction Industries Board'
    if 'tn.gov' in u and ('regboards' in u or 'commerce' in u or 'license' in u):
        return 'Tennessee Board for Licensing Contractors'

    # Major utilities (rebate sources)
    util_map = (
        ('alabamapower.com', 'Alabama Power'),
        ('georgiapower.com', 'Georgia Power'),
        ('idahopower.com', 'Idaho Power'),
        ('aepohio.com', 'AEP Ohio'),
        ('aesindiana.com', 'AES Indiana'),
        ('austinenergy.com', 'Austin Energy'),
        ('savings.austinenergy.com', 'Austin Energy'),
        ('cpsenergy.com', 'CPS Energy'),
        ('resi-savenow.cpsenergy.com', 'CPS Energy'),
        ('bgesmartenergy.com', 'BGE Smart Energy'),
        ('columbiagasohio.com', 'Columbia Gas of Ohio'),
        ('dteenergy.com', 'DTE Energy'),
        ('energyright.com', 'TVA EnergyRight'),
        ('energysmartnola.info', 'Energy Smart New Orleans'),
        ('energytrust.org', 'Energy Trust of Oregon'),
        ('eversource', 'Eversource'),
        ('focusonenergy.com', 'Focus on Energy (WI)'),
        ('fpl.com', 'Florida Power &amp; Light'),
        ('hawaiienergy.com', 'Hawaii Energy'),
        ('jea.com', 'JEA'),
        ('njcleanenergy.com', 'NJ Clean Energy'),
        ('pgworks.com', 'Philadelphia Gas Works'),
        ('powerforwardwithpso.com', 'PSO PowerForward'),
        ('smud.org', 'SMUD'),
        ('tampaelectric.com', 'Tampa Electric (TECO)'),
        ('tep.com', 'Tucson Electric Power'),
        ('texasgasservice.com', 'Texas Gas Service'),
        ('xcelenergy.com', 'Xcel Energy'),
        ('epelectric.com', 'El Paso Electric'),
        ('bayren.org', 'BayREN'),
    )
    for needle, label in util_map:
        if needle in u:
            return label

    # Statewide statute / law repositories
    if 'leg.state.fl.us' in u or 'flsenate.gov' in u:
        return 'Florida Legislature'
    if 'app.leg.wa.gov' in u:
        return 'Washington State Legislature'
    if 'law.lis.virginia.gov' in u:
        return 'Code of Virginia'
    if 'oregon.public.law' in u:
        return 'Oregon Revised Statutes'

    # City-permit / municipal sites: build "City of {city}" heading.
    city_permit_hosts = (
        'phoenix.gov', 'houstontx.gov', 'denvergov.org', 'seattle.gov',
        'sandiego.gov', 'phila.gov', 'portland.gov', 'tampa.gov',
        'rva.gov', 'dallascityhall.com', 'miamidade.gov', 'nyc.gov',
        'nola.gov', 'tools.slc.gov', 'pprbd.org', 'dob.dc.gov',
    )
    for host in city_permit_hosts:
        if host in u:
            # Special-case multi-utility / city-permit phrasing for REBATES
            if category == 'REBATES':
                return f'City of {escape(city_name)} Permitting'
            return f'City of {escape(city_name)} Planning &amp; Development'

    # Statewide .gov fallback (e.g. michigan.gov, oklahoma.gov w/o license)
    if '.gov' in u:
        return f'{escape(state_full)} State Resource'

    # Library / municode (city ordinance lookups)
    if 'library.municode.com' in u:
        return f'{escape(city_name)} Municipal Code'

    return None


def _h3_from_host_fallback(url):
    """Last-chance fallback: derive a title-cased label from URL host."""
    if not url:
        return None
    m = re.search(r'https?://(?:www\.)?([^/]+)', url)
    if not m:
        return None
    host = m.group(1).lower()
    # Map common city-permitting hosts to a clean label.
    nice = {
        'phoenix.gov': 'City of Phoenix',
        'houstontx.gov': 'City of Houston',
        'denvergov.org': 'City of Denver',
        'seattle.gov': 'City of Seattle',
        'sandiego.gov': 'City of San Diego',
        'phila.gov': 'City of Philadelphia',
        'portland.gov': 'City of Portland',
        'tampa.gov': 'City of Tampa',
        'rva.gov': 'City of Richmond',
        'pprbd.org': 'Pikes Peak Regional Building',
        'dob.dc.gov': 'DC Dept. of Buildings',
    }
    if host in nice:
        return nice[host]
    # Generic title-case for .gov hosts
    if '.gov' in host or '.org' in host:
        # Strip trailing .gov/.org
        base = re.sub(r'\.(gov|org|com|us|info|net)$', '', host)
        # Replace dots and hyphens with spaces
        base = base.replace('.', ' ').replace('-', ' ')
        return ' '.join(w.capitalize() for w in base.split() if w)
    return None


def _h3_overlaps_topic(h3_text, category):
    """True if the h3 text contains any topic word owned by the icon label."""
    if not h3_text:
        return True
    h = h3_text.lower()
    # Strip parentheticals and HTML entities for cleaner matching
    h_clean = re.sub(r'&[a-z]+;', ' ', h)
    h_clean = re.sub(r'\s+', ' ', h_clean).strip()
    for w in _TOPIC_WORDS_BY_CAT.get(category, ()):
        # Use word-boundary match for the topic word
        if re.search(r'\b' + re.escape(w) + r'\b', h_clean):
            return True
    return False


def _pick_url_for_category(category, paragraph_html):
    """Pick the most-relevant URL from paragraph_html for a given category.

    The first href isn't always the right one - e.g. Boston's "Licensing,
    Permits & Rebates" block lists energystar.gov FIRST, then a state
    licensing URL. For LICENSE/REBATES we scan all hrefs and prefer the
    URL whose host matches the category's institution profile.
    """
    if not paragraph_html:
        return None
    urls = re.findall(r'href="(https?://[^"]+)"', paragraph_html)
    if not urls:
        return None

    # Category-specific host preference order (substring match, lowercased)
    license_hosts = (
        'tdlr.', 'cslb.ca.gov', 'roc.az.gov', 'myfloridalicense.com',
        'dbpr.state.fl.us', 'dpor.virginia.gov', 'dca.ca.gov',
        'dol.wa.gov', 'lni.wa.gov', 'dol.ny.gov', 'dol.state.ny.us',
        'mass.gov', 'hacr.alabama.gov', 'lslbc.gov', 'nscb.nv.gov',
        'nvcontractorsboard.com', 'commerce.alaska.gov', 'srca.nm.gov',
        'nclicensing.org', 'dsps.wi.gov', 'com.ohio.gov', 'oplc.',
        'pahic.', 'cca.hawaii.gov', 'njconsumeraffairs.gov',
        'dllr.state.md.us', 'dllr.maryland.gov', 'dli.mn.gov',
        'oklahoma.gov', 'tn.gov', 'michigan.gov', 'state.',
        'license', 'contractor', 'roc.',
    )
    rebates_hosts = (
        'dsireusa.org', 'energystar.gov', 'energy.gov',
        # Utilities by domain fragment
        'alabamapower', 'georgiapower', 'idahopower', 'aepohio',
        'aesindiana', 'austinenergy', 'cpsenergy', 'bgesmart',
        'columbiagasohio', 'dteenergy', 'energyright', 'energysmartnola',
        'energytrust', 'eversource', 'focusonenergy', 'fpl.com',
        'hawaiienergy', 'jea.com', 'njcleanenergy', 'pgworks',
        'powerforwardwithpso', 'smud.org', 'tampaelectric', 'tep.com',
        'texasgasservice', 'xcelenergy', 'epelectric', 'bayren',
        'irs.gov', 'rebate',
    )
    climate_hosts = ('ncei.noaa.gov', 'noaa.gov', 'weather.gov')
    housing_hosts = ('census.gov',)

    pref = {
        'LICENSE': license_hosts,
        'REBATES': rebates_hosts,
        'CLIMATE': climate_hosts,
        'HOUSING': housing_hosts,
    }.get(category, ())

    for needle in pref:
        for u in urls:
            if needle in u.lower():
                return u
    # No category match - fall back to first URL.
    return urls[0]


def _derive_card_h3(category, raw_h3, paragraph_html, state_full, city_name):
    """Return the card H3 string. Prefers URL-derived institution name.

    Strategy:
      1. Pick the most-category-relevant URL from paragraph_html.
      2. Try the URL -> institution map (_h3_from_url) - TRUSTED. If a
         curated institution name matches the URL, use it even if it
         contains a topic-keyword (e.g. "Texas Dept. of Licensing & Reg"
         contains "Licensing" but is a legitimate primary-source name).
      3. If no curated match, try host-derived title-case fallback. Apply
         topic-overlap rejection here (host fallbacks are auto-generated
         and more likely to be tautological).
      4. Last resort: clean raw xlsx H3 (strip parentheticals). Reject if
         it overlaps the icon topic word.
      5. Force a generic primary-source heading.
    """
    # 1+2. URL primary-source mapping (curated table - trust it).
    # Special case: for the LICENSE card, only trust the URL if it's an
    # actual licensing-authority host - federal rebate URLs (energystar /
    # irs / energy.gov) shouldn't title the State License card.
    url = _pick_url_for_category(category, paragraph_html)
    candidate = _h3_from_url(url, category, state_full, city_name)
    if candidate:
        if category == 'LICENSE':
            # Reject federal-rebate institution names for the License card.
            non_license = ('energy star', 'irs section', 'doe', 'department of energy', 'dsire', 'building science')
            if not any(needle in candidate.lower() for needle in non_license):
                return candidate
        else:
            return candidate

    # 3. Host fallback (auto-generated - apply overlap check).
    # For the LICENSE card, also reject host fallbacks that point at federal
    # rebate domains (energystar / irs / energy.gov) - those don't belong
    # as a state License card heading.
    candidate = _h3_from_host_fallback(url)
    if candidate and not _h3_overlaps_topic(candidate, category):
        if category == 'LICENSE':
            non_license = ('energystar', 'irs', 'doe', 'energy.gov', 'dsire')
            host_l = (url or '').lower()
            if not any(needle in host_l for needle in non_license):
                return candidate
        else:
            return candidate

    # 4. Clean raw H3, last resort
    cleaned = re.sub(r'\s*\([^)]*\)\s*$', '', raw_h3 or '').strip()
    cleaned = cleaned or raw_h3 or ''
    if cleaned and not _h3_overlaps_topic(cleaned, category):
        return cleaned

    # 5. Force a generic primary-source heading so the card never reads
    # "Climate Profile / Climate Profile".
    fallback_by_cat = {
        'CLIMATE': 'NOAA Climate Normals',
        'HOUSING': 'U.S. Census ACS Data',
        'LICENSE': f'{escape(state_full)} Licensing Authority',
        'REBATES': 'Utility &amp; Permit Sources',
    }
    return fallback_by_cat.get(category, cleaned or 'Primary Source')


def local_data_card_from_block(category, h3_text, paragraph_html, state_full, city_name='', primary_paragraph_html=None):
    """Build one of the 4 cards from a parsed (h3, paragraph) pair.

    The card H3 is derived from the primary-source URL inside the paragraph
    (institution name) so it never duplicates the topic word that lives in
    the icon label above it. See _derive_card_h3() for the mapping.

    primary_paragraph_html: pass the FIRST paragraph only (without any
    overflow-appended body) so URL derivation only sees URLs that belong
    to the primary block. Defaults to paragraph_html for backward-compat.
    """
    icon_label_by_cat = {
        'CLIMATE':  '&#127777;&#65039; Climate Profile',
        'HOUSING':  '&#127968; Housing Stock',
        'LICENSE':  f'&#128203; {escape(state_full)} License',
        'REBATES':  '&#128176; Local Rebates &amp; Permits',
    }
    icon_html = icon_label_by_cat.get(category, '&#128202; Local Data')

    # Card H3 = primary-source institution derived from the URL of the
    # PRIMARY paragraph (not any appended overflow body).
    h3_source_html = primary_paragraph_html if primary_paragraph_html is not None else paragraph_html
    cleaned_h3_e = _derive_card_h3(category, h3_text, h3_source_html, state_full, city_name)

    # First href in primary paragraph → "→" footer link.
    m = _FIRST_HREF_RE.search(h3_source_html)
    url = m.group(1) if m else None
    if url:
        # The xlsx URLs may already be entity-encoded (&amp;). Trust the source.
        anchor = _anchor_label_for(url, state_full)
        link_html = (
            f'<a href="{url}" target="_blank" rel="nofollow noopener" '
            f'style="color: var(--orange-dark); font-weight: 600;">{anchor} &rarr;</a>'
        )
    else:
        # Fallback to a generic primary-source link if the paragraph has no link.
        link_html = (
            '<a href="https://www.dsireusa.org/" target="_blank" rel="nofollow noopener" '
            'style="color: var(--orange-dark); font-weight: 600;">DSIRE Database &rarr;</a>'
        )

    return (
        f'<div class="precaution-card" style="{PLAIN_CARD_STYLE}">\n'
        f'              <div class="precaution-icon" style="color: var(--blue);">{icon_html}</div>\n'
        f'              <h3>{cleaned_h3_e}</h3>\n'
        f'              <p>{paragraph_html}</p>\n'
        f'              <p style="margin-top: auto; padding-top: 8px; margin-bottom: 0;">{link_html}</p>\n'
        f'            </div>'
    )


def local_data_cards_from_context(c, state_info):
    """Return the 4 cards, parsed from local_context_html when available.

    Per-card graceful fallback: if a category's block is missing in the xlsx
    content, that ONE card uses the v4 generic-prose helper. Other cards
    still use the parsed primary-source content.
    """
    raw = (c.get('local_context_html') or '').strip()
    state_full = STATE_FULL.get(c['state'], c['state'])

    # Default to v4 generic cards (will be partially overwritten below).
    generic = local_data_cards(c, state_info)
    # Order matches local_data_cards return: [climate, housing, license, rebates]
    fallback_by_cat = {
        'CLIMATE': generic[0],
        'HOUSING': generic[1],
        'LICENSE': generic[2],
        'REBATES': generic[3],
    }
    fallback_count = 0

    if not raw:
        return generic, 4  # all 4 cards fell back to generic prose

    # Normalize legal-section symbol for clean rendering (matches v3 behavior).
    raw = raw.replace('&sect; ', 'Section ').replace('&sect;', 'Section ')

    pairs = parse_local_context_blocks(raw)
    if not pairs:
        return generic, 4

    # First-block-wins per category (later same-category blocks become OVERFLOW).
    chosen = {}  # cat -> (h3, p)
    overflow = []  # list of (h3, p)
    for h3, p in pairs:
        cat = categorize_block(h3)
        if cat == 'OVERFLOW':
            overflow.append((h3, p))
            continue
        if cat in chosen:
            overflow.append((h3, p))
            continue
        chosen[cat] = (h3, p)

    # Append overflow blocks to most-related card body. Heuristic: scan
    # overflow H3 with a second pass that *forces* a category by looking at
    # similar but more permissive keywords. Default = REBATES bucket.
    def _force_overflow_cat(h3_text):
        h = h3_text.lower()
        if any(k in h for k in ('cooling', 'heat', 'climate', 'snow', 'humid', 'desert', 'subarctic', 'tropical', 'extreme')):
            return 'CLIMATE'
        if any(k in h for k in ('housing', 'fuel', 'pre-war', 'rowhouse', 'electric', 'gas')):
            return 'HOUSING'
        if any(k in h for k in ('license', 'contractor', 'tdlr', 'roc')):
            return 'LICENSE'
        return 'REBATES'

    extra_for = {'CLIMATE': [], 'HOUSING': [], 'LICENSE': [], 'REBATES': []}
    for h3, p in overflow:
        target = _force_overflow_cat(h3)
        # Only stash overflow if target was matched (else drop quietly).
        extra_for[target].append((h3, p))

    cards = []
    for cat in ('CLIMATE', 'HOUSING', 'LICENSE', 'REBATES'):
        if cat in chosen:
            h3, p = chosen[cat]
            # Append first overflow body (no extra heading) as a 2nd <p> only
            # if the primary paragraph is shorter than ~600 chars (room to add).
            body_html = p
            primary_p = p  # Keep the original/primary paragraph for URL derivation
            if extra_for[cat] and len(_strip_tags(p)) < 600:
                _, extra_p = extra_for[cat][0]
                body_html = p + '</p>\n              <p>' + extra_p
            cards.append(local_data_card_from_block(
                cat, h3, body_html, state_full, c.get('city', ''),
                primary_paragraph_html=primary_p,
            ))
        else:
            cards.append(fallback_by_cat[cat])
            fallback_count += 1

    return cards, fallback_count


def local_data_cards(c, state_info):
    """Return the 4 stacked card HTML strings (joined later by the caller)."""
    city_e = escape(c['city'])
    state_full_e = escape(STATE_FULL.get(c['state'], c['state']))
    utility_e = escape(c['utility'])
    rebates_e = escape(c['rebates'])
    license_e = escape(c['license'])
    permit_e = escape(c['permit'])

    # Climate card
    climate_card = local_data_card(
        "&#127777;&#65039; Climate Profile",
        "NOAA NCEI 1991&ndash;2020 Normals",
        f"{city_e} climate normals are drawn from the nearest NOAA weather station. "
        f"Average summer high: <strong>{escape(c['summer_high'])}&deg;F</strong> &middot; "
        f"average winter low: <strong>{escape(c['winter_low'])}&deg;F</strong> &middot; "
        f"federal efficiency standard: <strong>{escape(c['seer'])}</strong>. "
        f"These figures shape system sizing, refrigerant choice, and which equipment "
        f"qualifies for the local utility programs.",
        '<a href="https://www.ncei.noaa.gov/access/us-climate-normals/" target="_blank" '
        'rel="nofollow noopener" style="color: var(--orange-dark); font-weight: 600;">'
        'NOAA NCEI Climate Normals &rarr;</a>',
    )

    # Housing card
    pop_str = f"{c['pop']:,}" if c.get('pop') else "many"
    housing_card = local_data_card(
        "&#127968; Housing Stock",
        "U.S. Census ACS",
        f"Population <strong>{pop_str}</strong> across {city_e}, {state_full_e}. The "
        f"American Community Survey (ACS) tracks heating-fuel mix, year-built distribution, "
        f"and unit type at the place level &mdash; these drive whether the typical {city_e} "
        f"home is on natural gas, electric, or heat-pump heating, and what equipment "
        f"capacity the contractor is sizing for.",
        '<a href="https://data.census.gov/" target="_blank" '
        'rel="nofollow noopener" style="color: var(--orange-dark); font-weight: 600;">'
        'Census ACS Data &rarr;</a>',
    )

    # License card — verified lookup from states.xlsx if available
    lookup_url = None
    lookup_body_name = None
    if state_info:
        body = (state_info.get('Licensing Body/Agency') or '').strip()
        url = (state_info.get('License Lookup URL') or '').strip()
        if body and url and url.upper() != 'N/A':
            lookup_url = url
            lookup_body_name = body
    if lookup_url and lookup_body_name:
        license_link_html = (
            f'<a href="{escape(lookup_url)}" target="_blank" rel="nofollow noopener" '
            f'style="color: var(--orange-dark); font-weight: 600;">'
            f'{escape(lookup_body_name)} License Lookup &rarr;</a>'
        )
    else:
        license_link_html = (
            '<a href="https://www.dsireusa.org/" target="_blank" rel="nofollow noopener" '
            'style="color: var(--orange-dark); font-weight: 600;">DSIRE State Programs &rarr;</a>'
        )

    if license_e.lower().startswith('no '):
        license_body = (
            f"{state_full_e} does not require a statewide HVAC contractor license. "
            f"<strong>Verify your contractor's insurance and any local registration before "
            f"authorizing work.</strong> Local permits in {city_e} are filed through "
            f"<strong>{permit_e}</strong>."
        )
    else:
        license_body = (
            f"Every HVAC contractor in {city_e} must hold a current "
            f"<strong>{license_e}</strong> on file with the state licensing authority. "
            f"<strong>Verify the license number before authorizing any work.</strong> "
            f"Local permits are filed through <strong>{permit_e}</strong>."
        )

    license_card = local_data_card(
        "&#128203; State Contractor License",
        f"{state_full_e} &mdash; verify before hire",
        license_body,
        license_link_html,
    )

    # Rebates card — OBBBA-aware (federal 25C terminated)
    rebates_card = local_data_card(
        "&#128176; Local Rebates &amp; Permits",
        f"{utility_e}, DSIRE, {permit_e}",
        f"{city_e} homeowners served by <strong>{utility_e}</strong> may qualify for "
        f"savings through <strong>{rebates_e}</strong> when installing qualifying "
        f"high-efficiency equipment. State HEAR rebates and utility programs remain "
        f"the active federal-funded path in 2026 &mdash; the federal Section 25C tax "
        f"credit was terminated for installations placed in service after Dec 31, 2025 "
        f"(P.L. 119-21).",
        '<a href="https://www.dsireusa.org/" target="_blank" rel="nofollow noopener" '
        'style="color: var(--orange-dark); font-weight: 600;">DSIRE Database &rarr;</a> '
        '&middot; <a href="https://www.energystar.gov/products/energy_star_home_upgrade/clean_heating_cooling" '
        'target="_blank" rel="nofollow noopener" '
        'style="color: var(--orange-dark); font-weight: 600;">ENERGY STAR Heating &amp; Cooling &rarr;</a>',
    )

    return [climate_card, housing_card, license_card, rebates_card]


# ============================================================
# SERVICES + COVERAGE 2-CARD ROW
# ============================================================

def services_and_coverage_cards(c, climate_type, slug, all_zips):
    """Return the two cards: services list + ZIPs/Neighborhoods list."""
    city_e = escape(c['city'])
    svcs = services_list(c['city'], climate_type)
    svc_items = "\n              ".join(f"<li>{s}</li>" for s in svcs)

    # ZIPs/Neighborhoods — pair positionally; same approach as v3.
    raw_n = [n.strip() for n in str(c['neighborhoods']).split(',') if n.strip()]
    raw_z = [z.strip() for z in str(c['zips']).split(',') if z.strip()]
    items = []
    pairs = min(len(raw_n), len(raw_z))
    for i in range(pairs):
        items.append(f'<li><strong>{escape(raw_n[i])}</strong> &mdash; ZIP {escape(raw_z[i])}</li>')
    for n in raw_n[pairs:]:
        items.append(f'<li><strong>{escape(n)}</strong></li>')
    extra_z = raw_z[pairs:]
    if extra_z:
        items.append(f'<li>Additional ZIPs: {escape(", ".join(extra_z))}</li>')
    if not items:
        items.append(f'<li>Coverage details available by phone &mdash; call (844) 582-1795.</li>')
    zip_items = "\n              ".join(items)

    services_card = (
        f'<div class="precaution-card" style="{PLAIN_CARD_STYLE}">\n'
        '            <div class="precaution-icon" style="color: var(--navy);">'
        f'&#128295; Services in {city_e}</div>\n'
        '            <h3>What our network covers</h3>\n'
        '            <ul style="margin-top: 0; margin-bottom: 0;">\n'
        f'              {svc_items}\n'
        '            </ul>\n'
        '          </div>'
    )
    zips_card = (
        f'<div class="precaution-card" id="neighborhoods" style="{PLAIN_CARD_STYLE}">\n'
        '            <div class="precaution-icon" style="color: var(--navy);">'
        '&#128205; ZIPs &amp; Neighborhoods</div>\n'
        '            <h3>Where we connect homeowners</h3>\n'
        '            <ul style="margin-top: 0; margin-bottom: 0;">\n'
        f'              {zip_items}\n'
        '            </ul>\n'
        '          </div>'
    )
    return services_card, zips_card


# ============================================================
# ALSO-SERVING METRO CARDS (card-driven port of v3 also_serving)
# ============================================================

def also_serving_section_cards(anchor_city, absorbed_data):
    """Card-driven 'Also Serving Metro' section. Returns "" if no absorbed cities."""
    if not absorbed_data:
        return ""

    anchor_e = escape(anchor_city)
    cards_html = []
    for ac in absorbed_data:
        c_e = escape(ac['city'])
        st_e = escape(ac['state'])
        n_e = escape(ac['neighborhoods'])
        z_e = escape(ac['zips'])
        p_e = escape(ac['permit'])
        cards_html.append(
            f'<div class="precaution-card" style="{PLAIN_CARD_STYLE}">\n'
            f'            <div class="precaution-icon" style="color: var(--navy);">&#128205; {c_e}, {st_e}</div>\n'
            '            <h3>Neighborhoods, ZIPs &amp; permits</h3>\n'
            f'            <p style="margin-bottom: 0;">Neighborhoods: <strong>{n_e}</strong>. '
            f'ZIP codes served: <strong>{z_e}</strong>. Local permits through <strong>{p_e}</strong>.</p>\n'
            '          </div>'
        )
    cards_joined = "\n          ".join(cards_html)

    return f'''
    <!-- Also Serving Metro Area -->
    <section class="section" style="padding: 72px 0; background:#fff;">
      <div class="container">
        <div style="text-align:center; margin-bottom: 36px;">
          {metro_pill()}
          <h2 style="font-size: 1.75rem; color: var(--navy); margin: 0 0 12px;">Also serving the greater {anchor_e} metro</h2>
          <p style="max-width: 720px; margin: 0 auto; font-size: 1.05rem; color: var(--gray-700); line-height: 1.7;">Our HVAC referral network extends beyond {anchor_e} proper into surrounding metro communities.</p>
        </div>
        <div class="precaution-cards" style="max-width: 760px; margin: 0 auto; display:grid; gap: 20px;">
          {cards_joined}
        </div>
      </div>
    </section>
'''


# ============================================================
# MID-PAGE CTA BAND
# ============================================================

def midpage_cta(c, climate_type):
    """Navy CTA band — uses gray-50 outer bg + navy gradient inner card.

    The 'sub-line' summarizes verifiable trust: independent · 24/7 · state-licensed.
    """
    city_e = escape(c['city'])
    license_e = escape(c['license'])
    if license_e.lower().startswith('no '):
        license_summary = "independent network"
    else:
        # Strip parentheticals/extra clauses for the one-liner.
        short = license_e.split(';')[0].split('(')[0].strip()
        # Cap visual length — cards stay clean.
        if len(short) > 50:
            short = short.split(',')[0].strip()
        license_summary = f"{short}-verified network"

    return f'''
    <!-- MID-PAGE CTA -->
    <section style="padding: 64px 0; background: var(--gray-50);">
      <div class="container">
        <div style="max-width: 760px; margin: 0 auto; background:linear-gradient(135deg, var(--navy-deep), var(--navy)); color:#fff; padding: 32px; border-radius: var(--radius-lg); text-align:center; box-shadow: 0 12px 40px rgba(10,22,40,0.18);">
          <p style="font-size: 1.4rem; font-weight: 700; font-family: var(--font-display); color:#fff; margin-bottom: 10px;">Ready to talk to a {city_e} HVAC pro?</p>
          <p style="margin-bottom: 22px; opacity: 0.85; font-size: 1rem;">Independent technicians &middot; 24/7 dispatch &middot; {license_summary}</p>
          <a href="tel:+18445821795" class="btn btn-primary btn-lg btn-vibrate"><span class="phone-icon">&#128222;</span> Call Now &mdash; (844) 582-1795</a>
          <p style="font-size: 0.72rem; color: rgba(255,255,255,0.5); margin: 16px auto 0; max-width: 460px; line-height: 1.5;">Disclosure: We are a referral service and may receive compensation for qualified calls. Calls may be routed to an independent provider network and may be recorded. Pricing and availability vary by provider and location.</p>
        </div>
      </div>
    </section>
'''


# ============================================================
# TRUST STRIP (3 wh-step cards, NO neighborhood list — that lives in Services)
# ============================================================

def trust_strip_section(c, climate_type, state_info):
    """Trust strip with 3 wh-step cards: 24/7 dispatch · metro coverage one-liner · state-license one-liner.

    NO neighborhood list here — that belongs in Services & Coverage only
    (content-duplication rule, CLAUDE.md line 411).
    """
    city_e = escape(c['city'])
    state_full_e = escape(STATE_FULL.get(c['state'], c['state']))
    license_e = escape(c['license'])

    # State licensing one-liner
    if license_e.lower().startswith('no '):
        license_h3 = f"{state_full_e} contractor verification"
        license_body = (
            f"{state_full_e} does not require a statewide HVAC contractor license. "
            f"Verify any contractor's insurance and local registration before you hire."
        )
    else:
        # Short license name for H3
        short = license_e.split(';')[0].split('(')[0].strip()
        if len(short) > 60:
            short = short.split(',')[0].strip()
        license_h3 = f"{escape(short)}"
        license_body = (
            f"All HVAC contractors in {state_full_e} should hold a current "
            f"<strong>{license_e}</strong>. "
        )
        # Append licensing-body link if available
        if state_info:
            body_name = (state_info.get('Licensing Body/Agency') or '').strip()
            url = (state_info.get('License Lookup URL') or '').strip()
            if body_name and url and url.upper() != 'N/A':
                license_body += (
                    f'Verify any contractor at the <a href="{escape(url)}" target="_blank" '
                    f'rel="nofollow noopener" style="color: var(--orange-dark); font-weight: 600;">'
                    f'{escape(body_name)}</a> before you hire.'
                )
            else:
                license_body += "Verify the license number before you hire."
        else:
            license_body += "Verify the license number before you hire."

    return f'''
    <!-- TRUST STRIP -->
    <section class="section" style="padding: 72px 0; background: var(--gray-50);">
      <div class="container">
        <div style="text-align:center; margin-bottom: 36px;">
          {trust_pill(city_e)}
          <h2 style="font-size: 1.75rem; color: var(--navy); margin: 0;">About the Cool Call Pro {city_e} network</h2>
        </div>

        <div class="wh-steps" style="max-width: 1100px; margin: 0 auto;">

          <div class="wh-step">
            <div class="wh-step-num" aria-hidden="true">
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            </div>
            <h3>24/7 {city_e} Dispatch</h3>
            <p>Independent HVAC providers offering round-the-clock emergency response across the {city_e} metro &mdash; including weekends and holidays. Overnight surcharges are set by the individual provider.</p>
          </div>

          <div class="wh-step">
            <div class="wh-step-num" aria-hidden="true">
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
            </div>
            <h3>{city_e} Metro Coverage</h3>
            <p>Independent providers across major {city_e} neighborhoods, routed to your area by current availability. The full ZIP-level coverage detail is in the <a href="#services" style="color: var(--orange-dark); font-weight: 600;">Services &amp; service area</a> section below.</p>
          </div>

          <div class="wh-step">
            <div class="wh-step-num" aria-hidden="true">
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            </div>
            <h3>{license_h3}</h3>
            <p>{license_body}</p>
          </div>

        </div>
      </div>
    </section>
'''


# ============================================================
# MAIN PAGE GENERATOR (CARD-DRIVEN LAYOUT)
# ============================================================

def generate_page(c, climate_type, nearby, absorbed_data, all_cities_lookup, state_info=None,
                  reviewed_iso=None, reviewed_readable=None):
    """Generate the new card-driven HTML for a city page."""
    profile = CLIMATE_PROFILES[climate_type]
    city = c['city']
    st = c['state']
    state_full = STATE_FULL.get(st, st)
    slug = city_slug(city, st)
    s_slug = state_slug(st)
    pop = c.get('pop') or 0
    pop_str = f"{pop:,}" if pop else "many"
    summer_high = c.get('summer_high') or ""
    winter_low = c.get('winter_low') or ""
    ac_cost = c['ac_cost']
    furnace_cost = c['furnace_cost']
    permit = c['permit']
    utility = c['utility']
    seer = c['seer']
    rebates = c['rebates']
    license_req = c['license']
    climate_zone = c['climate']
    zips = c['zips']

    # Escaped versions
    e_city = escape(city)
    e_st = escape(st)
    e_state = escape(state_full)
    e_ac = escape(ac_cost)
    e_furnace = escape(furnace_cost)
    e_permit = escape(permit)
    e_utility = escape(utility)
    e_seer = escape(seer)
    e_rebates = escape(rebates)
    e_climate = escape(climate_zone)

    # Title (≤60 chars, climate-aware)
    title_svc = profile['title_service']
    title_text = f"24/7 {title_svc} in {e_city}, {e_st} | Cool Call Pro"
    if len(title_text.replace("&amp;", "&")) > 60:
        title_text = f"HVAC Repair in {e_city}, {e_st} | Cool Call Pro"

    # Meta description (≤155 chars)
    meta_svc = profile['meta_desc_service']
    meta_desc = f"Need {meta_svc} in {e_city}, {e_st}? Cool Call Pro connects you 24/7. Call (844) 582-1795."

    # FAQ schema fields
    permit_faq_q = profile['permit_faq_q']
    cost_faq_q = profile['cost_faq_q']
    license_faq_html = license_faq_sentence(c, html=True)
    license_faq_plain = license_faq_sentence(c, html=False).replace('"', '\\"')
    schema_cost_text = schema_cost_faq_text(city, ac_cost, furnace_cost, climate_type)

    # ZIP coverage for FAQ (include absorbed if metro anchor)
    all_zips = zips
    if absorbed_data:
        for ac in absorbed_data:
            all_zips += ", " + ac['zips']
        zip_list = [z.strip() for z in all_zips.split(",")]
        all_zips = ", ".join(zip_list[:7])
    e_all_zips = escape(all_zips)

    # Last reviewed
    if not reviewed_iso or not reviewed_readable:
        today = date.today()
        reviewed_iso = today.isoformat()
        reviewed_readable = today.strftime("%B %-d, %Y") if os.name != 'nt' else today.strftime("%B %#d, %Y")
    meta_block = page_meta_html(reviewed_iso, reviewed_readable)

    # Service-zip JSON for schema (first 5 ZIPs only)
    service_zip_list = [z.strip() for z in zips.split(",") if z.strip()][:5]
    service_zip_json = ", ".join(f'"{z}"' for z in service_zip_list)

    # areaServed schema
    if absorbed_data:
        areas = [f'''{{
            "@type": "City",
            "name": "{city}",
            "containedInPlace": {{ "@type": "State", "name": "{state_full}" }}
          }}''']
        for ac in absorbed_data:
            areas.append(f'''{{
            "@type": "City",
            "name": "{ac['city']}",
            "containedInPlace": {{ "@type": "State", "name": "{state_full}" }}
          }}''')
        area_served_schema = '"areaServed": [\n          ' + ',\n          '.join(areas) + '\n          ]'
    else:
        area_served_schema = f'''"areaServed": {{
            "@type": "City",
            "name": "{city}",
            "containedInPlace": {{
              "@type": "State",
              "name": "{state_full}"
            }}
          }}'''

    service_schema = f''',
      {{
        "@type": "Service",
        "serviceType": "HVAC Repair and Installation Referral",
        "provider": {{
          "@type": "Organization",
          "name": "Cool Call Pro",
          "telephone": "+1-844-582-1795",
          "url": "https://coolcallpro.com"
        }},
        "areaServed": {{
          "@type": "City",
          "name": "{city}",
          "containedInPlace": {{ "@type": "State", "name": "{state_full}" }},
          "postalCode": [{service_zip_json}]
        }},
        "audience": {{ "@type": "Audience", "audienceType": "Homeowners" }}
      }}'''

    # ============================================================
    # BUILD SECTION HTML BLOCKS
    # ============================================================

    subhead = hero_subhead(climate_type, summer_high, winter_low)

    # Section 3: Emergency lane cards
    emergency_cards = emergency_cards_for_climate(climate_type, e_city, summer_high, winter_low)
    emergency_cards_html = "\n          ".join(emergency_cards)

    # Section 4: Trust strip (built as full <section>)
    trust_html = trust_strip_section(c, climate_type, state_info)

    # Section 5: Climate Profile + photo
    climate_h2 = climate_h2_text(c, climate_type)
    climate_intro_p = climate_profile_intro(c, climate_type)
    stat_cards_html = climate_stat_cards(c, climate_type)
    figure_html = inline_location_figure(slug, city, st)
    article_href, article_text = CLIMATE_ARTICLE_LINKS[climate_type]

    # Section 6: Local data 2x2 — primary-source content parsed from xlsx col 17
    intro_callout = local_data_intro_callout(c)
    data_cards, fallback_count = local_data_cards_from_context(c, state_info)
    if fallback_count:
        print(f"    [local-data] {city}, {st}: {fallback_count}/4 cards fell back to generic prose")
    data_cards_html = "\n            ".join(data_cards)
    warning_callout = local_data_warning_callout()

    # Section 7: Services + Coverage
    services_card, zips_card = services_and_coverage_cards(c, climate_type, slug, all_zips)

    # Section 8: Mid-page CTA band
    midpage_html = midpage_cta(c, climate_type)

    # Optional: Also-serving metro section (if anchor city)
    also_serving_html = also_serving_section_cards(city, absorbed_data)

    # Nearby
    nearby_html = ""
    for nc_name, nc_st, nc_slug in nearby:
        nearby_html += f'            <li><a href="{nc_slug}">{escape(nc_name)}, {escape(nc_st)}</a></li>\n'
    nearby_html += f'            <li><a href="{s_slug}">{e_state} HVAC Guide &#8594;</a></li>\n'
    nearby_html += f'            <li><a href="../locations">View all HVAC service areas &#8594;</a></li>\n'

    # ============================================================
    # ASSEMBLE FINAL HTML
    # ============================================================

    html = f'''<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title_text}</title>
  <meta name="description"
    content="{meta_desc}" />
  <link rel="canonical" href="https://coolcallpro.com/locations/{slug}" />

  <!-- Open Graph -->
  <meta property="og:type" content="website" />
  <meta property="og:title" content="{title_text}" />
  <meta property="og:description" content="Connect with independent HVAC professionals in {e_city}, {e_state}. {profile['og_service']}" />
  <meta property="og:url" content="https://coolcallpro.com/locations/{slug}" />
  <meta property="og:site_name" content="Cool Call Pro" />
  <meta property="og:image" content="https://coolcallpro.com/images/og-homepage.webp" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="24/7 {title_svc} in {e_city}, {e_st}" />
  <meta name="twitter:description" content="Connect with independent HVAC professionals in {e_city}, {e_state}." />
  <meta name="twitter:image" content="https://coolcallpro.com/images/og-homepage.webp" />

  <!-- Favicon -->
  <link rel="icon" href="/favicon.ico" type="image/x-icon" />
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />

  <link rel="stylesheet" href="../css/style.min.css" />
  <link rel="preload" href="/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/fonts/outfit-latin.woff2" as="font" type="font/woff2" crossorigin>

  <!-- Google tag (gtag.js) - GA4 — deferred until first interaction for LCP -->
  <script>
    (function() {{
      var loaded = false;
      function loadGA() {{
        if (loaded) return;
        loaded = true;
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
      }}
      ['click', 'scroll', 'touchstart', 'keydown'].forEach(function(evt) {{
        window.addEventListener(evt, loadGA, {{ once: true, passive: true }});
      }});
      setTimeout(loadGA, 4000);
    }})();
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
          {{"@type": "ListItem", "position": 3, "name": "{state_full}", "item": "https://coolcallpro.com/locations/{s_slug}"}},
          {{"@type": "ListItem", "position": 4, "name": "{city}, {st}", "item": "https://coolcallpro.com/locations/{slug}"}}
        ]
      }},
      {{
        "@type": "FAQPage",
        "mainEntity": [
          {{
            "@type": "Question",
            "name": "{permit_faq_q} in {city}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Yes, ensure your contractor files a mechanical permit with the {permit}."
            }}
          }},
          {{
            "@type": "Question",
            "name": "Are there HVAC rebates in {city}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "{city} homeowners served by {utility} may qualify for rebates through {rebates}. The federal Section 25C tax credit was terminated for installations placed in service after Dec 31, 2025 (OBBBA, P.L. 119-21); check current state HEAR rebates and utility programs for what's still available in 2026."
            }}
          }},
          {{
            "@type": "Question",
            "name": "What ZIP codes do you serve in {city}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Our network covers {city} and surrounding areas including {zips}. Call (844) 582-1795 to verify service availability for your specific ZIP code."
            }}
          }},
          {{
            "@type": "Question",
            "name": "{cost_faq_q} in {city}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "{schema_cost_text}"
            }}
          }},
          {{
            "@type": "Question",
            "name": "What HVAC license is required in {state_full}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "{license_faq_plain} Always verify your contractor credentials before authorizing work."
            }}
          }}
        ]
      }},
      {{
        "@type": "Organization",
        "name": "Cool Call Pro",
        "url": "https://coolcallpro.com",
        "description": "24/7 referral service connecting homeowners with independent HVAC professionals in {city}, {st}.",
        "contactPoint": {{
          "@type": "ContactPoint",
          "telephone": "+1-844-582-1795",
          "contactType": "customer service",
          {area_served_schema},
          "availableLanguage": "English"
        }}
      }}{service_schema}
    ]
  }}
  </script>

  <style>
    @font-face{{font-family:'Inter';font-style:normal;font-weight:400 900;font-display:swap;src:url('/fonts/inter-latin.woff2') format('woff2')}}@font-face{{font-family:'Outfit';font-style:normal;font-weight:400 800;font-display:swap;src:url('/fonts/outfit-latin.woff2') format('woff2')}}
    .city-hero {{
      background: linear-gradient(135deg, var(--navy-deep) 0%, var(--navy) 50%, var(--navy-mid) 100%);
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
      max-width: 720px;
      margin: 0 auto;
      opacity: 0.9;
      line-height: 1.7;
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
    .city-faq {{
      max-width: 760px;
      margin: 0 auto 48px;
    }}
    .city-faq h2 {{
      font-size: 1.6rem;
      margin-bottom: 20px;
      color: var(--navy);
    }}
    @media (max-width: 768px) {{
      .city-hero {{
        padding: 80px 0 60px;
      }}
      .city-hero h1 {{
        font-size: 1.8rem;
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
      <a href="../index" class="logo">
        <span class="logo-icon">&#10052;&#65039;</span>
        <span class="logo-text">CoolCall<span class="logo-accent">Pro</span></span>
      </a>
      <ul class="nav-links" id="navLinks">
        <li><a href="../emergency" class="nav-link emergency-link">&#128680; Emergency Service</a></li>
        <li><a href="../costs" class="nav-link">Cost Guide</a></li>
        <li><a href="../safety" class="nav-link">Safety Tips</a></li>
        <li><a href="../locations" class="nav-link active">&#128205; Locations</a></li>
        <li><a href="../articles" class="nav-link">Articles</a></li>
        <li><a href="../about" class="nav-link">About</a></li>
        <li><a href="../contact" class="nav-link">Contact</a></li>
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
        <span class="section-tag" style="background: rgba(255,255,255,0.1); color: #fff;">&#128205; {e_city}, {e_st}</span>
        <h1>{profile['h1_service']} in {e_city}, {e_st}</h1>
        <p>{subhead}</p>
        {meta_block}
        <div style="margin-top: 28px;">
          <a href="tel:+18445821795" class="btn btn-primary btn-lg btn-vibrate"><span class="phone-icon">&#128222;</span> Call Now &#8212; (844) 582-1795</a>
        </div>
        <div class="jump-links" style="margin-top: 16px;">
          <a href="#services" class="jump-link" style="color: rgba(255,255,255,0.8);">Services</a>
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
            <li><a href="../index">Home</a></li>
            <li><a href="../locations">Locations</a></li>
            <li><a href="{s_slug}">{e_state}</a></li>
            <li aria-current="page">{e_city}, {e_st}</li>
          </ol>
        </nav>
      </div>
    </div>

    <!-- EMERGENCY LANE -->
    <section class="section" style="padding: 72px 0 64px; background:#fff;" id="emergency-lane">
      <div class="container">
        <div style="text-align:center; margin-bottom: 36px;">
          {emergency_pill()}
          <h2 style="font-size: 1.75rem; color: var(--navy); margin: 0 0 22px;">Common {e_city} HVAC emergencies</h2>
          <a href="tel:+18445821795" class="btn btn-primary btn-lg btn-vibrate"><span class="phone-icon">&#128222;</span> Call Now &mdash; (844) 582-1795</a>
          <p style="font-size: 0.9rem; color: var(--gray-500); margin: 12px 0 0;">24/7 dispatch &middot; {e_city}-area network</p>
        </div>

        <div class="precaution-cards" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; max-width: 1100px; margin: 0 auto; align-items: stretch;">

          {emergency_cards_html}

        </div>
      </div>
    </section>
{trust_html}
    <!-- CLIMATE + PHOTO (combined section, white background) -->
    <section class="section" style="padding: 72px 0; background:#fff;">
      <div class="container">
        <div style="max-width: 1100px; margin: 0 auto;">
          <div style="text-align:center; margin-bottom: 36px;">
            {climate_pill()}
            <h2 style="font-size: 1.75rem; color: var(--navy); margin: 0 0 14px;">{climate_h2}</h2>
            <p style="max-width: 720px; margin: 0 auto; font-size: 1.05rem; color: var(--gray-700); line-height: 1.7;">{climate_intro_p}</p>
          </div>

          <div class="precaution-cards" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 40px;">
            {stat_cards_html}
          </div>

          {figure_html}

          <p style="text-align:center; font-size: 0.92rem; color: var(--gray-500); margin-top: 24px;">Read our guide on <a href="{article_href}" style="color: var(--orange-dark); font-weight: 600;">{article_text}</a>.</p>
        </div>
      </div>
    </section>

    <!-- LOCAL DATA 2x2 CARD GRID -->
    <section class="section" id="local-data" style="padding: 72px 0; background: var(--gray-50);">
      <div class="container">
        <div style="max-width: 1100px; margin: 0 auto;">
          <div style="text-align:center; margin-bottom: 32px;">
            {localdata_pill()}
            <h2 style="font-size: 1.75rem; color: var(--navy); margin: 0;">HVAC in {e_city}, {e_st}: local data &amp; sources</h2>
          </div>

          {intro_callout}

          <div class="precaution-cards" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 20px; align-items: stretch;">

            {data_cards_html}

          </div>

          {warning_callout}
        </div>
      </div>
    </section>

    <!-- SERVICES + ZIPS 2-COLUMN ROW -->
    <section class="section" id="services" style="padding: 72px 0; background:#fff;">
      <div class="container">
        <div style="text-align:center; margin-bottom: 36px;">
          {services_pill()}
          <h2 style="font-size: 1.75rem; color: var(--navy); margin: 0;">Services &amp; service area</h2>
        </div>
        <div class="precaution-cards" style="max-width: 1000px; margin: 0 auto; display:grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 20px; align-items: stretch;">

          {services_card}

          {zips_card}

        </div>
      </div>
    </section>
{midpage_html}{also_serving_html}
    <!-- FAQs -->
    <section class="section" id="faqs" style="padding: 72px 0; background:#fff;">
      <div class="container" style="max-width: 800px;">
        <div class="city-faq" style="text-align:center; margin-bottom: 36px;">
          {faq_pill()}
          <h2 style="font-size: 1.75rem; color: var(--navy); margin: 0;">Frequently Asked Questions &mdash; {e_city}, {e_st}</h2>
        </div>
        <div class="city-faq">
          <div class="faq-list" style="margin-top: 24px;">
            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>{permit_faq_q} in {e_city}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>Yes, ensure your contractor files a mechanical permit with the <strong>{e_permit}</strong>. Pulling the correct permits protects you as a homeowner and ensures work is inspected to code.</p>
                </div>
              </div>
            </div>

            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>Are there HVAC rebates in {e_city}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>Homeowners may qualify for savings through <strong>{e_utility}</strong>. Check with <strong>{e_rebates}</strong> for current offers. The federal Section 25C credit was terminated for installations after Dec 31, 2025 (OBBBA, P.L. 119-21); check current state and utility programs for 2026.</p>
                </div>
              </div>
            </div>

            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>What ZIP codes do you serve in {e_city}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>Our network covers {e_city} and surrounding areas including <strong>{e_all_zips}</strong>. Call <a href="tel:+18445821795" style="color: var(--orange-dark); font-weight: 600;">(844) 582-1795</a> to verify service availability for your specific ZIP code.</p>
                </div>
              </div>
            </div>

            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>{cost_faq_q} in {e_city}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>A standard AC replacement in {e_city} typically costs <strong>{e_ac}</strong>, and furnace installations run <strong>{e_furnace}</strong>. Costs vary based on system size, efficiency rating, and installation complexity. In {e_state}, new AC units must meet a minimum <strong>{e_seer}</strong> rating.</p>
                </div>
              </div>
            </div>

            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>What HVAC license is required in {e_state}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>{license_faq_html} Always verify your contractor's credentials before authorizing work. For {e_city} residents, permits are filed through the <strong>{e_permit}</strong>.</p>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </section>

    <!-- Nearby Service Areas -->
    <section class="section" style="padding: 72px 0; background: var(--gray-50);">
      <div class="container" style="max-width: 800px;">
        <div class="city-services">
          <h2 style="text-align:center;">Nearby HVAC Service Areas</h2>
          <ul>
{nearby_html}          </ul>
        </div>

        <!-- Sources & References (E-E-A-T) -->
        <div class="city-sources">
          <h3>Sources &amp; References</h3>
          <ul>
            <li><a href="https://www.energy.gov/energysaver/heat-and-cool" target="_blank" rel="nofollow noopener">U.S. Department of Energy &mdash; Home Heating &amp; Cooling</a></li>
            <li><a href="https://www.energystar.gov/" target="_blank" rel="nofollow noopener">U.S. ENERGY STAR (EPA)</a></li>
            <li><a href="https://www.dsireusa.org/" target="_blank" rel="nofollow noopener">DSIRE Database of State Incentives</a></li>
            <li><a href="https://www.irs.gov/credits-deductions/energy-efficient-home-improvement-credit" target="_blank" rel="nofollow noopener">IRS Section 25C Energy Efficient Home Improvement Credit</a></li>
          </ul>
        </div>
      </div>
    </section>

  </main>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <a href="../index" class="logo"><span class="logo-icon">&#10052;&#65039;</span><span
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
            <li><a href="../costs">Cost Guide</a></li>
            <li><a href="../emergency">Emergency Service</a></li>
            <li><a href="../safety">Safety Tips</a></li>
            <li><a href="../articles">All Articles</a></li>
            <li><a href="../locations">Locations</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3 class="footer-heading">Company</h3>
          <ul>
            <li><a href="../about">About Us</a></li>
            <li><a href="../contact">Contact</a></li>
            <li><a href="../author-gyanesh">Author</a></li>
            <li><a href="../privacy">Privacy Policy</a></li>
            <li><a href="../advertising-disclosure">Advertising Disclosure</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3 class="footer-heading">Service Areas</h3>
          <ul class="service-areas">
            <li><a href="atlanta-ga">Atlanta, GA</a></li>
            <li><a href="chicago-il">Chicago, IL</a></li>
            <li><a href="dallas-tx">Dallas, TX</a></li>
            <li><a href="houston-tx">Houston, TX</a></li>
            <li><a href="phoenix-az">Phoenix, AZ</a></li>
            <li><a href="../locations">All 50 states &#8594;</a></li>
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
        <p>&copy; <span class="copyright-year">2026</span> Cool Call Pro. All rights reserved. &nbsp;&#183;&nbsp; <a href="../privacy">Privacy
            Policy</a> &nbsp;&#183;&nbsp; <a href="../terms">Terms of Use</a> &nbsp;&#183;&nbsp; <a
            href="../disclaimer">Disclaimer</a> &nbsp;&#183;&nbsp; <a href="../advertising-disclosure">Advertising
            Disclosure</a> &nbsp;&#183;&nbsp; <a href="../image-credits">Image Credits</a></p>
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

    return html


# ============================================================
# MAIN ENTRYPOINT
# ============================================================

def main():
    import argparse
    from collections import defaultdict

    parser = argparse.ArgumentParser(description="Generate city pages v4 (card-driven layout)")
    parser.add_argument('--batch', type=int, help="Batch number (1=high priority)")
    parser.add_argument('--city', type=str, help="Generate single city by name")
    parser.add_argument('--dry-run', action='store_true', help="Preview without writing")
    parser.add_argument('--force', action='store_true',
                        help="Regenerate pages even if already published (used for template overhauls)")
    parser.add_argument('--output-path', type=str, default=None,
                        help="Override the output path for a single --city run "
                             "(e.g. _pilot_test/phoenix-az.html)")
    parser.add_argument('--output-dir', type=str, default=None,
                        help="Override the output directory (default: locations/). "
                             "Useful for routing all generated pages to _pilot_test/.")
    args = parser.parse_args()

    cities, all_cities = load_cities()
    states_meta = load_states()

    # Group by state for nearby logic
    by_state = defaultdict(list)
    for c in all_cities:
        if c['city'] not in REMOVED_CITIES and c['city'] not in ABSORBED:
            by_state[c['state']].append(c)

    force_targets = None
    if args.city:
        targets = [args.city]
    elif args.batch == 1:
        targets = BATCH_1
    elif args.batch == 2:
        targets = BATCH_2
    elif args.force:
        force_targets = [c for c in all_cities
                         if c['city'] not in REMOVED_CITIES
                         and c['city'] not in ABSORBED]
        targets = []
    else:
        targets = [c['city'] for c in all_cities
                   if c['city'] not in PUBLISHED_CITIES
                   and c['city'] not in REMOVED_CITIES
                   and c['city'] not in ABSORBED]

    output_dir = args.output_dir or OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    generated = 0
    skipped = 0
    errors = []

    if force_targets is not None:
        iter_list = [(c['city'], c) for c in force_targets]
    else:
        iter_list = []
        for city_name in targets:
            if city_name not in cities:
                errors.append(f"City '{city_name}' not found in xlsx")
                continue
            iter_list.append((city_name, cities[city_name]))

    for city_name, c in iter_list:
        # When --output-path or --output-dir is explicitly set, treat the run
        # as a manual regeneration -- ignore the PUBLISHED_CITIES skip list.
        force_pilot = bool(args.output_path or args.output_dir)
        if (city_name in PUBLISHED_CITIES and not args.force and not args.city
                and not force_pilot):
            print(f"  SKIP (already published): {city_name}")
            skipped += 1
            continue

        if city_name in ABSORBED:
            print(f"  SKIP (absorbed into {ABSORBED[city_name]}): {city_name}")
            skipped += 1
            continue

        if city_name in REMOVED_CITIES:
            print(f"  SKIP (removed - too small): {city_name}")
            skipped += 1
            continue

        climate_type = get_climate_type(city_name, c['climate'])

        absorbed_data = []
        if city_name in ANCHOR_ABSORBS:
            for abs_name in ANCHOR_ABSORBS[city_name]:
                if abs_name in cities:
                    absorbed_data.append(cities[abs_name])

        nearby = get_nearby_cities(c, by_state, cities)
        state_info = states_meta.get(c['state'])
        html = generate_page(c, climate_type, nearby, absorbed_data, cities, state_info=state_info)

        if args.output_path and args.city:
            filepath = args.output_path
            os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        else:
            slug = city_slug(city_name, c['state'])
            filepath = os.path.join(output_dir, f"{slug}.html")

        if args.dry_run:
            print(f"  DRY RUN: Would write {filepath} ({len(html)} chars) | climate={climate_type} | absorbed={len(absorbed_data)}")
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"  GENERATED: {filepath} | climate={climate_type} | absorbed={len(absorbed_data)} cities")

        generated += 1

    print(f"\n{'='*50}")
    print(f"Generated: {generated} | Skipped: {skipped} | Errors: {len(errors)}")
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")


if __name__ == "__main__":
    main()
