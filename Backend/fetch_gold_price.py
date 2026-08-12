import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def fetch(url):
    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
        )

        page.goto(url)
        page.wait_for_timeout(3000)
        content = page.content()
        browser.close()

    soup = BeautifulSoup(content, "html.parser")
    prices = soup.find_all("td", class_="text-end align-middle")
    fetch_time1 = soup.find("th", class_="text-center")

    price_pln = float(prices[0].text.replace(" ","").replace(",","."))
    price_pln_perg = price_pln / 31.1034768
    price_usd = float(prices[1].text.replace(" ","").replace(",","."))

    fetch_time = fetch_time1.text.split("na: ")[1].strip()

    return price_pln_perg, price_usd, fetch_time