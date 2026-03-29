# Kundli — Backlog

## Open

### Retention & Engagement
- [ ] **Email capture for dasha change alerts** — collect email on chart generation, notify when Mahadasha, Antardasha, or Pratyantar changes. Design doc below.

#### Design: Dasha Change Alerts

**Email provider:** Brevo (formerly Sendinblue). 9,000 emails/month free, 100K contacts, Python SDK. SendGrid killed free tier May 2025. Resend (3K/mo) and SMTP2GO (1K/mo) are too low.

**Storage:** Brevo contact list (not local files). Add contacts via Brevo API with custom attributes (next_md_lord, next_md_date, next_ad_lord, next_ad_date, next_pr_lord, next_pr_date, chart_url). Survives deploys, zero local persistence needed. 100K contacts free.

**Cron:** GitHub Actions scheduled workflow (free, 2K min/month). Runs daily, queries Brevo for contacts with dasha changes within 7 days, sends notification email. Move to Render Cron on paid plan.

**Notification frequency:**
- Mahadasha change: always notify (every few years)
- Antardasha change: always notify (every few months)
- Pratyantar change: opt-in only (every 2-4 weeks), off by default, checkbox on form

**Dual channel: email + web push:**
- Email for users who provide it (Brevo)
- Web push for users who allow browser notifications (free, no provider needed)
- Service worker already exists (PWA). Add push subscription on result page.
- Push open rates are 5-10x email. Higher conversion channel.
- Users who skip email can still get push. Both channels for users who opt into both.

**User flow:**
1. Optional email field on Kundli form: "Get notified when your dasha changes (optional)"
2. Checkbox: "Also notify for Pratyantar (sub-sub-period) changes" (off by default)
3. On chart generation, if email provided, call Brevo API to upsert contact with dasha dates
4. Result page shows: "🔔 Enable push notifications" button + "We will email you when your dasha period changes" confirmation
5. Cron job sends email 7 days before change with personalized chart link
6. Every email has unsubscribe link (Brevo handles this natively)

**Smart timing (personalized notification content):**
- Don't just say "your dasha is changing"
- Include the incoming lord, what it governs, and what to expect
- Example: "Your Antardasha is changing from Budh (Mercury) to Shukra (Venus) on Aug 22. Venus periods favor relationships, creativity, and financial growth. Here is what to expect."
- Content generated from existing `SIMPLE_DASHA_EFFECTS` dict in readings_data.json
- For Pratyantar: shorter message, just lord name and one-line effect

**Re-engagement loop:**
- Email/push links back to chart with `?ref=dasha_alert` parameter
- GA4 tracks `ref=dasha_alert` as a campaign source automatically
- Measures: did the alert bring them back? (visible in GA4 Acquisition report)
- Result page on return shows a banner: "Your dasha recently changed. Here is what is new."
- Chatbot auto-suggests: "Ask me about your new Antardasha period"

**Module:** `kundli/alerts.py` (~40 lines), thin wrapper around Brevo REST API. Env var: `BREVO_API_KEY`.

**Privacy:** Email stored in Brevo only. Push subscription stored in IndexedDB (client-side). Helper text: "We only use this to notify you about dasha changes. No spam." Brevo handles unsubscribe/GDPR compliance natively.

**New dependency:** None (use `requests` or `urllib` for Brevo API, no SDK needed). Web push uses existing service worker + browser Push API.

**Effort:** ~3 hours (form + alerts.py + Brevo integration + push subscription + GitHub Actions workflow + tests).

## Out of Scope (for now)
- Muhurt (Choghadiya, Rahukalam) — same reasoning
- Sky map / celestial object finder — companion app territory
- Consultation marketplace / astrologer connect — different business model
- Numerology / Tarot — different domain entirely
- LLM-powered chatbot — needs design decision on model/cost/latency, current regex approach is functional
- Educational tooltips — content-heavy, low ROI vs other features
- East Indian chart style — niche, North + South covers 95% of users
- Multiple ayanamsa (Raman, KP) — niche, Lahiri is standard
- Multi-language UI — translation effort too high for current stage
- User accounts + saved charts — needs auth + DB, different product phase
