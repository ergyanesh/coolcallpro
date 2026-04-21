"""
One-off surgical insertion: add a Service schema entry to every state hub's
JSON-LD @graph block. Inserts AFTER the existing Organization entry and
BEFORE the @graph closing bracket. Preserves every other byte in each file
(line endings, indentation, content) by using regex with backreferences.

Generated state hubs (going forward) get the same Service schema via the
matching addition in generate_state_hubs.py. This script only patches the
51 existing files in place.

Run: python scripts/add_state_hub_service_schema.py
Idempotent — re-running is a no-op (skips files that already have Service).
"""

import re
import sys
from pathlib import Path

LOCATIONS_DIR = Path(__file__).parent.parent / "locations"

# Match the closing pattern of the Organization entry inside @graph,
# capturing the state name so we can reuse it in the Service entry.
# Looks for:
#     "areaServed": {
#       "@type": "State",
#       "name": "<STATE NAME>"
#     }
#   }
# ]
# (where indentation may vary slightly, and we anchor to the @graph close)
INSERT_PATTERN = re.compile(
    r'(?P<area>"areaServed":\s*\{\s*"@type":\s*"State",\s*"name":\s*"(?P<state>[^"]+)"\s*\})'
    r'(?P<close_org>\s*\})'
    r'(?P<close_graph>\s*\]\s*\}\s*</script>)',
    re.MULTILINE,
)


def make_service_block(state_name: str) -> str:
    """Build the Service schema entry exactly matching the Organization
    indentation already used by the file (6 spaces for the entry, 8 for
    properties, 10 for nested values)."""
    return (
        ',\n'
        '      {\n'
        '        "@type": "Service",\n'
        '        "serviceType": "HVAC Repair and Installation Referral",\n'
        '        "provider": {\n'
        '          "@type": "Organization",\n'
        '          "name": "Cool Call Pro",\n'
        '          "telephone": "+1-844-582-1795",\n'
        '          "url": "https://coolcallpro.com"\n'
        '        },\n'
        '        "areaServed": {\n'
        '          "@type": "State",\n'
        f'          "name": "{state_name}"\n'
        '        },\n'
        '        "audience": { "@type": "Audience", "audienceType": "Homeowners" }\n'
        '      }'
    )


def patch_file(path: Path) -> str:
    """Return one of: 'patched', 'already_has_service', 'pattern_not_found'.

    Reads and writes in binary-preserving mode (newline="") so we keep the
    original CRLF line endings byte-for-byte. Path.read_text() / write_text()
    do universal newline translation by default, which would silently convert
    CRLF -> LF and produce a noisy diff on every line.
    """
    with path.open("r", encoding="utf-8", newline="") as fh:
        text = fh.read()

    # Skip if Service schema is already present (idempotent)
    if '"@type": "Service"' in text:
        return "already_has_service"

    match = INSERT_PATTERN.search(text)
    if not match:
        return "pattern_not_found"

    state_name = match.group("state")
    service_block = make_service_block(state_name)

    # Match the file's line ending style for the inserted block.
    if "\r\n" in text:
        service_block = service_block.replace("\n", "\r\n")

    new_text = (
        text[: match.end("close_org")]
        + service_block
        + text[match.end("close_org") :]
    )

    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(new_text)
    return "patched"


def main():
    state_hub_pat = re.compile(
        r'"areaServed":\s*\{\s*"@type":\s*"State"', re.MULTILINE
    )
    state_hubs = []
    for f in sorted(LOCATIONS_DIR.glob("*.html")):
        if state_hub_pat.search(f.read_text(encoding="utf-8")):
            state_hubs.append(f)

    print(f"Identified {len(state_hubs)} state hub files")
    counts = {"patched": 0, "already_has_service": 0, "pattern_not_found": 0}
    failures = []
    for f in state_hubs:
        result = patch_file(f)
        counts[result] += 1
        if result == "pattern_not_found":
            failures.append(f.name)

    print(f"  patched:                 {counts['patched']}")
    print(f"  already_has_service:     {counts['already_has_service']}")
    print(f"  pattern_not_found (FAIL): {counts['pattern_not_found']}")
    if failures:
        print("\nFiles where the insertion pattern was not found:")
        for name in failures:
            print(f"  - {name}")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
