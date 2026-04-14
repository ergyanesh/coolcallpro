"""
Updates the 20 published HVAC city pages with:
1. Climate zone hero images (replace generic hvac_emergency.webp)
2. Climate context paragraph (temperature, SEER, utility)
3. Licensing & trust paragraph
4. Rebates & savings paragraph
5. LocalBusiness schema markup (JSON-LD)
"""

import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCATIONS_DIR = os.path.join(BASE_DIR, "locations")

# ─── City Data ───────────────────────────────────────────────────────────────

CITIES = {
    "atlanta-ga": {
        "city": "Atlanta", "state": "GA", "state_full": "Georgia",
        "population": "520,070",
        "avg_summer_high": "89", "avg_winter_low": "34",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility": "Georgia Power",
        "utility_rebates": "Georgia Power Home Energy Improvement Program (HEIP)",
        "license_req": "Conditioned Air Contractor License (Class I or II)",
        "climate_zone": "Zone 3A (Warm-Humid)",
        "climate_type": "mixed-humid",
        "hero_image": "mixed-humid-climate-hvac-atlanta-hero.webp",
        "hero_alt": "Year-round HVAC solutions for mixed-humid climate with seasonal temperature swings",
        "neighborhoods": "Buckhead, Druid Hills, Ansley Park, Morningside-Lenox Park, Virginia-Highland",
        "zips": "30305, 30306, 30309, 30307, 30319",
        "ac_cost": "$4,000\u2013$7,800", "furnace_cost": "$3,200\u2013$6,200",
        "permit_office": "City of Atlanta Office of Buildings (Dept. of City Planning)",
    },
    "birmingham-al": {
        "city": "Birmingham", "state": "AL", "state_full": "Alabama",
        "population": "196,357",
        "avg_summer_high": "91", "avg_winter_low": "35",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility": "Alabama Power",
        "utility_rebates": "Alabama Power Heat Pump Loan Program",
        "license_req": "Heating & Air Conditioning Contractor License",
        "climate_zone": "Zone 3A (Warm-Humid)",
        "climate_type": "mixed-humid",
        "hero_image": "mixed-humid-climate-hvac-atlanta-hero.webp",
        "hero_alt": "Year-round HVAC solutions for mixed-humid climate with seasonal temperature swings",
        "neighborhoods": "Homewood, Vestavia Hills, Highland Park, Avondale, Crestwood",
        "zips": "35209, 35216, 35205, 35222, 35210",
        "ac_cost": "$3,800\u2013$6,500", "furnace_cost": "$3,000\u2013$5,500",
        "permit_office": "City of Birmingham Dept. of Planning, Engineering & Permits",
    },
    "boston-ma": {
        "city": "Boston", "state": "MA", "state_full": "Massachusetts",
        "population": "673,600",
        "avg_summer_high": "82", "avg_winter_low": "23",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility": "Eversource",
        "utility_rebates": "Mass Save Heat Pump Rebates (up to $10,000)",
        "license_req": "No state HVAC license required; EPA 608 required",
        "climate_zone": "Zone 5A (Cool-Humid)",
        "climate_type": "cold",
        "hero_image": "cold-climate-furnace-minneapolis-hero.webp",
        "hero_alt": "High-efficiency furnace installation for cold climate winter protection",
        "neighborhoods": "West Roxbury, Dorchester, Jamaica Plain, Roslindale, Hyde Park",
        "zips": "02132, 02124, 02130, 02131, 02136",
        "ac_cost": "$5,000\u2013$9,000", "furnace_cost": "$4,500\u2013$8,000",
        "permit_office": "City of Boston Inspectional Services Department (ISD)",
    },
    "charlotte-nc": {
        "city": "Charlotte", "state": "NC", "state_full": "North Carolina",
        "population": "943,476",
        "avg_summer_high": "90", "avg_winter_low": "32",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility": "Duke Energy Carolinas",
        "utility_rebates": "Duke Energy Smart $aver Program (up to $500/unit)",
        "license_req": "NC Heating & Cooling Contractor License (H1/H2/H3)",
        "climate_zone": "Zone 3A (Warm-Humid)",
        "climate_type": "mixed-humid",
        "hero_image": "mixed-humid-climate-hvac-atlanta-hero.webp",
        "hero_alt": "Year-round HVAC solutions for mixed-humid climate with seasonal temperature swings",
        "neighborhoods": "Myers Park, Dilworth, Ballantyne, Eastover, SouthPark",
        "zips": "28207, 28203, 28277, 28209, 28226",
        "ac_cost": "$3,800\u2013$7,500", "furnace_cost": "$3,000\u2013$6,000",
        "permit_office": "Mecklenburg County Code Enforcement (LUESA)",
    },
    "chicago-il": {
        "city": "Chicago", "state": "IL", "state_full": "Illinois",
        "population": "2,719,365",
        "avg_summer_high": "84", "avg_winter_low": "17",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility": "ComEd (Commonwealth Edison)",
        "utility_rebates": "ComEd Heat Pump Rebates ($1,400\u2013$2,075); Peoples Gas Rebates",
        "license_req": "No statewide license; Chicago requires General Contractor License",
        "climate_zone": "Zone 5A (Cool-Humid)",
        "climate_type": "cold",
        "hero_image": "cold-climate-furnace-minneapolis-hero.webp",
        "hero_alt": "High-efficiency furnace installation for cold climate winter protection",
        "neighborhoods": "Beverly, Edison Park, Portage Park, Lincoln Square, Bridgeport",
        "zips": "60634, 60618, 60643, 60625, 60632",
        "ac_cost": "$3,900\u2013$7,500", "furnace_cost": "$3,500\u2013$7,000",
        "permit_office": "Chicago Department of Buildings",
    },
    "dallas-tx": {
        "city": "Dallas", "state": "TX", "state_full": "Texas",
        "population": "1,326,087",
        "avg_summer_high": "96", "avg_winter_low": "38",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility": "Oncor Electric Delivery (TDU)",
        "utility_rebates": "Oncor Take a Load Off Texas Program (up to $3,400)",
        "license_req": "TX TDLR Air Conditioning & Refrigeration Contractor License",
        "climate_zone": "Zone 3A (Warm-Humid)",
        "climate_type": "mixed-humid",
        "hero_image": "mixed-humid-climate-hvac-atlanta-hero.webp",
        "hero_alt": "Year-round HVAC solutions for mixed-humid climate with seasonal temperature swings",
        "neighborhoods": "Highland Park, Lakewood, Preston Hollow, M Streets (Greenland Hills), Lake Highlands",
        "zips": "75205, 75214, 75230, 75225, 75238",
        "ac_cost": "$4,500\u2013$12,000", "furnace_cost": "$3,000\u2013$6,500",
        "permit_office": "City of Dallas Building Inspection Division",
    },
    "denver-co": {
        "city": "Denver", "state": "CO", "state_full": "Colorado",
        "population": "729,019",
        "avg_summer_high": "90", "avg_winter_low": "18",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility": "Xcel Energy",
        "utility_rebates": "Xcel Energy Whole Home Efficiency Program ($2,250/ton)",
        "license_req": "No statewide HVAC license required",
        "climate_zone": "Zone 5B (Cold-Dry)",
        "climate_type": "mountain",
        "hero_image": "mountain-climate-hvac-denver-hero.webp",
        "hero_alt": "High-altitude HVAC system engineered for mountain climate conditions",
        "neighborhoods": "Washington Park, Cherry Creek, Hilltop, Congress Park, Park Hill",
        "zips": "80209, 80206, 80220, 80210, 80218",
        "ac_cost": "$4,000\u2013$8,000", "furnace_cost": "$3,500\u2013$7,500",
        "permit_office": "Denver Community Planning and Development (CPD)",
    },
    "detroit-mi": {
        "city": "Detroit", "state": "MI", "state_full": "Michigan",
        "population": "645,705",
        "avg_summer_high": "83", "avg_winter_low": "19",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility": "DTE Energy",
        "utility_rebates": "DTE Energy Heating & Cooling Program",
        "license_req": "MI Mechanical Contractor License (LARA)",
        "climate_zone": "Zone 5A (Cool-Humid)",
        "climate_type": "cold",
        "hero_image": "cold-climate-furnace-minneapolis-hero.webp",
        "hero_alt": "High-efficiency furnace installation for cold climate winter protection",
        "neighborhoods": "Indian Village, University District, Boston-Edison, Rosedale Park, Palmer Park",
        "zips": "48221, 48224, 48219, 48235, 48227",
        "ac_cost": "$3,900\u2013$7,500", "furnace_cost": "$3,500\u2013$7,000",
        "permit_office": "Detroit BSEED (Buildings, Safety Engineering & Environmental Dept.)",
    },
    "houston-tx": {
        "city": "Houston", "state": "TX", "state_full": "Texas",
        "population": "2,390,125",
        "avg_summer_high": "95", "avg_winter_low": "43",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility": "CenterPoint Energy",
        "utility_rebates": "CenterPoint Energy Standard Offer Program (up to $500/unit)",
        "license_req": "TX TDLR Air Conditioning & Refrigeration Contractor License",
        "climate_zone": "Zone 2A (Hot-Humid)",
        "climate_type": "hot-humid",
        "hero_image": "hot-humid-climate-hvac-houston-hero.webp",
        "hero_alt": "Professional HVAC installation for hot-humid climate homes with humidity control",
        "neighborhoods": "The Heights, West University Place, Meyerland, Oak Forest, Tanglewood",
        "zips": "77024, 77005, 77019, 77007, 77008",
        "ac_cost": "$4,500\u2013$12,000", "furnace_cost": "$3,000\u2013$6,000",
        "permit_office": "Houston Permitting Center",
    },
    "kansas-city-mo": {
        "city": "Kansas City", "state": "MO", "state_full": "Missouri",
        "population": "516,032",
        "avg_summer_high": "90", "avg_winter_low": "22",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility": "Evergy",
        "utility_rebates": "Evergy FastTrack HVAC PAYS Program (~$1,000\u2013$1,300)",
        "license_req": "No statewide license; KC requires municipal trade license",
        "climate_zone": "Zone 4A (Mixed-Humid)",
        "climate_type": "cold",
        "hero_image": "cold-climate-furnace-minneapolis-hero.webp",
        "hero_alt": "High-efficiency furnace installation for cold climate winter protection",
        "neighborhoods": "Brookside, Waldo, Ward Parkway, Sunset Hill, Armour Hills",
        "zips": "64112, 64113, 64114, 64151, 64155",
        "ac_cost": "$3,800\u2013$7,200", "furnace_cost": "$3,000\u2013$6,200",
        "permit_office": "Kansas City Planning & Development \u2013 Permits Division",
    },
    "las-vegas-nv": {
        "city": "Las Vegas", "state": "NV", "state_full": "Nevada",
        "population": "678,922",
        "avg_summer_high": "105", "avg_winter_low": "40",
        "seer_minimum": "SEER2 14.3 + EER2 11.7 (Southwest Region)",
        "utility": "NV Energy",
        "utility_rebates": "NV Energy AC Rebates",
        "license_req": "NV C-21 Refrigeration & Air Conditioning License",
        "climate_zone": "Zone 3B (Warm-Dry)",
        "climate_type": "hot-dry",
        "hero_image": "desert-climate-hvac-phoenix-hero.webp",
        "hero_alt": "Desert climate AC system designed for extreme Southwest heat",
        "neighborhoods": "Summerlin, Spring Valley, Centennial Hills, Lone Mountain, Southwest Las Vegas",
        "zips": "89134, 89135, 89148, 89117, 89147",
        "ac_cost": "$4,500\u2013$8,000", "furnace_cost": "$3,000\u2013$5,500",
        "permit_office": "City of Las Vegas Building & Safety Department",
    },
    "milwaukee-wi": {
        "city": "Milwaukee", "state": "WI", "state_full": "Wisconsin",
        "population": "561,385",
        "avg_summer_high": "81", "avg_winter_low": "16",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility": "We Energies",
        "utility_rebates": "Focus on Energy / We Energies HVAC Rebates",
        "license_req": "No mandatory statewide license; optional HVAC Qualifier cert",
        "climate_zone": "Zone 5A (Cool-Humid)",
        "climate_type": "cold",
        "hero_image": "cold-climate-furnace-minneapolis-hero.webp",
        "hero_alt": "High-efficiency furnace installation for cold climate winter protection",
        "neighborhoods": "Bay View, Sherman Park, Washington Heights, Enderis Park, Wauwatosa East",
        "zips": "53207, 53210, 53213, 53208, 53215",
        "ac_cost": "$3,800\u2013$7,200", "furnace_cost": "$3,000\u2013$6,500",
        "permit_office": "Milwaukee Dept. of Neighborhood Services (DNS)",
    },
    "minneapolis-mn": {
        "city": "Minneapolis", "state": "MN", "state_full": "Minnesota",
        "population": "428,579",
        "avg_summer_high": "83", "avg_winter_low": "9",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility": "Xcel Energy",
        "utility_rebates": "Xcel Energy / CEE HVAC Rebates",
        "license_req": "No state license; $25,000 surety bond required",
        "climate_zone": "Zone 6A (Cold-Humid)",
        "climate_type": "cold",
        "hero_image": "cold-climate-furnace-minneapolis-hero.webp",
        "hero_alt": "High-efficiency furnace installation for cold climate winter protection",
        "neighborhoods": "Longfellow, Powderhorn, Nokomis, Northeast, Southwest/Linden Hills",
        "zips": "55406, 55407, 55417, 55418, 55410",
        "ac_cost": "$4,000\u2013$7,500", "furnace_cost": "$3,200\u2013$6,800",
        "permit_office": "City of Minneapolis CPED (Community Planning & Economic Development)",
    },
    "new-orleans-la": {
        "city": "New Orleans", "state": "LA", "state_full": "Louisiana",
        "population": "362,701",
        "avg_summer_high": "92", "avg_winter_low": "46",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility": "Entergy New Orleans",
        "utility_rebates": "Entergy New Orleans Energy Smart Program (up to $500)",
        "license_req": "LA Mechanical Work Contractor License (LSLBC)",
        "climate_zone": "Zone 2A (Hot-Humid)",
        "climate_type": "hot-humid",
        "hero_image": "hot-humid-climate-hvac-houston-hero.webp",
        "hero_alt": "Professional HVAC installation for hot-humid climate homes with humidity control",
        "neighborhoods": "Uptown, Lakeview, Garden District, Gentilly, Algiers Point",
        "zips": "70115, 70118, 70119, 70122, 70124",
        "ac_cost": "$3,800\u2013$7,000", "furnace_cost": "$2,800\u2013$5,800",
        "permit_office": "City of New Orleans Dept. of Safety & Permits",
    },
    "oklahoma-city-ok": {
        "city": "Oklahoma City", "state": "OK", "state_full": "Oklahoma",
        "population": "712,919",
        "avg_summer_high": "93", "avg_winter_low": "27",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility": "OG&E (Oklahoma Gas & Electric)",
        "utility_rebates": "OG&E Residential Energy Efficiency Program (up to $3,000)",
        "license_req": "OK Mechanical Contractor License (HVAC/R)",
        "climate_zone": "Zone 3A (Warm-Humid)",
        "climate_type": "mixed-humid",
        "hero_image": "mixed-humid-climate-hvac-atlanta-hero.webp",
        "hero_alt": "Year-round HVAC solutions for mixed-humid climate with seasonal temperature swings",
        "neighborhoods": "Nichols Hills, Heritage Hills, Mesta Park, Quail Creek, Crown Heights-Edgemere Heights",
        "zips": "73104, 73112, 73116, 73120, 73142",
        "ac_cost": "$3,800\u2013$7,000", "furnace_cost": "$3,000\u2013$6,000",
        "permit_office": "OKC Development Services Department",
    },
    "philadelphia-pa": {
        "city": "Philadelphia", "state": "PA", "state_full": "Pennsylvania",
        "population": "1,573,916",
        "avg_summer_high": "88", "avg_winter_low": "26",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility": "PECO Energy",
        "utility_rebates": "PECO Energy Rebates; EAP Residential HVAC Rebate Program",
        "license_req": "No statewide license; Philadelphia requires city license",
        "climate_zone": "Zone 4A (Mixed-Humid)",
        "climate_type": "cold",
        "hero_image": "cold-climate-furnace-minneapolis-hero.webp",
        "hero_alt": "High-efficiency furnace installation for cold climate winter protection",
        "neighborhoods": "Chestnut Hill, Roxborough, Mayfair, Mount Airy, South Philadelphia (Passyunk/Girard Estate)",
        "zips": "19118, 19128, 19136, 19111, 19148",
        "ac_cost": "$4,500\u2013$8,500", "furnace_cost": "$4,000\u2013$7,500",
        "permit_office": "Philadelphia Department of Licenses & Inspections (L&I)",
    },
    "phoenix-az": {
        "city": "Phoenix", "state": "AZ", "state_full": "Arizona",
        "population": "1,673,164",
        "avg_summer_high": "107", "avg_winter_low": "46",
        "seer_minimum": "SEER2 14.3 + EER2 11.7 (Southwest Region)",
        "utility": "APS / Salt River Project (SRP)",
        "utility_rebates": "SRP HVAC Rebates ($75\u2013$1,125/ton)",
        "license_req": "AZ ROC HVAC/R Contractor License",
        "climate_zone": "Zone 2B (Hot-Dry)",
        "climate_type": "hot-dry",
        "hero_image": "desert-climate-hvac-phoenix-hero.webp",
        "hero_alt": "Desert climate AC system designed for extreme Southwest heat",
        "neighborhoods": "Arcadia, Biltmore, Paradise Valley Village, Camelback East, Ahwatukee Foothills",
        "zips": "85018, 85016, 85028, 85032, 85048",
        "ac_cost": "$4,500\u2013$8,000", "furnace_cost": "$3,000\u2013$5,500",
        "permit_office": "City of Phoenix Planning & Development Department",
    },
    "san-antonio-tx": {
        "city": "San Antonio", "state": "TX", "state_full": "Texas",
        "population": "1,526,656",
        "avg_summer_high": "96", "avg_winter_low": "39",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility": "CPS Energy",
        "utility_rebates": "CPS Energy STEP Home Energy Rebate Program",
        "license_req": "TX TDLR Air Conditioning & Refrigeration Contractor License",
        "climate_zone": "Zone 2A (Hot-Humid)",
        "climate_type": "hot-humid",
        "hero_image": "hot-humid-climate-hvac-houston-hero.webp",
        "hero_alt": "Professional HVAC installation for hot-humid climate homes with humidity control",
        "neighborhoods": "Alamo Heights, Terrell Hills, Olmos Park, Stone Oak, King William",
        "zips": "78209, 78212, 78201, 78258, 78216",
        "ac_cost": "$4,200\u2013$10,000", "furnace_cost": "$2,800\u2013$5,500",
        "permit_office": "City of San Antonio Development Services Department",
    },
    "st-louis-mo": {
        "city": "St. Louis", "state": "MO", "state_full": "Missouri",
        "population": "279,695",
        "avg_summer_high": "90", "avg_winter_low": "24",
        "seer_minimum": "SEER2 13.4 (North Region)",
        "utility": "Ameren Missouri",
        "utility_rebates": "Ameren Missouri PAYS Program",
        "license_req": "No statewide license; St. Louis requires municipal license",
        "climate_zone": "Zone 4A (Mixed-Humid)",
        "climate_type": "mixed-humid",
        "hero_image": "mixed-humid-climate-hvac-atlanta-hero.webp",
        "hero_alt": "Year-round HVAC solutions for mixed-humid climate with seasonal temperature swings",
        "neighborhoods": "Tower Grove South, South Hampton, Bevo Mill, Shaw, Holly Hills",
        "zips": "63116, 63109, 63110, 63118, 63104",
        "ac_cost": "$3,500\u2013$7,200", "furnace_cost": "$2,800\u2013$6,000",
        "permit_office": "City of St. Louis Building Division (Dept. of Public Safety)",
    },
    "tampa-fl": {
        "city": "Tampa", "state": "FL", "state_full": "Florida",
        "population": "414,547",
        "avg_summer_high": "90", "avg_winter_low": "53",
        "seer_minimum": "SEER2 14.3 (Southeast Region)",
        "utility": "Tampa Electric (TECO)",
        "utility_rebates": "Tampa Electric (TECO) Heating & Cooling Program",
        "license_req": "FL Certified Air Conditioning Contractor License (Class A/B)",
        "climate_zone": "Zone 2A (Hot-Humid)",
        "climate_type": "hot-humid",
        "hero_image": "hot-humid-climate-hvac-houston-hero.webp",
        "hero_alt": "Professional HVAC installation for hot-humid climate homes with humidity control",
        "neighborhoods": "Seminole Heights, South Tampa (Palma Ceia), Hyde Park, Tampa Heights, Westshore",
        "zips": "33604, 33609, 33606, 33611, 33629",
        "ac_cost": "$5,500\u2013$9,000", "furnace_cost": "$3,500\u2013$6,000",
        "permit_office": "City of Tampa Construction Services Division",
    },
}


# ─── Content Templates ───────────────────────────────────────────────────────

def get_climate_paragraph(d):
    """Generate climate context paragraph based on climate type."""
    ct = d["climate_type"]
    if ct == "hot-humid":
        return (
            f'With summer highs averaging {d["avg_summer_high"]}\u00b0F and humidity levels that strain even the best systems, '
            f'{d["city"]} homeowners know their AC isn\u2019t optional\u2014it\u2019s survival. The good news? '
            f'Winter lows rarely dip below {d["avg_winter_low"]}\u00b0F, so heating costs stay manageable. '
            f'As a {d["climate_zone"]} climate zone, federal regulations require all new AC units meet a minimum '
            f'{d["seer_minimum"]} rating, which translates to real savings on your {d["utility"]} bill.'
        )
    elif ct == "hot-dry":
        return (
            f'When {d["city"]} summers push past {d["avg_summer_high"]}\u00b0F, your air conditioner works harder than '
            f'almost anywhere else in the country. The desert climate means low humidity but extreme heat, making proper '
            f'system sizing critical. Located in {d["climate_zone"]}, all new installations must meet '
            f'{d["seer_minimum"]} efficiency standards. Take advantage of {d["utility_rebates"]} to offset upgrade costs.'
        )
    elif ct == "mixed-humid":
        return (
            f'{d["city"]}\u2019s {d["climate_zone"]} climate means your HVAC system earns its keep year-round\u2014'
            f'battling {d["avg_summer_high"]}\u00b0F summer heat and winter lows near {d["avg_winter_low"]}\u00b0F. '
            f'This dual demand makes efficiency crucial. All new systems must meet {d["seer_minimum"]} standards, and '
            f'{d["utility"]} offers rebates through their {d["utility_rebates"]} to help offset costs.'
        )
    elif ct == "cold":
        return (
            f'{d["city"]} winters mean business, with temperatures plunging to {d["avg_winter_low"]}\u00b0F. '
            f'Your furnace isn\u2019t a luxury\u2014it\u2019s your lifeline. Located in {d["climate_zone"]}, '
            f'heating efficiency matters more here than almost anywhere. While summer highs reach '
            f'{d["avg_summer_high"]}\u00b0F (AC still matters!), the real focus is reliable heating. '
            f'{d["utility"]} offers {d["utility_rebates"]} to help upgrade aging systems.'
        )
    elif ct == "mountain":
        return (
            f'Denver\u2019s mile-high altitude creates unique HVAC challenges. Summer highs hit '
            f'{d["avg_summer_high"]}\u00b0F, but winter lows drop to {d["avg_winter_low"]}\u00b0F, and the thin air '
            f'affects equipment performance. As a {d["climate_zone"]} zone, you need contractors who understand '
            f'high-altitude installations. {d["utility"]} offers {d["utility_rebates"]} for energy-efficient upgrades.'
        )
    return ""


def get_licensing_paragraph(d):
    """Generate licensing & trust paragraph."""
    return (
        f'Before hiring any HVAC contractor in {d["state_full"]}, verify they hold the proper '
        f'<strong>{d["license_req"]}</strong>. Licensed contractors carry insurance, pull permits correctly, '
        f'and stand behind their work. For {d["city"]} residents, your local permit office is '
        f'<strong>{d["permit_office"]}</strong>\u2014any major installation should have a permit on file.'
    )


def get_rebates_paragraph(d):
    """Generate rebates & savings paragraph."""
    return (
        f'Before upgrading your system, check what\u2019s available to you. {d["city"]} homeowners served by '
        f'<strong>{d["utility"]}</strong> may qualify for savings through <strong>{d["utility_rebates"]}</strong> '
        f'when installing qualifying high-efficiency equipment. Federal tax credits for ENERGY STAR certified systems '
        f'may also apply. Contact your utility provider or HVAC contractor to confirm current eligibility and amounts.'
    )


def get_local_business_schema(d, slug):
    """Generate LocalBusiness JSON-LD schema."""
    return f'''      {{
        "@type": "LocalBusiness",
        "name": "HVAC Services in {d["city"]}, {d["state"]}",
        "description": "24/7 AC repair, furnace installation, and HVAC services in {d["city"]}, {d["state"]}. Serving {d["neighborhoods"]}.",
        "areaServed": {{
          "@type": "City",
          "name": "{d["city"]}",
          "containedInPlace": {{
            "@type": "State",
            "name": "{d["state_full"]}"
          }}
        }},
        "priceRange": "{d["ac_cost"]}",
        "knowsAbout": ["Air Conditioning", "Furnace Repair", "HVAC Installation", "Heat Pump"]
      }}'''


def get_new_sections_html(d):
    """Build the 3 new content sections HTML."""
    climate_p = get_climate_paragraph(d)
    licensing_p = get_licensing_paragraph(d)
    rebates_p = get_rebates_paragraph(d)

    return f'''
        <!-- Climate Context -->
        <div class="city-context">
          <p>{climate_p}</p>
        </div>

        <!-- Licensing & Trust -->
        <div class="city-services" style="margin-bottom: 40px;">
          <h2>Why {d["city"]} Homeowners Choose Local HVAC Pros</h2>
          <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">{licensing_p}</p>
        </div>

        <!-- Rebates & Savings -->
        <div class="city-services" style="margin-bottom: 48px;">
          <h2>Save Money on Your {d["city"]} HVAC Upgrade</h2>
          <p style="font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);">{rebates_p}</p>
        </div>'''


# ─── Update Logic ─────────────────────────────────────────────────────────────

def update_city_page(slug, data):
    filepath = os.path.join(LOCATIONS_DIR, f"{slug}.html")
    if not os.path.exists(filepath):
        print(f"  SKIP: {filepath} not found")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    original = html

    # 1. Replace hero background image
    html = html.replace(
        "url('../images/hvac_emergency.webp')",
        f"url('../images/{data['hero_image']}')"
    )

    # 2. Add LocalBusiness schema to the @graph array
    # Find the closing of the FAQPage entity and add LocalBusiness before the graph close
    local_biz = get_local_business_schema(data, slug)
    if '"LocalBusiness"' not in html:
        # Insert after the last FAQPage closing brace, before the @graph array close
        # Pattern: find the end of the FAQPage object (closing }), then the ] of @graph
        faq_end_pattern = r'(\s*}\s*\]\s*}\s*\]\s*}\s*</script>)'
        match = re.search(faq_end_pattern, html)
        if match:
            # We need to insert the LocalBusiness schema as a third item in the @graph array
            # Find: }]\n}\n]\n}\n</script>
            # The structure is: @graph: [ BreadcrumbList{}, FAQPage{} ]
            # We want: @graph: [ BreadcrumbList{}, FAQPage{}, LocalBusiness{} ]
            old_end = '      }\n    ]\n  }\n  </script>'
            new_end = f'      }},\n{local_biz}\n    ]\n  }}\n  </script>'
            # More flexible approach - find the FAQPage closing and add after it
            pass

        # Use a simpler, more reliable approach
        # Find the closing bracket of mainEntity array and its parent FAQPage object
        # Pattern: after the last FAQ answer, there's ]}, then ], then }
        old_schema_end = """      }
    ]
  }
  </script>"""
        new_schema_end = f"""      }},
{local_biz}
    ]
  }}
  </script>"""

        # Try the exact pattern first
        if old_schema_end in html:
            html = html.replace(old_schema_end, new_schema_end, 1)
        else:
            # Try with different indentation
            # Look for the pattern: end of FAQPage ] } ] } </script>
            pattern = re.compile(
                r'(\s*\}\s*\]\s*\}\s*\]\s*\}\s*</script>)',
                re.DOTALL
            )
            m = pattern.search(html)
            if m:
                old_block = m.group(0)
                # Parse structure: } ] } ] } </script>
                # We need to inject before the second-to-last ] }
                # Actually let's just insert the schema before the final ]\n  }\n  </script>
                insert_point = html.rfind(']\n  }\n  </script>')
                if insert_point == -1:
                    insert_point = html.rfind(']\r\n  }\r\n  </script>')
                if insert_point != -1:
                    html = html[:insert_point] + f',\n{local_biz}\n    ' + html[insert_point:]

    # 3. Add new content sections after the services list closing </div></div></section>
    new_sections = get_new_sections_html(data)

    # Check if sections already exist (idempotent)
    if "Why " + data["city"] + " Homeowners Choose Local HVAC Pros" not in html:
        # Insert after the closing </div> of city-services, before the parent </div></section>
        # The structure is:
        #   <div class="city-services" id="services">...</ul></div>
        # </div></section>
        # We want to insert between the services </div> and the container </div>

        # Find the services section end marker
        services_end = '</ul>\n        </div>\n      </div>\n    </section>'
        if services_end in html:
            html = html.replace(
                services_end,
                f'</ul>\n        </div>{new_sections}\n      </div>\n    </section>',
                1
            )
        else:
            # Try alternate whitespace
            alt_end = '</ul>\r\n        </div>\r\n      </div>\r\n    </section>'
            if alt_end in html:
                html = html.replace(
                    alt_end,
                    f'</ul>\r\n        </div>{new_sections}\r\n      </div>\r\n    </section>',
                    1
                )
            else:
                print(f"  WARNING: Could not find insertion point for new sections in {slug}")

    if html != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        return True
    return False


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Updating 20 published HVAC city pages...\n")
    updated = 0
    for slug, data in CITIES.items():
        print(f"  Processing {slug}...")
        if update_city_page(slug, data):
            print(f"  [OK] Updated {slug}")
            updated += 1
        else:
            print(f"  - No changes for {slug}")
    print(f"\nDone. Updated {updated} of {len(CITIES)} pages.")


if __name__ == "__main__":
    main()
