"""
Download per-city and per-state hero images from Wikimedia Commons via the
Wikipedia REST API.

For each city in cities_updated.xlsx and each state in states.xlsx:
  1. Resolve the Wikipedia article title (e.g. "Austin, Texas")
  2. Fetch the page summary -> originalimage.source
  3. Reject images NOT hosted on upload.wikimedia.org/wikipedia/commons/
     (this filters out fair-use images on en.wikipedia which we cannot reuse)
  4. Download original, resize to max 1600x900, convert to WebP @ q82
  5. Query Commons API for the image's license + author
  6. Save image + record attribution metadata

Outputs:
  images/cities/{city-st}.webp
  images/states/{state-slug}.webp
  images/_attributions.json   (full record per image)
  images/_failed.txt          (cities/states with no usable image)

Usage:
  python download_location_images.py                 # all
  python download_location_images.py --cities-only
  python download_location_images.py --states-only
  python download_location_images.py --limit 5       # test on first 5
  python download_location_images.py --city "Austin" # single city
"""
import argparse
import io
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from PIL import Image

ROOT = Path(__file__).parent
CITIES_XLSX = ROOT / "cities_updated.xlsx"
STATES_XLSX = ROOT / "states.xlsx"
IMAGES_DIR = ROOT / "images"
CITIES_OUT = IMAGES_DIR / "cities"
STATES_OUT = IMAGES_DIR / "states"
ATTRIBUTIONS_FILE = IMAGES_DIR / "_attributions.json"
FAILED_FILE = IMAGES_DIR / "_failed.txt"

USER_AGENT = "CoolCallProImageFetcher/1.0 (https://coolcallpro.com; gyanesh.gulshan@gmail.com)"
RATE_LIMIT_SECONDS = 1.0
MAX_WIDTH = 1600
MAX_HEIGHT = 900
WEBP_QUALITY = 82
REQUEST_TIMEOUT = 30

STATE_FULL = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'DC': 'District of Columbia', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii',
    'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming',
}


def slugify(text):
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')


def city_slug(city, state_abbr):
    return f"{slugify(city)}-{state_abbr.lower()}"


def state_slug(state_abbr):
    return slugify(STATE_FULL.get(state_abbr, state_abbr))


def wiki_session():
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json"})
    return s


def fetch_page_summary(session, title):
    """Return page summary JSON or None on 404."""
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title, safe='')}"
    r = session.get(url, timeout=REQUEST_TIMEOUT)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def candidate_titles_for_city(city, state_abbr):
    state_full = STATE_FULL.get(state_abbr, state_abbr)
    return [
        f"{city}, {state_full}",
        f"{city}, {state_abbr}",
        city,
    ]


def candidate_titles_for_state(state_abbr):
    state_full = STATE_FULL.get(state_abbr, state_abbr)
    # State capitol pages reliably return a real building photo (not a flag SVG).
    # Geography page is a good second pass for landscape shots.
    # Plain state name is last resort and usually returns the flag (rejected).
    candidates = [
        f"{state_full} State Capitol",
        f"Geography of {state_full}",
    ]
    # Disambiguation for state names that collide with non-state articles.
    disambiguated = {
        "Georgia": "Georgia (U.S. state)",
        "New York": "New York (state)",
        "Washington": "Washington (state)",
    }
    candidates.append(disambiguated.get(state_full, state_full))
    return candidates


def resolve_image_url(session, title_candidates):
    """Try each candidate; return (resolved_title, image_url, summary_dict) or (None, None, None)."""
    for title in title_candidates:
        time.sleep(RATE_LIMIT_SECONDS)
        try:
            summary = fetch_page_summary(session, title)
        except requests.HTTPError as e:
            print(f"  HTTP error for '{title}': {e}", file=sys.stderr)
            continue
        if not summary:
            continue
        orig = summary.get("originalimage", {})
        url = orig.get("source")
        if not url:
            # Sometimes only thumbnail is set
            url = summary.get("thumbnail", {}).get("source")
        if not url:
            continue
        # Filter: must be a Commons-hosted image (reusable license)
        if "upload.wikimedia.org/wikipedia/commons/" not in url:
            print(f"  Skipping non-Commons image for '{title}' ({url[:80]}...)")
            continue
        # Filter: skip SVG (flags, seals, coats-of-arms — can't be rasterized
        # without cairosvg, and they're useless as hero images anyway).
        if url.lower().endswith('.svg'):
            print(f"  Skipping SVG (likely flag/seal) for '{title}'")
            continue
        # Get full-resolution URL by stripping thumbnail path
        full_url = upgrade_to_original(url)
        return summary.get("title", title), full_url, summary
    return None, None, None


def upgrade_to_original(thumb_url):
    """Convert a Commons thumbnail URL to its original.

    Thumb pattern: .../commons/thumb/a/ab/Filename.jpg/640px-Filename.jpg
    Original pattern: .../commons/a/ab/Filename.jpg
    """
    if "/commons/thumb/" not in thumb_url:
        return thumb_url
    # Drop the trailing thumbnail filename and the /thumb/ path segment
    parts = thumb_url.split("/commons/thumb/", 1)[1].rsplit("/", 1)[0]
    return f"https://upload.wikimedia.org/wikipedia/commons/{parts}"


def fetch_image_metadata(session, image_url):
    """Query Commons for license/author of an image. Returns dict or empty."""
    # Extract filename from URL and decode percent-encoding (commas, parens, etc.)
    filename = image_url.rsplit("/", 1)[-1]
    if not filename:
        return {}
    filename = requests.utils.unquote(filename)
    time.sleep(RATE_LIMIT_SECONDS)
    api_url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "iiprop": "extmetadata|url",
        "titles": f"File:{filename}",
    }
    try:
        r = session.get(api_url, params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except (requests.RequestException, ValueError) as e:
        print(f"  Metadata fetch failed: {e}", file=sys.stderr)
        return {}
    pages = data.get("query", {}).get("pages", {})
    for _, page in pages.items():
        infos = page.get("imageinfo", [])
        if not infos:
            continue
        meta = infos[0].get("extmetadata", {}) or {}
        def _val(key):
            v = meta.get(key, {})
            return v.get("value") if isinstance(v, dict) else None
        return {
            "license_short": _val("LicenseShortName"),
            "license_url": _val("LicenseUrl"),
            "artist_html": _val("Artist"),
            "credit_html": _val("Credit"),
            "description_html": _val("ImageDescription"),
            "commons_url": f"https://commons.wikimedia.org/wiki/File:{filename}",
        }
    return {}


def strip_html(s):
    if not s:
        return ""
    return re.sub(r"<[^>]+>", "", s).strip()


def download_and_convert(session, image_url, out_path):
    time.sleep(RATE_LIMIT_SECONDS)
    r = session.get(image_url, timeout=REQUEST_TIMEOUT, stream=True)
    r.raise_for_status()
    img = Image.open(io.BytesIO(r.content))
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")
    img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.LANCZOS)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "WEBP", quality=WEBP_QUALITY, method=6)
    return out_path.stat().st_size


def load_existing_attributions():
    if ATTRIBUTIONS_FILE.exists():
        try:
            return json.loads(ATTRIBUTIONS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_attributions(data):
    ATTRIBUTIONS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def append_failed(label, reason):
    FAILED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with FAILED_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{label}\t{reason}\n")


def process_one(session, kind, label, slug, title_candidates, out_dir, attributions, force=False):
    """Returns True on success, False on skip/failure."""
    out_path = out_dir / f"{slug}.webp"
    key = f"{kind}/{slug}"

    if not force and out_path.exists() and key in attributions:
        print(f"[skip] {label} (already downloaded)")
        return True

    print(f"[fetch] {label}")
    resolved_title, image_url, summary = resolve_image_url(session, title_candidates)
    if not image_url:
        print(f"  No usable Commons image found.")
        append_failed(label, "no_commons_image")
        return False

    print(f"  -> {resolved_title}")
    print(f"  -> {image_url}")
    try:
        size = download_and_convert(session, image_url, out_path)
    except Exception as e:
        print(f"  Download/convert failed: {e}", file=sys.stderr)
        append_failed(label, f"download_error: {e}")
        return False

    meta = fetch_image_metadata(session, image_url)
    attributions[key] = {
        "kind": kind,
        "label": label,
        "slug": slug,
        "file": str(out_path.relative_to(ROOT)).replace("\\", "/"),
        "file_size_bytes": size,
        "wikipedia_title": resolved_title,
        "wikipedia_url": (summary or {}).get("content_urls", {}).get("desktop", {}).get("page"),
        "image_source_url": image_url,
        "commons_url": meta.get("commons_url"),
        "license": meta.get("license_short"),
        "license_url": meta.get("license_url"),
        "artist": strip_html(meta.get("artist_html")),
        "credit": strip_html(meta.get("credit_html")),
        "description": strip_html(meta.get("description_html"))[:300],
    }
    save_attributions(attributions)
    print(f"  OK ({size // 1024} KB, {meta.get('license_short') or 'license unknown'})")
    return True


def load_cities(filter_city=None, limit=None):
    df = pd.read_excel(CITIES_XLSX)
    rows = []
    for _, r in df.iterrows():
        city = (r.get("City") or "").strip()
        state = (r.get("State") or "").strip()
        if not city or not state:
            continue
        if filter_city and filter_city.lower() not in city.lower():
            continue
        rows.append((city, state))
    if limit:
        rows = rows[:limit]
    return rows


def load_states(limit=None):
    df = pd.read_excel(STATES_XLSX)
    rows = []
    for _, r in df.iterrows():
        abbr = (r.get("State Abbreviation") or "").strip()
        if not abbr:
            continue
        rows.append(abbr)
    if limit:
        rows = rows[:limit]
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cities-only", action="store_true")
    p.add_argument("--states-only", action="store_true")
    p.add_argument("--city", help="Single city name substring filter")
    p.add_argument("--limit", type=int, help="Process only the first N entries")
    p.add_argument("--force", action="store_true", help="Re-download even if file exists")
    args = p.parse_args()

    IMAGES_DIR.mkdir(exist_ok=True)
    CITIES_OUT.mkdir(parents=True, exist_ok=True)
    STATES_OUT.mkdir(parents=True, exist_ok=True)

    attributions = load_existing_attributions()
    session = wiki_session()

    success = 0
    failed = 0

    if not args.states_only:
        cities = load_cities(filter_city=args.city, limit=args.limit)
        print(f"\n=== Processing {len(cities)} cities ===\n")
        for city, state in cities:
            slug = city_slug(city, state)
            label = f"{city}, {state}"
            titles = candidate_titles_for_city(city, state)
            ok = process_one(session, "city", label, slug, titles, CITIES_OUT, attributions, force=args.force)
            success += int(ok)
            failed += int(not ok)

    if not args.cities_only and not args.city:
        states = load_states(limit=args.limit)
        print(f"\n=== Processing {len(states)} states ===\n")
        for abbr in states:
            slug = state_slug(abbr)
            label = STATE_FULL.get(abbr, abbr)
            titles = candidate_titles_for_state(abbr)
            ok = process_one(session, "state", label, slug, titles, STATES_OUT, attributions, force=args.force)
            success += int(ok)
            failed += int(not ok)

    print(f"\n=== Done. Success: {success}, Failed: {failed} ===")
    print(f"Attributions: {ATTRIBUTIONS_FILE}")
    if FAILED_FILE.exists():
        print(f"Failures logged: {FAILED_FILE}")


if __name__ == "__main__":
    main()
