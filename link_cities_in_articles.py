"""
Mechanical article -> city page linker (Phase 4.1 of the city-page SEO plan).

For each article HTML file, finds the FIRST mention of each city that has a
published page and wraps that mention in an <a> to the city page. Only the
first mention per (article, city) pair is linked. Skips cities already
wrapped in an anchor. Does not touch <head>, <script>, or JSON-LD.
"""

import openpyxl
import os
import re

ARTICLES_ROOT = [
    "article-ac-summer.html",
    "article-carbon-monoxide.html",
    "article-emergency.html",
    "article-fall-prep.html",
    "article-furnace.html",
    "article-heat-pump.html",
    "article-hvac-financing.html",
    "article-maintenance.html",
    "article-refrigerant.html",
    "article-repair-vs-replace.html",
    "article-spring-ac.html",
    "article-winter-storm.html",
]
# Cities whose names collide with brand names, adjectives, or common English
# — skip to avoid false-positive links (e.g. "Wells Fargo" -> Fargo, ND).
STOP_LIST = {
    "Fargo",        # Wells Fargo
    "Mobile",       # adjective
    "Spring",       # season
    "Columbia",     # university, record label, country
    "Jackson",      # common surname
    "Jefferson",    # historical figure
    "Madison",      # historical figure
    "Lincoln",      # Abraham Lincoln / car brand
    "Washington",   # person / state / D.C.
    "Salem",        # Salem witch trials
    "Phoenix",      # mythological bird
    "Aurora",       # borealis (but absorbed anyway)
    "Charlotte",    # common first name
    "Richmond",     # common surname
    "Augusta",      # common first name
    "Savannah",     # common first name
    "Concord",      # concord grape
    "Dover",        # Dover sole
    "Independence", # common English noun
    "Liberty",      # common English noun
    "Reading",      # activity
    "Mesa",         # geological feature
    "Fremont",      # common surname
    "Jupiter",      # planet
    "Cambridge",    # university
    "Oxford",       # university
    "Hartford",     # insurance company
}

ARTICLES_SUB = [
    "articles/ac-compressor-buzzing-fan-not-spinning.html",
    "articles/furnace-blowing-cold-air-winter.html",
    "articles/hvac-leaking-water-inside-house.html",
    "articles/why-is-my-ac-blowing-warm-air.html",
]


def load_cities():
    wb = openpyxl.load_workbook("cities_updated.xlsx")
    ws = wb.active
    out = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        name, state = row[0], row[1]
        slug = (name.lower().replace(" ", "-").replace(".", "").replace("'", "")
                + "-" + state.lower())
        path = os.path.join("locations", slug + ".html")
        if os.path.exists(path):
            out.append((name, state, slug))
    out.sort(key=lambda x: -len(x[0]))
    return out


def split_main(html):
    """Return (head_part, main_part, tail_part). main_part is where we link."""
    m = re.search(r"<main[^>]*>", html)
    if not m:
        return html, "", ""
    start = m.end()
    e = re.search(r"</main>", html[start:])
    if not e:
        return html, "", ""
    end = start + e.start()
    return html[:start], html[start:end], html[end:]


def already_linked_to(main_html, slug, rel_prefix):
    target = f'href="{rel_prefix}locations/{slug}"'
    return target in main_html


def wrap_first_mention(main_html, city, state, slug, rel_prefix):
    """Find first mention of `city` in body text (not in any HTML tag, not inside
    an existing <a>, not inside <script> or <style>). Wrap it. Return (new_html, wrapped_bool)."""
    # Build a mask of "safe" text regions: outside tags, outside <script>/<style>.
    # Strategy: walk through the HTML, track whether we're inside a tag, script,
    # style, or anchor. Only replace within body text and only when not inside <a>.
    link_open = f'<a href="{rel_prefix}locations/{slug}">'
    link_close = '</a>'
    pattern = re.compile(r"\b" + re.escape(city) + r"\b")

    i = 0
    n = len(main_html)
    in_tag = False
    in_script = False
    in_style = False
    anchor_depth = 0
    # We need positions — collect all candidate positions then pick first.
    candidate_pos = -1

    # To avoid quadratic work, scan the HTML char-by-char once, tracking state,
    # and at each character run the regex against a slice starting there only
    # if we're in "safe body text". Optimization: instead, find all pattern
    # matches, then for each check if its position is in safe state via a
    # precomputed mask.

    # Build mask: True where char is in safe body text.
    mask = bytearray(n)
    while i < n:
        ch = main_html[i]
        if in_script:
            # look for </script>
            end = main_html.find("</script>", i)
            if end == -1:
                break
            i = end + len("</script>")
            in_script = False
            continue
        if in_style:
            end = main_html.find("</style>", i)
            if end == -1:
                break
            i = end + len("</style>")
            in_style = False
            continue
        if ch == "<":
            # Tag start — detect script/style/a open/close
            # Read tag name
            m = re.match(r"<\s*/?\s*([a-zA-Z0-9]+)", main_html[i:i+20])
            tag_name = m.group(1).lower() if m else ""
            is_close = main_html[i:i+2] == "</"
            # Find tag end
            end = main_html.find(">", i)
            if end == -1:
                break
            if tag_name == "script" and not is_close:
                in_script = True
                i = end + 1
                continue
            if tag_name == "style" and not is_close:
                in_style = True
                i = end + 1
                continue
            if tag_name == "a":
                if is_close:
                    if anchor_depth > 0:
                        anchor_depth -= 1
                else:
                    anchor_depth += 1
            i = end + 1
            continue
        # regular char
        if anchor_depth == 0:
            mask[i] = 1
        i += 1

    # Find earliest match fully within mask
    for m in pattern.finditer(main_html):
        s, e = m.start(), m.end()
        if all(mask[p] for p in range(s, e)):
            candidate_pos = s
            break

    if candidate_pos < 0:
        return main_html, False
    # Wrap
    s = candidate_pos
    e = s + len(city)
    new = main_html[:s] + link_open + main_html[s:e] + link_close + main_html[e:]
    return new, True


def process_file(path, cities, rel_prefix):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    head, main_part, tail = split_main(html)
    if not main_part:
        return 0
    wrapped_count = 0
    for city, state, slug in cities:
        if city in STOP_LIST:
            continue
        if already_linked_to(main_part, slug, rel_prefix):
            continue
        new_main, wrapped = wrap_first_mention(main_part, city, state, slug, rel_prefix)
        if wrapped:
            main_part = new_main
            wrapped_count += 1
    if wrapped_count:
        new_html = head + main_part + tail
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_html)
    return wrapped_count


def main():
    cities = load_cities()
    print(f"Loaded {len(cities)} linkable cities")
    total = 0
    for p in ARTICLES_ROOT:
        n = process_file(p, cities, rel_prefix="")
        print(f"  {p}: {n} links added")
        total += n
    for p in ARTICLES_SUB:
        n = process_file(p, cities, rel_prefix="../")
        print(f"  {p}: {n} links added")
        total += n
    print(f"\nTotal links added: {total}")


if __name__ == "__main__":
    main()
