import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def fetch(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
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

    #print(fetch_time)
    #print(price_pln_perg)
    #print(price_usd)
    return price_pln_perg, price_usd, fetch_time