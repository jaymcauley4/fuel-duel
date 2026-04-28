# Station Change Reference

Everything you need to swap one or both stations. Do this once, do it right.

---

## Current stations

| Side    | Station name     | GasBuddy ID | GasBuddy URL                          |
|---------|------------------|-------------|---------------------------------------|
| Canada  | 40 Fuel, Sarnia  | `199752`    | gasbuddy.com/station/199752           |
| USA     | Speedway, Port Huron | `53084` | gasbuddy.com/station/53084            |

---

## How to find a new station ID

1. Go to [gasbuddy.com](https://www.gasbuddy.com) and search for the station.
2. Click through to the station's page.
3. The ID is the number at the end of the URL — e.g. `gasbuddy.com/station/`**`53084`**.

---

## Files to change (and exactly what to change)

There are **3 files** that must be updated. Everything else updates automatically.

---

### 1. `scraper/update_prices.py` — lines 39–49

This is where the scraper job is told which station to visit and what name to display.

**For the USA side**, change `id` and `station_name`:
```python
"port_huron": {
    "id": 53084,              # ← replace with new GasBuddy ID
    "station_name": "Speedway",  # ← replace with the station's real name
    ...
},
```

**For the Canada side**, change `id` and `station_name`:
```python
"sarnia": {
    "id": 199752,             # ← replace with new GasBuddy ID
    "station_name": "40 Fuel",   # ← replace with the station's real name
    ...
},
```

---

### 2. `scraper/scraper.py` — lines 15–18

This is a lookup table that maps each station ID to its unit type. If the new ID is not listed here, the scraper silently fails with `unknown_station_id` and returns no price.

```python
STATION_UNITS = {
    199752: "CAD_cents_per_L",   # ← swap 199752 for new Canadian station ID
    53084:  "USD_per_gal",       # ← swap 53084 for new US station ID
}
```

**Important:** Keep the unit string exactly as-is (`"CAD_cents_per_L"` for any Canadian station, `"USD_per_gal"` for any US station). Only the number changes.

Also update the test runner at the bottom of the same file — line 61:
```python
for sid in (199752, 53084):   # ← swap whichever ID you changed
```
This line only runs when you manually test the scraper; it does not affect the live site.

---

### 3. `scraper/probe.py` — line 4

This is a developer diagnostic tool (not part of the live scraper), but keep it in sync to avoid confusion:
```python
STATION_URL = "https://www.gasbuddy.com/station/53084"   # ← swap if changing USA station
```

---

## Files you do NOT need to touch

| File | Why it's safe to leave alone |
|------|------------------------------|
| `js/app.js` | Reads from `data/prices.json` using the keys `sarnia` and `port_huron` — those keys never change, only the values inside them do |
| `index.html` | Pure display layer; no station IDs anywhere |
| `css/style.css` | No station references |
| `data/prices.json` | Auto-overwritten by the scraper on every run |
| `.github/workflows/update-prices.yml` | Runs `update_prices.py` — no station IDs in the workflow itself |

---

## After making changes — how to verify

Run the scraper manually from Terminal:

```bash
cd "/Users/jaymcauley/Projects/Fuel Duel"
source venv/bin/activate
python scraper/update_prices.py
```

A successful run looks like:
```
  port_huron: 4.29 (price_usd_per_gallon)
  sarnia: 163.4 (price_cad_cents_per_litre)
  fx_usd_cad: 1.363415
Written to data/prices.json
```

If a station fails you'll see `FAILED — unknown_station_id` (wrong ID in `STATION_UNITS`) or `FAILED — timeout` (GasBuddy didn't load). Double-check the ID and retry once before assuming it's broken.

---

## Also update README.md (optional but tidy)

`README.md` lines 54–55 have a station reference table. It's documentation only — the site works without updating it — but keeping it accurate avoids confusion later.
