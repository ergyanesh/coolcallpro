"""
Deterministic article -> city link selection.

Given an article's slug and cluster, returns N city links chosen so that:
1. Climate matches the cluster's target zones.
2. Same (slug, cluster) always returns the same cities — regenerating doesn't churn.
3. Small climate pools get spaced between picks (anti over-linking).
4. Link equity spreads across all 115 published cities, not just 5 hard-coded ones.

Used by:
- The hvac-article-writer skill during article creation (Instruction 0).
- generate_city_pages_v3.py when picking the 3-article rotation per city page.

NOTE: The CLIMATE_MAP / ZONE_4A_DECISIONS / REMOVED_CITIES / ABSORBED dicts below
must stay in sync with generate_city_pages_v3.py. If you update one, update both.
"""

import hashlib
import pandas as pd


# ---------------------------------------------------------------------------
# Climate + city filtering constants (keep in sync with generate_city_pages_v3.py)
# ---------------------------------------------------------------------------

CLIMATE_MAP = {
    "Zone 1A (Very Hot-Humid)": "tropical",
    "Zone 2A (Hot-Humid)": "hot-humid",
    "Zone 2B (Hot-Dry)": "hot-dry",
    "Zone 3A (Warm-Humid)": "mixed-humid",
    "Zone 3B (Warm-Dry)": "hot-dry",
    "Zone 3C (Warm-Marine)": "coastal",
    "Zone 4A (Mixed-Humid)": None,  # needs manual decision
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

ZONE_4A_DECISIONS = {
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

REMOVED_CITIES = {"Fairbanks", "Binghamton", "Johnstown", "Danville"}

ABSORBED = {
    "Gilbert": "Phoenix", "Chula Vista": "San Diego", "Fremont": "San Jose",
    "Santa Cruz": "San Jose", "Santa Rosa": "San Francisco",
    "Aurora": "Denver", "Boulder": "Denver", "Stamford": "Bridgeport",
    "Hialeah": "Miami", "St. Petersburg": "Tampa", "Davenport": "Des Moines",
    "Rockford": "Chicago", "Pittsfield": "Springfield", "Flint": "Detroit",
    "Jersey City": "Newark", "Trenton": "Newark", "Henderson": "Las Vegas",
    "Utica": "Syracuse", "Akron": "Cleveland", "Canton": "Cleveland",
    "Youngstown": "Cleveland", "Scranton": "Allentown",
    "Arlington": "Dallas", "Plano": "Dallas", "Irving": "Dallas",
    "Grand Prairie": "Dallas", "Garland": "Dallas",
    "Chesapeake": "Virginia Beach", "Tacoma": "Seattle",
    "Rochester": "Buffalo", "Elmira": "Binghamton"
}

STATE_SLUG = {
    "AL": "alabama", "AK": "alaska", "AZ": "arizona", "AR": "arkansas",
    "CA": "california", "CO": "colorado", "CT": "connecticut", "DC": "district-of-columbia",
    "DE": "delaware", "FL": "florida", "GA": "georgia", "HI": "hawaii",
    "IA": "iowa", "ID": "idaho", "IL": "illinois", "IN": "indiana",
    "KS": "kansas", "KY": "kentucky", "LA": "louisiana", "MA": "massachusetts",
    "MD": "maryland", "ME": "maine", "MI": "michigan", "MN": "minnesota",
    "MO": "missouri", "MS": "mississippi", "MT": "montana", "NC": "north-carolina",
    "ND": "north-dakota", "NE": "nebraska", "NH": "new-hampshire", "NJ": "new-jersey",
    "NM": "new-mexico", "NV": "nevada", "NY": "new-york", "OH": "ohio",
    "OK": "oklahoma", "OR": "oregon", "PA": "pennsylvania", "RI": "rhode-island",
    "SC": "south-carolina", "SD": "south-dakota", "TN": "tennessee", "TX": "texas",
    "UT": "utah", "VA": "virginia", "VT": "vermont", "WA": "washington",
    "WI": "wisconsin", "WV": "west-virginia", "WY": "wyoming",
}


# ---------------------------------------------------------------------------
# Cluster -> climate weighting (single source of truth for Part 3 of the plan)
# ---------------------------------------------------------------------------

CLUSTER_CLIMATE_WEIGHTS = {
    "C1_ac":       {"hot-humid": 0.40, "tropical": 0.10, "hot-dry": 0.25, "mixed-humid": 0.25},
    "C2_furnace":  {"cold": 0.50, "subarctic": 0.10, "mountain": 0.25, "mixed-humid": 0.15},
    "C3_heatpump": {"coastal": 0.30, "mixed-humid": 0.40, "mountain": 0.30},
    "C4_cost":     "all_rotated",
    "C5_compare":  "all_rotated",
    "C6_maint":    "all_rotated",
}


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def _derive_climate_type(city_name: str, climate_zone: str) -> str:
    ct = CLIMATE_MAP.get(climate_zone)
    if ct is None and "4A" in str(climate_zone):
        ct = ZONE_4A_DECISIONS.get(city_name, "mixed-humid")
    if ct is None:
        ct = "mixed-humid"
    return ct


def _city_slug(city: str, state_abbr: str) -> str:
    slug = city.lower().replace(" ", "-").replace(".", "")
    return f"{slug}-{state_abbr.lower()}"


def _seed(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest(), 16) & 0xFFFFFFFF


def load_city_pools(xlsx_path: str = "cities_updated.xlsx") -> dict:
    """Read xlsx -> {climate_type: [city_dict, ...]} for published, non-absorbed cities.

    Returned pools are sorted by slug so output is stable across runs.
    """
    df = pd.read_excel(xlsx_path)
    pools: dict = {}
    for _, row in df.iterrows():
        if row.get('City Page Published') != 'Yes':
            continue
        city = row['City']
        if city in REMOVED_CITIES or city in ABSORBED:
            continue
        state = row['State']
        climate_zone = row['Climate Zone']
        ct = _derive_climate_type(city, climate_zone)
        entry = {
            'city': city,
            'state': state,
            'slug': _city_slug(city, state),
            'climate_type': ct,
        }
        pools.setdefault(ct, []).append(entry)
    for ct in pools:
        pools[ct].sort(key=lambda x: x['slug'])
    return pools


def _allocate(weights: dict, n: int) -> dict:
    """Largest-remainder allocation of n picks across buckets with fractional weights."""
    raw = {k: n * v for k, v in weights.items()}
    floors = {k: int(v) for k, v in raw.items()}
    remaining = n - sum(floors.values())
    remainders = sorted(raw.items(), key=lambda kv: kv[1] - int(kv[1]), reverse=True)
    for k, _ in remainders[:remaining]:
        floors[k] += 1
    return floors


def _city_hash_score(article_slug: str, cluster: str, climate: str, city_slug: str) -> str:
    """Stable per-(article, climate, city) hash. Sorting a pool by this score
    gives each article a different deterministic ordering of the same cities,
    which spreads link equity across the whole pool over many articles."""
    return hashlib.md5(f"{article_slug}|{cluster}|{climate}|{city_slug}".encode()).hexdigest()


def pick_cities(article_slug: str, cluster: str, n: int = 4,
                xlsx_path: str = "cities_updated.xlsx") -> list:
    """Deterministic city selection for an article.

    Returns a list of n dicts: [{'city', 'state', 'slug', 'climate_type'}, ...].
    Same (article_slug, cluster) always returns the same cities.

    Selection is per-climate hash-shuffle: each article gets its own deterministic
    ordering of every climate pool, then takes the top `count` for that climate.
    This avoids the contiguous-window picking pattern that caused the previous
    algorithm to repeatedly favor cities at certain pool indices (Tucson at 7
    inbound while NYC/Columbus/Buffalo sat at 0 — see M6 in ACTION-PLAN).
    """
    pools = load_city_pools(xlsx_path)

    weights = CLUSTER_CLIMATE_WEIGHTS.get(cluster, "all_rotated")
    if weights in ("all_rotated", "seasonal"):
        total = sum(len(p) for p in pools.values())
        weights = {ct: len(p) / total for ct, p in pools.items() if p}

    alloc = _allocate(weights, n)

    picks = []
    for climate, count in alloc.items():
        pool = pools.get(climate, [])
        if not pool or count == 0:
            continue
        ordered = sorted(
            pool,
            key=lambda c: _city_hash_score(article_slug, cluster, climate, c['slug']),
        )
        picks.extend(ordered[:count])

    # Backfill: if a small pool couldn't deliver its allocated share, pull from
    # the union of remaining cities, again hash-shuffled deterministically.
    if len(picks) < n:
        picked_slugs = {p['slug'] for p in picks}
        remaining = [c for pool in pools.values() for c in pool if c['slug'] not in picked_slugs]
        remaining.sort(
            key=lambda c: _city_hash_score(article_slug, cluster, 'backfill', c['slug']),
        )
        for c in remaining:
            picks.append(c)
            if len(picks) >= n:
                break

    return picks[:n]


def get_state_hubs(cities: list, max_hubs: int = 2) -> list:
    """Return up to max_hubs distinct (state_slug, state_abbr) from the given cities."""
    seen_states = []
    for c in cities:
        st = c['state']
        if st not in seen_states:
            seen_states.append(st)
    return [(STATE_SLUG[s], s) for s in seen_states[:max_hubs] if s in STATE_SLUG]


# ---------------------------------------------------------------------------
# CLI for manual verification
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python article_city_linker.py <article_slug> <cluster> [n]")
        print("Clusters: C1_ac C2_furnace C3_heatpump C4_cost C5_compare C6_maint")
        sys.exit(1)
    slug, cluster = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    cities = pick_cities(slug, cluster, n)
    print(f"\nArticle: {slug}  |  Cluster: {cluster}  |  N={n}")
    print("-" * 60)
    for c in cities:
        print(f"  {c['city']}, {c['state']:>3} ({c['climate_type']:>11})  ->  locations/{c['slug']}.html")
    state_hubs = get_state_hubs(cities)
    print(f"\nState hubs:")
    for slug_s, abbr in state_hubs:
        print(f"  {abbr}  ->  locations/{slug_s}.html")
