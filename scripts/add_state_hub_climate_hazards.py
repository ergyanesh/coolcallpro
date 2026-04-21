"""
One-off surgical insertion: add a "Climate Hazards Affecting <State> HVAC
Systems" section to every state hub. Hazard list per state is read from
states.xlsx ("Climate Hazards" column, comma-separated). Per-hazard HVAC
impact + pro-action copy is read from climate_hazards.json.

All facts sourced from FEMA National Risk Index (hazard categories +
per-state exposure) and NOAA NCEI storm data. Every action sentence routes
to a technician or call-a-pro path per the Cool Call Pro editorial safety
policy (safety_rules.py). No homeowner hazardous-task instructions.

Inserts a new <section> BEFORE the "<!-- Service Areas -->" anchor. Since
the Common HVAC Issues section (added in an earlier commit) was inserted
at the same anchor, this new Climate Hazards block lands between Common
HVAC Issues and Service Areas.

Byte-preserving: reads/writes with newline="" to keep CRLF, matches the
surrounding indentation style used by the existing state hub template.

Run:   python scripts/add_state_hub_climate_hazards.py
Idempotent -- re-running is a no-op (skips files that already have the
"Climate Hazards Affecting" H2).
"""

import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
LOCATIONS_DIR = ROOT / "locations"
STATES_XLSX = ROOT / "states.xlsx"
HAZARDS_JSON = ROOT / "climate_hazards.json"

ANCHOR = "    <!-- Service Areas -->"
SENTINEL_H2 = "<h2>Climate Hazards Affecting"


def load_hazard_vocab() -> dict:
    with HAZARDS_JSON.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data["hazards"]


def load_state_hazards() -> dict:
    df = pd.read_excel(STATES_XLSX)
    if "Climate Hazards" not in df.columns:
        print("ERROR: states.xlsx has no 'Climate Hazards' column.")
        print("Run: python scripts/add_states_climate_hazards_column.py")
        sys.exit(2)
    out = {}
    for _, row in df.iterrows():
        state = str(row["State Name"]).strip()
        raw = str(row["Climate Hazards"]).strip()
        if not raw or raw.lower() == "nan":
            continue
        out[state] = [h.strip() for h in raw.split(",") if h.strip()]
    return out


def format_hazard_list_prose(hazards: list[str]) -> str:
    """Oxford-comma list for the intro sentence, wrapping each in <strong>."""
    strong = [f"<strong>{h}</strong>" for h in hazards]
    if len(strong) == 1:
        return strong[0]
    if len(strong) == 2:
        return f"{strong[0]} and {strong[1]}"
    return ", ".join(strong[:-1]) + f", and {strong[-1]}"


def build_section(state_name: str, hazards: list[str], vocab: dict) -> str:
    """Build the Climate Hazards <section> block. Starts and ends with a
    newline so it slots in cleanly before the Service Areas anchor, matching
    the indentation of the existing state hub template (4-space base, 6-space
    container, 8-space inner div, 10-space headings/paragraphs)."""
    intro_list = format_hazard_list_prose(hazards)

    lis = []
    for hz in hazards:
        info = vocab.get(hz)
        if not info:
            raise KeyError(f"Unknown hazard '{hz}' for state '{state_name}' "
                           f"-- add it to climate_hazards.json")
        lis.append(
            f"            <li><strong>{hz}:</strong> {info['impact']} {info['action']}</li>"
        )
    lis_html = "\n".join(lis)

    return (
        "\n"
        "    <!-- Climate Hazards -->\n"
        "    <section class=\"section\" style=\"padding: 0;\">\n"
        "      <div class=\"container\">\n"
        "        <div class=\"city-services\" style=\"margin-bottom: 40px;\">\n"
        f"          <h2>Climate Hazards Affecting {state_name} HVAC Systems</h2>\n"
        f"          <p style=\"font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);\">According to the FEMA National Risk Index and NOAA storm data, {state_name} faces elevated exposure to {intro_list}. Each event damages or stresses residential HVAC systems in specific ways that an HVAC professional should diagnose after the fact.</p>\n"
        "          <ul>\n"
        f"{lis_html}\n"
        "          </ul>\n"
        "          <p style=\"font-size: 0.9rem; color: var(--gray-700); margin-top: 20px;\">Source: <a href=\"https://hazards.fema.gov/nri/\" rel=\"nofollow noopener\" style=\"color: var(--orange-dark);\">FEMA National Risk Index</a> and <a href=\"https://www.ncei.noaa.gov/access/billions/\" rel=\"nofollow noopener\" style=\"color: var(--orange-dark);\">NOAA National Centers for Environmental Information</a>.</p>\n"
        "        </div>\n"
        "      </div>\n"
        "    </section>\n"
    )


def patch_file(path: Path, state_name: str, hazards: list[str], vocab: dict) -> str:
    """Return 'patched' | 'already_has_section' | 'anchor_not_found'."""
    with path.open("r", encoding="utf-8", newline="") as fh:
        text = fh.read()

    if SENTINEL_H2 in text:
        return "already_has_section"

    if ANCHOR not in text:
        return "anchor_not_found"

    block = build_section(state_name, hazards, vocab)

    sep = "\r\n" if "\r\n" in text else "\n"
    if sep == "\r\n":
        block = block.replace("\n", "\r\n")

    new_text = text.replace(ANCHOR, block.rstrip("\r\n") + sep + ANCHOR, 1)

    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(new_text)
    return "patched"


def main() -> int:
    vocab = load_hazard_vocab()
    state_hazards = load_state_hazards()

    state_pat = re.compile(
        r'"areaServed":\s*\{\s*"@type":\s*"State",\s*"name":\s*"(?P<state>[^"]+)"\s*\}',
        re.MULTILINE,
    )

    counts = {"patched": 0, "already_has_section": 0, "anchor_not_found": 0,
              "no_hazards_data": 0, "unknown_hazard": 0}
    failures = []

    for path in sorted(LOCATIONS_DIR.glob("*.html")):
        with path.open("r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        m = state_pat.search(text)
        if not m:
            continue  # not a state hub
        state_name = m.group("state")
        hazards = state_hazards.get(state_name)
        if not hazards:
            counts["no_hazards_data"] += 1
            failures.append(f"{path.name}: no hazards data in states.xlsx for '{state_name}'")
            continue
        try:
            result = patch_file(path, state_name, hazards, vocab)
        except KeyError as exc:
            counts["unknown_hazard"] += 1
            failures.append(f"{path.name}: {exc}")
            continue
        counts[result] = counts.get(result, 0) + 1
        if result == "anchor_not_found":
            failures.append(f"{path.name}: '<!-- Service Areas -->' anchor not found")

    print("Results:")
    print(f"  patched:             {counts['patched']}")
    print(f"  already_has_section: {counts['already_has_section']}")
    print(f"  anchor_not_found:    {counts['anchor_not_found']}")
    print(f"  no_hazards_data:     {counts['no_hazards_data']}")
    print(f"  unknown_hazard:      {counts['unknown_hazard']}")
    if failures:
        print("\nFailures:")
        for msg in failures:
            print(f"  - {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
