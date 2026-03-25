# Kundli — Vedic Birth Chart Generator

A Python CLI tool for generating Vedic birth charts (Kundli) with planetary positions, house cusps, chart diagrams, aspects, yogas, and Vimshottari Dasha.

## Features

- All 9 Navagraha positions (sign, degree, nakshatra, pada)
- 12 house cusps (Placidus system)
- North Indian and South Indian chart diagrams (terminal)
- Vedic planetary aspects (special aspects for Mars, Jupiter, Saturn)
- Yoga detection (Gajakesari, Budhaditya, Chandra-Mangal)
- Vimshottari Dasha timeline with current period highlighted

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m kundli.app \
  --date 23-09-1996 \
  --time 22:17 \
  --location "PGIMER, Chandigarh, India" \
  --tz 5.5 \
  --chart both
```

### Options

| Flag         | Description                              | Default |
|--------------|------------------------------------------|---------|
| `--date`     | Birth date (DD-MM-YYYY)                  | required |
| `--time`     | Birth time in 24h format (HH:MM)         | required |
| `--location` | Birth place (geocoded via Nominatim)     | required |
| `--tz`       | Timezone offset from UTC                 | 5.5 (IST) |
| `--chart`    | Chart style: `north`, `south`, or `both` | both |


## Rollback Strategy

If a deployment fails or introduces a regression:

1. **Render**: Go to Dashboard > your service > Events. Click "Rollback" on the last successful deploy.
2. **Manual**: `git revert HEAD && git push` to revert the last commit and trigger a new deploy.
3. **Docker**: Tag every release image. Roll back by deploying the previous tag.
4. **Verify**: After rollback, check `/health` endpoint returns `{"status": "ok"}`.
5. **Post-mortem**: Document what went wrong in `.kiro/conversations.md` before re-attempting the fix.
