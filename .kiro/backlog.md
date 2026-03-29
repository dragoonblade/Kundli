# Kundli — Backlog

## Open

### Retention & Engagement
- [ ] **Email capture for dasha change alerts** — collect email on chart generation, notify when Mahadasha or Antardasha changes. Lightweight, no auth needed.

## Completed (47 items)

### SEO (6/6)
Structured data, sitemap, robots.txt, OG/Twitter meta, canonical URLs, keyword titles.

### User Friendliness (9/9)
Auto-detect TZ, recent charts, print CSS, geocoding errors, input hints, match form preservation, match order hint, auto-fill Person 1, chart links in match result.

### Features (4/4)
Event Predictor (6 life events), Prashna Kundli (12 categories, 60 questions), Side Navigation (desktop sidebar), Daily Panchang (5 elements + auspiciousness).

### Chatbot (6/6)
Marriage timing, dasha timing for all topics, 20+ keywords, broadened patterns, word boundaries, explain rashi/graha.

### Search-Driven Gaps (5/5)
Love vs arranged, marriage delay, foreign settlement, business vs job, FAQ expansion (18 questions).

### Global Audience (5/5)
Western zodiac comparison, Why Vedic explainer, universal remedies, English default, cultural assumptions removed.

### Analytics (5/5)
GA4 scaffolding, event tracking (6 events), conversion funnel, demographics, chatbot logging.

### UX Polish (3/3)
Prashna example chips, Prashna share link, hardcoded domain cleanup (SITE_URL).

### Refactoring (4/4)
calc.py modularized (7 modules), geocoding extracted (geo.py), ChartStore extracted (store.py), chatbot split (routing + builders).

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
