"""
One-off surgical replacement: swap the universal "How It Works" section on
every state hub for a state-specific "Why Call a {State} HVAC Pro" section
populated entirely from states.xlsx.

The new section renders four factual cards:
  1. Climate Load     -- Avg Summer High, Avg Winter Low, CDD, HDD
  2. Licensing        -- License Requirement + (for "Yes" states only) Licensing Body/Agency
  3. Efficiency Code  -- SEER2 Minimum + SEER2 Region (federal standard effective 2023-01-01)
  4. Weather Risks    -- Climate Hazards (3 per state, FEMA NRI-sourced)

No invented data. Each bullet cites a specific xlsx cell; the FEMA NRI and
the federal efficiency-standard effective date are the only non-xlsx
claims, both of which are independently verifiable public facts.

The replacement matches the existing visual structure (section-dark,
steps-grid with step-card children, the identical Call Now CTA) so the
visual flow around the FAQs section is preserved.

Byte-preserving (newline=""), CRLF-preserving, idempotent (skips files
that already contain the new sentinel).

Run: python scripts/replace_state_hub_how_it_works.py
"""

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
LOCATIONS_DIR = ROOT / "locations"
STATES_XLSX = ROOT / "states.xlsx"

SENTINEL = "Why Call a"

START_ANCHOR = "    <!-- How It Works -->"

# Match from START_ANCHOR inclusive through the first "    </section>" that
# precedes the FAQs section. Non-greedy; lookahead preserves the whitespace
# between the removed section and <!-- FAQs -->.
BLOCK_PATTERN_LF = re.compile(
    r'    <!-- How It Works -->.*?    </section>(?=\n+    <!-- FAQs -->)',
    re.DOTALL,
)
BLOCK_PATTERN_CRLF = re.compile(
    r'    <!-- How It Works -->.*?    </section>(?=(?:\r\n)+    <!-- FAQs -->)',
    re.DOTALL,
)


def _n(v) -> str:
    """Format an integer with a thousands separator. Accepts int, float, or str."""
    if v is None:
        return ""
    try:
        return f"{int(float(v)):,}"
    except (TypeError, ValueError):
        return str(v)


def build_block(row: dict) -> str:
    """Build the full replacement section HTML. All text is drawn from the
    xlsx row provided. Raises ValueError if required fields are missing so
    the patcher fails loudly rather than silently emitting blanks."""
    name = str(row.get("State Name", "")).strip()
    if not name:
        raise ValueError("missing State Name")

    sh = row.get("Avg Summer High (F)")
    wl = row.get("Avg Winter Low (F)")
    cdd = row.get("Annual Cooling Degree Days")
    hdd = row.get("Annual Heating Degree Days")
    seer_min = row.get("SEER2 Minimum")
    seer_region = str(row.get("SEER2 Region", "")).strip()
    req = str(row.get("State HVAC License Requirement", "")).strip()
    agency = str(row.get("Licensing Body/Agency", "")).strip()
    hazards_csv = str(row.get("Climate Hazards", "")).strip()

    missing = [k for k, v in {
        "Avg Summer High (F)": sh,
        "Avg Winter Low (F)": wl,
        "Annual Cooling Degree Days": cdd,
        "Annual Heating Degree Days": hdd,
        "SEER2 Minimum": seer_min,
        "SEER2 Region": seer_region,
        "State HVAC License Requirement": req,
        "Climate Hazards": hazards_csv,
    }.items() if v is None or v == "" or str(v).lower() == "nan"]
    if missing:
        raise ValueError(f"missing xlsx fields for {name}: {missing}")

    hazards = [h.strip() for h in hazards_csv.split(",") if h.strip()]
    if len(hazards) < 3:
        raise ValueError(f"{name} has fewer than 3 hazards: {hazards}")

    # Licensing bullet varies by requirement value
    if req.lower().startswith("yes"):
        lic_p = (
            f"{name} requires HVAC contractors to hold a state license from the "
            f"<strong>{agency}</strong>. Unlicensed work can void manufacturer "
            f"warranties and complicate insurance claims."
        )
    else:
        lic_p = (
            f"{name} does not issue a statewide HVAC contractor license; licensing "
            f"and permits are handled by local cities and counties. Hire a contractor "
            f"who carries liability insurance, pulls permits with your local building "
            f"department, and can provide local references."
        )

    # Number formatting
    sh_s = _n(sh)
    wl_s = _n(wl)
    cdd_s = _n(cdd)
    hdd_s = _n(hdd)
    # SEER2 minimum can be a float like 13.4 or 14.3
    try:
        seer_min_s = f"{float(seer_min):g}"
    except (TypeError, ValueError):
        seer_min_s = str(seer_min)

    hz1, hz2, hz3 = hazards[0], hazards[1], hazards[2]

    return (
        f"    <!-- Why Call a {name} Pro -->\n"
        f"    <section class=\"section section-dark\" id=\"why-pro\">\n"
        f"      <div class=\"container\">\n"
        f"        <div class=\"section-header\">\n"
        f"          <span class=\"section-tag\"\n"
        f"            style=\"background: rgba(255,165,0,0.15); color: var(--orange-light); border-color: rgba(255,165,0,0.3);\">&#128205;\n"
        f"            {name} HVAC Context</span>\n"
        f"          <h2 class=\"section-title\">Why Call a {name} HVAC Pro</h2>\n"
        f"          <p class=\"section-sub\">Four facts from climate and licensing data specific to <strong>{name}</strong>.</p>\n"
        f"        </div>\n"
        f"\n"
        f"        <div class=\"steps-grid\">\n"
        f"\n"
        f"          <div class=\"step-card\">\n"
        f"            <div class=\"step-number\">01</div>\n"
        f"            <div class=\"step-icon\">&#127777;&#65039;</div>\n"
        f"            <h3>Climate Load</h3>\n"
        f"            <p>{name} averages <strong>{sh_s}&deg;F</strong> summer highs and <strong>{wl_s}&deg;F</strong> winter lows, with <strong>{cdd_s}</strong> annual cooling degree days and <strong>{hdd_s}</strong> heating degree days. A mis-sized or poorly-charged system fails early under that load.</p>\n"
        f"          </div>\n"
        f"\n"
        f"          <div class=\"step-card\">\n"
        f"            <div class=\"step-number\">02</div>\n"
        f"            <div class=\"step-icon\">&#128221;</div>\n"
        f"            <h3>Licensing</h3>\n"
        f"            <p>{lic_p}</p>\n"
        f"          </div>\n"
        f"\n"
        f"          <div class=\"step-card\">\n"
        f"            <div class=\"step-number\">03</div>\n"
        f"            <div class=\"step-icon\">&#128161;</div>\n"
        f"            <h3>Efficiency Code</h3>\n"
        f"            <p>New central AC units installed in {name} must meet <strong>SEER2 {seer_min_s}</strong> (<strong>{seer_region}</strong> SEER2 region) under the federal efficiency standard effective January 1, 2023. A pro ensures the installed system is compliant and sized correctly.</p>\n"
        f"          </div>\n"
        f"\n"
        f"          <div class=\"step-card\">\n"
        f"            <div class=\"step-number\">04</div>\n"
        f"            <div class=\"step-icon\">&#127744;&#65039;</div>\n"
        f"            <h3>Weather Risks</h3>\n"
        f"            <p>FEMA's National Risk Index identifies <strong>{hz1}</strong>, <strong>{hz2}</strong>, and <strong>{hz3}</strong> as elevated hazards in {name}. A technician inspects outdoor equipment for damage after any major weather event before restart.</p>\n"
        f"          </div>\n"
        f"\n"
        f"        </div>\n"
        f"\n"
        f"        <div style=\"text-align: center; margin-top: 48px;\">\n"
        f"          <a href=\"tel:+18445821795\" class=\"btn btn-primary btn-lg btn-vibrate\"><span class=\"phone-icon\">&#128222;</span> Call Now &#8212; (844) 582-1795</a>\n"
        f"        </div>\n"
        f"      </div>\n"
        f"    </section>"
    )


def patch_file(path: Path, row: dict) -> str:
    with path.open("r", encoding="utf-8", newline="") as fh:
        text = fh.read()

    if SENTINEL in text and "Why Call a " in text:
        return "already_replaced"
    if START_ANCHOR not in text:
        return "anchor_not_found"

    is_crlf = "\r\n" in text
    pattern = BLOCK_PATTERN_CRLF if is_crlf else BLOCK_PATTERN_LF

    if not pattern.search(text):
        return "block_pattern_not_found"

    block = build_block(row)
    if is_crlf:
        block = block.replace("\n", "\r\n")

    new_text, n_subs = pattern.subn(block, text, count=1)
    if n_subs != 1:
        return "replace_failed"

    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(new_text)
    return "patched"


def main() -> int:
    df = pd.read_excel(STATES_XLSX)
    by_name = {str(r["State Name"]).strip(): dict(r) for _, r in df.iterrows()}

    state_hub_pat = re.compile(
        r'"areaServed":\s*\{\s*"@type":\s*"State",\s*"name":\s*"(?P<state>[^"]+)"\s*\}',
        re.MULTILINE,
    )
    counts = {"patched": 0, "already_replaced": 0,
              "anchor_not_found": 0, "block_pattern_not_found": 0,
              "no_data": 0, "error": 0, "replace_failed": 0}
    failures = []
    for path in sorted(LOCATIONS_DIR.glob("*.html")):
        with path.open("r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        m = state_hub_pat.search(text)
        if not m:
            continue
        state_name = m.group("state")
        row = by_name.get(state_name)
        if not row:
            counts["no_data"] += 1
            failures.append(f"{path.name}: no xlsx data for '{state_name}'")
            continue
        try:
            result = patch_file(path, row)
        except ValueError as exc:
            counts["error"] += 1
            failures.append(f"{path.name}: {exc}")
            continue
        counts[result] = counts.get(result, 0) + 1
        if result in ("anchor_not_found", "block_pattern_not_found", "replace_failed"):
            failures.append(f"{path.name}: {result}")

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
