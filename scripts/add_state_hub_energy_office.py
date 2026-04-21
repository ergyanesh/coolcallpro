"""
One-off surgical insertion: add a "State Energy Office and HVAC Rebate
Resources" section to every state hub.

Reads per-state agency name + URL from states.xlsx ("State Energy Office
Name" / "State Energy Office URL" columns, populated from NASEO data via
scripts/add_states_energy_office_columns.py). Also emits a per-state
DSIRE programs link and a standing ENERGY STAR federal tax credits link.

Inserts BEFORE the "<!-- Service Areas -->" anchor, which places the block
directly after Climate Hazards on every hub.

Byte-preserving: reads/writes with newline="" to keep CRLF byte-for-byte.
Idempotent: re-running is a no-op (skips files that already have the
"Energy Office and HVAC Rebate Resources" H2).

All facts sourced from:
  - NASEO State Energy Offices Directory (https://www.naseo.org/state-energy-offices)
  - DSIRE programs database (https://programs.dsireusa.org/)
  - ENERGY STAR federal tax credits page (https://www.energystar.gov/about/federal-tax-credits)

Run:   python scripts/add_state_hub_energy_office.py
"""

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
LOCATIONS_DIR = ROOT / "locations"
STATES_XLSX = ROOT / "states.xlsx"

ANCHOR = "    <!-- Service Areas -->"
SENTINEL_H2 = "Energy Office and HVAC Rebate Resources"


def load_state_data() -> dict:
    df = pd.read_excel(STATES_XLSX)
    required = ["State Name", "State Abbreviation",
                "State Energy Office Name", "State Energy Office URL"]
    for col in required:
        if col not in df.columns:
            print(f"ERROR: states.xlsx missing column '{col}'.")
            print("Run: python scripts/add_states_energy_office_columns.py")
            sys.exit(2)
    out = {}
    for _, row in df.iterrows():
        abbr = str(row["State Abbreviation"]).strip()
        name = str(row["State Name"]).strip()
        office = str(row["State Energy Office Name"]).strip()
        url = str(row["State Energy Office URL"]).strip()
        if abbr and url and url.lower() != "nan":
            out[name] = {"abbr": abbr, "office": office, "url": url}
    return out


def strip_scheme(url: str) -> str:
    """Shorten a URL to a user-friendly display form (strip https:// + trailing /)."""
    s = re.sub(r"^https?://", "", url).rstrip("/")
    return s


def build_section(state_name: str, abbr: str, office: str, url: str) -> str:
    """Pure-content section (no leading/trailing newlines). Same shape as
    the Common HVAC Issues and Climate Hazards builders so the generator's
    _compose_state_hub_extra_sections helper can join them cleanly."""
    display = strip_scheme(url)
    dsire_url = f"https://programs.dsireusa.org/system/program?state={abbr}"
    return (
        "    <!-- State Energy Office Resources -->\n"
        "    <section class=\"section\" style=\"padding: 0;\">\n"
        "      <div class=\"container\">\n"
        "        <div class=\"city-services\" style=\"margin-bottom: 40px;\">\n"
        f"          <h2>{state_name} Energy Office and HVAC Rebate Resources</h2>\n"
        f"          <p style=\"font-size: 1.05rem; line-height: 1.85; color: var(--gray-700);\">For current HVAC rebates, energy-efficiency incentives, and federal Inflation Reduction Act (IRA) program coordination in {state_name}, consult these authoritative sources:</p>\n"
        "          <ul>\n"
        f"            <li><strong>{office}</strong> &mdash; <a href=\"{url}\" rel=\"nofollow noopener\" style=\"color: var(--orange-dark); font-weight: 600;\">{display}</a>. The state-level energy agency that coordinates HVAC rebates, weatherization assistance, and IRA program administration in {state_name}.</li>\n"
        f"            <li><strong>DSIRE {state_name} listing</strong> &mdash; <a href=\"{dsire_url}\" rel=\"nofollow noopener\" style=\"color: var(--orange-dark); font-weight: 600;\">programs.dsireusa.org/system/program?state={abbr}</a>. N.C. State University's comprehensive database of every federal, state, local, and utility incentive program available to {state_name} homeowners.</li>\n"
        "            <li><strong>ENERGY STAR federal tax credits</strong> &mdash; <a href=\"https://www.energystar.gov/about/federal-tax-credits\" rel=\"nofollow noopener\" style=\"color: var(--orange-dark); font-weight: 600;\">energystar.gov/about/federal-tax-credits</a>. IRA Section 25C tax credit up to $2,000 for qualifying heat pumps and $600 for central AC, available nationwide and stackable with state and utility rebates.</li>\n"
        "          </ul>\n"
        "          <p style=\"font-size: 0.9rem; color: var(--gray-700); margin-top: 20px;\">Source: <a href=\"https://www.naseo.org/state-energy-offices\" rel=\"nofollow noopener\" style=\"color: var(--orange-dark);\">NASEO State Energy Offices Directory</a> (National Association of State Energy Officials).</p>\n"
        "        </div>\n"
        "      </div>\n"
        "    </section>"
    )


def patch_file(path: Path, state_name: str, entry: dict) -> str:
    with path.open("r", encoding="utf-8", newline="") as fh:
        text = fh.read()

    if SENTINEL_H2 in text:
        return "already_has_section"
    if ANCHOR not in text:
        return "anchor_not_found"

    block = build_section(state_name, entry["abbr"], entry["office"], entry["url"])
    sep = "\r\n" if "\r\n" in text else "\n"
    if sep == "\r\n":
        block = block.replace("\n", "\r\n")

    # Insert before the Service Areas anchor. The anchor is preceded in the
    # file by "...</section>\n" (Climate Hazards' close, directly adjacent).
    # We emit: "\n" + block + "\n" so the result is
    # "...</section>\n" + "\n<block>\n" + "    <!-- Service Areas -->"
    # = one blank line before the new section, no blank after (same pattern
    # as the existing Climate Hazards -> Service Areas spacing).
    insertion = sep + block + sep
    new_text = text.replace(ANCHOR, insertion + ANCHOR, 1)

    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(new_text)
    return "patched"


def main() -> int:
    states = load_state_data()
    state_hub_pat = re.compile(
        r'"areaServed":\s*\{\s*"@type":\s*"State",\s*"name":\s*"(?P<state>[^"]+)"\s*\}',
        re.MULTILINE,
    )
    counts = {"patched": 0, "already_has_section": 0, "anchor_not_found": 0,
              "no_data": 0}
    failures = []
    for path in sorted(LOCATIONS_DIR.glob("*.html")):
        with path.open("r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        m = state_hub_pat.search(text)
        if not m:
            continue
        state_name = m.group("state")
        entry = states.get(state_name)
        if not entry:
            counts["no_data"] += 1
            failures.append(f"{path.name}: no xlsx data for state '{state_name}'")
            continue
        result = patch_file(path, state_name, entry)
        counts[result] = counts.get(result, 0) + 1
        if result == "anchor_not_found":
            failures.append(f"{path.name}: '<!-- Service Areas -->' anchor not found")

    print("Results:")
    print(f"  patched:             {counts['patched']}")
    print(f"  already_has_section: {counts['already_has_section']}")
    print(f"  anchor_not_found:    {counts['anchor_not_found']}")
    print(f"  no_data:             {counts['no_data']}")
    if failures:
        print("\nFailures:")
        for msg in failures:
            print(f"  - {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
