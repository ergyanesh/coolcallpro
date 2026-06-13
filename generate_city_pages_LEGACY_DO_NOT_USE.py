# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!! LEGACY GENERATOR -- DO NOT RUN. PRODUCTION USES v3 / v4.            !!!
# !!! Renamed 2026-06-13. Reason: this file emits canonical with .html    !!!
# !!! suffix, which would re-introduce the duplicate-URL drift that       !!!
# !!! commit cb5f9a3 fixed. Production uses generate_city_pages_v3.py     !!!
# !!! (city pages) and generate_state_hubs.py (state hubs).               !!!
# !!! Kept for git-history reference only. If you genuinely need it, fix  !!!
# !!! line 64 (.html canonical) first before running.                     !!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import openpyxl
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
XLSX_PATH = os.path.join(BASE_DIR, 'cities.xlsx')
LOCATIONS_DIR = os.path.join(BASE_DIR, 'locations')

os.makedirs(LOCATIONS_DIR, exist_ok=True)

wb = openpyxl.load_workbook(XLSX_PATH)
ws = wb.active

# State abbreviation mapping
STATE_ABBR = {
    'AZ': 'Arizona', 'TX': 'Texas', 'MN': 'Minnesota', 'IL': 'Illinois',
    'NV': 'Nevada', 'CO': 'Colorado', 'GA': 'Georgia', 'MA': 'Massachusetts',
    'NC': 'North Carolina', 'FL': 'Florida', 'OK': 'Oklahoma', 'MO': 'Missouri',
    'LA': 'Louisiana', 'PA': 'Pennsylvania', 'MI': 'Michigan', 'WI': 'Wisconsin',
    'AL': 'Alabama'
}

def slugify(city, state):
    slug = f"{city}-{state}".lower().replace(' ', '-').replace('.', '')
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    return slug

def generate_page(city, state, cost_range, neighborhoods, zips, permit_office, utility):
    slug = slugify(city, state)
    state_full = STATE_ABBR.get(state, state)

    # Fix encoding: replace common mojibake
    cost_range = cost_range.replace('\u2013', '\u2013').replace('â\x80\x93', '\u2013').replace('Ã¢â‚¬â€œ', '\u2013')
    # Clean up any remaining bad chars
    cost_range = re.sub(r'[^\$0-9,.\u2013\-\s]', '', cost_range)
    if '\u2013' not in cost_range and '-' not in cost_range:
        cost_range = cost_range.replace('  ', ' - ')

    neighborhoods_list = [n.strip() for n in neighborhoods.split(',')]
    neighborhoods_display = ', '.join(neighborhoods_list[:4]) + f', and {neighborhoods_list[4]}' if len(neighborhoods_list) >= 5 else ', '.join(neighborhoods_list)

    zips_list = [z.strip() for z in zips.split(',')]
    zips_display = ', '.join(zips_list)

    # Service bullets - inject city into at least 2
    services = [
        f"Emergency AC Repair in {city}",
        f"Furnace Repair &amp; Heating Service in {city}",
        "Central Air Conditioning Installation &amp; Replacement",
        "HVAC System Maintenance &amp; Tune-Ups",
        "Ductwork Inspection, Cleaning &amp; Sealing"
    ]
    services_html = '\n'.join([f'              <li>{s}</li>' for s in services])

    html = f'''<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>24/7 Emergency HVAC Repair &amp; AC Service in {city}, {state} | Cool Call Pro</title>
  <meta name="description"
    content="Need emergency HVAC repair in {city}, {state_full}? Cool Call Pro connects you with 24/7 local HVAC technicians covering {zips_list[0]} and surrounding areas. Call (844) 582-1795." />
  <link rel="canonical" href="https://coolcallpro.com/locations/{slug}.html" />

  <!-- Open Graph -->
  <meta property="og:type" content="website" />
  <meta property="og:title" content="24/7 Emergency HVAC Repair &amp; AC Service in {city}, {state} | Cool Call Pro" />
  <meta property="og:description" content="Connect with independent HVAC professionals in {city}, {state_full}. Emergency AC and furnace service available 24/7." />
  <meta property="og:url" content="https://coolcallpro.com/locations/{slug}.html" />
  <meta property="og:site_name" content="Cool Call Pro" />
  <meta property="og:image" content="https://coolcallpro.com/images/og-homepage.webp" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="24/7 Emergency HVAC Repair &amp; AC Service in {city}, {state}" />
  <meta name="twitter:description" content="Connect with independent HVAC professionals in {city}, {state_full}." />
  <meta name="twitter:image" content="https://coolcallpro.com/images/og-homepage.webp" />

  <!-- Favicon -->
  <link rel="icon" href="/favicon.ico" type="image/x-icon" />
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />

  <link rel="stylesheet" href="../css/style.min.css" />
  <link rel="preconnect" href="https://fonts.googleapis.com" crossorigin="anonymous">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preload" as="style"
    href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Outfit:wght@400;600;700;800&display=swap"
    onload="this.onload=null;this.rel='stylesheet'">
  <noscript>
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Outfit:wght@400;600;700;800&display=swap"
      rel="stylesheet">
  </noscript>

  <!-- Google tag (gtag.js) - GA4 -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-WD0ND0K60Q"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-WD0ND0K60Q');
  </script>

  <!-- Structured Data: Local Business + FAQ -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "BreadcrumbList",
        "itemListElement": [
          {{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://coolcallpro.com/"}},
          {{"@type": "ListItem", "position": 2, "name": "Locations", "item": "https://coolcallpro.com/locations.html"}},
          {{"@type": "ListItem", "position": 3, "name": "{city}, {state}", "item": "https://coolcallpro.com/locations/{slug}.html"}}
        ]
      }},
      {{
        "@type": "FAQPage",
        "mainEntity": [
          {{
            "@type": "Question",
            "name": "Do I need a permit to replace my AC in {city}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Yes, ensure your contractor files a mechanical permit with the {permit_office}."
            }}
          }},
          {{
            "@type": "Question",
            "name": "Are there HVAC rebates in {city}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Upgrading to a high-efficiency unit may qualify you for rebates through {utility}."
            }}
          }},
          {{
            "@type": "Question",
            "name": "What ZIP codes do you serve in {city}?",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "Our network covers {city} and surrounding areas including {zips_display}. Call (844) 582-1795 to verify service availability for your specific ZIP code."
            }}
          }}
        ]
      }}
    ]
  }}
  </script>

  <style>
    .city-hero {{
      background: linear-gradient(rgba(10, 22, 40, 0.88), rgba(10, 22, 40, 0.88)), url('../images/hvac_emergency.webp');
      background-size: cover;
      background-position: center;
      color: white;
      padding: 100px 0 80px;
      text-align: center;
    }}
    .city-hero h1 {{
      font-family: var(--font-display);
      font-size: 2.6rem;
      font-weight: 800;
      line-height: 1.2;
      margin-bottom: 20px;
      letter-spacing: -0.02em;
    }}
    .city-hero p {{
      font-size: 1.15rem;
      max-width: 620px;
      margin: 0 auto;
      opacity: 0.9;
      line-height: 1.7;
    }}
    .city-context {{
      font-size: 1.1rem;
      line-height: 1.85;
      color: var(--gray-700);
      max-width: 760px;
      margin: 0 auto 40px;
    }}
    .city-services {{
      max-width: 760px;
      margin: 0 auto 48px;
    }}
    .city-services h2 {{
      font-size: 1.6rem;
      margin-bottom: 16px;
      color: var(--navy);
    }}
    .city-services ul {{
      list-style: none;
      padding: 0;
    }}
    .city-services ul li {{
      padding: 12px 0 12px 28px;
      position: relative;
      font-size: 1.05rem;
      color: var(--gray-700);
      border-bottom: 1px solid var(--gray-100);
    }}
    .city-services ul li::before {{
      content: "\\2714";
      color: var(--orange);
      font-weight: 700;
      position: absolute;
      left: 0;
      top: 12px;
    }}
    .city-faq {{
      max-width: 760px;
      margin: 0 auto 48px;
    }}
    .city-faq h2 {{
      font-size: 1.6rem;
      margin-bottom: 20px;
      color: var(--navy);
    }}
    @media (max-width: 768px) {{
      .city-hero {{
        padding: 80px 0 60px;
      }}
      .city-hero h1 {{
        font-size: 1.8rem;
      }}
    }}
  </style>
</head>

<body>

  <!-- Skip to Content -->
  <a href="#main-content" class="skip-link">Skip to main content</a>

  <!-- Top Bar -->
  <div class="topbar">
    <div class="container topbar-inner" style="justify-content: center; padding: 10px; font-weight: 600;">
      <span class="topbar-text">24/7 Referral Service &#8212; Connecting Homeowners with Independent HVAC Professionals</span>
    </div>
  </div>

  <!-- Header -->
  <header class="header" id="header">
    <nav class="nav container" role="navigation" aria-label="Main navigation">
      <a href="../index.html" class="logo">
        <span class="logo-icon">&#10052;&#65039;</span>
        <span class="logo-text">CoolCall<span class="logo-accent">Pro</span></span>
      </a>
      <ul class="nav-links" id="navLinks">
        <li><a href="../emergency.html" class="nav-link emergency-link">&#128680; Emergency Service</a></li>
        <li><a href="../costs.html" class="nav-link">Cost Guide</a></li>
        <li><a href="../safety.html" class="nav-link">Safety Tips</a></li>
        <li><a href="../locations.html" class="nav-link active">&#128205; Locations</a></li>
        <li><a href="../articles.html" class="nav-link">Articles</a></li>
        <li><a href="../about.html" class="nav-link">About</a></li>
        <li><a href="../contact.html" class="nav-link">Contact</a></li>
      </ul>
      <a href="tel:+18445821795" class="btn btn-cta nav-cta btn-vibrate" id="headerNavCta" aria-hidden="true"
        tabindex="-1" style="opacity: 0; pointer-events: none; transition: opacity 0.3s ease;"><span
          class="phone-icon">&#128222;</span>
        <span class="hide-on-mobile">(844) 582-1795</span></a>
      <button class="hamburger" id="hamburger" aria-label="Menu">&#9776;</button>
    </nav>
  </header>

  <!-- Main Content -->
  <main id="main-content">

    <!-- Hero Section -->
    <section class="city-hero" id="hero">
      <div class="container">
        <span class="section-tag" style="background: rgba(255,255,255,0.1); color: #fff;">&#128205; {city}, {state}</span>
        <h1>24/7 Emergency HVAC Repair &amp; AC Service in {city}, {state}</h1>
        <p>Connect with independent local HVAC professionals in {city}, {state_full}. Emergency AC repair, furnace service, and system installation available 24/7.</p>
        <div style="margin-top: 28px;">
          <a href="tel:+18445821795" class="btn btn-primary btn-lg btn-vibrate"><span class="phone-icon">&#128222;</span> Call Now — (844) 582-1795</a>
        </div>
        <div class="jump-links" style="margin-top: 16px;">
          <a href="#services" class="jump-link" style="color: rgba(255,255,255,0.8);">Services</a>
          <span class="jump-link-dot" style="color: rgba(255,255,255,0.5);">&#8226;</span>
          <a href="#how-it-works" class="jump-link" style="color: rgba(255,255,255,0.8);">How It Works</a>
          <span class="jump-link-dot" style="color: rgba(255,255,255,0.5);">&#8226;</span>
          <a href="#faqs" class="jump-link" style="color: rgba(255,255,255,0.8);">FAQs</a>
        </div>
      </div>
    </section>

    <!-- Breadcrumb -->
    <div class="breadcrumb-nav">
      <div class="container">
        <nav aria-label="Breadcrumb">
          <ol class="breadcrumb-list">
            <li><a href="../index.html">Home</a></li>
            <li><a href="../locations.html">Locations</a></li>
            <li aria-current="page">{city}, {state}</li>
          </ol>
        </nav>
      </div>
    </div>

    <!-- Local Context Paragraph -->
    <section class="section" style="padding: 48px 0 0;">
      <div class="container">
        <div class="city-context">
          <p>Need emergency HVAC repair in <strong>{city}, {state_full}</strong>? Whether you live in <strong>{neighborhoods_display}</strong>, we connect you with 24/7 technicians covering <strong>{zips_display}</strong>. A standard AC replacement in the area typically costs between <strong>{cost_range}</strong>. Ensure your contractor pulls the proper mechanical permits through the <strong>{permit_office}</strong>.</p>
        </div>

        <!-- Services List -->
        <div class="city-services" id="services">
          <h2>HVAC Services in {city}, {state}</h2>
          <ul>
{services_html}
          </ul>
        </div>
      </div>
    </section>

    <!-- How It Works (same as home page) -->
    <section class="section section-dark" id="how-it-works">
      <div class="container">
        <div class="section-header">
          <span class="section-tag"
            style="background: rgba(255,165,0,0.15); color: var(--orange-light); border-color: rgba(255,165,0,0.3);">&#9889;
            Simple Process</span>
          <h2 class="section-title">How It Works</h2>
          <p class="section-sub">From your first call to getting connected with an independent HVAC provider in {city}, {state} &#8212; here's
            exactly what happens.</p>
        </div>

        <div class="steps-grid">

          <div class="step-card">
            <div class="step-number">01</div>
            <div class="step-icon"><span class="phone-icon">&#128222;</span></div>
            <h3>Call and Tell Us Your Issue</h3>
            <p>Call our 24/7 service line and tell us your HVAC issue. Your request will be routed to an independent professional serving {city} and surrounding areas.</p>
          </div>

          <div class="step-card">
            <div class="step-number">02</div>
            <div class="step-icon">&#128269;</div>
            <h3>Connect with an HVAC Provider</h3>
            <p>We connect you with an independent HVAC professional serving your {city}, {state} ZIP code. Licensing, insurance, and availability vary by provider.</p>
          </div>

          <div class="step-card">
            <div class="step-number">03</div>
            <div class="step-icon">&#128736;&#65039;</div>
            <h3>Review Options &amp; Schedule</h3>
            <p>A local {city} provider will confirm availability and discuss options. Service options and dispatch times vary by area.</p>
          </div>

        </div>

        <div style="text-align: center; margin-top: 48px;">
          <a href="tel:+18445821795" class="btn btn-primary btn-lg btn-vibrate"><span class="phone-icon">&#128222;</span> Call Now — (844) 582-1795</a>
        </div>
      </div>
    </section>

    <!-- FAQs -->
    <section class="section" id="faqs">
      <div class="container" style="max-width: 800px;">
        <div class="city-faq">
          <h2>Frequently Asked Questions &#8212; {city}, {state}</h2>
          <div class="faq-list" style="margin-top: 24px;">
            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>Do I need a permit to replace my AC in {city}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>Yes, ensure your contractor files a mechanical permit with the <strong>{permit_office}</strong>. Pulling the correct permits protects you as a homeowner and ensures work is inspected to code.</p>
                </div>
              </div>
            </div>

            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>Are there HVAC rebates in {city}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>Upgrading to a high-efficiency unit may qualify you for rebates through <strong>{utility}</strong>. Contact them directly or ask your HVAC contractor about available energy efficiency incentives in {city}.</p>
                </div>
              </div>
            </div>

            <div class="faq-item">
              <button class="faq-q" aria-expanded="false">
                <span>What ZIP codes do you serve in {city}?</span>
                <span class="faq-icon"></span>
              </button>
              <div class="faq-a">
                <div class="faq-a-inner">
                  <p>Our network covers {city} and surrounding areas including <strong>{zips_display}</strong>. Call <a href="tel:+18445821795" style="color: var(--orange); font-weight: 600;">(844) 582-1795</a> to verify service availability for your specific ZIP code.</p>
                </div>
              </div>
            </div>
          </div>

          <div style="text-align: center; margin-top: 32px;">
            <a href="tel:+18445821795" class="btn btn-primary btn-lg btn-vibrate"><span class="phone-icon">&#128222;</span> Call Now — (844) 582-1795</a>
          </div>
        </div>
      </div>
    </section>

  </main>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <a href="../index.html" class="logo"><span class="logo-icon">&#10052;&#65039;</span><span
              class="logo-text">CoolCall<span class="logo-accent">Pro</span></span></a>
          <p>Connecting homeowners with independent HVAC professionals across the US. Available 24/7 in many areas.</p>
          <div class="footer-contact">
            <a href="tel:+18445821795" class="footer-phone">(844) 582-1795</a>
            <span>24/7 Service Line</span>
          </div>
        </div>
        <div class="footer-col">
          <h4>Resources</h4>
          <ul>
            <li><a href="../costs.html">Cost Guide</a></li>
            <li><a href="../emergency.html">Emergency Service</a></li>
            <li><a href="../safety.html">Safety Tips</a></li>
            <li><a href="../articles.html">All Articles</a></li>
            <li><a href="../locations.html">Locations</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Company</h4>
          <ul>
            <li><a href="../about.html">About Us</a></li>
            <li><a href="../contact.html">Contact</a></li>
            <li><a href="../author-gyanesh.html">Author</a></li>
            <li><a href="../privacy.html">Privacy Policy</a></li>
            <li><a href="../advertising-disclosure.html">Advertising Disclosure</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Service Areas</h4>
          <ul class="service-areas">
            <li>Texas (All major cities)</li>
            <li>Florida (Tampa, Miami, Orlando)</li>
            <li>Arizona (Phoenix metro)</li>
            <li>Georgia (Atlanta metro)</li>
            <li>California (LA, San Diego)</li>
            <li>North Carolina</li>
            <li>Illinois (Chicago area)</li>
            <li><a href="../locations.html">All 50 states &#8594;</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p><strong style="color: rgba(255,255,255,0.82);">How this site works:</strong> We publish HVAC cost and
          troubleshooting information and may connect callers to independent service providers. We do not perform HVAC
          services ourselves. Pricing, availability, and response times vary by provider and location.</p>
        <p><strong style="color: rgba(255,255,255,0.82);">Editorial standards:</strong> Our content focuses on helpful
          troubleshooting tips and realistic pricing information. We avoid guarantees; actual pricing depends on the
          provider and situation. We clearly disclose compensation for referrals. We update content for clarity and
          accuracy when needed.</p>
        <p><strong style="color: rgba(255,255,255,0.82);">Disclaimer:</strong> Cool Call Pro is a free service to assist homeowners in connecting with local service providers. All contractors/providers are independent and Cool Call Pro does not warrant or guarantee any work performed. It is the responsibility of the homeowner to verify that the hired contractor furnishes the necessary license and insurance required for the work being performed. All persons depicted in a photo or video are actors or models and not contractors listed on Cool Call Pro.</p>
        <p>&copy; 2026 Cool Call Pro. All rights reserved. &nbsp;&#183;&nbsp; <a href="../privacy.html">Privacy
            Policy</a> &nbsp;&#183;&nbsp; <a href="../terms.html">Terms of Use</a> &nbsp;&#183;&nbsp; <a
            href="../disclaimer.html">Disclaimer</a> &nbsp;&#183;&nbsp; <a href="../advertising-disclosure.html">Advertising
            Disclosure</a></p>
      </div>
    </div>
  </footer>

  <script src="../js/main.min.js"></script>

  <!-- Mobile Call Bar -->
  <div class="mobile-call-bar">
    <a href="tel:+18445821795"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style="width: 1.25em; height: 1.25em; position: relative; top: 0.15em;"><path d="M20.01 15.38c-1.23 0-2.42-.2-3.53-.56-.35-.12-.74-.03-1.01.24l-1.57 1.97c-2.83-1.35-5.48-3.9-6.89-6.83l1.95-1.66c.27-.28.35-.67.24-1.02-.37-1.11-.56-2.3-.56-3.53 0-.54-.45-.99-.99-.99H4.19C3.65 3 3 3.24 3 3.99 3 13.28 10.73 21 20.01 21c.71 0 1.01-.63 1.01-1.18v-3.45c0-.54-.45-.99-.99-.99z"/></svg> Call Now &#8212; (844) 582-1795</a>
  </div>
</body>

</html>'''

    filepath = os.path.join(LOCATIONS_DIR, f'{slug}.html')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    return slug, city, state


# Process all rows
generated = []
for row in ws.iter_rows(min_row=2, values_only=True):
    city, state, cost, neighborhoods, zips, permit, utility = [str(v) if v else '' for v in row]
    if city and state:
        slug, c, s = generate_page(city, state, cost, neighborhoods, zips, permit, utility)
        generated.append((slug, c, s))
        print(f"Generated: locations/{slug}.html")

print(f"\nTotal pages generated: {len(generated)}")

# Output the list for locations.html update
print("\n--- LINKS FOR LOCATIONS.HTML ---")
for slug, city, state in sorted(generated, key=lambda x: x[1]):
    print(f'<a href="locations/{slug}.html" style="color: var(--orange); font-weight: 600;">{city}, {state}</a>')
