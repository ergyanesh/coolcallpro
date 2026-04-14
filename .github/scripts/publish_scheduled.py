#!/usr/bin/env python3
"""
Scheduled article publisher.

Reads _drafts/*.html files. Filename must start with YYYY-MM-DD date prefix.
If today's date >= the prefix date, the article is "due" to publish:
  - Moves the file from _drafts/ to articles/ (stripping the date prefix)
  - Updates articles.html hub to include the new article card
  - Updates sitemap.xml to include the new URL
  - Adds a redirect in _redirects for the clean URL

Example: _drafts/2026-04-15-ductwork-basics.html
  On April 15 or later, becomes: articles/ductwork-basics.html

Outputs to GITHUB_OUTPUT whether anything was published (for the workflow to decide to commit).
"""

import os
import re
import sys
import shutil
from datetime import date
from pathlib import Path

DRAFTS_DIR = Path("_drafts")
ARTICLES_DIR = Path("articles")
ARTICLES_HUB = Path("articles.html")
SITEMAP = Path("sitemap.xml")
REDIRECTS = Path("_redirects")

# Filename pattern: YYYY-MM-DD-slug.html
DATE_PREFIX_RE = re.compile(r'^(\d{4})-(\d{2})-(\d{2})-(.+)\.html$')


def find_due_drafts():
    """Return list of (draft_path, target_slug, article_date) for drafts due today or earlier."""
    if not DRAFTS_DIR.exists():
        return []

    today = date.today()
    due = []

    for f in sorted(DRAFTS_DIR.iterdir()):
        if not f.is_file() or not f.name.endswith('.html'):
            continue

        match = DATE_PREFIX_RE.match(f.name)
        if not match:
            print(f"SKIP (no date prefix): {f.name}", file=sys.stderr)
            continue

        y, m, d, slug = match.groups()
        try:
            article_date = date(int(y), int(m), int(d))
        except ValueError:
            print(f"SKIP (invalid date): {f.name}", file=sys.stderr)
            continue

        if article_date <= today:
            due.append((f, slug, article_date))

    return due


def extract_article_title(filepath):
    """Extract the <h1> title from an article HTML file."""
    content = filepath.read_text(encoding='utf-8')
    match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
    if match:
        # Strip HTML tags from inside h1
        title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
        return title
    return None


def extract_article_description(filepath):
    """Extract meta description."""
    content = filepath.read_text(encoding='utf-8')
    match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', content)
    if match:
        return match.group(1)
    return ""


def add_to_sitemap(slug):
    """Add the new article URL to sitemap.xml."""
    if not SITEMAP.exists():
        print(f"WARN: {SITEMAP} not found", file=sys.stderr)
        return False

    content = SITEMAP.read_text(encoding='utf-8')
    new_url = f"https://coolcallpro.com/articles/{slug}"

    if new_url in content:
        return False  # already there

    today_iso = date.today().isoformat()
    new_entry = (
        f'  <url>\n'
        f'    <loc>{new_url}</loc>\n'
        f'    <lastmod>{today_iso}</lastmod>\n'
        f'    <changefreq>monthly</changefreq>\n'
        f'    <priority>0.8</priority>\n'
        f'  </url>\n'
    )

    # Insert before </urlset>
    content = content.replace('</urlset>', new_entry + '</urlset>')
    SITEMAP.write_text(content, encoding='utf-8')
    return True


def add_to_redirects(slug):
    """Add a 301 redirect for the .html version -> clean URL."""
    if not REDIRECTS.exists():
        return False

    content = REDIRECTS.read_text(encoding='utf-8')
    redirect_line = f"/articles/{slug}.html /articles/{slug} 301"

    if redirect_line in content:
        return False

    # Append to end
    if not content.endswith('\n'):
        content += '\n'
    content += redirect_line + '\n'
    REDIRECTS.write_text(content, encoding='utf-8')
    return True


def extract_article_image(filepath):
    """Extract the first article image (for use in the hub card)."""
    content = filepath.read_text(encoding='utf-8')
    # Look for the lead image inside the article content
    match = re.search(r'<img\s+src="(images/[^"]+\.webp)"\s+alt="([^"]*)"', content)
    if match:
        return match.group(1), match.group(2)
    return None, ""


def extract_article_category(filepath):
    """Extract the article category from the tag class (tag-emergency, tag-maintenance, etc)."""
    content = filepath.read_text(encoding='utf-8')
    match = re.search(r'article-tag\s+tag-(\w+)', content)
    if match:
        return match.group(1)
    return "maintenance"  # safe default


def add_to_articles_hub(slug, title, description, filepath):
    """Add a card to articles.html hub for the new article.

    Finds the articles-list-grid container and inserts a new card at the top.
    """
    if not ARTICLES_HUB.exists():
        return False

    content = ARTICLES_HUB.read_text(encoding='utf-8')

    image_src, image_alt = extract_article_image(filepath)
    category = extract_article_category(filepath)

    # Map category to emoji + label (matches existing site conventions)
    category_map = {
        "emergency": ("&#128680;", "Emergency"),
        "safety": ("&#9888;&#65039;", "Safety"),
        "cost": ("&#128176;", "Cost"),
        "maintenance": ("&#128295;", "Maintenance"),
        "seasonal": ("&#127777;&#65039;", "Seasonal"),
    }
    emoji, cat_label = category_map.get(category, ("&#128295;", "Maintenance"))

    today_month = date.today().strftime("%b %Y")

    img_html = (
        f'<div class="article-img-wrap"><img src="{image_src}" alt="{image_alt}" '
        f'loading="lazy" width="640" height="640" />'
        f'<span class="article-tag tag-{category}">{emoji} {cat_label}</span></div>'
    ) if image_src else ''

    card = f'''
                    <article class="article-card" data-category="{category}">
                        {img_html}
                        <div class="article-body">
                            <div class="article-meta"><span>{today_month}</span></div>
                            <h3><a href="articles/{slug}">{title}</a></h3>
                            <p>{description}</p>
                            <div class="article-footer"><a href="articles/{slug}" class="read-more">Read Article &rarr;</a></div>
                        </div>
                    </article>
'''

    # Match the real container in this site
    marker_re = re.compile(r'(<div class="articles-list-grid"[^>]*>)', re.MULTILINE)
    match = marker_re.search(content)
    if not match:
        print(f"WARN: Could not find 'articles-list-grid' in {ARTICLES_HUB}. Manual add required.", file=sys.stderr)
        return False

    insert_pos = match.end()
    new_content = content[:insert_pos] + card + content[insert_pos:]
    ARTICLES_HUB.write_text(new_content, encoding='utf-8')
    return True


def publish_article(draft_path, slug, article_date):
    """Move a draft into articles/ and update site indexes."""
    ARTICLES_DIR.mkdir(exist_ok=True)
    target_path = ARTICLES_DIR / f"{slug}.html"

    if target_path.exists():
        print(f"WARN: Target already exists, skipping: {target_path}", file=sys.stderr)
        return False

    # Move file
    shutil.move(str(draft_path), str(target_path))
    print(f"PUBLISHED: {draft_path.name} -> {target_path}")

    # Extract title and description for hub/sitemap
    title = extract_article_title(target_path) or slug.replace('-', ' ').title()
    description = extract_article_description(target_path)

    # Update indexes
    add_to_sitemap(slug)
    add_to_redirects(slug)
    add_to_articles_hub(slug, title, description, target_path)

    return True


def main():
    due = find_due_drafts()

    if not due:
        print("No drafts due for publishing today.")
        set_output("published", "false")
        return

    print(f"Found {len(due)} draft(s) due for publishing:")
    for path, slug, d in due:
        print(f"  - {path.name} (scheduled {d})")

    published_count = 0
    for draft_path, slug, article_date in due:
        if publish_article(draft_path, slug, article_date):
            published_count += 1

    set_output("published", "true" if published_count > 0 else "false")
    set_output("count", str(published_count))
    print(f"\nTotal published: {published_count}")


def set_output(key, value):
    """Write to GITHUB_OUTPUT for the workflow to read."""
    output_file = os.environ.get('GITHUB_OUTPUT')
    if output_file:
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"{key}={value}\n")


if __name__ == '__main__':
    main()
