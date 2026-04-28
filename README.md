# Fuel Duel

A small website that compares **current gas prices between Sarnia, ON (Canada) and Port Huron, MI (USA)**, tells you which side of the border is cheaper right now, and calculates how much you'd save based on the size of your fuel tank.

## What it does

1. Fetches the latest pump prices on both sides of the Blue Water Bridge.
2. Normalises the units (Canadian ¢/litre vs. American $/gallon) and the currency (CAD ↔ USD).
3. Shows a clear winner and the dollar amount you'd save filling up on the cheaper side.

## Project layout

```
Fuel Duel/
├── scraper/
│   └── scraper.py     # Fetches live prices from GasBuddy (run via GitHub Actions)
├── venv/              # Python virtual environment (NOT tracked in git)
├── .gitignore         # Files git should ignore
└── README.md          # This file
```

## How to start working on the project (every time)

Open Terminal and run:

```bash
cd "/Users/jaymcauley/Projects/Fuel Duel"
source venv/bin/activate
```

After running `source venv/bin/activate`, your terminal prompt will change to start with `(venv)` — that's how you know the sandbox is active. From then on, `python` and `pip` refer to the project's private Python, not your system one.

To leave the sandbox when you're done:

```bash
deactivate
```

## Build status

| Component | Status | Notes |
|---|---|---|
| `scraper/scraper.py` | ✅ Done | Fetches Regular price from both stations |
| GitHub Actions workflow | 🔜 Next | Runs scraper on a schedule, writes `prices.json` |
| `prices.json` | 🔜 Next | Static file the webpage reads |
| Webpage | 🔜 Next | Reads `prices.json`, does unit/currency conversion, shows winner |

## Scraper details

Fetches the Regular unleaded price from two GasBuddy station pages using Playwright (headless Chromium) with `playwright-stealth` to bypass Cloudflare.

| Station | GasBuddy ID | URL | Unit |
|---|---|---|---|
| 40 Fuel, Sarnia ON | 199752 | gasbuddy.com/station/199752 | CAD ¢/L |
| Speedway, Port Huron MI | 53084 | gasbuddy.com/station/53084 | USD/gal |

**Selector** (verified 2026-04-27):
```
span[class*="FuelTypePriceDisplay-module__price"]
```
First match on the page = Regular fuel (page always orders: Regular, Midgrade, Premium, Diesel).
The partial class match (`*=`) handles GasBuddy's hashed suffix (e.g. `___3iizb`) which may change on site updates.

**Sanity checks:** CAD price must be 100–250 ¢/L · USD price must be $2.00–$6.00/gal. Out of range returns `{"price": None, "error": "out_of_range"}`.

## Tools installed

| Tool | Version (at setup) | Purpose |
| --- | --- | --- |
| Python | 3.9.6 (Apple-bundled) | Programming language |
| Git | 2.50.1 | Version control |
| Homebrew | 5.1.8 | Mac package manager |
| Playwright | 1.58.0 | Headless browser automation (scrapes price pages) |
| Chromium | 145.0.7632.6 (Playwright-bundled) | The browser Playwright drives |

## Re-running the setup from scratch

If you ever need to rebuild the environment (e.g. on a new Mac, or after deleting `venv/`):

```bash
cd "/Users/jaymcauley/Projects/Fuel Duel"
python3 -m venv venv
source venv/bin/activate
pip install playwright playwright-stealth
playwright install chromium
```

## Git baseline

The first commit (`Initial empty commit (baseline)`) is intentionally empty — it gives a clean rollback point if anything ever goes wrong. To roll back to that baseline:

```bash
git log --oneline           # find the baseline commit hash
git reset --hard <hash>     # ⚠️ destroys uncommitted work — be sure first
```

## Notes

- Browser binaries Playwright downloads live in `~/Library/Caches/ms-playwright/` (macOS standard cache location), not in this folder.
- `.env` files and other secrets are gitignored. Never commit API keys.
