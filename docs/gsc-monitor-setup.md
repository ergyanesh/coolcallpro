# GSC Indexation Monitor — One-Time Setup

This document covers the one-time setup steps to enable the automated daily
GSC indexation monitor (`scripts/gsc_index_monitor.py` + the
`.github/workflows/gsc-index-monitor.yml` GitHub Action). Once these steps
are complete, the system runs unattended and alerts on de-indexation drops
within 24 hours.

You only do this **once**. Total time: ~15 minutes.

---

## What you're setting up

A Google service account that the GitHub Action will use to call the
Search Console API daily, fetch the indexation status of every URL in
`sitemap.xml`, diff against yesterday, and alert if more than 5 URLs were
dropped from the index in 24 hours.

The script does NOT need write access to GSC. Read-only is sufficient.

---

## Path A — Service Account (recommended for unattended runs)

This is the path the GitHub Action uses. The service account JSON lives as
a GitHub secret; no human intervention is required after setup.

### Step 1 — Create a Google Cloud project (skip if you have one)

1. Open https://console.cloud.google.com/
2. Top bar → project dropdown → **NEW PROJECT**.
3. Project name: `coolcallpro-monitoring` (or whatever you prefer).
4. Click **Create**. Wait ~30 seconds for the project to be created.
5. Switch to the new project via the top bar dropdown.

### Step 2 — Enable the Search Console API

1. In the search bar at the top, type: **Search Console API**.
2. Click the result → **Enable**. Wait ~10 seconds.

### Step 3 — Create the service account

1. Navigation menu (☰) → **IAM & Admin** → **Service Accounts**.
2. **+ Create Service Account**.
3. Service account name: `gsc-index-monitor`.
4. Description: `Daily Search Console indexation status pull for coolcallpro.com`.
5. Click **Create and Continue**.
6. Skip the optional "Grant access" step → click **Continue** → **Done**.

### Step 4 — Download the JSON key

1. In the service accounts list, click the email of the one you just created
   (looks like `gsc-index-monitor@coolcallpro-monitoring.iam.gserviceaccount.com`).
2. **KEYS** tab → **ADD KEY** → **Create new key**.
3. Choose **JSON** → **Create**.
4. A file downloads to your computer. **Treat this like a password.**
5. **Copy the email address** of the service account from the page — you'll
   need it for the next step.

### Step 5 — Grant the service account access to your GSC property

1. Open https://search.google.com/search-console/users
2. Make sure you're on the property `sc-domain:coolcallpro.com` (top-left
   property selector). If you have a URL-prefix property only, use that one
   instead; the script's `SITE_URL` constant matches what you grant access
   to.
3. **Add user** → paste the service account email from Step 4 → **Permission**:
   **Restricted** is sufficient (Restricted = read-only; the script doesn't
   need to submit sitemaps or perform any write operation).
4. **Add**.

### Step 6 — Add the JSON as a GitHub secret

1. Open the downloaded JSON file in a text editor. Copy the **entire
   contents** (curly brace to curly brace, including all the line breaks).
2. Open https://github.com/ergyanesh/coolcallpro/settings/secrets/actions
3. **New repository secret**.
4. Name: `GSC_SERVICE_ACCOUNT_JSON` (must match exactly; the workflow looks
   up this exact name).
5. Value: paste the JSON content.
6. **Add secret**.

### Step 7 — Test the workflow manually

1. Open https://github.com/ergyanesh/coolcallpro/actions/workflows/gsc-index-monitor.yml
2. Click **Run workflow** → leave branch as `main` → **Run workflow**.
3. Wait ~2 minutes. The run should succeed. Look at the logs for:
   - "Sitemap has 220 URLs"
   - "Fetching URLs with impressions (last 28d)..."
   - "Wrote .gsc_state/report-YYYY-MM-DD.md"
4. After the run, the report file will be auto-committed to the repo. Open
   it: `.gsc_state/report-YYYY-MM-DD.md` — this is your first baseline
   snapshot.

From this point forward, the workflow runs daily at 14:00 UTC. If the
indexed-URL count drops by more than 5 in a single day, you get:
- A GitHub issue tagged `indexation` + `alert` with the dropped URLs and
  their `coverageState` reasons
- The next day's report shows the diff persistently

### Optional Step 8 — Wire up email alerts

The GitHub issue is the primary alert channel. If you also want email,
either:

- **(easier)** Enable GitHub's built-in email-on-issue setting for your
  account: https://github.com/notifications/profile → ensure "Participating
  notifications" is set to "Email."
- **(more configurable)** Add a step to the workflow that calls an SMTP
  action — the [`dawidd6/action-send-mail`](https://github.com/dawidd6/action-send-mail)
  action is the standard.

  **Do NOT use an `@coolcallpro.com` mailbox as the sender.** Google
  Workspace for this domain is being cancelled (2026-08-07) and the domain
  is moving to an SPF `-all` / DMARC `p=reject` posture, meaning no server
  is authorized to send as `@coolcallpro.com` — mail sent from it will be
  rejected outright. Use a Gmail app password, or a transactional provider
  on its own sending domain. See
  [workspace-cancellation-runbook.md](workspace-cancellation-runbook.md).

**Ownership warning:** the Cloud project and service account created in
Steps 1-4 must not be owned solely by a `@coolcallpro.com` Google account.
If they are, cancelling Workspace deletes them and this monitor silently
stops running. See Part 1 §4 of the
[cancellation runbook](workspace-cancellation-runbook.md).

---

## Path B — Local OAuth (if you don't want a service account)

Use this if you prefer to run the script on your own machine via Windows
Task Scheduler instead of via GitHub Actions.

### Step 1-4 — Same as Path A

Create the Cloud project, enable the API, but in **Step 3** instead of a
service account, create an **OAuth 2.0 Client ID**:

1. Navigation → **APIs & Services** → **Credentials**.
2. **+ Create credentials** → **OAuth client ID**.
3. Application type: **Desktop app**.
4. Name: `coolcallpro-gsc-local`.
5. **Create**. Click **DOWNLOAD JSON**. Save as
   `gsc-oauth-client.json` somewhere safe.

### Step 5 — Authorize once

```powershell
pip install google-auth-oauthlib google-api-python-client
python -c @"
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file(
    'gsc-oauth-client.json',
    scopes=['https://www.googleapis.com/auth/webmasters.readonly']
)
creds = flow.run_local_server(port=0)
import json
with open('gsc-oauth-token.json', 'w') as f:
    f.write(creds.to_json())
print('Wrote gsc-oauth-token.json — keep this file secret.')
"@
```

A browser will open. Sign in with the Google account that owns the GSC
property and grant access. The script stores a refresh token in
`gsc-oauth-token.json`.

### Step 6 — Schedule daily run

```powershell
$env:GSC_OAUTH_CREDENTIALS_FILE = "C:\Users\gyane\gsc-oauth-token.json"
python scripts/gsc_index_monitor.py
```

Wrap this in a Windows Task Scheduler task that runs daily at, say, 09:00
local time. Logs to `.gsc_state/report-YYYY-MM-DD.md`.

---

## Quotas

The script is designed to fit comfortably within GSC API quotas:

- **URL Inspection API**: 2,000 calls/day per site, 600 calls/minute per
  site. The site has ~220 URLs; a daily full sweep uses 11% of the daily
  quota, leaving headroom for ad-hoc investigation.
- **Search Analytics API**: 1,200 calls/minute per site, 25,000 rows per
  call. The daily pull is a single paginated call.

If you exceed quota (won't happen at current site size), the script
gracefully reports the error per-URL and continues. No crash.

---

## What if the workflow alerts you?

When an indexation drop is detected (>5 URLs removed from index in 24h):

1. Open the GitHub issue. It lists the dropped URLs with each one's
   `coverageState` reason (e.g., "Duplicate, Google chose different
   canonical than user", "Soft 404", "Crawled — currently not indexed").
2. For each reason category, the standard remediations are:
   - **"Duplicate, Google chose different canonical than user"**: review the
     URL's canonical tag — Google may be right that another URL is the
     "real" canonical. Fix the canonical or accept Google's choice.
   - **"Soft 404"**: the page exists (200 OK) but Google considers it
     low-quality / too thin. Add unique content, especially above the fold.
   - **"Crawled — currently not indexed"**: Google saw the page but chose
     not to index. Often a quality signal. Same fix as soft-404.
   - **"Excluded by 'noindex' tag"**: an accidental noindex got added. Check
     the page's `<meta robots>` and remove the noindex.
3. The same script can be re-run after a fix to confirm the URL is
   re-indexed: `python scripts/gsc_index_monitor.py --full-inspect`.

---

## What if you stop wanting this?

Disable the workflow at
https://github.com/ergyanesh/coolcallpro/actions/workflows/gsc-index-monitor.yml
→ **... menu** → **Disable workflow**.

Delete the secret at
https://github.com/ergyanesh/coolcallpro/settings/secrets/actions

Delete the service account at the Cloud Console **Service Accounts** page.

No other cleanup needed; the `.gsc_state/` directory and the script just
sit dormant.
