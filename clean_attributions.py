"""
Clean up messy `artist` fields in images/_attributions.json.

Wikimedia's Artist field can dump multi-line metadata, OSM coordinates,
"X at English Wikipedia" suffixes, talk-page links, etc. This trims to a
clean, displayable photographer name.

Run once after download_location_images.py; safe to re-run (idempotent).
"""
import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).parent
ATTRIBUTIONS = ROOT / "images" / "_attributions.json"


def clean_artist(raw):
    if not raw:
        return "Unknown photographer"
    s = raw.strip()
    # Cut at first newline (geo dumps, derivative-work notes, copyright notices)
    s = s.split("\n", 1)[0].strip()
    # Strip "Camera location..." OSM blob
    s = re.sub(r"\s*Camera location.*", "", s, flags=re.IGNORECASE).strip()
    # Strip " (talk)" annotations
    s = re.sub(r"\s*\(talk\)", "", s, flags=re.IGNORECASE)
    # Strip "X at/of English Wikipedia" suffixes
    s = re.sub(r"\s+(at|of|from)\s+English\s+Wikipedia\.?$", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^The original uploader was\s+", "", s, flags=re.IGNORECASE)
    # Strip "File:foo.jpg: " prefix
    s = re.sub(r"^File:[^:]+:\s*", "", s)
    # Strip "This image or media was taken or created by X" verbose preamble.
    # Stop at phrases that introduce trailing prose (not at periods, since names
    # may contain initials like "Matt H. Wade").
    m = re.match(
        r"^This (?:image|file|media|photo)[^.]*?\bby\s+(.+?)(?:\s+(?:To see|click|Please|If you|This (?:image|file)|@)|\Z)",
        s, re.IGNORECASE
    )
    if m:
        s = m.group(1).strip().rstrip(".,;: ")
    # Strip "Original: X Derivative work: Y" → keep just X (or Y if X empty)
    m = re.match(r"^Original:\s*([^:]+?)(?:Derivative work:.*)?$", s, re.IGNORECASE)
    if m:
        s = m.group(1).strip()
    # Strip extra context after " - " or " from " (likely org names / URLs / locations)
    # but only when result is still substantive
    for sep in [" - ", " from "]:
        if sep in s:
            head = s.split(sep, 1)[0].strip()
            if len(head) >= 3:
                s = head
    # Strip trailing org dumps after comma-separated location ("X, NPS, ...")
    if s.count(",") >= 2:
        s = s.split(",", 1)[0].strip()
    # Cap length (keep credit short and clean)
    if len(s) > 60:
        s = s[:57].rstrip(",.;: -") + "…"
    return s.strip() or "Unknown photographer"


def main():
    data = json.loads(ATTRIBUTIONS.read_text(encoding="utf-8"))
    changed = 0
    for key, rec in data.items():
        original = rec.get("artist") or ""
        # Preserve original under a separate key for traceability (only first time)
        if "artist_raw" not in rec:
            rec["artist_raw"] = original
        cleaned = clean_artist(rec.get("artist_raw") or original)
        if cleaned != rec.get("artist"):
            rec["artist"] = cleaned
            changed += 1
            print(f"  {rec['label']}: {original[:60]!r} -> {cleaned!r}")
    ATTRIBUTIONS.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nCleaned {changed} of {len(data)} entries.")


if __name__ == "__main__":
    main()
