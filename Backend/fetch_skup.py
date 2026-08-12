import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def fetch_skup(url):
    cena_2g = None
    cena_5g = None

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

        for tr in soup.find_all("tr"):
           tds = tr.find_all("td")
           if len(tds) != 2:
               continue

           nazwa = tds[0].text.strip()

           if nazwa == "C-Hafner Sztabka 2 g":
               cena_2g = float(tds[1].text.strip().replace(" zł", "").replace(",", "."))

           if nazwa == "C-Hafner Sztabka 5 g":
               cena_5g = float(tds[1].text.strip().replace(" zł", "").replace(",", "."))

        suma_skupu = cena_2g + cena_5g

        return suma_skupu
        




