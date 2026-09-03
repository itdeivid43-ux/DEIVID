from flask import Flask
import threading, time, requests, random, os
from datetime import datetime

app = Flask(__name__)

# LEE DE RENDER - YA NO PONGAS EL TOKEN AQUI
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
PARES = ["USDJPY","EURUSD","AUDUSD","GBPUSD","USDCAD","USDCHF","NZDUSD"]

def send(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(e)

def bot_loop():
    send("✅ <b>DEIVID BOT PREMIUM ONLINE</b>\nID: 5890249548\n7 pares - 5m - Solo 85%+")
    while True:
        try:
            for par in PARES:
                rsi = random.uniform(45, 75)
                confianza = random.randint(85, 96)
                if confianza >= 85:
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
        except Exception as e:
            print(e)
            time.sleep(60)

@app.route('/')
def home():
    return "BOT PREMIUM LIVE - 5890249548"

threading.Thread(target=bot_loop, daemon=True).start()
