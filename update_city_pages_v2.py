"""
update_city_pages_v2.py — Programmatic SEO overhaul for HVAC city pages
Implements all 7 fixes from the QC plan (16 March 2026):
  1. Replace LocalBusiness schema with Organization
  2. Rewrite opening paragraph (add Population, referral language)
  3. Remove fluff from Rebates paragraph
  4. Add H2 heading for climate paragraph
  5. Vary services list by climate zone
  6. Internal linking (locations + articles + hub)
  7. Expand FAQs from 3 to 5

Reads from cities_updated.xlsx directly. Generates full HTML pages.
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCATIONS_DIR = os.path.join(BASE_DIR, "locations")

# ─── City Data (all 16 columns from cities_updated.xlsx) ─────────────────────

CITIES = {
    "atlanta-ga": {
        "city": "Atlanta", "state": "GA", "state_full": "Georgia",
        "ac_cost": "$4,000\u2013$7,800", "furnace_cost": "$3,200\u2013$6,200",
        "neighborhoods": "Buckhead, Druid Hills, Ansley Park, Morningside-Lenox Park, Virginia-Highland",
        "zips": "30305, 30306, 30309, 30307, 30319",
        "permit_office": "City of Atlanta Office of Buildings (Dept. of City Planning)",
        "utility": "Georgia Power",
        "population": "520,070",
        "avg_summer_high": "89", "avg_winter_low": "34",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility_rebates": "Georgia Power Home Energy Improvement Program (HEIP)",
        "license_req": "Conditioned Air Contractor License (Class I or II)",
        "climate_zone": "Zone 3A (Warm-Humid)",
        "climate_type": "mixed-humid",
        "hero_image": "mixed-humid-climate-hvac-atlanta-hero.webp",
        "hero_alt": "Year-round HVAC solutions for mixed-humid climate with seasonal temperature swings",
    },
    "birmingham-al": {
        "city": "Birmingham", "state": "AL", "state_full": "Alabama",
        "ac_cost": "$3,800\u2013$6,500", "furnace_cost": "$3,000\u2013$5,500",
        "neighborhoods": "Homewood, Vestavia Hills, Highland Park, Avondale, Crestwood",
        "zips": "35209, 35216, 35205, 35222, 35210",
        "permit_office": "City of Birmingham Dept. of Planning, Engineering & Permits",
        "utility": "Alabama Power",
        "population": "196,357",
        "avg_summer_high": "91", "avg_winter_low": "35",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility_rebates": "Alabama Power Heat Pump Loan Program",
        "license_req": "Heating & Air Conditioning Contractor License",
        "climate_zone": "Zone 3A (Warm-Humid)",
        "climate_type": "mixed-humid",
        "hero_image": "mixed-humid-climate-hvac-atlanta-hero.webp",
        "hero_alt": "Year-round HVAC solutions for mixed-humid climate with seasonal temperature swings",
    },
    "boston-ma": {
        "city": "Boston", "state": "MA", "state_full": "Massachusetts",
        "ac_cost": "$5,000\u2013$9,000", "furnace_cost": "$4,500\u2013$8,000",
        "neighborhoods": "West Roxbury, Dorchester, Jamaica Plain, Roslindale, Hyde Park",
        "zips": "02132, 02124, 02130, 02131, 02136",
        "permit_office": "City of Boston Inspectional Services Department (ISD)",
        "utility": "Eversource",
        "population": "673,600",
        "avg_summer_high": "82", "avg_winter_low": "23",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility_rebates": "Mass Save Heat Pump Rebates (up to $10,000)",
        "license_req": "No state HVAC license required; EPA 608 required",
        "climate_zone": "Zone 5A (Cool-Humid)",
        "climate_type": "cold",
        "hero_image": "cold-climate-furnace-minneapolis-hero.webp",
        "hero_alt": "High-efficiency furnace installation for cold climate winter protection",
    },
    "charlotte-nc": {
        "city": "Charlotte", "state": "NC", "state_full": "North Carolina",
        "ac_cost": "$3,800\u2013$7,500", "furnace_cost": "$3,000\u2013$6,000",
        "neighborhoods": "Myers Park, Dilworth, Ballantyne, Eastover, SouthPark",
        "zips": "28207, 28203, 28277, 28209, 28226",
        "permit_office": "Mecklenburg County Code Enforcement (LUESA)",
        "utility": "Duke Energy Carolinas",
        "population": "943,476",
        "avg_summer_high": "90", "avg_winter_low": "32",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility_rebates": "Duke Energy Smart $aver Program (up to $500/unit)",
        "license_req": "NC Heating & Cooling Contractor License (H1/H2/H3)",
        "climate_zone": "Zone 3A (Warm-Humid)",
        "climate_type": "mixed-humid",
        "hero_image": "mixed-humid-climate-hvac-atlanta-hero.webp",
        "hero_alt": "Year-round HVAC solutions for mixed-humid climate with seasonal temperature swings",
    },
    "chicago-il": {
        "city": "Chicago", "state": "IL", "state_full": "Illinois",
        "ac_cost": "$3,900\u2013$7,500", "furnace_cost": "$3,500\u2013$7,000",
        "neighborhoods": "Beverly, Edison Park, Portage Park, Lincoln Square, Bridgeport",
        "zips": "60634, 60618, 60643, 60625, 60632",
        "permit_office": "Chicago Department of Buildings",
        "utility": "ComEd (Commonwealth Edison)",
        "population": "2,719,365",
        "avg_summer_high": "84", "avg_winter_low": "17",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility_rebates": "ComEd Heat Pump Rebates ($1,400\u2013$2,075); Peoples Gas Rebates",
        "license_req": "No statewide license; Chicago requires General Contractor License",
        "climate_zone": "Zone 5A (Cool-Humid)",
        "climate_type": "cold",
        "hero_image": "cold-climate-furnace-minneapolis-hero.webp",
        "hero_alt": "High-efficiency furnace installation for cold climate winter protection",
    },
    "dallas-tx": {
        "city": "Dallas", "state": "TX", "state_full": "Texas",
        "ac_cost": "$4,500\u2013$12,000", "furnace_cost": "$3,000\u2013$6,500",
        "neighborhoods": "Highland Park, Lakewood, Preston Hollow, M Streets (Greenland Hills), Lake Highlands",
        "zips": "75205, 75214, 75230, 75225, 75238",
        "permit_office": "City of Dallas Building Inspection Division",
        "utility": "Oncor Electric Delivery (TDU)",
        "population": "1,326,087",
        "avg_summer_high": "96", "avg_winter_low": "38",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility_rebates": "Oncor Take a Load Off Texas Program (up to $3,400)",
        "license_req": "TX TDLR Air Conditioning & Refrigeration Contractor License",
        "climate_zone": "Zone 3A (Warm-Humid)",
        "climate_type": "mixed-humid",
        "hero_image": "mixed-humid-climate-hvac-atlanta-hero.webp",
        "hero_alt": "Year-round HVAC solutions for mixed-humid climate with seasonal temperature swings",
    },
    "denver-co": {
        "city": "Denver", "state": "CO", "state_full": "Colorado",
        "ac_cost": "$4,000\u2013$8,000", "furnace_cost": "$3,500\u2013$7,500",
        "neighborhoods": "Washington Park, Cherry Creek, Hilltop, Congress Park, Park Hill",
        "zips": "80209, 80206, 80220, 80210, 80218",
        "permit_office": "Denver Community Planning and Development (CPD)",
        "utility": "Xcel Energy",
        "population": "729,019",
        "avg_summer_high": "90", "avg_winter_low": "18",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility_rebates": "Xcel Energy Whole Home Efficiency Program ($2,250/ton)",
        "license_req": "No statewide HVAC license required",
        "climate_zone": "Zone 5B (Cold-Dry)",
        "climate_type": "mountain",
        "hero_image": "mountain-climate-hvac-denver-hero.webp",
        "hero_alt": "High-altitude HVAC system engineered for mountain climate conditions",
    },
    "detroit-mi": {
        "city": "Detroit", "state": "MI", "state_full": "Michigan",
        "ac_cost": "$3,900\u2013$7,500", "furnace_cost": "$3,500\u2013$7,000",
        "neighborhoods": "Indian Village, University District, Boston-Edison, Rosedale Park, Palmer Park",
        "zips": "48221, 48224, 48219, 48235, 48227",
        "permit_office": "Detroit BSEED (Buildings, Safety Engineering & Environmental Dept.)",
        "utility": "DTE Energy",
        "population": "645,705",
        "avg_summer_high": "83", "avg_winter_low": "19",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility_rebates": "DTE Energy Heating & Cooling Program",
        "license_req": "MI Mechanical Contractor License (LARA)",
        "climate_zone": "Zone 5A (Cool-Humid)",
        "climate_type": "cold",
        "hero_image": "cold-climate-furnace-minneapolis-hero.webp",
        "hero_alt": "High-efficiency furnace installation for cold climate winter protection",
    },
    "houston-tx": {
        "city": "Houston", "state": "TX", "state_full": "Texas",
        "ac_cost": "$4,500\u2013$12,000", "furnace_cost": "$3,000\u2013$6,000",
        "neighborhoods": "The Heights, West University Place, Meyerland, Oak Forest, Tanglewood",
        "zips": "77024, 77005, 77019, 77007, 77008",
        "permit_office": "Houston Permitting Center",
        "utility": "CenterPoint Energy",
        "population": "2,390,125",
        "avg_summer_high": "95", "avg_winter_low": "43",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility_rebates": "CenterPoint Energy Standard Offer Program (up to $500/unit)",
        "license_req": "TX TDLR Air Conditioning & Refrigeration Contractor License",
        "climate_zone": "Zone 2A (Hot-Humid)",
        "climate_type": "hot-humid",
        "hero_image": "hot-humid-climate-hvac-houston-hero.webp",
        "hero_alt": "Professional HVAC installation for hot-humid climate homes with humidity control",
    },
    "kansas-city-mo": {
        "city": "Kansas City", "state": "MO", "state_full": "Missouri",
        "ac_cost": "$3,800\u2013$7,200", "furnace_cost": "$3,000\u2013$6,200",
        "neighborhoods": "Brookside, Waldo, Ward Parkway, Sunset Hill, Armour Hills",
        "zips": "64112, 64113, 64114, 64151, 64155",
        "permit_office": "Kansas City Planning & Development \u2013 Permits Division",
        "utility": "Evergy",
        "population": "516,032",
        "avg_summer_high": "90", "avg_winter_low": "22",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility_rebates": "Evergy FastTrack HVAC PAYS Program (~$1,000\u2013$1,300)",
        "license_req": "No statewide license; KC requires municipal trade license",
        "climate_zone": "Zone 4A (Mixed-Humid)",
        "climate_type": "cold",
        "hero_image": "cold-climate-furnace-minneapolis-hero.webp",
        "hero_alt": "High-efficiency furnace installation for cold climate winter protection",
    },
    "las-vegas-nv": {
        "city": "Las Vegas", "state": "NV", "state_full": "Nevada",
        "ac_cost": "$4,500\u2013$8,000", "furnace_cost": "$3,000\u2013$5,500",
        "neighborhoods": "Summerlin, Spring Valley, Centennial Hills, Lone Mountain, Southwest Las Vegas",
        "zips": "89134, 89135, 89148, 89117, 89147",
        "permit_office": "City of Las Vegas Building & Safety Department",
        "utility": "NV Energy",
        "population": "678,922",
        "avg_summer_high": "105", "avg_winter_low": "40",
        "seer_minimum": "SEER2 14.3 + EER2 11.7 (Southwest Region)",
        "utility_rebates": "NV Energy AC Rebates",
        "license_req": "NV C-21 Refrigeration & Air Conditioning License",
        "climate_zone": "Zone 3B (Warm-Dry)",
        "climate_type": "hot-dry",
        "hero_image": "desert-climate-hvac-phoenix-hero.webp",
        "hero_alt": "Desert climate AC system designed for extreme Southwest heat",
    },
    "milwaukee-wi": {
        "city": "Milwaukee", "state": "WI", "state_full": "Wisconsin",
        "ac_cost": "$3,800\u2013$7,200", "furnace_cost": "$3,000\u2013$6,500",
        "neighborhoods": "Bay View, Sherman Park, Washington Heights, Enderis Park, Wauwatosa East",
        "zips": "53207, 53210, 53213, 53208, 53215",
        "permit_office": "Milwaukee Dept. of Neighborhood Services (DNS)",
        "utility": "We Energies",
        "population": "561,385",
        "avg_summer_high": "81", "avg_winter_low": "16",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility_rebates": "Focus on Energy / We Energies HVAC Rebates",
        "license_req": "No mandatory statewide license; optional HVAC Qualifier cert",
        "climate_zone": "Zone 5A (Cool-Humid)",
        "climate_type": "cold",
        "hero_image": "cold-climate-furnace-minneapolis-hero.webp",
        "hero_alt": "High-efficiency furnace installation for cold climate winter protection",
    },
    "minneapolis-mn": {
        "city": "Minneapolis", "state": "MN", "state_full": "Minnesota",
        "ac_cost": "$4,000\u2013$7,500", "furnace_cost": "$3,200\u2013$6,800",
        "neighborhoods": "Longfellow, Powderhorn, Nokomis, Northeast, Southwest/Linden Hills",
        "zips": "55406, 55407, 55417, 55418, 55410",
        "permit_office": "City of Minneapolis CPED (Community Planning & Economic Development)",
        "utility": "Xcel Energy",
        "population": "428,579",
        "avg_summer_high": "83", "avg_winter_low": "9",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility_rebates": "Xcel Energy / CEE HVAC Rebates",
        "license_req": "No state license; $25,000 surety bond required",
        "climate_zone": "Zone 6A (Cold-Humid)",
        "climate_type": "cold",
        "hero_image": "cold-climate-furnace-minneapolis-hero.webp",
        "hero_alt": "High-efficiency furnace installation for cold climate winter protection",
    },
    "new-orleans-la": {
        "city": "New Orleans", "state": "LA", "state_full": "Louisiana",
        "ac_cost": "$3,800\u2013$7,000", "furnace_cost": "$2,800\u2013$5,800",
        "neighborhoods": "Uptown, Lakeview, Garden District, Gentilly, Algiers Point",
        "zips": "70115, 70118, 70119, 70122, 70124",
        "permit_office": "City of New Orleans Dept. of Safety & Permits",
        "utility": "Entergy New Orleans",
        "population": "362,701",
        "avg_summer_high": "92", "avg_winter_low": "46",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility_rebates": "Entergy New Orleans Energy Smart Program (up to $500)",
        "license_req": "LA Mechanical Work Contractor License (LSLBC)",
        "climate_zone": "Zone 2A (Hot-Humid)",
        "climate_type": "hot-humid",
        "hero_image": "hot-humid-climate-hvac-houston-hero.webp",
        "hero_alt": "Professional HVAC installation for hot-humid climate homes with humidity control",
    },
    "oklahoma-city-ok": {
        "city": "Oklahoma City", "state": "OK", "state_full": "Oklahoma",
        "ac_cost": "$3,800\u2013$7,000", "furnace_cost": "$3,000\u2013$6,000",
        "neighborhoods": "Nichols Hills, Heritage Hills, Mesta Park, Quail Creek, Crown Heights-Edgemere Heights",
        "zips": "73104, 73112, 73116, 73120, 73142",
        "permit_office": "OKC Development Services Department",
        "utility": "OG&amp;E (Oklahoma Gas &amp; Electric)",
        "population": "712,919",
        "avg_summer_high": "93", "avg_winter_low": "27",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility_rebates": "OG&amp;E Residential Energy Efficiency Program (up to $3,000)",
        "license_req": "OK Mechanical Contractor License (HVAC/R)",
        "climate_zone": "Zone 3A (Warm-Humid)",
        "climate_type": "mixed-humid",
        "hero_image": "mixed-humid-climate-hvac-atlanta-hero.webp",
        "hero_alt": "Year-round HVAC solutions for mixed-humid climate with seasonal temperature swings",
    },
    "philadelphia-pa": {
        "city": "Philadelphia", "state": "PA", "state_full": "Pennsylvania",
        "ac_cost": "$4,500\u2013$8,500", "furnace_cost": "$4,000\u2013$7,500",
        "neighborhoods": "Chestnut Hill, Roxborough, Mayfair, Mount Airy, South Philadelphia (Passyunk/Girard Estate)",
        "zips": "19118, 19128, 19136, 19111, 19148",
        "permit_office": "Philadelphia Department of Licenses &amp; Inspections (L&amp;I)",
        "utility": "PECO Energy",
        "population": "1,573,916",
        "avg_summer_high": "88", "avg_winter_low": "26",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility_rebates": "PECO Energy Rebates; EAP Residential HVAC Rebate Program",
        "license_req": "No statewide license; Philadelphia requires city license",
        "climate_zone": "Zone 4A (Mixed-Humid)",
        "climate_type": "cold",
        "hero_image": "cold-climate-furnace-minneapolis-hero.webp",
        "hero_alt": "High-efficiency furnace installation for cold climate winter protection",
    },
    "phoenix-az": {
        "city": "Phoenix", "state": "AZ", "state_full": "Arizona",
        "ac_cost": "$4,500\u2013$8,000", "furnace_cost": "$3,000\u2013$5,500",
        "neighborhoods": "Arcadia, Biltmore, Paradise Valley Village, Camelback East, Ahwatukee Foothills",
        "zips": "85018, 85016, 85028, 85032, 85048",
        "permit_office": "City of Phoenix Planning &amp; Development Department",
        "utility": "APS / Salt River Project (SRP)",
        "population": "1,673,164",
        "avg_summer_high": "107", "avg_winter_low": "46",
        "seer_minimum": "SEER2 14.3 + EER2 11.7 (Southwest Region)",
        "utility_rebates": "SRP HVAC Rebates ($75\u2013$1,125/ton)",
        "license_req": "AZ ROC HVAC/R Contractor License",
        "climate_zone": "Zone 2B (Hot-Dry)",
        "climate_type": "hot-dry",
        "hero_image": "desert-climate-hvac-phoenix-hero.webp",
        "hero_alt": "Desert climate AC system designed for extreme Southwest heat",
    },
    "san-antonio-tx": {
        "city": "San Antonio", "state": "TX", "state_full": "Texas",
        "ac_cost": "$4,200\u2013$10,000", "furnace_cost": "$2,800\u2013$5,500",
        "neighborhoods": "Alamo Heights, Terrell Hills, Olmos Park, Stone Oak, King William",
        "zips": "78209, 78212, 78201, 78258, 78216",
        "permit_office": "City of San Antonio Development Services Department",
        "utility": "CPS Energy",
        "population": "1,526,656",
        "avg_summer_high": "96", "avg_winter_low": "39",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility_rebates": "CPS Energy STEP Home Energy Rebate Program",
        "license_req": "TX TDLR Air Conditioning &amp; Refrigeration Contractor License",
        "climate_zone": "Zone 2A (Hot-Humid)",
        "climate_type": "hot-humid",
        "hero_image": "hot-humid-climate-hvac-houston-hero.webp",
        "hero_alt": "Professional HVAC installation for hot-humid climate homes with humidity control",
    },
    "st-louis-mo": {
        "city": "St. Louis", "state": "MO", "state_full": "Missouri",
        "ac_cost": "$3,500\u2013$7,200", "furnace_cost": "$2,800\u2013$6,000",
        "neighborhoods": "Tower Grove South, South Hampton, Bevo Mill, Shaw, Holly Hills",
        "zips": "63116, 63109, 63110, 63118, 63104",
        "permit_office": "City of St. Louis Building Division (Dept. of Public Safety)",
        "utility": "Ameren Missouri",
        "population": "279,695",
        "avg_summer_high": "90", "avg_winter_low": "24",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility_rebates": "Ameren Missouri PAYS Program",
        "license_req": "No statewide license; St. Louis requires municipal license",
        "climate_zone": "Zone 4A (Mixed-Humid)",
        "climate_type": "mixed-humid",
        "hero_image": "mixed-humid-climate-hvac-atlanta-hero.webp",
        "hero_alt": "Year-round HVAC solutions for mixed-humid climate with seasonal temperature swings",
    },
    "tampa-fl": {
        "city": "Tampa", "state": "FL", "state_full": "Florida",
        "ac_cost": "$5,500\u2013$9,000", "furnace_cost": "$3,500\u2013$6,000",
        "neighborhoods": "Seminole Heights, South Tampa (Palma Ceia), Hyde Park, Tampa Heights, Westshore",
        "zips": "33604, 33609, 33606, 33611, 33629",
        "permit_office": "City of Tampa Construction Services Division",
        "utility": "Tampa Electric (TECO)",
        "population": "414,547",
        "avg_summer_high": "90", "avg_winter_low": "53",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility_rebates": "Tampa Electric (TECO) Heating &amp; Cooling Program",
        "license_req": "FL Certified Air Conditioning Contractor License (Class A/B)",
        "climate_zone": "Zone 2A (Hot-Humid)",
        "climate_type": "hot-humid",
        "hero_image": "hot-humid-climate-hvac-houston-hero.webp",
        "hero_alt": "Professional HVAC installation for hot-humid climate homes with humidity control",
    },
}

# ─── Related Cities (for internal linking, grouped by climate region) ─────────

RELATED_CITIES = {
    "hot-humid": ["houston-tx", "tampa-fl", "new-orleans-la", "san-antonio-tx"],
    "hot-dry": ["phoenix-az", "las-vegas-nv"],
    "mixed-humid": ["atlanta-ga", "birmingham-al", "charlotte-nc", "dallas-tx", "oklahoma-city-ok", "st-louis-mo"],
    "cold": ["chicago-il", "detroit-mi", "minneapolis-mn", "milwaukee-wi", "kansas-city-mo", "boston-ma", "philadelphia-pa"],
    "mountain": ["denver-co"],
}

# ─── Article Links by Climate Type ────────────────────────────────────────────

CLIMATE_ARTICLE_LINK = {
    "hot-humid": ('<a href="../article-ac-summer.html" style="color: var(--orange); font-weight: 600;">preparing your AC for summer</a>', "article-ac-summer"),
    "hot-dry": ('<a href="../article-spring-ac.html" style="color: var(--orange); font-weight: 600;">spring AC preparation</a>', "article-spring-ac"),
    "mixed-humid": ('<a href="../article-heat-pump.html" style="color: var(--orange); font-weight: 600;">heat pump options</a>', "article-heat-pump"),
    "cold": ('<a href="../article-furnace.html" style="color: var(--orange); font-weight: 600;">furnace troubleshooting</a>', "article-furnace"),
    "mountain": ('<a href="../article-winter-storm.html" style="color: var(--orange); font-weight: 600;">winter storm HVAC preparation</a>', "article-winter-storm"),
}


# ─── Content Generation Functions ─────────────────────────────────────────────

def get_opening_paragraph(d):
    """Fix 2: Opening paragraph with Population + referral language."""
    return (
        f'Serving <strong>{d["population"]}</strong> residents across <strong>{d["city"]}, {d["state_full"]}</strong>, '
        f'Cool Call Pro connects homeowners in <strong>{d["neighborhoods"]}</strong> with independent 24/7 HVAC technicians. '
        f'Our referral network covers <strong>{d["zips"]}</strong> and surrounding areas. '
        f'If your system is beyond repair, a standard AC replacement in the {d["city"]} area typically runs '
        f'<strong>{d["ac_cost"]}</strong>, and furnace installations average <strong>{d["furnace_cost"]}</strong>. '
        f'Your contractor should pull mechanical permits through the <strong>{d["permit_office"]}</strong>.'
    )


def get_climate_h2(d):
    """Fix 4: Climate-zone-specific H2."""
    ct = d["climate_type"]
    if ct == "hot-humid":
        return f'{d["city"]}\'s Hot-Humid Climate &amp; Your HVAC System'
    elif ct == "hot-dry":
        return f'Desert Heat &amp; HVAC Demands in {d["city"]}'
    elif ct == "mixed-humid":
        return f'Year-Round HVAC Demands in {d["city"]}, {d["state"]}'
    elif ct == "cold":
        return f'{d["city"]} Winters &amp; Heating Requirements'
    elif ct == "mountain":
        return f'High-Altitude HVAC Challenges in {d["city"]}'
    return f'HVAC Climate Considerations in {d["city"]}'


def get_climate_paragraph(d):
    """Climate context paragraph with inline article link."""
    ct = d["climate_type"]
    article_link = CLIMATE_ARTICLE_LINK[ct][0]

    if ct == "hot-humid":
        return (
            f'With summer highs averaging {d["avg_summer_high"]}\u00b0F and humidity levels that strain even the best systems, '
            f'{d["city"]} homeowners know their AC isn\'t optional. Winter lows rarely dip below {d["avg_winter_low"]}\u00b0F, '
            f'so heating costs stay manageable. As a {d["climate_zone"]} climate zone, federal regulations require all new AC units '
            f'meet a minimum {d["seer_minimum"]} rating, which translates to lower energy bills with {d["utility"]}. '
            f'Learn more about {article_link}.'
        )
    elif ct == "hot-dry":
        return (
            f'When {d["city"]} summers push past {d["avg_summer_high"]}\u00b0F, your air conditioner works harder than '
            f'almost anywhere else in the country. The desert climate means low humidity but extreme heat, making proper '
            f'system sizing critical. Located in {d["climate_zone"]}, all new installations must meet '
            f'{d["seer_minimum"]} efficiency standards. Winter lows around {d["avg_winter_low"]}\u00b0F still require '
            f'reliable heating. Read our guide on {article_link}.'
        )
    elif ct == "mixed-humid":
        return (
            f'{d["city"]}\'s {d["climate_zone"]} climate means your HVAC system earns its keep year-round\u2014'
            f'battling {d["avg_summer_high"]}\u00b0F summer heat and winter lows near {d["avg_winter_low"]}\u00b0F. '
            f'This dual demand makes efficiency crucial. All new systems must meet {d["seer_minimum"]} standards, and '
            f'{d["utility"]} serves as the primary utility provider. Explore {article_link} for your home.'
        )
    elif ct == "cold":
        return (
            f'{d["city"]} winters mean business, with temperatures plunging to {d["avg_winter_low"]}\u00b0F. '
            f'Your furnace isn\'t a luxury\u2014it\'s your lifeline. Located in {d["climate_zone"]}, '
            f'heating efficiency matters more here than almost anywhere. While summer highs reach '
            f'{d["avg_summer_high"]}\u00b0F, the real focus is reliable heating. '
            f'{d["utility"]} serves the area. See our guide on {article_link}.'
        )
    elif ct == "mountain":
        return (
            f'{d["city"]}\'s mile-high altitude creates unique HVAC challenges. Summer highs hit '
            f'{d["avg_summer_high"]}\u00b0F, but winter lows drop to {d["avg_winter_low"]}\u00b0F, and the thin air '
            f'affects equipment performance. As a {d["climate_zone"]} zone, you need contractors who understand '
            f'high-altitude installations. {d["utility"]} serves the area. Read about {article_link}.'
        )
    return ""


def get_services_list(d):
    """Fix 5: Climate-zone-varied services list."""
    ct = d["climate_type"]
    city = d["city"]
    if ct == "hot-humid":
        return [
            f"Emergency AC Repair in {city}",
            "Humidity Control &amp; Dehumidification",
            "Central AC Installation &amp; Replacement",
            "HVAC System Maintenance &amp; Tune-Ups",
            "Ductwork Inspection, Cleaning &amp; Mold Prevention",
        ]
    elif ct == "hot-dry":
        return [
            f"Emergency AC Repair in {city}",
            f"Central AC Installation &amp; Replacement in {city}",
            "HVAC System Maintenance &amp; Tune-Ups",
            "Ductwork Sealing &amp; Insulation",
            "Thermostat &amp; Smart Home Integration",
        ]
    elif ct == "mixed-humid":
        return [
            f"Emergency AC &amp; Furnace Repair in {city}",
            "Heat Pump Installation &amp; Service",
            "Central Heating &amp; Cooling Replacement",
            "HVAC System Maintenance &amp; Tune-Ups",
            "Ductwork Inspection, Cleaning &amp; Sealing",
        ]
    elif ct == "cold":
        return [
            f"Emergency Furnace Repair in {city}",
            f"Boiler &amp; Heating System Service in {city}",
            "Furnace &amp; Heating Installation",
            "HVAC System Maintenance &amp; Tune-Ups",
            "Ductwork Inspection, Cleaning &amp; Sealing",
        ]
    elif ct == "mountain":
        return [
            f"Emergency Furnace &amp; AC Repair in {city}",
            "High-Altitude HVAC Calibration",
            "Furnace &amp; AC Installation",
            "HVAC System Maintenance &amp; Tune-Ups",
            "Ductwork Inspection &amp; Humidifier Service",
        ]
    return []


def get_licensing_paragraph(d):
    """Licensing paragraph with cost guide link. Handles states with no license requirement."""
    if d["license_req"].lower().startswith("no "):
        license_text = (
            f'In {d["state_full"]}, <strong>{d["license_req"]}</strong>. '
            f'Even without a state license mandate, reputable contractors carry insurance, pull permits correctly, '
            f'and stand behind their work.'
        )
    else:
        license_text = (
            f'Before hiring any HVAC contractor in {d["state_full"]}, verify they hold the proper '
            f'<strong>{d["license_req"]}</strong>. Licensed contractors carry insurance, pull permits correctly, '
            f'and stand behind their work.'
        )
    return (
        f'{license_text} For {d["city"]} residents, your local permit office is '
        f'<strong>{d["permit_office"]}</strong>\u2014any major installation should have a permit on file. '
        f'See our <a href="../costs.html" style="color: var(--orange); font-weight: 600;">HVAC cost guide</a> '
        f'for detailed pricing breakdowns.'
    )


def get_rebates_paragraph(d):
    """Fix 3: Factual rebates paragraph with financing link."""
    return (
        f'{d["city"]} homeowners served by <strong>{d["utility"]}</strong> may qualify for savings through '
        f'<strong>{d["utility_rebates"]}</strong> when installing qualifying high-efficiency equipment. '
        f'Federal tax credits for ENERGY STAR certified systems may also apply. Contact your utility provider '
        f'or HVAC contractor to confirm current eligibility and amounts. Learn about '
        f'<a href="../article-hvac-financing.html" style="color: var(--orange); font-weight: 600;">HVAC financing options</a>.'
    )


GEOGRAPHIC_NEIGHBORS = {
    "phoenix-az": ["las-vegas-nv", "dallas-tx", "san-antonio-tx"],
    "las-vegas-nv": ["phoenix-az", "denver-co", "dallas-tx"],
    "denver-co": ["oklahoma-city-ok", "kansas-city-mo", "las-vegas-nv"],
}


def get_nearby_cities_html(slug, d):
    """Fix 6: Nearby Service Areas block."""
    ct = d["climate_type"]
    # Use geographic neighbors if available (for small climate groups)
    if slug in GEOGRAPHIC_NEIGHBORS:
        others = GEOGRAPHIC_NEIGHBORS[slug][:3]
    else:
        region_cities = RELATED_CITIES.get(ct, [])
        others = [s for s in region_cities if s != slug][:3]

    links_html = ""
    for other_slug in others:
        other_data = CITIES.get(other_slug)
        if other_data:
            links_html += f'            <li><a href="{other_slug}.html">{other_data["city"]}, {other_data["state"]}</a></li>\n'

    return f'''    <!-- Nearby Service Areas -->
    <section class="section" style="padding: 32px 0 48px;">
      <div class="container" style="max-width: 800px;">
        <div class="city-services">
          <h2>Nearby HVAC Service Areas</h2>
          <ul>
{links_html}            <li><a href="../locations.html">View all HVAC service areas &#8594;</a></li>
          </ul>
        </div>
      </div>
    </section>'''


def get_faq_license_text(d):
    """Helper: license FAQ answer text that handles 'No license' states."""
    if d["license_req"].lower().startswith("no "):
        return f'In {d["state_full"]}, {d["license_req"]}. Always verify your contractor credentials before authorizing work.'
    return f'In {d["state_full"]}, HVAC contractors should hold a {d["license_req"]}. Always verify your contractor credentials before authorizing work.'


def get_faq_schema(d):
    """Fix 7: FAQPage schema with 5 FAQs."""
    city = d["city"]
    state = d["state"]
    state_full = d["state_full"]
    return f'''      {{
        "@type": "FAQPage",
        "mainEntity": [
          {{
            "@type": "Question",
            "name": "Do I need a permit to replace my AC in {city}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Yes, ensure your contractor files a mechanical permit with the {d['permit_office']}."
            }}
          }},
          {{
            "@type": "Question",
            "name": "Are there HVAC rebates in {city}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Upgrading to a high-efficiency unit may qualify you for savings through {d['utility']}. Check with {d['utility_rebates']} for current offers."
            }}
          }},
          {{
            "@type": "Question",
            "name": "What ZIP codes do you serve in {city}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Our network covers {city} and surrounding areas including {d['zips']}. Call (844) 582-1795 to verify service availability for your specific ZIP code."
            }}
          }},
          {{
            "@type": "Question",
            "name": "How much does HVAC replacement cost in {city}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "A standard AC replacement in {city} typically costs {d['ac_cost']}, and furnace installations run {d['furnace_cost']}. Costs vary based on system size, efficiency rating, and installation complexity."
            }}
          }},
          {{
            "@type": "Question",
            "name": "What HVAC license is required in {state_full}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "{get_faq_license_text(d)}"
            }}
          }}
        ]
      }}'''


def get_organization_schema(d, slug):
    """Fix 1: Organization schema (replaces LocalBusiness)."""
    return f'''      {{
        "@type": "Organization",
        "name": "Cool Call Pro",
        "url": "https://coolcallpro.com",
        "description": "24/7 referral service connecting homeowners with independent HVAC professionals in {d['city']}, {d['state']}.",
        "contactPoint": {{
          "@type": "ContactPoint",
          "telephone": "+1-844-582-1795",
          "contactType": "customer service",
          "areaServed": {{
            "@type": "City",
            "name": "{d['city']}",
            "containedInPlace": {{
              "@type": "State",
              "name": "{d['state_full']}"
            }}
          }},
          "availableLanguage": "English"
        }}
      }}'''


def get_h1(d):
    """Climate-specific H1 to avoid identical H1 pattern across all city pages."""
    ct = d["climate_type"]
    city = d["city"]
    state = d["state"]
    if ct == "hot-humid":
        return f"24/7 AC Repair &amp; Emergency HVAC Service in {city}, {state}"
    elif ct == "hot-dry":
        return f"Emergency AC &amp; Cooling Service in {city}, {state} — 24/7"
    elif ct == "mixed-humid":
        return f"Year-Round HVAC Repair &amp; AC Service in {city}, {state}"
    elif ct == "cold":
        return f"24/7 Furnace Repair &amp; Emergency Heating in {city}, {state}"
    elif ct == "mountain":
        return f"High-Altitude HVAC Repair &amp; Service in {city}, {state}"
    return f"24/7 Emergency HVAC Repair &amp; AC Service in {city}, {state}"


def get_title(d):
    """Shorter title for <title> tag (max 60 chars including ' | Cool Call Pro')."""
    ct = d["climate_type"]
    city = d["city"]
    state = d["state"]
    if ct == "hot-humid":
        return f"24/7 AC &amp; HVAC Repair in {city}, {state}"
    elif ct == "hot-dry":
        return f"Emergency AC Service in {city}, {state}"
    elif ct == "mixed-humid":
        return f"HVAC &amp; AC Service in {city}, {state}"
    elif ct == "cold":
        return f"Furnace &amp; Heating Repair in {city}, {state}"
    elif ct == "mountain":
        return f"HVAC Repair &amp; Service in {city}, {state}"
    return f"HVAC Repair &amp; AC Service in {city}, {state}"


# ─── Full Page HTML Template ──────────────────────────────────────────────────

def generate_page(slug, d):
    """Generate complete HTML page for a city."""
    services = get_services_list(d)
    services_html = "\n".join(f"              <li>{s}</li>" for s in services)
    opening_p = get_opening_paragraph(d)
    climate_h2 = get_climate_h2(d)
    climate_p = get_climate_paragraph(d)
    licensing_p = get_licensing_paragraph(d)
    rebates_p = get_rebates_paragraph(d)
    nearby_html = get_nearby_cities_html(slug, d)
    faq_schema = get_faq_schema(d)
    org_schema = get_organization_schema(d, slug)

    # FAQ license answer (handles "No license" states)
    if d["license_req"].lower().startswith("no "):
        faq_license_html = f'In {d["state_full"]}, <strong>{d["license_req"]}</strong>. Always verify your contractor\'s credentials before authorizing work. For {d["city"]} residents, permits are filed through the <strong>{d["permit_office"]}</strong>.'
    else:
        faq_license_html = f'In {d["state_full"]}, HVAC contractors should hold a <strong>{d["license_req"]}</strong>. Always verify your contractor\'s credentials before authorizing work. For {d["city"]} residents, permits are filed through the <strong>{d["permit_office"]}</strong>.'

    # Climate-specific H1 (used in page body) and shorter title (used in <title> tag)
    page_h1 = get_h1(d)
    page_title = get_title(d)

    # First ZIP for meta description
    first_zip = d["zips"].split(",")[0].strip()

    return f'''<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{page_title} | Cool Call Pro</title>
  <meta name="description"
    content="Need HVAC repair in {d["city"]}, {d["state_full"]}? Cool Call Pro connects you to 24/7 local technicians covering {first_zip} and nearby areas. Call (844) 582-1795." />
  <link rel="canonical" href="https://coolcallpro.com/locations/{slug}" />

  <!-- Open Graph -->
  <meta property="og:type" content="website" />
  <meta property="og:title" content="{page_title} | Cool Call Pro" />
  <meta property="og:description" content="Connect with independent HVAC professionals in {d["city"]}, {d["state_full"]}. Emergency AC and furnace service available 24/7." />
  <meta property="og:url" content="https://coolcallpro.com/locations/{slug}" />
  <meta property="og:site_name" content="Cool Call Pro" />
  <meta property="og:image" content="https://coolcallpro.com/images/og-homepage.webp" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{page_title}" />
  <meta name="twitter:description" content="Connect with independent HVAC professionals in {d["city"]}, {d["state_full"]}." />
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
          {{"@type": "ListItem", "position": 3, "name": "{d["city"]}, {d["state"]}", "item": "https://coolcallpro.com/locations/{slug}"}}
        ]
      }},
{faq_schema},
{org_schema}
    ]
  }}
  </script>

  <style>
    .city-hero {{
      background: linear-gradient(rgba(10, 22, 40, 0.88), rgba(10, 22, 40, 0.88)), url('../images/{d["hero_image"]}');
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
      color: var(--orange);
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
        <span class="section-tag" style="background: rgba(255,255,255,0.1); color: #fff;">&#128205; {d["city"]}, {d["state"]}</span>
        <h1>{page_h1}</h1>
        <p>Connect with independent local HVAC professionals in {d["city"]}, {d["state_full"]}. Emergency AC repair, furnace service, and system installation available 24/7.</p>
        <div style="margin-top: 28px;">
          <a href="tel:+18445821795" class="btn btn-primary btn-lg btn-vibrate"><span class="phone-icon">&#128222;</span> Call Now &#8212; (844) 582-1795</a>
        </div>
        <div class="jump-links" style="margin-top: 16px;">
          <a href="#services" class="jump-link" style="color: rgba(255,255,255,0.8);">Services</a>
          <span class="jump-link-dot" style="color: rgba(255,255,255,0.5);">&#8226;</span>
          <a href="#how-it-works" class="jump-link" style="color: rgba(255,255,255,0.8);">How It Works</a>
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
            <li aria-current="page">{d["city"]}, {d["state"]}</li>
          </ol>
        </nav>
      </div>
    </div>

    <!-- Local Context Paragraph -->
    <section class="section" style="padding: 48px 0 0;">
      <div class="container">
        <div class="city-context">
          <p>{opening_p}</p>
        </div>

        <!-- Climate Context -->
        <div class="city-services" style="margin-bottom: 40px;">
          <h2>{climate_h2}</h2>
          <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">{climate_p}</p>
        </div>

        <!-- Services List -->
        <div class="city-services" id="services">
          <h2>HVAC Services in {d["city"]}, {d["state"]}</h2>
          <ul>
{services_html}
          </ul>
        </div>

        <!-- Licensing & Trust -->
        <div class="city-services" style="margin-bottom: 40px;">
          <h2>Why {d["city"]} Homeowners Choose Licensed HVAC Pros</h2>
          <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">{licensing_p}</p>
        </div>

        <!-- Rebates & Incentives -->
        <div class="city-services" style="margin-bottom: 48px;">
          <h2>HVAC Rebates &amp; Incentives in {d["city"]}, {d["state"]}</h2>
          <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">{rebates_p}</p>
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
          <p class="section-sub">From your first call to getting connected with an independent HVAC provider in <strong>{d["city"]}, {d["state"]}</strong> &#8212; here's exactly what happens.</p>
        </div>

        <div class="steps-grid">

          <div class="step-card">
            <div class="step-number">01</div>
            <div class="step-icon"><span class="phone-icon">&#128222;</span></div>
            <h3>Call and Tell Us Your Issue</h3>
            <p>Call our 24/7 service line and tell us your HVAC issue. Your request will be routed to an independent professional serving <strong>{d["city"]}</strong> and surrounding areas.</p>
          </div>

          <div class="step-card">
            <div class="step-number">02</div>
            <div class="step-icon">&#128269;</div>
            <h3>Connect with an HVAC Provider</h3>
            <p>We connect you with an independent HVAC professional serving your <strong>{d["city"]}, {d["state"]}</strong> ZIP code. Licensing, insurance, and availability vary by provider.</p>
          </div>

          <div class="step-card">
            <div class="step-number">03</div>
            <div class="step-icon">&#128736;&#65039;</div>
            <h3>Review Options &amp; Schedule</h3>
            <p>A local <strong>{d["city"]}</strong> provider will confirm availability and discuss options. Service options and dispatch times vary by area.</p>
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
          <h2>Frequently Asked Questions &#8212; {d["city"]}, {d["state"]}</h2>
          <div class="faq-list" style="margin-top: 24px;">
            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>Do I need a permit to replace my AC in {d["city"]}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>Yes, ensure your contractor files a mechanical permit with the <strong>{d["permit_office"]}</strong>. Pulling the correct permits protects you as a homeowner and ensures work is inspected to code.</p>
                </div>
              </div>
            </div>

            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>Are there HVAC rebates in {d["city"]}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>Homeowners may qualify for savings through <strong>{d["utility"]}</strong>. Check with <strong>{d["utility_rebates"]}</strong> for current offers. Federal ENERGY STAR tax credits may also apply.</p>
                </div>
              </div>
            </div>

            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>What ZIP codes do you serve in {d["city"]}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>Our network covers {d["city"]} and surrounding areas including <strong>{d["zips"]}</strong>. Call <a href="tel:+18445821795" style="color: var(--orange); font-weight: 600;">(844) 582-1795</a> to verify service availability for your specific ZIP code.</p>
                </div>
              </div>
            </div>

            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>How much does HVAC replacement cost in {d["city"]}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>A standard AC replacement in {d["city"]} typically costs <strong>{d["ac_cost"]}</strong>, and furnace installations run <strong>{d["furnace_cost"]}</strong>. Costs vary based on system size, efficiency rating, and installation complexity. In {d["state_full"]}, new AC units must meet a minimum <strong>{d["seer_minimum"]}</strong> rating.</p>
                </div>
              </div>
            </div>

            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>What HVAC license is required in {d["state_full"]}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>{faq_license_html}</p>
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

{nearby_html}

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


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Generating 20 HVAC city pages (v2 - full overhaul)...\n")
    generated = 0
    for slug, data in CITIES.items():
        filepath = os.path.join(LOCATIONS_DIR, f"{slug}.html")
        html = generate_page(slug, data)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  [OK] {slug}.html")
        generated += 1
    print(f"\nDone. Generated {generated} pages.")


if __name__ == "__main__":
    main()
