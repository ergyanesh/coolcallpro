"""
One-off surgical replacement: swap the universal hero-subtext lead on every
state hub for a climate-group-specific lead derived from states.xlsx.

Current lead (same on all 51 hubs):
    "Connect with independent local HVAC professionals across every city
     and ZIP code in {State}. {hero_service}"

New lead (five variants keyed by the same climate profile the generator
already uses for hero_service):
    Tropical (Hawaii):
        "Independent local HVAC professionals serve every city and ZIP
         code across {State}'s year-round cooling climate. {hero_service}"
    Heavy-winter / Subarctic (Alaska):
        "Independent local HVAC professionals serve every city and ZIP
         code across {State}'s subarctic climate and extended heating
         season. {hero_service}"
    Winter-dominant:
        "Independent local HVAC professionals serve every city and ZIP
         code across {State}'s long heating season. {hero_service}"
    Summer-dominant:
        "Independent local HVAC professionals serve every city and ZIP
         code across {State}'s cooling-dominated climate. {hero_service}"
    Both / Mixed:
        "Independent local HVAC professionals serve every city and ZIP
         code across {State}'s mixed cooling and heating demand.
         {hero_service}"

Every lead clause restates the xlsx-driven climate category in plain
English; no new numeric claims are introduced. The second sentence
(hero_service) is preserved verbatim from the existing file to avoid
touching content the generator's state_profile already drives.

Byte-preserving (newline=""), CRLF-preserving, idempotent (skips files
where the sentinel "Independent local HVAC professionals serve" is
already present).

Run: python scripts/replace_state_hub_hero_subtext.py
"""

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
LOCATIONS_DIR = ROOT / "locations"
STATES_XLSX = ROOT / "states.xlsx"

SENTINEL = "Independent local HVAC professionals serve"


def climate_lead(peak: str, system: str, zones: str) -> str:
    """Return the noun-phrase lead clause (without state possessive prefix).

    The lead restates a categorical fact already present in states.xlsx and
    does not introduce numeric claims. The "subarctic" phrase is reserved
    for states that contain IECC Climate Zone 8 (Subarctic) in the
    "Climate Zones Present" column -- only Alaska qualifies. States with
    Zone 7 alone ("Very Cold" in the IECC naming) get the generic
    "long heating season" lead because their population centers largely
    sit in warmer zones, and calling their entire climate "subarctic"
    would be an assumption the xlsx does not support."""
    p = (peak or "").lower()
    s = (system or "").lower()
    z = str(zones or "").lower()
    # Split on comma + whitespace for strict token matching on IECC zones
    # (so "7, 8" -> {"7", "8"} and "5A, 6A, 7" -> {"5a", "6a", "7"}; a raw
    # substring check on "8" would otherwise not match the full CSV cleanly).
    z_tokens = {t.strip() for t in z.replace(",", " ").split() if t.strip()}

    # Tropical: Hawaii (mini-split dominant or Zone 1A only)
    if "mini-split" in s or ("1a" in z_tokens and "2a" not in z_tokens):
        return "year-round cooling climate"
    # Subarctic: Peak=Winter + IECC Zone 8 present (Alaska only in current data).
    # Zone 7 alone ("Very Cold") does not qualify -- states like MI, MN, WI
    # have population centers in warmer zones, so labeling their entire
    # climate "subarctic" would overreach what states.xlsx asserts.
    if "winter" in p and "8" in z_tokens:
        return "subarctic climate and extended heating season"
    # Winter-dominant (any Winter peak without Zone 8)
    if "winter" in p:
        return "long heating season"
    # Summer-dominant
    if "summer" in p:
        return "cooling-dominated climate"
    # Balanced / Both
    return "mixed cooling and heating demand"


def build_new_paragraph(state_name: str, lead: str, hero_service: str) -> str:
    """Build the new hero paragraph, preserving the state's existing
    hero_service sentence byte-for-byte."""
    return (
        f"<p>Independent local HVAC professionals serve every city and ZIP code across "
        f"{state_name}&rsquo;s {lead}. {hero_service}</p>"
    )


def patch_file(path: Path, state_name: str, peak: str, system: str, zones: str) -> str:
    with path.open("r", encoding="utf-8", newline="") as fh:
        text = fh.read()

    if SENTINEL in text:
        return "already_replaced"

    # Match: "<p>Connect with independent local HVAC professionals across
    # every city and ZIP code in {State}. <hero_service>.</p>"
    # We pluck <hero_service> out of the file (preserving it verbatim) and
    # reassemble the paragraph with the new lead.
    old_prefix = (
        f"<p>Connect with independent local HVAC professionals across every "
        f"city and ZIP code in {re.escape(state_name)}\\. "
    )
    # hero_service varies: the 5 known values all end in "available 24/7." and sit
    # before "</p>". Non-greedy match captures it exactly once.
    pat = re.compile(old_prefix + r"(?P<service>[^<]*?available 24/7\.)</p>")
    m = pat.search(text)
    if not m:
        return "pattern_not_found"

    hero_service = m.group("service")
    lead = climate_lead(peak, system, zones)
    new_para = build_new_paragraph(state_name, lead, hero_service)
    new_text = text[: m.start()] + new_para + text[m.end() :]

    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(new_text)
    return "patched"


def main() -> int:
    df = pd.read_excel(STATES_XLSX)
    required = [
        "State Name",
        "Peak HVAC Demand Season",
        "Dominant HVAC System Type",
        "Climate Zones Present",
    ]
    for col in required:
        if col not in df.columns:
            print(f"ERROR: states.xlsx missing '{col}'.")
            return 2
    by_name = {
        str(r["State Name"]).strip(): {
            "peak": str(r["Peak HVAC Demand Season"] or "").strip(),
            "system": str(r["Dominant HVAC System Type"] or "").strip(),
            "zones": str(r["Climate Zones Present"] or "").strip(),
        }
        for _, r in df.iterrows()
    }

    state_hub_pat = re.compile(
        r'"areaServed":\s*\{\s*"@type":\s*"State",\s*"name":\s*"(?P<state>[^"]+)"\s*\}',
        re.MULTILINE,
    )
    counts = {"patched": 0, "already_replaced": 0, "pattern_not_found": 0, "no_data": 0}
    failures = []
    for path in sorted(LOCATIONS_DIR.glob("*.html")):
        with path.open("r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        m = state_hub_pat.search(text)
        if not m:
            continue
        state_name = m.group("state")
        d = by_name.get(state_name)
        if not d:
            counts["no_data"] += 1
            failures.append(f"{path.name}: no xlsx row for '{state_name}'")
            continue
        result = patch_file(path, state_name, d["peak"], d["system"], d["zones"])
        counts[result] = counts.get(result, 0) + 1
        if result == "pattern_not_found":
            failures.append(f"{path.name}: hero paragraph pattern not found")

    print("Results:")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    if failures:
        print("\nFailures:")
        for msg in failures:
            print(f"  - {msg}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
