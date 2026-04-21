"""
One-off fix for external links added in tasks #1-#2.

Two problems being fixed:

1. Two broken citation URLs:
     - FEMA NRI at hazards.fema.gov/nri/ is currently returning
       ERR_CONNECTION_CLOSED (SSL cert issues on that subdomain).
       Swapping to the canonical fema.gov page which Playwright
       verified live: https://www.fema.gov/flood-maps/products-tools/
                      national-risk-index
     - NOAA NCEI at www.ncei.noaa.gov/access/billions/ is timing out
       (NCEI appears to have infrastructure issues today). NCEI root
       is also unreachable. Swapping to a stable NOAA page that
       Playwright verified live: https://www.noaa.gov/climate
       (this redirects from climate.gov and is the NOAA-wide climate
       resources landing page). NOAA label simplified accordingly.

2. Every external link I added across the Climate Hazards section
   (task #1) and State Energy Office Resources section (task #2)
   used rel="nofollow noopener" but omitted target="_blank". Site
   convention (and the existing License Lookup URL pattern on the
   same pages) opens external links in a new tab. This patch adds
   target="_blank" to all six external-link patterns I added per
   state hub.

Byte-preserving (newline=""), CRLF-preserving. Idempotent -- the
target-add regex uses a negative lookbehind so URLs that already
have target="_blank" are not double-targeted on re-run.
"""

import re
import sys
from pathlib import Path

LOCATIONS_DIR = Path(__file__).parent.parent / "locations"

# Literal substitutions in order. The URL/label swaps use the OLD
# (bare-rel, no-target) form of the href attribute to avoid matching
# any already-fixed links. The trailing target-add pass then handles
# the remaining links that still lack target="_blank".

FEMA_OLD_URL = "https://hazards.fema.gov/nri/"
FEMA_NEW_URL = "https://www.fema.gov/flood-maps/products-tools/national-risk-index"

NOAA_OLD_URL = "https://www.ncei.noaa.gov/access/billions/"
NOAA_NEW_URL = "https://www.noaa.gov/climate"
NOAA_OLD_LABEL = "NOAA National Centers for Environmental Information"
NOAA_NEW_LABEL = "NOAA climate data"

# Regex: add target="_blank" before rel="nofollow noopener" UNLESS
# target="_blank" already precedes it (idempotency).
TARGET_PAT = re.compile(r'(?<!target="_blank" )rel="nofollow noopener"')


def patch_file(path: Path) -> dict:
    with path.open("r", encoding="utf-8", newline="") as fh:
        text = fh.read()

    counters = {
        "fema_url": 0,
        "noaa_url": 0,
        "noaa_label": 0,
        "target_added": 0,
    }

    # 1. FEMA URL swap
    new_text, n = re.subn(re.escape(FEMA_OLD_URL), FEMA_NEW_URL, text)
    counters["fema_url"] = n
    text = new_text

    # 2. NOAA URL swap (only within the hazards section's citation link)
    new_text, n = re.subn(re.escape(NOAA_OLD_URL), NOAA_NEW_URL, text)
    counters["noaa_url"] = n
    text = new_text

    # 3. NOAA label swap (in the same citation link only)
    new_text, n = re.subn(re.escape(NOAA_OLD_LABEL), NOAA_NEW_LABEL, text)
    counters["noaa_label"] = n
    text = new_text

    # 4. Add target="_blank" before every rel="nofollow noopener" that
    #    doesn't already have it. Negative lookbehind makes this idempotent.
    new_text, n = TARGET_PAT.subn(
        'target="_blank" rel="nofollow noopener"',
        text,
    )
    counters["target_added"] = n
    text = new_text

    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return counters


def main() -> int:
    state_hub_pat = re.compile(
        r'"areaServed":\s*\{\s*"@type":\s*"State"'
    )
    totals = {"fema_url": 0, "noaa_url": 0, "noaa_label": 0, "target_added": 0}
    hubs_touched = 0
    for path in sorted(LOCATIONS_DIR.glob("*.html")):
        with path.open("r", encoding="utf-8", newline="") as fh:
            sample = fh.read(8000)
        if not state_hub_pat.search(sample):
            continue
        counts = patch_file(path)
        for k in totals:
            totals[k] += counts[k]
        hubs_touched += 1

    print(f"Patched {hubs_touched} state hubs.")
    print(f"  FEMA URL replacements:  {totals['fema_url']}")
    print(f"  NOAA URL replacements:  {totals['noaa_url']}")
    print(f"  NOAA label replacements: {totals['noaa_label']}")
    print(f"  target=_blank added:    {totals['target_added']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
