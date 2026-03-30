# Kundli — Environment Variables

All env vars are optional except `KUNDLI_SECRET_KEY` in production. The app degrades gracefully when any are missing.

## Required for Production

| Variable | Value | Purpose |
|----------|---------|---------|
| `KUNDLI_SECRET_KEY` | `f952b849060e064e232ede9a49d2123869fd09489b6cc337104900e14e8f0911` (any random string) | Flask session signing. Without it, uses an insecure fallback and logs a warning. Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |

## Optional

| Variable | Value | Default | Purpose |
|----------|---------|---------|---------|
| `GA4_ID` | `G-R4HEFYX3L2` | Google Analytics 4 measurement ID. When set, loads GA4 script on all pages and enables event tracking. |
| `BREVO_API_KEY` | `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` | Brevo (Sendinblue) API key for dasha change email alerts. When empty, email capture form still shows but alerts are not stored. |
| `SITE_URL` | `https://kundli-2c3b.onrender.com` | Base URL for canonical links, OG tags, and share URLs in templates. Static files (sitemap, robots, llms.txt) still have hardcoded URLs. |
| `REDIS_URL` | `redis://default:rrT33kSMsTH119N8YTNWQltnIbFR9uRP@redis-11837.crce199.us-west-2-2.ec2.cloud.redislabs.com:11837` | Redis connection for ChartStore. When empty, uses file-based JSON store in /tmp. |
| `LOG_FORMAT` | `json` | Set to `json` for structured JSON logging (useful for log aggregators). |
| `PORT` | `8080` | Server port for Flask/Gunicorn. |
| `FLASK_DEBUG` | `0` | Enable Flask debug mode. Never set in production. |

## How to Get Each Value

### KUNDLI_SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output. Set it once, never change it (changing it invalidates all active sessions).

### GA4_ID
1. Go to https://analytics.google.com
2. Admin (gear icon) > Create Property
3. Enter property name: "Kundli"
4. Create a Web data stream with URL: `https://kundli-2c3b.onrender.com`
5. Copy the Measurement ID (format: `G-XXXXXXXXXX`)

Free forever. No credit card needed.

### BREVO_API_KEY
1. Go to https://brevo.com and sign up (free, no credit card)
2. Go to Settings > SMTP & API > API Keys
3. Click "Generate a new API key"
4. Copy the key (format: `xkeysib-xxxxxxxx...`)

Free tier: 9,000 emails/month, 300/day, 100K contacts.

Set in two places:
- Render dashboard: Environment > `BREVO_API_KEY`
- GitHub repo: Settings > Secrets and variables > Actions > `BREVO_API_KEY`

### REDIS_URL
Only needed if you want cross-worker chart persistence. On Render:
1. Dashboard > New > Redis
2. Copy the Internal URL (format: `redis://red-xxxxx:6379`)

Render free Redis: 25MB, no persistence guarantee. Fine for chart cache (TTL 1 hour).

### SITE_URL
Only set this if you use a custom domain. Otherwise the default works.

## Where to Set Them

**Render (production):**
Dashboard > Your Service > Environment > Add Environment Variable

**Local development:**
```bash
export KUNDLI_SECRET_KEY="dev-secret-key"
export GA4_ID=""
export BREVO_API_KEY=""
```

Or create a `.env` file (not committed to git):
```
KUNDLI_SECRET_KEY=dev-secret-key
GA4_ID=
BREVO_API_KEY=
```

**GitHub Actions (for cron jobs):**
Repo > Settings > Secrets and variables > Actions > New repository secret
