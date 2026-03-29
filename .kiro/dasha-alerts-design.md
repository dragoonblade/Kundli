# Dasha Change Alerts — Design Doc and Task Breakdown

## Problem

Zero retention. Every user is a new user. No mechanism to bring people back after they generate a chart.

## Solution

Capture an optional email at chart generation. Store the next dasha change dates in Brevo's contact list. When a change approaches, send a personalized notification that brings them back. Also offer web push as a second channel for users who skip email.

## Architecture

```
User submits email on Kundli form
    |
    v
Flask app --> Brevo API (upsert contact with dasha dates)
                  |
                  v
           Brevo stores contact + custom attributes:
           NEXT_MD_LORD, NEXT_MD_DATE, NEXT_AD_LORD, NEXT_AD_DATE,
           NEXT_PR_LORD, NEXT_PR_DATE, CHART_URL, NOTIFY_PR
                  |
    +-------------+
    |
    v
GitHub Actions cron (daily, 6am UTC)
    |
    +-- Query Brevo: contacts where NEXT_AD_DATE <= today+7
    |
    +-- For each match:
    |   +-- Build personalized email from SIMPLE_DASHA_EFFECTS
    |   +-- Send via Brevo transactional email API
    |   +-- Update contact with NEXT dasha dates after the change
    |
    +-- Log summary to GitHub Actions output
```

## Email Provider

Brevo (formerly Sendinblue). Selected because:
- 9,000 emails/month free (highest free tier available)
- 100K contacts free
- No credit card required
- REST API, no SDK needed (use stdlib urllib or requests)
- Native unsubscribe/GDPR compliance
- SendGrid killed free tier May 2025
- Resend (3K/mo) and SMTP2GO (1K/mo) are too low

## Storage

Brevo contact list (not local files). Custom attributes per contact:
- `NEXT_MD_LORD`: string (e.g. "Shani")
- `NEXT_MD_DATE`: string (e.g. "2031-01-15")
- `NEXT_AD_LORD`: string (e.g. "Budh")
- `NEXT_AD_DATE`: string (e.g. "2026-08-22")
- `NEXT_PR_LORD`: string (e.g. "Shukra")
- `NEXT_PR_DATE`: string (e.g. "2026-04-15")
- `CHART_URL`: string (shareable link with ref param)
- `NOTIFY_PR`: boolean (opted into Pratyantar notifications)

Survives deploys. Zero local persistence needed.

## Notification Frequency

| Level | Frequency | Default | User control |
|-------|-----------|---------|-------------|
| Mahadasha | Every few years | Always notify | Cannot opt out |
| Antardasha | Every few months | Always notify | Cannot opt out |
| Pratyantar | Every 2-4 weeks | Off | Opt-in checkbox on form |

## Dual Channel: Email + Web Push

- Email for users who provide it (Brevo)
- Web push for users who allow browser notifications (free, no provider)
- Service worker already exists (PWA). Add push subscription on result page.
- Push open rates are 5-10x email. Higher conversion channel.
- Users who skip email can still get push. Both channels for users who opt into both.

## Smart Timing (Personalized Content)

Don't just say "your dasha is changing." Include:
- The incoming lord name (Sanskrit + English)
- What it governs
- What to expect

Example email:
> Your Antardasha is changing from Budh (Mercury) to Shukra (Venus) on Aug 22.
> Venus periods favor relationships, creativity, and financial growth.
> Here is what to expect: [View Your Chart]

Content source: existing `SIMPLE_DASHA_EFFECTS` dict in readings_data.json.
For Pratyantar: shorter message, just lord name and one-line effect.

## Re-engagement Loop

- Email/push links back to chart with `?ref=dasha_alert` parameter
- GA4 tracks `ref=dasha_alert` as campaign source automatically (Acquisition report)
- Result page on return shows banner: "Your dasha recently changed. Here is what is new."
- Chatbot auto-suggests: "Ask me about your new Antardasha period"
- Measurable: did the alert bring them back?

## Privacy

- Email stored in Brevo only (not on our server)
- Push subscription stored in IndexedDB (client-side only)
- Helper text: "We only use this to notify you about dasha changes. No spam."
- Brevo handles unsubscribe and GDPR compliance natively
- Every email has unsubscribe link
- Dedicated /unsubscribe endpoint on our site

## New Dependencies

None. Use `urllib.request` (stdlib) for Brevo API calls. Web push uses existing service worker + browser Push API.

## Env Vars

| Variable | Where | Purpose |
|----------|-------|---------|
| `BREVO_API_KEY` | Render + GitHub Secrets | Brevo REST API authentication |

When empty, alert functions return silently. Form still shows, chart still generates.

---

## Task Breakdown

### Task 1: `kundli/alerts.py` — Brevo API wrapper
**Assignee:** Backend
**Effort:** 45 min
**Depends on:** Nothing

**Build:**
- `kundli/alerts.py` (~40 lines)
- `upsert_alert(email, dashas, birth_params, notify_pratyantar=False)` — compute next MD/AD/PR change dates, POST to Brevo contacts API
- `remove_alert(email)` — DELETE from Brevo contacts API
- `_next_change(dashas, now)` — helper: walk dasha list, return next MD/AD/PR lord+date

**API calls:**
- `POST https://api.brevo.com/v3/contacts` with `{"email": "...", "attributes": {...}, "updateEnabled": true}`
- `DELETE https://api.brevo.com/v3/contacts/{email}`
- Header: `api-key: {BREVO_API_KEY}`

**Rules:**
- If `BREVO_API_KEY` is empty, return silently (no crash)
- Use `urllib.request` (no new pip dependency)
- Wrap API calls in try/except, log errors, never crash the caller

**Tests (`tests/test_alerts.py`):**
- `test_next_change` — verify correct MD/AD/PR dates from reference chart
- `test_upsert_no_api_key` — returns None, no error
- `test_remove_no_api_key` — returns False, no error
- `test_upsert_payload_structure` — mock urllib, verify JSON body has correct attributes

---

### Task 2: Form UI — email field + pratyantar checkbox
**Assignee:** Frontend
**Effort:** 20 min
**Depends on:** Nothing (parallel with Task 1)

**Change `templates/index.html`:**
- Add after timezone field in Kundli form:
  - Email input: `type="email"`, `name="alert_email"`, not required
  - Checkbox: `name="notify_pratyantar"`, unchecked by default
  - Helper text: "We only use this to notify you about dasha changes. No spam."
- Preserve `alert_email` value on form validation error (add to `form_vals` dict)

**Acceptance criteria:**
- Email field visible, not required, does not block form submission
- Checkbox unchecked by default
- Values preserved on error
- No visual regression on mobile (test at 320px width)

---

### Task 3: Wire alerts into chart generation
**Assignee:** Backend
**Effort:** 20 min
**Depends on:** Task 1 + Task 2

**Change `kundli/web.py`:**
- In `_generate_chart()`: read `alert_email` and `notify_pratyantar` from form
- If email non-empty, call `upsert_alert(email, dashas, birth_params, notify_pratyantar)`
- Pass `alert_email=email` to result template
- Import `upsert_alert` from `kundli.alerts`

**Rules:**
- Alert call is fire-and-forget (try/except, log error, never block chart)
- Chart generation works identically with or without email

**Tests:**
- `test_chart_with_email` — POST with email, verify result page shows confirmation
- `test_chart_without_email` — POST without email, verify no confirmation, no error

---

### Task 4: Result page confirmation banner
**Assignee:** Frontend
**Effort:** 15 min
**Depends on:** Task 3

**Change `templates/result.html`:**
- After info section, add conditional banner:
  - Shows email address and "we will notify you" message
  - Includes unsubscribe link
- Only renders when `alert_email` is truthy

**Acceptance criteria:**
- Banner shows only when email was provided
- Unsubscribe link points to `/unsubscribe?email=...`
- Does not show on shareable link visits

---

### Task 5: Unsubscribe endpoint
**Assignee:** Backend
**Effort:** 15 min
**Depends on:** Task 1

**Change `kundli/web.py`:**
- New route: `GET /unsubscribe?email=X`
- Calls `remove_alert(email)`
- Renders simple confirmation page

**New template: `templates/unsubscribe.html`:**
- "You have been unsubscribed. You will no longer receive dasha change notifications."
- Link back to homepage

**Tests:**
- `test_unsubscribe_removes` — verify endpoint returns 200
- `test_unsubscribe_no_email` — verify no crash

---

### Task 6: Re-engagement banner + chatbot suggestion
**Assignee:** Frontend
**Effort:** 20 min
**Depends on:** Nothing (parallel with all tasks)

**Change `templates/result.html`:**
- Add hidden banner that shows when URL has `?ref=dasha_alert`
- JS: check URL params on load, show banner if ref matches

**Change `kundli/chatbot.py`:**
- Add "When did my dasha change?" to greeting suggestions

**Acceptance criteria:**
- Banner only shows with `?ref=dasha_alert` in URL
- GA4 tracks ref parameter automatically (no code needed)
- Chatbot greeting updated

---

### Task 7: GitHub Actions cron workflow + send script
**Assignee:** SDE-2/SDE-3 (not junior)
**Effort:** 45 min
**Depends on:** Task 1

**New file: `.github/workflows/dasha-alerts.yml`:**
- Schedule: daily at 6am UTC
- Manual trigger (workflow_dispatch) for testing
- Steps: checkout, setup Python 3.12, pip install pyswisseph, run send script
- Secret: `BREVO_API_KEY`

**New file: `kundli/send_alerts.py` (~50 lines):**
- Query Brevo contacts API: filter `NEXT_AD_DATE <= today+7` or `NEXT_MD_DATE <= today+7`
- For each match:
  - Look up `SIMPLE_DASHA_EFFECTS` for the incoming lord
  - Build email: lord name (Sanskrit + English), one-line effect, chart link with `?ref=dasha_alert`
  - Send via Brevo transactional email API
  - Compute the NEXT dasha dates after this change, update contact attributes
- Print summary to stdout

**Rules:**
- Idempotent: running twice on same day does not double-send (check if change date is within 0-7 day window, not past)
- Handles empty results gracefully
- Logs count of emails sent

---

## Execution Order

```
Day 1 (parallel):
  Task 1 (backend)  ---|
  Task 2 (frontend) ---|--- all independent
  Task 6 (frontend) ---|

Day 2 (sequential):
  Task 3 (needs 1+2)
  Task 4 (needs 3)
  Task 5 (needs 1)

Day 3:
  Task 7 (needs 1)
  Integration test
  Deploy
```

**Total effort:** ~3 hours across 2 people over 1-2 days.
