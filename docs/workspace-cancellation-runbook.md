# Google Workspace Cancellation Runbook

**Status:** open — created 2026-08-07, when `hello@` / `admin@coolcallpro.com`
were removed from the site and the `/contact` form became the only written
channel.

Cancelling Workspace deletes the Google **account** `admin@coolcallpro.com` (and
any other @coolcallpro.com user), not just the mailbox. Anything owned by or
logged in as that account goes with it. This runbook is ordered by severity ×
recoverability — do it top to bottom, and **do not cancel until every item in
Part 1 is checked off.**

The single question to ask at each step: *was this set up under
`admin@coolcallpro.com` / `hello@coolcallpro.com`, or under
`gyanesh.gulshan@gmail.com`?* If it's a @coolcallpro.com account, migrate it.
If it's already the Gmail account, tick the box and move on.

---

## Part 1 — Must be done BEFORE cancelling

### 1. Domain registration — Squarespace Domains ⚠ most severe

`coolcallpro.com` is registered with **Squarespace Domains II LLC** (this is the
old Google Domains business, migrated to Squarespace in 2023) and **expires
2027-03-04**. DNS is delegated to Cloudflare (`christian.ns.cloudflare.com`,
`katelyn.ns.cloudflare.com`), but Cloudflare is only the DNS host — Squarespace
still controls the registration.

If the Squarespace account login, or the registrant contact email, is a
@coolcallpro.com address, then after cancellation you cannot log in to renew or
transfer, and renewal notices bounce. **Losing the domain is the one failure on
this list that is not recoverable** — the site, all 182 indexed pages, and the
entire SEO history go with it.

- [ ] Log in at https://account.squarespace.com/domains — note which email you
      used. If it's @coolcallpro.com, change the account email to
      `gyanesh.gulshan@gmail.com` **now**.
- [ ] Check the domain's registrant/admin/tech contact email in the domain's
      contact settings. Change any @coolcallpro.com address to the Gmail one.
- [ ] Confirm auto-renew is ON and the card on file is current.
- [ ] Optional but worth it: transfer the domain to **Cloudflare Registrar**
      (at-cost pricing, and consolidates it with the DNS you already run there).
      Requires the domain to be unlocked and >60 days since last transfer.

### 2. Google Analytics 4 — data is unrecoverable

Property `G-WD0ND0K60Q`. If the only account with Admin on the GA4 property is
`admin@coolcallpro.com`, deleting that account orphans the property. Unlike
Search Console there is **no DNS-based way to re-claim it** — recovery means
Google support, and it usually fails.

- [ ] https://analytics.google.com → Admin → **Account access management** AND
      **Property access management** (both levels, they're separate).
- [ ] Add `gyanesh.gulshan@gmail.com` with role **Administrator** at both levels.
- [ ] Accept the invite from the Gmail account and confirm it shows as
      Administrator before proceeding.

### 3. Google Search Console

Property `sc-domain:coolcallpro.com`. Lower risk than GA4 — verification is via
the `google-site-verification=JcMB8fi-...` DNS TXT record at the apex, which you
control through Cloudflare. If you lost the account you could re-verify from a
new one and the historical data (16-month window) would come back. Do it anyway
so there's no gap.

- [ ] https://search.google.com/search-console/users → **Add user** →
      `gyanesh.gulshan@gmail.com` → Permission: **Owner** (not Full — Owner is
      what survives independently).
- [ ] Do **NOT** delete the `google-site-verification` TXT record in Cloudflare.
      It is the domain's proof of ownership.

### 4. Google Cloud project `coolcallpro-monitoring`

Hosts the `gsc-index-monitor@coolcallpro-monitoring.iam.gserviceaccount.com`
service account whose JSON key is the `GSC_SERVICE_ACCOUNT_JSON` GitHub secret.
That key is what the daily GSC indexation monitor
(`.github/workflows/gsc-index-monitor.yml`) authenticates with. If the project is
deleted with the Workspace org, the key stops working and the daily monitor
silently starts failing.

- [ ] https://console.cloud.google.com → select project `coolcallpro-monitoring`
      → **IAM & Admin → IAM** → grant `gyanesh.gulshan@gmail.com` the **Owner**
      role.
- [ ] Also check **IAM & Admin → Settings**: if the project sits under a Workspace
      *organization*, it must be **migrated out of the org** before cancellation,
      not just re-shared. A project inside an org that gets deleted goes with it
      regardless of who has Owner. If it shows "Organization: coolcallpro.com",
      that's the case — moving it needs to happen while the org still exists.
- [ ] Recovery path if this is missed: recreate the project + service account
      from scratch following `docs/gsc-monitor-setup.md` Steps 1-6, then replace
      the GitHub secret. ~15 minutes, no data loss (reports are committed to the
      repo in `.gsc_state/`).

### 5. Contact-form Apps Script + Sheet

Covered in detail in the commit that removed the site email. Same ownership
question.

- [ ] Open the Sheet the form writes to; check the owning account.
- [ ] If @coolcallpro.com: create the Sheet fresh on the Gmail account and deploy
      the script from `scripts/contact-form-apps-script.gs`, then paste the new
      `/exec` URL into `CONTACT_FORM_ENDPOINT` in `js/main.js`.
- [ ] If already Gmail: just add the `Email` column by pasting the updated script
      and redeploying as a **new version** of the existing deployment (keeps the
      URL, so no code change needed).

### 6. Anything else logged in as @coolcallpro.com

- [ ] **MarketCall** partner account — this is the revenue channel. Check the
      login email and the notification email on the account. If either is
      @coolcallpro.com, change it. Missing a MarketCall notice costs money.
- [ ] **Cloudflare** account email (the Pages project + DNS live here).
- [ ] **GitHub** account email for `ergyanesh/coolcallpro`.
- [ ] Bing Webmaster Tools / IndexNow, if ever set up.
- [ ] Any password-reset destination pointing at @coolcallpro.com anywhere.

---

## Part 2 — Email DNS, after cancellation

Once Workspace is gone, the current records describe a mail setup that no longer
exists. Current state:

| Record | Current value | Problem |
|---|---|---|
| `MX` | `smtp.google.com` (pri 1) | Points at Workspace. Mail to @coolcallpro.com bounces. |
| `TXT` apex | `v=spf1 include:_spf.google.com ~all` | Authorizes Google to send as you. Obsolete, and `~all` (softfail) is permissive. |
| `TXT google._domainkey` | `v=DKIM1; k=rsa; p=MIIBIjANBg…` | Dead signing key. |
| `TXT _dmarc` | `v=DMARC1; p=none; rua=mailto:admin@coolcallpro.com` | Reports go to a mailbox that no longer exists. `p=none` = no protection. |

**Nothing in this project sends email as @coolcallpro.com.** Verified 2026-08-07:
no GitHub workflow sends mail (only `gsc-index-monitor.yml` uses a secret, for
API auth); the YMYL and GSC alert routines send from Anthropic infrastructure to
`gyanesh.gulshan@gmail.com`, not from this domain. That fact is what makes the
strict posture below safe.

### Recommended: Cloudflare Email Routing (free)

This is the option that makes both breakages disappear rather than working around
them. Cloudflare Email Routing forwards `admin@coolcallpro.com` →
`gyanesh.gulshan@gmail.com` at no cost. You keep the professional address for
receiving, DMARC reports keep arriving, and any Squarespace / MarketCall /
Cloudflare mail still addressed to @coolcallpro.com still reaches you.

Receive-only — it does not let you *send* as admin@coolcallpro.com. That's the
one thing you give up with Workspace.

1. Cloudflare dashboard → `coolcallpro.com` → **Email** → **Email Routing** →
   Get started.
2. Add destination address `gyanesh.gulshan@gmail.com` and **click the
   verification link Cloudflare emails you**. Do this step *before* cancelling
   Workspace — it needs no DNS change and creates no cutover.
3. Create routes: `admin@coolcallpro.com` → your Gmail. Add `hello@` too if you
   want it to keep working. Optionally set a catch-all.
4. Cloudflare will offer to replace the MX records and set SPF automatically —
   accept it. **This is the cutover**: the moment MX changes, mail stops going to
   Workspace. Do it after you've stopped relying on the Workspace inbox.

### Then tighten the remaining records

- [ ] **Delete** the `google._domainkey` TXT record — dead key, nothing signs
      with it any more.
- [ ] **SPF** should end up as
      `v=spf1 include:_spf.mx.cloudflare.net -all`. Cloudflare sets the include;
      change the tail from `~all` to `-all` yourself. `-all` means "no server is
      authorized to send as this domain," which is now literally true.
- [ ] **DMARC** → replace the `_dmarc` TXT record with:

      v=DMARC1; p=reject; rua=mailto:gyanesh.gulshan@gmail.com; fo=1; aspf=s; adkim=s

  `p=reject` is correct **immediately** here — it does not need a monitoring
  period. The `p=none` → `p=quarantine` staging planned in `NEXT-TASKS.txt`
  existed to confirm which legitimate senders exist before tightening. With
  Workspace gone there are none, so every message claiming to be from
  @coolcallpro.com is forged and should be rejected outright. This is stronger
  anti-spoofing protection than you have today.

  `p=reject` on your domain does **not** interfere with Cloudflare forwarding
  your inbound mail — inbound is evaluated against the *original sender's*
  DMARC policy, not yours.

- [ ] If you ever want to send as @coolcallpro.com again (Gmail "Send mail as"
      through an SMTP relay), you must add that relay to SPF and loosen `-all`
      first, or your own mail will be rejected.

### If you skip Email Routing entirely

Then admin@ and hello@ simply stop existing. In that case:

- [ ] Set a **null MX** to declare the domain accepts no mail (RFC 7505): a
      single MX record with priority `0` and target `.` — this makes senders fail
      fast instead of retrying for days.
- [ ] Same SPF `-all` and DMARC `p=reject` as above, but point `rua=` at your
      Gmail address directly.
- [ ] Re-check every item in Part 1 §6 first — with no forwarding, any account
      still using a @coolcallpro.com address becomes unrecoverable.

---

## Verifying afterwards

```bash
# Should show Cloudflare MX (or a single "." for null MX), never smtp.google.com
nslookup -type=MX coolcallpro.com 1.1.1.1

# SPF should end in -all; google-site-verification must still be present
nslookup -type=TXT coolcallpro.com 1.1.1.1

# Should be p=reject with a gmail rua
nslookup -type=TXT _dmarc.coolcallpro.com 1.1.1.1

# Should be NXDOMAIN / no record once deleted
nslookup -type=TXT google._domainkey.coolcallpro.com 1.1.1.1
```

Also confirm the daily monitor still runs after cancellation — check that a new
`.gsc_state/report-YYYY-MM-DD.md` commit lands within 24h. If it stops, the
service-account key died with the Cloud project (Part 1 §4).
