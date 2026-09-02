import os, requests, time, threading
from datetime import datetime
from flask import Flask
import pytz

app = Flask(__name__)
@app.route('/')
def home():
    return "BOT 28 PARES MEDIO LIVE"

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVEDATA_API_KEY")
EC = pytz.timezone("America/Guayaquil")

PARES = ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","EUR/JPY","GBP/JPY","USD/CHF","EUR/GBP","USD/CAD","NZD/USD","EUR/AUD","GBP/CAD","AUD/CAD","AUD/CHF","AUD/JPY","AUD/NZD","CAD/CHF","CAD/JPY","CHF/JPY","EUR/CAD","EUR/CHF","EUR/NZD","GBP/AUD","GBP/CHF","GBP/NZD","NZD/CAD","NZD/CHF","NZD/JPY"]

def send(t):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": t}, timeout=15)
    except:
        pass

def get_stoch(par):
    try:
        url = f"https://api.twelvedata.com/stoch?symbol={par}&interval=5min&apikey={API_KEY}&k_period=13&d_period=3&slowing=3"
        r = requests.get(url, timeout=15).json()
        k = float(r['values'][0]['k'])
        d = float(r['values'][0]['d'])
        return k, d
    except:
        return None, None

def bot_loop():
    send("✅ BOT 28 PARES MODO MEDIO CONECTADO - Señal cada 10-15 min")
    while True:
        try:
            ahora = datetime.now(EC)
            hora = ahora.strftime("%H:%M")
            for par in PARES:
                k, d = get_stoch(par)
                if k is None:
                    continue
                if k < 40 and d < 45 and k > d:
                    send(f"🟢 COMPRA 5M {par} {hora} EC Stoch {k:.1f}/{d:.1f}")
                elif k > 60 and d > 55 and k < d:
                    send(f"🔴 VENTA 5M {par} {hora} EC Stoch {k:.1f}/{d:.1f}")
                time.sleep(6)
            time.sleep(120)
        except:
            time.sleep(10)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
