"""
Add the MarketCall-required "Service availability" disclaimer paragraph
site-wide to every HTML page that already carries the locked MarketCall
disclaimer paragraph.

The new disclaimer is required by MarketCall partner agreement (rule
update May 2026) because the site uses "24/7" and "same-day" language.
MUST appear on every page with a footer.

Verbatim text (DO NOT EDIT — same lock policy as the original disclaimer):

    Same-day and 24/7 emergency services are subject to provider
    participation, location, technician availability, and demand.
    Availability is not guaranteed and may vary by market and
    appointment capacity.

Insertion strategy: append a new <p> immediately after the existing
locked "<p><strong>Disclaimer:</strong> Cool Call Pro is a free service
..." paragraph. Idempotent — if the new disclaimer is already present,
the file is skipped.

Run from repo root: python scripts/add_marketcall_availability_disclaimer.py
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Verbatim signature to find the existing disclaimer
EXISTING_DISCLAIMER_SIGNATURE = "All persons depicted in a photo or video are actors or models and not contractors listed on Cool Call Pro.</p>"

# New disclaimer paragraph to insert
NEW_DISCLAIMER_PARAGRAPH = (
    '\n                <p><strong style="color: rgba(255,255,255,0.9);">Service availability:</strong> '
    "Same-day and 24/7 emergency services are subject to provider participation, "
    "location, technician availability, and demand. Availability is not guaranteed "
    "and may vary by market and appointment capacity.</p>"
)

# New disclaimer signature for idempotency check (verbatim MarketCall text)
NEW_DISCLAIMER_SIGNATURE = (
    "Same-day and 24/7 emergency services are subject to provider participation, "
    "location, technician availability, and demand."
)

# Skip these — they're tooling, snapshots, or test sandbox
SKIP_DIRS = {"_pilot_test", "_dist", ".git", ".github", "node_modules"}
SKIP_FILES = {"scratch_page.html"}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & SKIP_DIRS:
        return True
    if path.name in SKIP_FILES:
        return True
    return False


def patch_file(path: Path) -> str:
    """Returns 'patched', 'already-present', 'no-disclaimer', or 'error: ...'"""
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return f"error: read failed ({e})"

    if EXISTING_DISCLAIMER_SIGNATURE not in text:
        return "no-disclaimer"

    if NEW_DISCLAIMER_SIGNATURE in text:
        return "already-present"

    # Find the existing disclaimer paragraph ending and insert after it
    new_text = text.replace(
        EXISTING_DISCLAIMER_SIGNATURE,
        EXISTING_DISCLAIMER_SIGNATURE + NEW_DISCLAIMER_PARAGRAPH,
        1,  # only replace the first occurrence — multiple footers in one file would be unusual
    )

    if new_text == text:
        return "error: replacement made no change (regex anchor not found in expected form)"

    try:
        path.write_text(new_text, encoding="utf-8")
    except Exception as e:
        return f"error: write failed ({e})"

    return "patched"


def main():
    counts = {"patched": 0, "already-present": 0, "no-disclaimer": 0, "errors": 0}
    errors = []

    # Walk every .html file
    for html_path in REPO_ROOT.rglob("*.html"):
        rel = html_path.relative_to(REPO_ROOT)
        if should_skip(rel):
            continue

        result = patch_file(html_path)

        if result == "patched":
            counts["patched"] += 1
            print(f"  [PATCH] {rel}")
        elif result == "already-present":
            counts["already-present"] += 1
        elif result == "no-disclaimer":
            counts["no-disclaimer"] += 1
        else:
            counts["errors"] += 1
            errors.append(f"{rel}: {result}")

    print()
    print(f"Patched:           {counts['patched']}")
    print(f"Already present:   {counts['already-present']}")
    print(f"No disclaimer:     {counts['no-disclaimer']} (footer-less pages — expected)")
    print(f"Errors:            {counts['errors']}")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
