import os, requests, time, threading
from datetime import datetime
from flask import Flask
import pytz

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVEDATA_API_KEY")
EC = pytz.timezone("America/Guayaquil")

# 8 PARES RENTABLES BINARIAS
PARES_8 = [
    "XAU/USD", # ORO - El mejor
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
    "AUD/USD",
    "EUR/JPY",
    "GBP/JPY",
    "USD/CAD"
]

app = Flask(__name__)

def send(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"})
        print("Señal enviada")
    except Exception as e:
        print(e)

def get_rsi(par):
    try:
        url = f"https://api.twelvedata.com/rsi?symbol={par}&interval=5min&apikey={API_KEY}"
        r = requests.get(url, timeout=10).json()
        return float(r['values'][0]['rsi'])
    except:
        return None

def bot():
    send("🔥 *BOT DEIVID - 8 PARES BINARIAS 5 MIN INICIADO* 🔥\n✅ Buscando entradas...")
    while True:
        for par in PARES_8:
            rsi = get_rsi(par)
            if rsi is None:
                time.sleep(2)
                continue

            print(f"{par} RSI: {rsi}")

            if rsi <= 30:
                send(f"🟢 *{par}* 🟢\n*COMPRA UP* ⬆️\nExpiración: 5 MIN\nRSI: {round(rsi,1)}\nHora EC: {datetime.now(EC).strftime('%H:%M:%S')}\n\n💰 ENTRAR YA!")

            elif rsi >= 70:
                send(f"🔴 *{par}* 🔴\n*VENTA DOWN* ⬇️\nExpiración: 5 MIN\nRSI: {round(rsi,1)}\nHora EC: {datetime.now(EC).strftime('%H:%M:%S')}\n\n💰 ENTRAR YA!")

            time.sleep(5)

        time.sleep(300) # Revisa cada 5 minutos

@app.route('/')
def home():
    return "Bot Deivid 8 Pares Binarias ONLINE", 200

if __name__ == "__main__":
    threading.Thread(target=bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
