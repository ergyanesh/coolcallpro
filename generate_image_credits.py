"""
Generate image-credits.html from images/_attributions.json.

This page satisfies the CC BY / CC BY-SA attribution requirements for every
location image used on the site. Linked from every page footer.

Also generates sitemap-images.xml — a separate XML sitemap for image search,
listing each image and the page it appears on.
"""
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
ATTRIBUTIONS = ROOT / "images" / "_attributions.json"
OUTPUT_HTML = ROOT / "image-credits.html"
OUTPUT_SITEMAP = ROOT / "sitemap-images.xml"


def html_escape(s):
    if not s:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def xml_escape(s):
    return html_escape(s)


def license_badge_color(license_short):
    """Return a (bg, fg) color pair for a license badge."""
    if not license_short:
        return ("var(--gray-100)", "var(--gray-700)")
    short = license_short.lower()
    if "cc0" in short or "public domain" in short:
        return ("#e6f4ea", "#1e7e34")  # green for permissive
    if "by-sa" in short:
        return ("#fff3cd", "#856404")  # amber for share-alike
    if "by" in short:
        return ("#dbeafe", "#1e40af")  # blue for attribution
    return ("var(--gray-100)", "var(--gray-700)")


def render_credit_card(rec):
    label = html_escape(rec["label"])
    artist = html_escape(rec.get("artist") or "Unknown photographer")
    license_short = rec.get("license") or "License unspecified"
    license_short_e = html_escape(license_short)
    license_url = html_escape(rec.get("license_url") or "")
    commons_url = html_escape(rec.get("commons_url") or rec.get("image_source_url") or "#")
    file_rel = html_escape(rec["file"])
    width = rec.get("width") or 1600
    height = rec.get("height") or 900
    bg, fg = license_badge_color(license_short)
    license_link = (
        f'<a href="{license_url}" target="_blank" rel="nofollow noopener" style="color: inherit; text-decoration: none;">{license_short_e}</a>'
        if license_url else license_short_e
    )
    return f"""
                <article class="credit-card">
                    <a href="{commons_url}" target="_blank" rel="nofollow noopener" class="credit-card-img-wrap" aria-label="View {label} on Wikimedia Commons">
                        <img src="{file_rel}" alt="{label}" width="{width}" height="{height}" loading="lazy" decoding="async" />
                    </a>
                    <div class="credit-card-body">
                        <h3 class="credit-card-title">{label}</h3>
                        <p class="credit-card-artist"><span aria-hidden="true">&#128247;</span> {artist}</p>
                        <div class="credit-card-meta">
                            <span class="credit-license-badge" style="background: {bg}; color: {fg};">{license_link}</span>
                            <a href="{commons_url}" target="_blank" rel="nofollow noopener" class="credit-source-link">View source &#8594;</a>
                        </div>
                    </div>
                </article>"""


def render_html(records):
    cities = sorted([r for r in records if r["kind"] == "city"], key=lambda x: x["label"])
    states = sorted([r for r in records if r["kind"] == "state"], key=lambda x: x["label"])
    cities_cards = "".join(render_credit_card(r) for r in cities)
    states_cards = "".join(render_credit_card(r) for r in states)

    return f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <script>
        window.addEventListener('load', function() {{
            var s = document.createElement('script');
            s.src = 'https://www.googletagmanager.com/gtag/js?id=G-WD0ND0K60Q';
            s.async = true;
            document.head.appendChild(s);
            s.onload = function() {{
                window.dataLayer = window.dataLayer || [];
                function gtag(){{dataLayer.push(arguments);}}
                window.gtag = gtag;
                gtag('js', new Date());
                gtag('config', 'G-WD0ND0K60Q');
            }};
        }});
    </script>

    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="robots" content="index, follow" />
    <title>Image Credits &amp; Attributions | Cool Call Pro</title>
    <meta name="description" content="Photo credits and license attributions for all city and state images used on Cool Call Pro. Sourced from Wikimedia Commons under CC BY, CC BY-SA, and public domain licenses." />
    <link rel="canonical" href="https://coolcallpro.com/image-credits" />

    <meta property="og:type" content="website" />
    <meta property="og:title" content="Image Credits | Cool Call Pro" />
    <meta property="og:description" content="Photo credits and license attributions for images on Cool Call Pro." />
    <meta property="og:url" content="https://coolcallpro.com/image-credits" />
    <meta property="og:site_name" content="Cool Call Pro" />
    <meta property="og:image" content="https://coolcallpro.com/images/og-homepage.webp" />

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="Image Credits | Cool Call Pro" />
    <meta name="twitter:description" content="Photo credits for images on Cool Call Pro." />
    <meta name="twitter:image" content="https://coolcallpro.com/images/og-homepage.webp" />

    <link rel="icon" href="/favicon.ico" type="image/x-icon" />
    <link rel="icon" href="/favicon.svg" type="image/svg+xml" />

    <link rel="stylesheet" href="css/style.min.css" />
    <link rel="dns-prefetch" href="https://www.googletagmanager.com">
    <link rel="preload" href="/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="/fonts/outfit-latin.woff2" as="font" type="font/woff2" crossorigin>

    <style>
        .credits-intro {{ font-size: 1.05rem; line-height: 1.7; color: var(--gray-700); max-width: 760px; margin: 0 auto 48px; text-align: center; }}
        .credits-section-heading {{ font-family: var(--font-display); font-size: 1.75rem; font-weight: 700; color: var(--navy); margin: 56px 0 8px; letter-spacing: -0.01em; }}
        .credits-section-sub {{ color: var(--gray-600); margin: 0 0 28px; font-size: 0.95rem; }}

        .credit-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            content-visibility: auto;
            contain-intrinsic-size: 1px 380px;
        }}
        .credit-card {{
            background: #fff;
            border: 1px solid var(--gray-100);
            border-radius: var(--radius);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
        }}
        .credit-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 24px rgba(10,22,40,0.10); border-color: var(--gray-200); }}
        .credit-card-img-wrap {{
            display: block;
            position: relative;
            aspect-ratio: 16 / 9;
            overflow: hidden;
            background: var(--gray-100);
        }}
        .credit-card-img-wrap img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            transition: transform 0.4s ease;
        }}
        .credit-card:hover .credit-card-img-wrap img {{ transform: scale(1.04); }}
        .credit-card-body {{ padding: 16px 18px 18px; display: flex; flex-direction: column; gap: 8px; }}
        .credit-card-title {{
            font-family: var(--font-display);
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--navy);
            margin: 0;
            line-height: 1.3;
        }}
        .credit-card-artist {{
            font-size: 0.85rem;
            color: var(--gray-600);
            margin: 0;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .credit-card-meta {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-top: 4px;
            padding-top: 12px;
            border-top: 1px solid var(--gray-100);
        }}
        .credit-license-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }}
        .credit-source-link {{
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--blue);
            text-decoration: none;
            white-space: nowrap;
        }}
        .credit-source-link:hover {{ text-decoration: underline; }}

        .license-summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 24px;
        }}
        .license-summary-card {{
            padding: 24px 22px;
            border-radius: var(--radius);
            border: 1px solid var(--gray-100);
            background: #fff;
        }}
        .license-summary-card h3 {{
            font-family: var(--font-display);
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--navy);
            margin: 0 0 6px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .license-summary-badge {{
            display: inline-block;
            padding: 3px 9px;
            border-radius: 999px;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}
        .license-summary-card p {{ color: var(--gray-700); font-size: 0.93rem; line-height: 1.55; margin: 0 0 10px; }}
        .license-summary-card a {{ color: var(--blue); font-weight: 600; font-size: 0.85rem; text-decoration: none; }}
        .license-summary-card a:hover {{ text-decoration: underline; }}
    </style>

    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": [
        {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://coolcallpro.com/"}},
        {{"@type": "ListItem", "position": 2, "name": "Image Credits", "item": "https://coolcallpro.com/image-credits"}}
      ]
    }}
    </script>
</head>

<body>

    <a href="#main-content" class="skip-link">Skip to main content</a>

    <div class="topbar">
        <div class="container topbar-inner" style="justify-content: center; padding: 10px; font-weight: 600;">
            <span class="topbar-text">24/7 Referral Service &mdash; Connecting Homeowners with Independent HVAC Professionals</span>
        </div>
    </div>

    <header class="header" id="header">
        <nav class="nav container" role="navigation" aria-label="Main navigation">
            <a href="/" class="logo"><span class="logo-icon">&#10052;&#65039;</span><span class="logo-text">CoolCall<span class="logo-accent">Pro</span></span></a>
            <ul class="nav-links" id="navLinks">
                <li><a href="emergency" class="nav-link emergency-link">&#128680; Emergency Service</a></li>
                <li><a href="costs" class="nav-link">Cost Guide</a></li>
                <li><a href="safety" class="nav-link">Safety Tips</a></li>
                <li><a href="locations" class="nav-link">&#128205; Locations</a></li>
                <li><a href="articles" class="nav-link">Articles</a></li>
                <li><a href="about" class="nav-link">About</a></li>
                <li><a href="contact" class="nav-link">Contact</a></li>
            </ul>
            <a href="tel:+18445821795" class="btn btn-cta nav-cta btn-vibrate" id="headerNavCta" aria-hidden="true" tabindex="-1" style="opacity: 0; pointer-events: none; transition: opacity 0.3s ease;"><span class="phone-icon">&#128222;</span> <span class="hide-on-mobile">(844) 582-1795</span></a>
            <button class="hamburger" id="hamburger" aria-label="Menu">&#9776;</button>
        </nav>
    </header>

    <main id="main-content">

        <div class="page-hero">
            <div class="container">
                <span class="section-tag">&#128247; Credits</span>
                <h1>Image Credits &amp; Attributions</h1>
                <p>Last Updated: {date.today().strftime('%B %Y')}</p>
            </div>
        </div>

        <div class="breadcrumb-nav">
            <div class="container">
                <nav aria-label="Breadcrumb">
                    <ol class="breadcrumb-list">
                        <li><a href="/">Home</a></li>
                        <li aria-current="page">Image Credits</li>
                    </ol>
                </nav>
            </div>
        </div>

        <section class="section">
            <div class="container" style="max-width: 1280px;">
                <p class="credits-intro">Cool Call Pro uses freely licensed photographs from <a href="https://commons.wikimedia.org/" target="_blank" rel="nofollow noopener">Wikimedia Commons</a> for our city and state location pages. Each image is reproduced under its respective Creative Commons or public domain license, with full attribution below. If you are the rights holder of an image and would like attribution adjusted or the image removed, please <a href="contact">contact us</a>.</p>

                <h2 id="cities" class="credits-section-heading">City Photos</h2>
                <p class="credits-section-sub">{len(cities)} cities &middot; click any card to view the original on Wikimedia Commons</p>
                <div class="credit-grid">{cities_cards}
                </div>

                <h2 id="states" class="credits-section-heading">State Photos</h2>
                <p class="credits-section-sub">{len(states)} states &middot; sourced from Wikimedia Commons</p>
                <div class="credit-grid">{states_cards}
                </div>

                <h2 id="licenses" class="credits-section-heading">License Summary</h2>
                <p class="credits-section-sub">All images on this site are reused under one of the following Creative Commons licenses</p>
                <div class="license-summary-grid">
                    <div class="license-summary-card">
                        <h3><span class="license-summary-badge" style="background: #dbeafe; color: #1e40af;">CC BY</span> Attribution</h3>
                        <p>Free to use, share, and adapt with credit to the original photographer. Versions 2.0, 3.0, and 4.0.</p>
                        <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="nofollow noopener">View license terms &#8594;</a>
                    </div>
                    <div class="license-summary-card">
                        <h3><span class="license-summary-badge" style="background: #fff3cd; color: #856404;">CC BY-SA</span> Share-Alike</h3>
                        <p>Free to use with attribution; any derivative works must be released under the same license. Versions 2.0, 3.0, and 4.0.</p>
                        <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="nofollow noopener">View license terms &#8594;</a>
                    </div>
                    <div class="license-summary-card">
                        <h3><span class="license-summary-badge" style="background: #e6f4ea; color: #1e7e34;">CC0 / PD</span> Public Domain</h3>
                        <p>No restrictions on use. Photographer has waived all rights or the work is in the public domain.</p>
                        <a href="https://creativecommons.org/publicdomain/zero/1.0/" target="_blank" rel="nofollow noopener">View license terms &#8594;</a>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <footer class="footer">
        <div class="container">
            <div class="footer-grid">
                <div class="footer-brand">
                    <a href="/" class="logo"><span class="logo-icon">&#10052;&#65039;</span><span class="logo-text">CoolCall<span class="logo-accent">Pro</span></span></a>
                    <p>Connecting homeowners with independent HVAC professionals across the US. Available 24/7 in many areas.</p>
                    <div class="footer-contact">
                        <a href="tel:+18445821795" class="footer-phone">(844) 582-1795</a>
                        <span>24/7 Service Line</span>
                    </div>
                </div>
                <div class="footer-col">
                    <h3 class="footer-heading">Resources</h3>
                    <ul>
                        <li><a href="costs">Cost Guide</a></li>
                        <li><a href="emergency">Emergency Service</a></li>
                        <li><a href="safety">Safety Tips</a></li>
                        <li><a href="articles">All Articles</a></li>
                        <li><a href="locations">Locations</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3 class="footer-heading">Company</h3>
                    <ul>
                        <li><a href="about">About Us</a></li>
                        <li><a href="contact">Contact</a></li>
                        <li><a href="author-gyanesh">Author</a></li>
                        <li><a href="privacy">Privacy Policy</a></li>
                        <li><a href="advertising-disclosure">Advertising Disclosure</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h3 class="footer-heading">Service Areas</h3>
                    <ul class="service-areas">
                        <li><a href="locations/atlanta-ga">Atlanta, GA</a></li>
                        <li><a href="locations/chicago-il">Chicago, IL</a></li>
                        <li><a href="locations/dallas-tx">Dallas, TX</a></li>
                        <li><a href="locations/houston-tx">Houston, TX</a></li>
                        <li><a href="locations/phoenix-az">Phoenix, AZ</a></li>
                        <li><a href="locations">All 50 states &#8594;</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p><strong style="color: rgba(255,255,255,0.9);">How this site works:</strong> We publish HVAC cost and troubleshooting information and may connect callers to independent service providers. We do not perform HVAC services ourselves. Pricing, availability, and response times vary by provider and location.</p>
                <p><strong style="color: rgba(255,255,255,0.9);">Disclaimer:</strong> Cool Call Pro is a free service to assist homeowners in connecting with local service providers. All contractors/providers are independent and Cool Call Pro does not warrant or guarantee any work performed.</p>
                <p>&copy; <span class="copyright-year">2026</span> Cool Call Pro. All rights reserved. &nbsp;&middot;&nbsp; <a href="privacy">Privacy Policy</a> &nbsp;&middot;&nbsp; <a href="terms">Terms of Use</a> &nbsp;&middot;&nbsp; <a href="disclaimer">Disclaimer</a> &nbsp;&middot;&nbsp; <a href="advertising-disclosure">Advertising Disclosure</a> &nbsp;&middot;&nbsp; <a href="image-credits">Image Credits</a></p>
            </div>
        </div>
    </footer>

    <script src="js/main.min.js" defer></script>

    <div class="mobile-call-bar">
        <a href="tel:+18445821795"><svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width: 1.25em; height: 1.25em; position: relative; top: 0.15em;"><path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56-.35-.12-.74-.03-1.01.24l-1.57 1.97c-2.83-1.35-5.48-3.9-6.89-6.83l1.95-1.66c.27-.28.35-.67.24-1.02-.37-1.11-.56-2.3-.56-3.53 0-.54-.45-.99-.99-.99H4.19C3.65 3 3 3.24 3 3.99 3 13.28 10.73 21 20.01 21c.71 0 1.01-.63 1.01-1.18v-3.45c0-.54-.45-.99-.99-.99z"/></svg> Call Now &mdash; (844) 582-1795</a>
    </div>
<script>document.querySelectorAll(".copyright-year").forEach(function(el){{el.textContent=new Date().getFullYear()}});</script>
</body>

</html>
"""


def render_image_sitemap(records):
    """Generate sitemap-images.xml mapping each image to its page URL."""
    BASE = "https://coolcallpro.com"
    rows = []
    for rec in records:
        slug = rec["slug"]
        if rec["kind"] == "city":
            page_url = f"{BASE}/locations/{slug}"
        else:
            page_url = f"{BASE}/locations/{slug}"
        image_url = f"{BASE}/{rec['file']}"
        title = xml_escape(rec["label"])
        caption = xml_escape((rec.get("description") or rec["label"])[:200])
        license_url = xml_escape(rec.get("license_url") or rec.get("commons_url") or "")
        license_block = f"      <image:license>{license_url}</image:license>\n" if license_url else ""
        rows.append(
            f"  <url>\n"
            f"    <loc>{page_url}</loc>\n"
            f"    <image:image>\n"
            f"      <image:loc>{xml_escape(image_url)}</image:loc>\n"
            f"      <image:title>{title}</image:title>\n"
            f"      <image:caption>{caption}</image:caption>\n"
            f"{license_block}"
            f"    </image:image>\n"
            f"  </url>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
        + "\n".join(rows) + "\n"
        '</urlset>\n'
    )


def main():
    if not ATTRIBUTIONS.exists():
        print(f"Missing {ATTRIBUTIONS}. Run download_location_images.py first.")
        return
    data = json.loads(ATTRIBUTIONS.read_text(encoding="utf-8"))
    records = list(data.values())

    OUTPUT_HTML.write_text(render_html(records), encoding="utf-8")
    print(f"Wrote {OUTPUT_HTML} ({len(records)} entries)")

    OUTPUT_SITEMAP.write_text(render_image_sitemap(records), encoding="utf-8")
    print(f"Wrote {OUTPUT_SITEMAP}")


if __name__ == "__main__":
    main()
