import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def fetch_skup(url):
    cena_2g = None
    cena_5g = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
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

        #print(cena_2g)
        #print(cena_5g)

        suma_skupu = cena_2g + cena_5g

        return suma_skupu
               

        




