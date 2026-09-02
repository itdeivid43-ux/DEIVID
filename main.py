import requests, os, threading, time
from flask import Flask
from datetime import datetime
import pytz

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
app = Flask(__name__)
PARES = ["EURUSD","GBPUSD","USDJPY","AUDUSD","EURJPY"]

def send_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mensaje}
        r = requests.post(url, data=data, timeout=20)
        print(f"Telegram -> {r.status_code}")
    except Exception as e:
        print(f"Error tg: {e}")

def analizar(par):
    try:
        symbol = f"{par}=X"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=1d"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=15)
        print(f"{par} Yahoo -> {r.status_code}")
        j = r.json()
        closes = j['chart']['result'][0]['indicators']['quote'][0]['close']
        closes = [c for c in closes if c is not None]
        if len(closes) < 50:
            return f"{par}: pocos datos ({len(closes)})"

        precio = closes[-1]
        ema9 = sum(closes[-9:])/9
        ema21 = sum(closes[-21:])/21

        if ema9 > ema21:
            return f"🟢 {par} COMPRA - Precio {precio:.5f} > EMA"
        elif ema9 < ema21:
            return f"🔴 {par} VENTA - Precio {precio:.5f} < EMA"
        else:
            return f"{par} LATERAL"
    except Exception as e:
        print(f"Error {par}: {e}")
        return f"{par} ERROR: {e}"

def bot_loop():
    time.sleep(5)
    tz = pytz.timezone('America/Guayaquil')
    hora = datetime.now(tz).strftime('%H:%M')
    send_telegram(f"🔧 BOT DEBUG PRENDIDO {hora} EC\nProbando 5 pares principales...\nSi ves esto, Telegram SI funciona.")

    while True:
        try:
            hora = datetime.now(tz).strftime('%H:%M')
            print(f"=== SCAN {hora} ===")
            reporte = f"📊 REPORTE {hora} EC\n\n"
            for par in PARES:
                res = analizar(par)
                reporte += res + "\n"
                time.sleep(1)

            send_telegram(reporte)
            time.sleep(180) # cada 3 min
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(60)

@app.route('/')
def home(): return "Deivid DEBUG Live"

threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
