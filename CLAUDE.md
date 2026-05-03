# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

Fuel Duel compares current gas prices between Sarnia, ON and Port Huron, MI across the Blue Water Bridge. A Python scraper runs every 6 hours (GitHub Actions), writes results to `data/prices.json`, and a static HTML/JS/CSS frontend reads that file to show which side of the border is cheaper.

There are no Node.js dependencies, no build step, and no test framework. The frontend is deployed as static files.

## Running the scraper locally

```bash
cd "/Users/jaymcauley/Projects/Fuel Duel"
source venv/bin/activate
python scraper/update_prices.py
```

If the venv doesn't exist yet, rebuild it:
```bash
python3 -m venv venv
source venv/bin/activate
pip install playwright playwright-stealth
playwright install chromium
```

## Viewing the frontend

Open `index.html` directly in a browser — no server needed. The page fetches `data/prices.json` via a relative path, so it must be opened from the project root (or served locally if the browser blocks file:// fetches).

## Architecture

```
GitHub Actions (every 6h)
  └── scraper/update_prices.py   ← orchestrates everything
        ├── scraper/scraper.py   ← Playwright + playwright-stealth, hits GasBuddy
        └── FX rate APIs (no auth required)
              └── data/prices.json   ← written here, committed by Actions bot

index.html  ←─ js/app.js reads data/prices.json on page load
              └── css/style.css
```

**scraper.py** uses a partial CSS selector (`span[class*="FuelTypePriceDisplay-module__price"]`) because GasBuddy appends hashed suffixes to class names. It grabs the first match (Regular fuel). playwright-stealth is required to bypass Cloudflare.

**update_prices.py** defines the two stations and their GasBuddy IDs. It tries two FX rate APIs (jsDelivr CDN → exchangerate-api.com) and falls back to the last known rate if both fail.

**app.js** applies a 2.75% FX markup (credit card fees) on top of the mid-market rate, optionally adds bridge toll costs (7 CAD + 5 USD), and calculates savings per tank fill.

## Changing stations

Read `STATIONS.md` before touching any station IDs. Three files must be updated in sync: `scraper/update_prices.py`, `scraper/scraper.py`, and `scraper/probe.py`. `probe.py` is a debug tool — run it to dump raw HTML when a GasBuddy selector stops working.

## Data format

`data/prices.json` shape (the frontend depends on these exact keys):
```json
{
  "sarnia":      { "price_cad_cents_per_litre": float, "station_name": str, "fetched_at": ISO },
  "port_huron":  { "price_usd_per_gallon": float,      "station_name": str, "fetched_at": ISO },
  "fx_usd_cad":  float,
  "updated_at":  ISO
}
```

## GitHub Actions

`.github/workflows/update-prices.yml` — runs on a 6-hour cron and can be triggered manually from the Actions tab. It commits `data/prices.json` only when prices change (the commit message is `chore: update gas prices`).
