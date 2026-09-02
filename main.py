import os, requests, time, threading
from datetime import datetime
from flask import Flask
import pytz

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVEDATA_API_KEY")
EC = pytz.timezone("America/Guayaquil")
URL = "https://deivid.onrender.com"

PARES_8 = ["XAU/USD", "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "EUR/JPY", "GBP/JPY", "USD/CAD"]

app = Flask(__name__)

def send(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def get_rsi(par):
    try:
        url = f"https://api.twelvedata.com/rsi?symbol={par}&interval=5min&apikey={API_KEY}"
        return float(requests.get(url, timeout=10).json()['values'][0]['rsi'])
    except:
        return None

# BOT QUE NO SE CAE
def keep_alive():
    while True:
        try:
            requests.get(URL, timeout=10)
            print(f"Keep alive ping {datetime.now(EC).strftime('%H:%M:%S')}")
        except:
            pass
        time.sleep(240) # se auto-pingea cada 4 min

def bot():
    send("✅ BOT 8 PARES INICIADO - ANTI-CAIDA ACTIVADO")
    while True:
        try:
            for par in PARES_8:
                rsi = get_rsi(par)
                if rsi is None:
                    time.sleep(3)
                    continue
                print(f"{par} RSI {rsi}")
                if rsi <= 30:
                    send(f"🟢 *{par} COMPRA UP* ⬆️ 5 MIN | RSI {round(rsi,1)}")
                elif rsi >= 70:
                    send(f"🔴 *{par} VENTA DOWN* ⬇️ 5 MIN | RSI {round(rsi,1)}")
                time.sleep(5)
            time.sleep(300)
        except Exception as e:
            print(f"Error bot, reiniciando: {e}")
            time.sleep(30)

@app.route('/')
def home():
    return "Bot Deivid 8 Pares Binarias ONLINE - ANTI CAIDA", 200

if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    threading.Thread(target=bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
