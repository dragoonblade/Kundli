# Kundli — Backlog

## Open

### SEO
- [x] **Structured data (JSON-LD)** — SoftwareApplication schema on index, FAQPage schema on /faq. Enables Google rich snippets.
- [x] **Sitemap.xml** — list /, /faq, and shareable chart URL pattern
- [x] **robots.txt** — basic crawl directives
- [x] **Open Graph + Twitter meta tags** — preview cards when shared on WhatsApp/Twitter/Facebook
- [x] **Canonical URLs** — prevent duplicate content from shareable links
- [x] **Keyword-rich page titles** — "Free Kundli Generator Online, Vedic Birth Chart by Date of Birth"

### User Friendliness
- [x] **Auto-detect timezone** — use browser Intl API to pre-select TZ dropdown
- [x] **Recent charts on index** — show last 3 from IndexedDB (already stored, just surface it)
- [x] **Print-friendly CSS** — @media print styles for clean Ctrl+P
- [x] **Better geocoding errors** — Photon fallback geocoder, "Try a nearby city" message, retry logic
- [x] **Input hints** — placeholder text on date/time fields
- [x] **Match form preserves inputs on error** — all 10 fields retained when validation fails
- [x] **Match form order hint** — explains Person 1/2 order matters for Varna scoring
- [x] **Auto-fill match Person 1 from last chart** — after generating a Kundli, switching to Match tab pre-fills Person 1
- [x] **Chart links in match result** — "View Full Chart" link for each person in comparison cards

### Features
- [ ] **Event Predictor** — timeline of favorable periods for major life events (marriage, children, career, wealth) based on dasha lord + house lordship. Shows past periods as "strong period for X" and future as "upcoming favorable window." Framed as tendencies, not certainties. Complements Life Areas (what) with timing (when).
- [ ] **Prashna Kundli (Horary)** — third tab on landing page alongside Kundli and Match. Cast a chart for the current moment to answer a specific question. No birth time needed.
  - [ ] Question categories with example questions (12 categories, ~60 questions):
    - Career/Job: "Will I get this job?", "Will I pass the interview?", "Should I change jobs?", "Will I get a promotion?", "Will I get a transfer?", "Will I get selected for government job?", "Is AI going to take my job?", "Should I quit my job?"
    - Education/Exams: "Will I pass my exam?", "Will I get into this college?", "Will I clear the competitive exam (UPSC, NEET, JEE)?", "Will I get the scholarship?", "Should I pursue higher studies or work?"
    - Relationships/Marriage: "Will he/she propose?", "Will this relationship work out?", "When will I get married?", "Love marriage or arranged marriage?", "Should I trust this person?", "Is this the right person for me?"
    - Breakup/Reconciliation: "Will my ex come back?", "Will we reconcile?", "Is he/she cheating on me?", "Should I forgive and go back?", "Will this separation be permanent?"
    - Finance/Wealth: "Will I get the loan approved?", "Will this investment pay off?", "Will I recover my money?", "Will I get a salary hike?", "Should I invest in stocks/property now?", "When will my financial condition improve?"
    - Business/Entrepreneurship: "Will my business succeed?", "Should I start this business?", "Will I find a business partner?", "Should I take this business risk?", "Will this deal go through?"
    - Pregnancy/Children: "Will I conceive?", "When will I get pregnant?", "Will the pregnancy be safe?", "Will IVF/treatment work?" (NOTE: skip gender prediction, ethical concern)
    - Health/Recovery: "Will I recover from this illness?", "Is this treatment the right one?", "Will the surgery be successful?", "Will my family member recover?"
    - Travel/Relocation: "Should I move abroad?", "Will my visa get approved?", "Will this trip go well?", "Will I settle in a foreign country?", "Should I relocate for this job?"
    - Legal/Disputes: "Will I win this court case?", "Will the dispute settle?", "Will I get my property back?", "Will the police case be resolved?"
    - Lost/Missing: "Will my lost item be found?", "Where is my lost item?", "Will the missing person return?", "Will I recover my stolen property?"
    - General Timing: "Is this the right time to start?", "Will I get the house/property?", "Should I sign this contract?", "Will this plan work out?", "Is today auspicious for this decision?"
  - [ ] House mapping per category:
    - Career/Job: 10th house (profession), 6th (service/competition)
    - Education/Exams: 5th house (intellect), 4th (education), 9th (higher learning)
    - Relationships/Marriage: 7th house (partner), 5th (romance)
    - Breakup/Reconciliation: 7th house (partner), 5th (romance), 12th (loss)
    - Finance/Wealth: 2nd house (wealth), 11th (gains), 8th (windfalls)
    - Business/Entrepreneurship: 7th house (business/partnerships), 10th (profession), 11th (gains)
    - Pregnancy/Children: 5th house (children), 1st (body), 9th (fortune)
    - Health/Recovery: 1st house (body), 6th (disease), 8th (chronic)
    - Travel/Relocation: 3rd house (short travel), 9th (long travel), 12th (foreign lands)
    - Legal/Disputes: 6th house (litigation), 7th (opponent)
    - Lost/Missing: 2nd house (possessions), 4th (home), 7th (thief), ruler of item's house
    - General Timing: relevant house based on question context
  - [ ] Chart cast for current datetime + user's location
  - [ ] Check Lagna lord strength, Moon placement, relevant house lord and occupants
  - [ ] Show favorable/unfavorable indicators with constructive framing
  - [ ] "Indicators suggest..." not "The answer is yes/no"
  - [ ] Reuses existing compute_planets, compute_houses, build_planet_house_map
  - [ ] New /prashna route, prashna form tab, prashna result template
- [ ] **Side navigation for Full Chart view** — sticky vertical nav on desktop (left sidebar) replacing horizontal scroll nav. Collapses to horizontal on mobile. Shows all 15 section links without scrolling.

### Refactoring
- [x] **Modularize calc.py** — split 590-line monolith into 7 focused modules:
  - `kundli/core.py` — constants (SIGNS, NAKSHATRAS, PLANETS), helpers (76 lines)
  - `kundli/planets.py` — compute_planets, compute_houses, build_planet_house_map, aspects (99 lines)
  - `kundli/dasha.py` — Vimshottari + Yogini dasha (103 lines)
  - `kundli/yogas.py` — 25 yoga detections (148 lines)
  - `kundli/doshas.py` — Manglik, Kalsarpa, Sade Sati (55 lines)
  - `kundli/strength.py` — Shadbala calculation (44 lines)
  - `kundli/varga.py` — 17 divisional charts (62 lines)
  - `kundli/calc.py` re-export facade (34 lines), all existing imports still work
  - Direct-import tests for all 7 modules + facade verification

### Chatbot
- [x] **Marriage timing answers** — "when will I get married?" now returns 7th lord dasha periods, Venus/Jupiter windows
- [x] **Dasha timing for all life questions** — "will I pass my exam?", "will I get the job?", etc. now show relevant house lord dasha periods
- [x] **20+ new topic keywords** — interview, lottery, crush, propose, visa, stocks, UPSC, NEET, JEE, conceive, surgery, dispute, ex come back, like me, etc.
- [x] **Broadened advice pattern** — catches "will my/he/she/this", "does", "do I" (not just "will I/should I")
- [x] **Word boundary matching** — prevents false positives like "art" in "start"
- [x] **Explain rashi/graha** — added to explain regex pattern

### Search-Driven Gaps (top user queries we don't answer)
- [ ] **Love vs arranged marriage indicator** — 7th house lord placement + Venus strength analysis. "Your chart suggests..." not "You will have..."
- [ ] **Marriage delay analysis** — if 7th house is afflicted by Saturn/Rahu/Ketu, explain why and suggest remedies
- [ ] **Foreign settlement yoga** — Rahu in 7th/9th/12th, 12th lord in 1st/9th, connections between 4th and 12th house
- [ ] **Business vs job indicator** — 7th house (business) vs 10th house (service) strength comparison
- [ ] **Expand FAQ with top searched questions** — "When will I get married?", "Am I Manglik?", "Which gemstone should I wear?", "Career prediction by date of birth"

### Global Audience (non-Indian users)
- [ ] **Western zodiac comparison** — show "Your Vedic Sun sign is Kanya (Virgo in Western astrology)" alongside Vedic signs
- [ ] **"Why Vedic?" explainer** — sidereal vs tropical, why Vedic is different, when to use which. Add to FAQ and Study mode.
- [ ] **Culturally neutral remedies** — add universal alternatives (meditation, gemstones, colors, affirmations) alongside Hindu-specific ones (pujas, temples, mantras)
- [ ] **Default to English** — detect browser language, default to English names if not Hindi/Sanskrit locale
- [ ] **Remove cultural assumptions** — review dosha remedies, match result text for India-only references. Frame for global audience.

### Analytics
- [ ] **Google Analytics 4** — add GA4 tag to all pages, track page views, chart generations, match submissions
- [ ] **Event tracking** — custom events for: Generate Kundli, Check Compatibility, Download PDF, Copy Share Link, Save Offline, Install App, FAQ search, Study lesson opened
- [ ] **Conversion funnel** — track: landing → form fill → chart generated → PDF download / match check
- [ ] **User demographics** — geo, device, referral source to validate diaspora vs domestic India split
- [ ] **Chatbot analytics** — log question types, confidence scores, fallback rate to improve chatbot

## Out of Scope (for now)
- Panchang (daily tithi, paksha, yoga, karana) — different product surface, not core Kundli
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
