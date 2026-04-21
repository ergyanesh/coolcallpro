"""
One-off surgical insertion: add FAQ #6 ("What HVAC permits are required in
{State}?") to every state hub, in both the visible FAQ accordion and the
JSON-LD FAQPage schema.

Data source is states.xlsx:
  - "State HVAC License Requirement" column (36 "Yes" states + 15
    "Varies by jurisdiction" states across the 51 total)
  - "Licensing Body/Agency" column (cited verbatim in the Yes-states answer)

The answer text is factual and applies uniformly across all states in
its category:
  - Yes-states: permits are issued by local city/county building departments;
    contractor must carry state license from the named agency.
  - Varies-states: licensing + permits are handled at the local level.

Byte-preserving (newline="" preserves CRLF), idempotent (skips files that
already contain the FAQ #6 sentinel).

Run: python scripts/add_state_hub_permits_faq.py
"""

import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
LOCATIONS_DIR = ROOT / "locations"
STATES_XLSX = ROOT / "states.xlsx"

SENTINEL = "What HVAC permits are required in"

# JSON-LD insertion anchor: "          }\n        ]" -- the last question's
# closing brace followed by mainEntity's closing bracket. Unique per file
# (only the FAQPage array closes with that indent pattern).
SCHEMA_ANCHOR_LF = "          }\n        ]"
SCHEMA_ANCHOR_CRLF = "          }\r\n        ]"

# Visible-FAQ insertion anchor: the .faq-list div's closing </div>, right
# before the "Call Now" centered button. Unique per file.
VIS_ANCHOR_LF = "          </div>\n\n          <div style=\"text-align: center;"
VIS_ANCHOR_CRLF = "          </div>\r\n\r\n          <div style=\"text-align: center;"


def _answer_plain(state_name: str, req: str, agency: str) -> str:
    """Schema-safe plain-text answer (no HTML, em-dash preserved as U+2014)."""
    if str(req).strip().lower().startswith("yes"):
        return (
            f"HVAC work in {state_name} typically requires a mechanical or building permit "
            f"from your local city or county building department. Covered work includes central AC "
            f"replacement, furnace installation, refrigerant-line modifications, and duct changes. "
            f"The installer must also hold a state license issued by the {agency}, "
            f"and in most jurisdictions your technician pulls the permit on your behalf. "
            f"Permit fees, inspection requirements, and submittal rules vary by municipality — "
            f"confirm with your technician before work begins."
        )
    return (
        f"{state_name} does not impose a statewide HVAC contractor license. Permit and "
        f"licensing rules are set by the local city or county building department where the "
        f"work occurs. Most jurisdictions require a mechanical or building permit for central "
        f"AC replacement, furnace installation, gas-line connections, and duct modifications. "
        f"Ask your HVAC technician to confirm the specific permit requirements for your address "
        f"— they typically pull the permit on your behalf."
    )


def _answer_html(state_name: str, req: str, agency: str) -> str:
    """Visible-FAQ answer. Wraps the agency name in <strong> for Yes-states;
    uses &mdash; for the em-dash. Returns a single <p>...</p>."""
    if str(req).strip().lower().startswith("yes"):
        return (
            f"<p>HVAC work in {state_name} typically requires a mechanical or building permit "
            f"from your local city or county building department. Covered work includes central AC "
            f"replacement, furnace installation, refrigerant-line modifications, and duct changes. "
            f"The installer must also hold a state license issued by the <strong>{agency}</strong>, "
            f"and in most jurisdictions your technician pulls the permit on your behalf. "
            f"Permit fees, inspection requirements, and submittal rules vary by municipality &mdash; "
            f"confirm with your technician before work begins.</p>"
        )
    return (
        f"<p>{state_name} does not impose a statewide HVAC contractor license. Permit and "
        f"licensing rules are set by the local city or county building department where the "
        f"work occurs. Most jurisdictions require a mechanical or building permit for central "
        f"AC replacement, furnace installation, gas-line connections, and duct modifications. "
        f"Ask your HVAC technician to confirm the specific permit requirements for your address "
        f"&mdash; they typically pull the permit on your behalf.</p>"
    )


def _schema_entry(state_name: str, answer_plain: str) -> str:
    """Build the JSON-LD Question entry. json.dumps handles quote escaping
    and preserves the em-dash as a literal U+2014."""
    q = f"What HVAC permits are required in {state_name}?"
    return (
        ",\n"
        "          {\n"
        "            \"@type\": \"Question\",\n"
        f"            \"name\": {json.dumps(q, ensure_ascii=False)},\n"
        "            \"acceptedAnswer\": {\n"
        "              \"@type\": \"Answer\",\n"
        f"              \"text\": {json.dumps(answer_plain, ensure_ascii=False)}\n"
        "            }\n"
        "          }"
    )


def _visible_entry(state_name: str, answer_html: str) -> str:
    """Build the visible .faq-item block. Output has no leading/trailing
    newlines; caller inserts with the file's line-ending style."""
    q = f"What HVAC permits are required in {state_name}?"
    return (
        "            <div class=\"faq-item\">\n"
        "              <button class=\"faq-q\" aria-expanded=\"false\">\n"
        f"                <span>{q}</span>\n"
        "                <span class=\"faq-icon\"></span>\n"
        "              </button>\n"
        "              <div class=\"faq-a\">\n"
        "                <div class=\"faq-a-inner\">\n"
        f"                  {answer_html}\n"
        "                </div>\n"
        "              </div>\n"
        "            </div>"
    )


def patch_file(path: Path, state_name: str, req: str, agency: str) -> str:
    with path.open("r", encoding="utf-8", newline="") as fh:
        text = fh.read()

    if SENTINEL in text:
        return "already_has_faq"

    is_crlf = "\r\n" in text
    schema_anchor = SCHEMA_ANCHOR_CRLF if is_crlf else SCHEMA_ANCHOR_LF
    vis_anchor = VIS_ANCHOR_CRLF if is_crlf else VIS_ANCHOR_LF

    if schema_anchor not in text:
        return "schema_anchor_not_found"
    if vis_anchor not in text:
        return "vis_anchor_not_found"

    answer_plain = _answer_plain(state_name, req, agency)
    answer_html = _answer_html(state_name, req, agency)
    schema_entry = _schema_entry(state_name, answer_plain)
    visible_entry = _visible_entry(state_name, answer_html)

    if is_crlf:
        schema_entry = schema_entry.replace("\n", "\r\n")
        visible_entry = visible_entry.replace("\n", "\r\n")

    # Schema: inject new question entry just before the "          }\n        ]"
    # close -- i.e., append to the mainEntity array before the closing ].
    # schema_entry already starts with ",\n" and ends with the new "}"; place
    # it between the previous question's close and the ].
    sep = "\r\n" if is_crlf else "\n"
    schema_replacement = "          }" + schema_entry + sep + "        ]"
    text = text.replace(schema_anchor, schema_replacement, 1)

    # Visible: inject before the closing </div> of .faq-list + the centered
    # CTA that follows it. Preserve the blank line between the new item and
    # the closing div by prepending our entry with a newline and following
    # with the existing anchor exactly.
    vis_replacement = visible_entry + sep + vis_anchor
    text = text.replace(vis_anchor, vis_replacement, 1)

    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return "patched"


def main() -> int:
    df = pd.read_excel(STATES_XLSX)
    for col in ("State Name", "State HVAC License Requirement", "Licensing Body/Agency"):
        if col not in df.columns:
            print(f"ERROR: states.xlsx missing '{col}'.")
            return 2
    by_name = {str(row["State Name"]).strip(): {
        "req": str(row["State HVAC License Requirement"] or "").strip(),
        "agency": str(row["Licensing Body/Agency"] or "").strip(),
    } for _, row in df.iterrows()}

    state_hub_pat = re.compile(
        r'"areaServed":\s*\{\s*"@type":\s*"State",\s*"name":\s*"(?P<state>[^"]+)"\s*\}',
        re.MULTILINE,
    )

    counts = {"patched": 0, "already_has_faq": 0,
              "schema_anchor_not_found": 0, "vis_anchor_not_found": 0,
              "no_data": 0}
    failures = []
    for path in sorted(LOCATIONS_DIR.glob("*.html")):
        with path.open("r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        m = state_hub_pat.search(text)
        if not m:
            continue
        state_name = m.group("state")
        data = by_name.get(state_name)
        if not data or not data["req"] or not data["agency"]:
            counts["no_data"] += 1
            failures.append(f"{path.name}: no licensing data for '{state_name}'")
            continue
        result = patch_file(path, state_name, data["req"], data["agency"])
        counts[result] = counts.get(result, 0) + 1
        if result in ("schema_anchor_not_found", "vis_anchor_not_found"):
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
