from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fetch_gold_price import fetch
from fetch_skup import fetch_skup
import threading
import time


app = FastAPI()

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
    cena_zakupu = 4158

    cache["price_pln_perg"] = price_pln_perg
    cache["price_usd"] = price_usd
    cache["suma_skupu"] = suma_skupu
    cache["zysk_strata"] = suma_skupu - cena_zakupu
    cache["fetch_time"] = fetch_time



def background_updater():
    while True:
        update_cache()
        time.sleep(150)

@app.get("/", response_class=HTMLResponse)
def home():
    if cache["price_pln_perg"] is None:
        return """
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Loading...</title>
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    background: #0f172a;
                    color: #e2e8f0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                }
                .loader-card {
                    background: #1e293b;
                    border-radius: 16px;
                    padding: 40px;
                    text-align: center;
                }
                .spinner {
                    width: 36px;
                    height: 36px;
                    border: 4px solid #334155;
                    border-top: 4px solid #f8fafc;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 16px;
                }
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            </style>
        </head>
        <body>
            <div class="loader-card">
                <div class="spinner"></div>
                <p>Loading gold prices, please wait...</p>
            </div>
        </body>
        </html>
        """

    kolor = "#16a34a" if cache['zysk_strata'] >= 0 else "#dc2626"
    znak = "Profit" if cache['zysk_strata'] >= 0 else "Loss"

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>My Gold Portfolio</title>
        <style>
            body {{
                font-family: 'Segoe UI', sans-serif;
                background: #0f172a;
                color: #e2e8f0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }}
            .card {{
                background: #1e293b;
                border-radius: 16px;
                padding: 32px 40px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.4);
                max-width: 420px;
                width: 100%;
            }}
            h1 {{
                font-size: 22px;
                margin-bottom: 24px;
                color: #f8fafc;
            }}
            .row {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #334155;
                font-size: 15px;
            }}
            .row:last-child {{
                border-bottom: none;
            }}
            .label {{
                color: #94a3b8;
            }}
            .value {{
                font-weight: 600;
            }}
            .result {{
                margin-top: 20px;
                padding: 16px;
                border-radius: 10px;
                background: {kolor}22;
                border: 1px solid {kolor};
                text-align: center;
            }}
            .result .amount {{
                font-size: 26px;
                font-weight: 700;
                color: {kolor};
            }}
            .result .label {{
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>💰 My Gold Portfolio</h1>
            <div class="row">
                <span class="label">Gold price</span>
                <span class="value">{cache['price_pln_perg']:.2f} PLN/g</span>
            </div>
            <div class="row">
                <span class="label">Gold price</span>
                <span class="value">{cache['price_usd']:.2f} USD/oz</span>
            </div>
            <div class="row">
                <span class="label">Bars value (buyback)</span>
                <span class="value">{cache['suma_skupu']:.2f} PLN</span>
            </div>
            <div class="result">
                <div class="label">{znak}</div>
                <div class="amount">{cache['zysk_strata']:+.2f} PLN</div>
            </div>
        </div>
        <p style="color: #64748b; font-size: 12px; margin-top: 12px; text-align: center;">
            Last updated: {cache['fetch_time']}
        </p>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    import uvicorn
    thread = threading.Thread(target=background_updater, daemon=True)
    thread.start()
    uvicorn.run(app, host="127.0.0.1", port=8000)
