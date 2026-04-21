"""
One-off surgical insertion: add a "Common HVAC Issues in <State>" section
to every state hub, linking to cluster articles whose focus matches the
state's peak HVAC demand season (Summer / Winter / Both).

All data comes from states.xlsx ("Peak HVAC Demand Season" column) and
all linked URLs are articles that already exist on the site. No invented
prose — the intro sentence states a fact already present in xlsx; the
bullets are link-only with brief descriptions of each article's topic.

Inserts a new <section> BEFORE the "<!-- Service Areas -->" anchor comment.
Byte-preserving: reads/writes with newline="" to keep CRLF, matches the
surrounding indentation style used by the existing state hub template.

Run:   python scripts/add_state_hub_common_issues.py
Idempotent — re-running is a no-op (skips files that already have the
"Common HVAC Issues in" H2).
"""

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
LOCATIONS_DIR = ROOT / "locations"
STATES_XLSX = ROOT / "states.xlsx"


# Article link sets per peak demand season. Every href points to an
# article file that already exists on the site. State hubs sit at
# /locations/<state>.html, so paths are relative with "../" prefix.

SUMMER_LINKS = [
    ("../articles/complete-ac-troubleshooting-guide.html",
     "Complete AC troubleshooting guide",
     "the full diagnostic framework for every AC failure mode"),
    ("../articles/ac-not-cooling-below-80.html",
     "AC running but not cooling below 80&deg;?",
     "low refrigerant, weak capacitor, dirty coil, or undersized system"),
    ("../articles/ac-circuit-breaker-trips.html",
     "AC circuit breaker keeps tripping",
     "failing compressor, weak capacitor, or dirty condenser coil"),
    ("../articles/ac-freezing-up-in-summer.html",
     "AC freezing up in summer",
     "airflow restriction or refrigerant problem"),
    ("../articles/water-dripping-from-vent.html",
     "Water dripping from ceiling vent",
     "clogged condensate drain or frozen-coil thaw"),
    ("../articles/ac-contactor-clicking.html",
     "AC contactor clicking but nothing happens",
     "electrical fault in the outdoor unit"),
]

WINTER_LINKS = [
    ("../article-furnace.html",
     "Furnace not igniting?",
     "ignition failure diagnosis and repair costs"),
    ("../articles/furnace-blowing-cold-air-winter.html",
     "Furnace blowing cold air in winter",
     "filter, ignitor, flame sensor, or gas valve fault"),
    ("../article-carbon-monoxide.html",
     "Carbon monoxide: the invisible killer",
     "CO detection, warning signs, and safety steps"),
    ("../article-winter-storm.html",
     "Protect your HVAC during a winter storm",
     "freeze prep, power-outage safeguards, post-storm inspection"),
    ("../article-heat-pump.html",
     "Heat pump not working?",
     "cold-weather performance, defrost cycle, common failures"),
    ("../article-maintenance.html",
     "12-month HVAC maintenance checklist",
     "seasonal tune-up timing and pro-only tasks"),
]

BOTH_LINKS = [
    ("../articles/complete-ac-troubleshooting-guide.html",
     "Complete AC troubleshooting guide",
     "diagnosis for every AC failure mode"),
    ("../article-furnace.html",
     "Furnace not igniting?",
     "ignition failure diagnosis and repair costs"),
    ("../article-heat-pump.html",
     "Heat pump not working?",
     "year-round heat-pump performance and repairs"),
    ("../articles/ac-circuit-breaker-trips.html",
     "AC circuit breaker keeps tripping",
     "electrical fault in the outdoor unit"),
    ("../article-maintenance.html",
     "12-month HVAC maintenance checklist",
     "seasonal tune-ups for both cooling and heating"),
    ("../articles/2026-hvac-cost-guide.html",
     "Honest 2026 HVAC cost guide",
     "diagnostic, repair, and replacement pricing"),
]

INTRO_BY_SEASON = {
    "Summer": "Cooling is the dominant HVAC demand in {state}. The most common emergency and troubleshooting topics for a cooling-driven climate:",
    "Winter": "{state}'s long heating season drives most HVAC calls. Common furnace and heating failures we see:",
    "Both": "{state} sees both cooling and heating demand year-round. Common HVAC troubleshooting topics for a mixed-demand climate:",
}


def build_section(state_name: str, season: str) -> str:
    """Build the full HTML section block matching the existing indent pattern
    of the state hub template. Starts with a leading newline so it slots in
    cleanly before the '<!-- Service Areas -->' anchor."""
    if season == "Summer":
        links = SUMMER_LINKS
    elif season == "Winter":
        links = WINTER_LINKS
    else:
        links = BOTH_LINKS

    intro = INTRO_BY_SEASON.get(season, INTRO_BY_SEASON["Both"]).format(state=state_name)

    lis = []
    for href, label, desc in links:
        lis.append(
            f'            <li><a href="{href}" style="color: var(--orange-dark); font-weight: 600;">{label}</a> &mdash; {desc}</li>'
        )
    lis_html = "\n".join(lis)

    return (
        "\n"
        "    <!-- Common HVAC Issues -->\n"
        "    <section class=\"section\" style=\"padding: 0;\">\n"
        "      <div class=\"container\">\n"
        "        <div class=\"city-services\" style=\"margin-bottom: 40px;\">\n"
        f"          <h2>Common HVAC Issues in {state_name}</h2>\n"
        f"          <p style=\"font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);\">{intro}</p>\n"
        "          <ul>\n"
        f"{lis_html}\n"
        "          </ul>\n"
        "        </div>\n"
        "      </div>\n"
        "    </section>\n"
    )


def patch_file(path: Path, state_name: str, season: str) -> str:
    """Return 'patched' | 'already_has_section' | 'anchor_not_found'."""
    with path.open("r", encoding="utf-8", newline="") as fh:
        text = fh.read()

    if "<h2>Common HVAC Issues in" in text:
        return "already_has_section"

    anchor = "    <!-- Service Areas -->"
    if anchor not in text:
        return "anchor_not_found"

    block = build_section(state_name, season)

    # Match surrounding line endings. If file uses CRLF, convert our block.
    if "\r\n" in text:
        block = block.replace("\n", "\r\n")

    new_text = text.replace(anchor, block + "\n" + anchor, 1) if "\r\n" not in text \
        else text.replace(anchor, block + "\r\n" + anchor, 1)

    # Simpler: replace anchor with (block + anchor), preserving block's newline style
    # Re-do cleanly below to avoid confusion
    if "\r\n" in text:
        sep = "\r\n"
    else:
        sep = "\n"
    new_text = text.replace(anchor, block.rstrip("\r\n") + sep + anchor, 1)

    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(new_text)
    return "patched"


def main():
    df = pd.read_excel(STATES_XLSX)
    # Build state-name → peak-season lookup (normalize case)
    season_by_state = {
        str(row["State Name"]).strip(): str(row["Peak HVAC Demand Season"]).strip()
        for _, row in df.iterrows()
    }

    # State hub files: same detection as the Service-schema patch.
    state_pat = re.compile(
        r'"areaServed":\s*\{\s*"@type":\s*"State",\s*"name":\s*"(?P<state>[^"]+)"\s*\}',
        re.MULTILINE,
    )

    counts = {"patched": 0, "already_has_section": 0, "anchor_not_found": 0, "no_season_data": 0}
    failures = []
    per_season = {"Summer": 0, "Winter": 0, "Both": 0}

    for path in sorted(LOCATIONS_DIR.glob("*.html")):
        with path.open("r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        m = state_pat.search(text)
        if not m:
            continue  # not a state hub
        state_name = m.group("state")
        season = season_by_state.get(state_name)
        if not season or season not in ("Summer", "Winter", "Both"):
            counts["no_season_data"] += 1
            failures.append(f"{path.name}: unknown season '{season}' for state '{state_name}'")
            continue

        result = patch_file(path, state_name, season)
        counts[result] = counts.get(result, 0) + 1
        if result == "patched":
            per_season[season] = per_season.get(season, 0) + 1
        elif result == "anchor_not_found":
            failures.append(f"{path.name}: '<!-- Service Areas -->' anchor not found")

    print(f"Results:")
    print(f"  patched:             {counts['patched']} (Summer: {per_season['Summer']}, Winter: {per_season['Winter']}, Both: {per_season['Both']})")
    print(f"  already_has_section: {counts['already_has_section']}")
    print(f"  anchor_not_found:    {counts['anchor_not_found']}")
    print(f"  no_season_data:      {counts['no_season_data']}")
    if failures:
        print("\nFailures:")
        for msg in failures:
            print(f"  - {msg}")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
