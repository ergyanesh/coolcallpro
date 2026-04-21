"""
One-off surgical cleanup: the Common HVAC Issues patch script (c09e7cc)
prepended a leading newline to its inserted block which, combined with the
pre-existing blank line before "<!-- Service Areas -->", left every state
hub with TWO blank lines between the Cost Overview "</section>" and the
"<!-- Common HVAC Issues -->" comment. The generator now produces a single
blank line there, so this script normalizes the 51 live state hubs to match.

Byte-preserving: reads/writes with newline="" to keep CRLF byte-for-byte.
Idempotent: the find-and-replace pattern targets the triple-newline run
and leaves already-normalized files untouched.

Run:   python scripts/normalize_state_hub_blank_lines.py
"""

import re
import sys
from pathlib import Path

LOCATIONS_DIR = Path(__file__).parent.parent / "locations"

# Match Cost Overview close + 3 newlines + Common HVAC Issues comment.
# The generator (and the original pre-patch template) produces 2 newlines
# here (one blank line). 3 newlines = two blank lines, which we collapse.
# Anchored on literal strings so we only touch state hubs with the prior-
# commit drift and not any unrelated region.
LF_PATTERN = re.compile(
    r"(    </section>)(\n{3})(    <!-- Common HVAC Issues -->)"
)
CRLF_PATTERN = re.compile(
    r"(    </section>)(\r\n){3}(    <!-- Common HVAC Issues -->)"
)


def patch_file(path: Path) -> str:
    """Return 'normalized' | 'already_clean' | 'no_match'."""
    with path.open("r", encoding="utf-8", newline="") as fh:
        text = fh.read()

    if "<!-- Common HVAC Issues -->" not in text:
        return "no_match"

    # Detect file's line ending style and pick the matching pattern
    if "\r\n" in text:
        pat = CRLF_PATTERN
        replacement = r"\1\r\n\r\n\3"
    else:
        pat = LF_PATTERN
        replacement = r"\1\n\n\3"

    if not pat.search(text):
        return "already_clean"

    new_text = pat.sub(replacement, text, count=1)
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(new_text)
    return "normalized"


def main() -> int:
    state_hub_pat = re.compile(
        r'"areaServed":\s*\{\s*"@type":\s*"State",\s*"name":\s*"[^"]+"\s*\}'
    )
    counts = {"normalized": 0, "already_clean": 0, "no_match": 0}
    for path in sorted(LOCATIONS_DIR.glob("*.html")):
        with path.open("r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        if not state_hub_pat.search(text):
            continue
        result = patch_file(path)
        counts[result] = counts.get(result, 0) + 1

    print("Results:")
    print(f"  normalized:    {counts['normalized']}")
    print(f"  already_clean: {counts['already_clean']}")
    print(f"  no_match:      {counts['no_match']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
