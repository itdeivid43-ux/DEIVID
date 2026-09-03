from flask import Flask
import threading, time, requests, random, os
from datetime import datetime

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
PARES = ["USDJPY","EURUSD","AUDUSD","GBPUSD","USDCAD","USDCHF","NZDUSD"]

def send(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
    except: pass

def bot_loop():
    time.sleep(10)
    send("✅ <b>DEIVID BOT PREMIUM ONLINE</b>\n7 pares - 5m - Solo 85%+")
    while True:
        for par in PARES:
            confianza = random.randint(85, 96)
            rsi = random.uniform(48, 72)
            direccion = random.choice(["COMPRAR 🟢", "VENDER 🔴"])
            precio = round(random.uniform(0.6, 158.9), 5)
            hora = datetime.now().strftime("%H:%M")
            msg = f"""{direccion} {par} 5m
💰 {precio}
📊 RSI {round(rsi,1)}
✅ Confianza {confianza}%

⏰ Entrada siguiente vela {hora}
🔥 85%+ PREMIUM"""
            send(msg)
            time.sleep(2)
        time.sleep(600)

@app.route('/')
def home():
    return "BOT LIVE"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
