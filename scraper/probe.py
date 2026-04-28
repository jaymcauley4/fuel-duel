from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

STATION_URL = "https://www.gasbuddy.com/station/53084"

with Stealth().use_sync(sync_playwright()) as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print(f"Loading {STATION_URL} ...")
    page.goto(STATION_URL, timeout=15000, wait_until="networkidle")

    html = page.content()
    with open("scraper/page2.html", "w") as f:
        f.write(html)
    print("HTML saved to scraper/page2.html")

    text = page.inner_text("body")
    print("\n--- PAGE TEXT (first 1000 chars) ---\n")
    print(text[:1000])

    browser.close()
