# Kundli — Conversation Tracker

## Session: 2026-03-29 (current)

### Summary

Cleared the entire backlog (47 items done), added 12 new modules, expanded from 201 to 283 tests, and refactored the codebase for maintainability. 18 commits.

### Stats
- **18 commits** this session
- **283 tests**, all passing, **83% code coverage**
- **3,674 lines** of Python across 27 modules
- **27 HTML templates** (1 skeleton + 19 includes + 2 macros + 5 pages)
- **1,281 lines** of CSS
- **1 open backlog item** (email capture for dasha alerts)

### What was built

**Refactoring: calc.py modularization**
- Split 590-line calc.py into 7 focused modules: core.py (76), planets.py (99), dasha.py (103), yogas.py (148), doshas.py (55), strength.py (44), varga.py (62)
- calc.py kept as 34-line re-export facade, zero import changes needed
- 25 direct-import tests for all 7 modules + facade verification

**Chatbot: dasha timing for all life questions**
- Marriage timing: 7th lord dasha periods, Venus/Jupiter windows
- Generic topic timing: any "will I..." question gets house lord dasha analysis
- 20+ new topic keywords: interview, lottery, crush, propose, visa, stocks, UPSC, NEET, JEE, conceive, surgery, dispute, ex come back
- Broadened advice pattern: catches "will my/he/she/this", "does", "do I"
- Word boundary matching prevents false positives
- Explain rashi/graha added to explain regex

**Search-driven gaps (5 items)**
- Love vs arranged marriage indicator (5th/7th lord connection, Venus, Rahu)
- Marriage delay analysis (Saturn/Rahu/Ketu on 7th, Venus combustion)
- Foreign settlement yoga (Rahu placement, 12th lord, 4th-12th connection)
- Business vs job indicator (7th vs 10th house strength scoring)
- FAQ expanded from 12 to 18 questions with updated JSON-LD

**Global audience (5 items)**
- Western zodiac comparison in chart info section
- "Why Vedic?" explainer in FAQ
- UNIVERSAL_REMEDIES dict with culturally neutral alternatives
- Dosha section split into "Traditional Remedies" + "Universal Practices"
- trackEvent() noop defined on all pages

**Analytics (5 items)**
- GA4 scaffolding via GA4_ID env var, ga4.html include on all 4 pages
- Event tracking: generate_kundli, check_compatibility, download_pdf, save_offline, copy_share_link, faq_search
- CSP updated for googletagmanager.com
- Context processor injects ga4_id globally

**Features: Event Predictor**
- New kundli/predictor.py (65 lines)
- 6 life events: marriage, children, career, wealth, education, travel
- Past strong periods and upcoming favorable windows
- Active period highlighting

**Features: Prashna Kundli (Horary)**
- New kundli/prashna.py (100 lines) with 12 question categories
- Third tab on landing page alongside Kundli and Match
- /prashna POST route, prashna_result.html template
- Lagna lord, Moon, house lord analysis with favorable/unfavorable indicators
- 60 example questions as clickable chips per category
- Copy Share Link on result page

**Features: Side Navigation**
- Desktop (1024px+): sticky left sidebar via CSS grid
- All section links visible without scrolling
- Mobile: unchanged horizontal scroll nav

**Features: Daily Panchang**
- New kundli/panchang.py (85 lines): Tithi, Nakshatra, Yoga, Karana, Paksha
- Panchang card on landing page between tabs and forms
- Auspiciousness indicator based on Tithi and Yoga
- "What is Panchang?" explainer for global audience

**UX improvements**
- Match form preserves all 10 inputs on validation error
- Match form order hint (Person 1/2 matters for Varna)
- Auto-fill match Person 1 from last generated chart
- "View Full Chart" links in match result comparison cards
- Better geocoding error messages

**Refactoring: codebase cleanup**
- Extracted geocoding to kundli/geo.py (55 lines), deduplicated web.py + app.py
- Extracted ChartStore to kundli/store.py (112 lines)
- Split chatbot.py (627 -> 199 lines) into routing + builders (429 lines)
- web.py reduced from 651 to 494 lines
- Fixed 9 unused imports via ruff
- SITE_URL env var replaces 4 hardcoded domain references in templates

**SEO updates**
- sitemap.xml: added /prashna
- llms.txt: new features listed
- llms-full.txt: chatbot section, global audience, updated stats
- FAQ JSON-LD: 8 questions (was 4)

### Key Decisions
- Prashna uses current moment chart (no birth time), 12 categories with house mappings
- Event Predictor scans both Mahadasha and Antardasha for relevant house lords
- Panchang computed server-side per request (~5ms), no caching needed yet
- Universal remedies kept separate from traditional (not replacing, augmenting)
- GA4 scaffolded with noop fallback so trackEvent() never throws
- Side nav uses CSS grid only, zero JS changes
- Chatbot builders extracted to separate file but all imports still work through chatbot.py

### Remaining Backlog (1 item)
- **Email capture for dasha change alerts** — needs design decision on email infrastructure

---

## Session: 2026-03-24 to 2026-03-26 (multi-day)

### Summary

Built a production-grade Vedic Birth Chart (Kundli) generator from a basic CLI tool into a full-featured web application with 91 commits across two days.

### Final Stats
- **91 commits** on main branch
- **201 tests**, all passing, **93% code coverage**
- **3,037 lines** of Python across 15 modules
- **23 HTML templates** (1 skeleton + 17 includes + 2 macros + 3 pages)
- **1,246 lines** of CSS
- **16 open backlog items** (features, search gaps, global audience, analytics)

### What was built

**Core Astrological Engine**
- 9 Navagraha positions (sidereal, Lahiri ayanamsa)
- 12 house cusps (Placidus system)
- Vimshottari Dasha: 3 levels deep (Mahadasha, Antardasha, Pratyantar)
- Yogini Dasha: 36-year alternative system
- 25 yoga detections (Gajakesari, Budhaditya, Panch Mahapurusha, Dhana, Raja, etc.)
- 3 dosha detections (Manglik, Kalsarpa, Sade Sati) with remedies
- Shadbala (4-factor planetary strength)
- Ashtakavarga (Bhinnashtakavarga + Sarvashtakavarga, SAV=337)
- 17 divisional charts (D-1 through D-60)
- Current transits (Gochar) mapped to natal houses
- Daily personalized insights from transits
- Vedic planetary aspects with special aspects

**Kundli Matching (Gun Milan)**
- Ashtakoota 8-Koota scoring (36-point scale)
- Koota interpretations per score
- Strengths and challenges summary
- Manglik detection per person with mismatch warning
- Nadi, Bhakoot, Manglik dosha remedies
- Side-by-side chart comparison (Moon, Sun, Lagna, Nakshatra, Dasha)
- Dasha compatibility analysis

**Web Application**
- Flask web UI with 3 views: My Horoscope, Study, Full Chart
- Tabbed landing page (Kundli / Match)
- Sticky section nav with scroll-spy
- Language toggle (Sanskrit / English)
- Light/dark theme toggle
- Loading spinner on form submit
- Chat widget with localStorage persistence
- PDF export (birth chart + match, both with chart diagrams)
- PNG chart export
- Shareable links (/?d=DATE&t=TIME&l=LOC&z=TZ)
- Offline PWA with IndexedDB chart storage
- FAQ page with 6 categories, 12 questions, search filter

**Study Mode (12 lessons)**
- Foundations, Signs, Planets, Houses, Placements, Aspects
- Lordship, Yogas, Dasha, Doshas, Divisional Charts, Full Reading
- Each lesson uses the user's own chart data as curriculum

**Match Study Mode**
- How Kundli Matching Works explainer
- Per-koota Learn More expandables (8 detailed explanations)
- Reading guide and myths debunked

**CLI**
- Full chart generation with --date, --time, --location, --tz
- Match mode with --match and second person args
- 3-level dasha display with CURRENT markers
- Dosha output with Sade Sati

**REST API**
- POST /api/chart: JSON in/out, session-free
- Full chart data (planets, houses, dashas, yogas)

**Infrastructure**
- Docker (non-root user, healthcheck, access logs)
- GitHub Actions CI (tests, Bandit security scan, pip-audit)
- Rate limiting (60/min default, 10/min match, 20/min API)
- Redis chart store (optional, file-based fallback)
- Security headers (HSTS, X-Frame-Options, CSP, X-Content-Type-Options)
- Request ID middleware (UUID per request in logs + response header)
- Structured JSON logging (opt-in via LOG_FORMAT=json)
- Geocoding: builtin cities + Photon primary + Nominatim fallback

**SEO and Discoverability**
- Open Graph + Twitter meta tags on all pages
- JSON-LD structured data (SoftwareApplication, FAQPage)
- Keyword-rich page titles
- sitemap.xml, robots.txt, canonical URLs
- llms.txt and llms-full.txt for AI assistant discoverability

**Code Quality**
- 93% test coverage across 201 tests
- Content standards: zero em dashes, clean grammar, constructive framing
- Modular templates: result.html is 76 lines with 17 includes
- Readings data externalized to JSON (50KB inline dicts removed)
- PEP 8 enforced via ruff, docstrings on public functions

### Key Decisions
- Lahiri ayanamsa only (standard in India, covers 95% of users)
- Placidus house system (most common, fails at extreme latitudes)
- reportlab over weasyprint for PDF (no system dependencies)
- File-based chart store with optional Redis (minimal dependencies)
- Three-view split: Horoscope (casual), Study (learner), Full Chart (professional)
- Person 1/Person 2 labels (neutral) over Boy/Girl (traditional)
- Regex chatbot kept (LLM deferred to out of scope)
- Photon as primary geocoder (higher rate limit than Nominatim)
- No subagents for implementation (direct changes only)
- Tests updated after every code change
- Sections reordered by popularity (doshas and dasha moved up per competitor analysis)
