import threading
import time

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from Backend.fetch_gold_price import fetch
from Backend.fetch_skup import fetch_skup

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

templates = Jinja2Templates(directory="frontend/templates")

CENA_ZAKUPU = 4158  
cache = {
    "price_pln_perg": None,
    "price_usd": None,
    "suma_skupu": None,
    "zysk_strata": None,
    "fetch_time": None,
}


def update_cache():
    price_pln_perg, price_usd, fetch_time = fetch("https://mennica.apart.pl/kurs")
    suma_skupu = fetch_skup("https://mennica.apart.pl/skup")

    cache["price_pln_perg"] = price_pln_perg
    cache["price_usd"] = price_usd
    cache["suma_skupu"] = suma_skupu
    cache["zysk_strata"] = suma_skupu - CENA_ZAKUPU
    cache["fetch_time"] = fetch_time
    print("Cache updated:", cache)


def background_updater():
    while True:
        update_cache()
        time.sleep(300)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if cache["price_pln_perg"] is None:
        return templates.TemplateResponse(request, "loading.html")

    zysk_strata = cache["zysk_strata"]
    kolor = "#16a34a" if zysk_strata >= 0 else "#dc2626"
    znak = "Profit" if zysk_strata >= 0 else "Loss"

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "price_pln_perg": cache["price_pln_perg"],
            "price_usd": cache["price_usd"],
            "suma_skupu": cache["suma_skupu"],
            "zysk_strata": zysk_strata,
            "fetch_time": cache["fetch_time"],
            "kolor": kolor,
            "znak": znak,
        },
    )


if __name__ == "__main__":
    import uvicorn

    thread = threading.Thread(target=background_updater, daemon=True)
    thread.start()
    uvicorn.run(app, host="127.0.0.1", port=8000)
