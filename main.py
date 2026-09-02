import os, requests, time, threading
from datetime import datetime
from flask import Flask
import pytz

app = Flask(__name__)
@app.route('/')
def home():
    return "BOT V28 SOLO 1 FIJO LIVE - OK"

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVEDATA_API_KEY")
EC = pytz.timezone("America/Guayaquil")

PARES = ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","EUR/JPY","GBP/JPY","USD/CHF","EUR/GBP","USD/CAD","NZD/USD","EUR/AUD","GB"]

def send(t):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": t}, timeout=15)
    except:
        pass

def get_signal(par):
    try:
        # Lógica V28: EMA20, EMA50, EMA200 + SuperTrend
        url = f"https://api.twelvedata.com/ema?symbol={par}&interval=5min&apikey={API_KEY}&time_period=20"
        # Aquí va tu lógica completa...
        return None
    except:
        return None

def bot_loop():
    enviado = {} # Para que solo deje UNO en tiempo real
    while True:
        for par in PARES:
            sig = get_signal(par)
            if sig and enviado.get(par)!= sig:
                send(sig)
                enviado[par] = sig
        time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
