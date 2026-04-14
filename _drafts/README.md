# Scheduled Article Drafts

Drop HTML articles here with filenames prefixed by their **publish date** in `YYYY-MM-DD-slug.html` format.

Example:
```
_drafts/
├── 2026-04-15-ductwork-sizing-guide.html
├── 2026-04-17-heat-pump-vs-furnace.html
└── 2026-04-19-smart-thermostats.html
```

## How it works

1. Every day at **9:00 AM EST**, a GitHub Action (`publish-scheduled-articles.yml`) runs.
2. It looks for any `_drafts/*.html` file where the date prefix is **today or earlier**.
3. For each due article, it:
   - Moves the file to `articles/{slug}.html` (strips the date prefix)
   - Adds the URL to `sitemap.xml`
   - Adds a 301 redirect in `_redirects`
   - Adds a card to `articles.html` hub
4. Commits the changes to `main`.
5. Cloudflare Pages auto-deploys within ~60 seconds.

## Manual trigger

You can also trigger the workflow manually from:
**GitHub → Actions → "Publish Scheduled Articles" → Run workflow**

This is useful if you want to publish something immediately without waiting for the daily cron.

## Notes

- Filenames must match the pattern `YYYY-MM-DD-slug.html`. Other files are ignored.
- Articles that don't have a date prefix stay here indefinitely (safe).
- The slug becomes the final URL: `2026-04-15-ductwork-sizing-guide.html` → `coolcallpro.com/articles/ductwork-sizing-guide`
