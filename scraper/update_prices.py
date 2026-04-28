import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from scraper import get_price


def fetch_fx_rate():
    """Fetch mid-market USD→CAD rate. Tries two free APIs, no key required."""
    apis = [
        # jsDelivr-hosted community currency API — free, no auth, very reliable
        ('https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json',
         lambda d: d['usd']['cad']),
        # Fallback: exchangerate-api v4 open endpoint
        ('https://api.exchangerate-api.com/v4/latest/USD',
         lambda d: d['rates']['CAD']),
    ]
    req_headers = {'User-Agent': 'FuelDuel/1.0 (github.com/jaymcauley/fuel-duel)'}

    for url, extract in apis:
        try:
            req = urllib.request.Request(url, headers=req_headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read())
                rate = round(extract(data), 6)
                print(f"  fx_usd_cad: {rate}")
                return rate
        except Exception as e:
            print(f"  FX API failed ({url}): {e}")

    print("  All FX APIs failed — keeping existing rate if available")
    return None

DATA_FILE = Path(__file__).parent.parent / "data" / "prices.json"

STATIONS = {
    "sarnia": {
        "id": 199752,
        "station_name": "40 Fuel",
        "price_key": "price_cad_cents_per_litre",
    },
    "port_huron": {
        "id": 53084,
        "station_name": "Speedway",
        "price_key": "price_usd_per_gallon",
    },
}


def load_existing():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {}


def main():
    DATA_FILE.parent.mkdir(exist_ok=True)
    output = load_existing()

    for city, cfg in STATIONS.items():
        result = get_price(cfg["id"])
        if result.get("price") is not None:
            output[city] = {
                cfg["price_key"]: result["price"],
                "station_name": cfg["station_name"],
                "fetched_at": result["fetched_at"],
            }
            output[city].pop("error", None)
            print(f"  {city}: {result['price']} ({cfg['price_key']})")
        else:
            err = result.get("error", "unknown")
            print(f"  {city}: FAILED — {err}")
            if city in output:
                output[city]["error"] = err
            else:
                output[city] = {"error": err}

    # FX rate — fetched server-side so browser needs zero extra network calls
    fx = fetch_fx_rate()
    if fx is not None:
        output["fx_usd_cad"] = fx

    output["updated_at"] = datetime.now(timezone.utc).isoformat()
    DATA_FILE.write_text(json.dumps(output, indent=2))
    print(f"\nWritten to {DATA_FILE}")


if __name__ == "__main__":
    main()
