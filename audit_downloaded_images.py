"""
Generate a single-page HTML preview of all downloaded location images.

Reads images/_attributions.json and produces images/_preview.html with one
card per image showing: thumbnail, label, license, photographer, source link,
and a "REPLACE" / "OK" toggle for visual triage.

Open in a browser:
  python audit_downloaded_images.py
  start images/_preview.html   (Windows)
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
ATTRIBUTIONS = ROOT / "images" / "_attributions.json"
OUTPUT = ROOT / "images" / "_preview.html"


def main():
    if not ATTRIBUTIONS.exists():
        print(f"No attributions file at {ATTRIBUTIONS}. Run download_location_images.py first.")
        return

    data = json.loads(ATTRIBUTIONS.read_text(encoding="utf-8"))
    cities = sorted([v for v in data.values() if v["kind"] == "city"], key=lambda x: x["label"])
    states = sorted([v for v in data.values() if v["kind"] == "state"], key=lambda x: x["label"])

    def card(rec):
        rel = rec["file"]
        label = rec["label"]
        license_short = rec.get("license") or "UNKNOWN"
        license_url = rec.get("license_url") or "#"
        artist = rec.get("artist") or "Unknown"
        commons_url = rec.get("commons_url") or rec.get("image_source_url") or "#"
        wiki_url = rec.get("wikipedia_url") or "#"
        license_color = "#38a169" if license_short and "CC" in license_short else "#c53030"
        return f"""
        <div class="card">
          <img src="../{rel}" alt="{label}" loading="lazy" />
          <div class="meta">
            <div class="label">{label}</div>
            <div class="license" style="color:{license_color};">{license_short}</div>
            <div class="artist">By {artist}</div>
            <div class="links">
              <a href="{commons_url}" target="_blank" rel="noopener">Commons</a> ·
              <a href="{wiki_url}" target="_blank" rel="noopener">Wikipedia</a>
            </div>
          </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Image Preview — Cool Call Pro</title>
<style>
  body {{ font: 14px/1.4 system-ui, sans-serif; background: #f5f5f5; margin: 0; padding: 24px; }}
  h1 {{ font-size: 22px; margin: 0 0 8px; }}
  .summary {{ color: #555; margin-bottom: 24px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }}
  .card {{ background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
  .card img {{ width: 100%; height: 180px; object-fit: cover; display: block; background: #ddd; }}
  .meta {{ padding: 10px 12px; }}
  .label {{ font-weight: 600; font-size: 15px; margin-bottom: 4px; }}
  .license {{ font-size: 12px; font-weight: 600; }}
  .artist {{ font-size: 12px; color: #666; margin: 2px 0; }}
  .links {{ font-size: 12px; margin-top: 4px; }}
  .links a {{ color: #1a73e8; text-decoration: none; }}
  h2 {{ margin-top: 32px; font-size: 18px; }}
</style>
</head>
<body>
<h1>Location Image Preview</h1>
<div class="summary">
  Cities: {len(cities)} &middot; States: {len(states)} &middot;
  Click image to inspect on Commons. Anything that looks wrong (map, coat-of-arms,
  obscure landmark, low quality) — note the city/state name and we'll replace.
</div>

<h2>Cities ({len(cities)})</h2>
<div class="grid">
  {''.join(card(r) for r in cities)}
</div>

<h2>States ({len(states)})</h2>
<div class="grid">
  {''.join(card(r) for r in states)}
</div>
</body>
</html>
"""
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    print(f"Open: file:///{OUTPUT.as_posix()}")


if __name__ == "__main__":
    main()
