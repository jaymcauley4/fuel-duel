# Selector: span[class*="FuelTypePriceDisplay-module__price"]
# Verified: 2026-04-27
# Target HTML (both stations use identical structure):
#   <span class="text__xl___2MXGo text__bold___1C6Z_ text__left___1iOw3
#               FuelTypePriceDisplay-module__price___3iizb">154.9¢</span>
# First match on page = Regular fuel (page order: Regular, Midgrade, Premium, Diesel)
# Hash suffix (e.g. ___3iizb) may change on site updates — partial match handles this.

from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import Stealth

SELECTOR = 'span[class*="FuelTypePriceDisplay-module__price"]'

STATION_UNITS = {
    199752: "CAD_cents_per_L",
    53084:  "USD_per_gal",
}

SANITY = {
    "CAD_cents_per_L": (100, 250),
    "USD_per_gal":     (2.00, 6.00),
}


def get_price(station_id):
    unit = STATION_UNITS.get(station_id)
    if unit is None:
        return {"price": None, "error": "unknown_station_id"}

    url = f"https://www.gasbuddy.com/station/{station_id}"

    try:
        with Stealth().use_sync(sync_playwright()) as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=15000, wait_until="networkidle")

            raw = page.locator(SELECTOR).first.inner_text(timeout=5000)
            browser.close()

        price = float(raw.replace("¢", "").replace("$", "").strip())

        low, high = SANITY[unit]
        if not (low <= price <= high):
            return {"price": None, "error": "out_of_range"}

        return {
            "price": price,
            "unit": unit,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    except PlaywrightTimeoutError:
        return {"price": None, "error": "timeout"}
    except Exception as e:
        return {"price": None, "error": str(e)}


if __name__ == "__main__":
    for sid in (199752, 53084):
        print(f"Station {sid}: {get_price(sid)}")
