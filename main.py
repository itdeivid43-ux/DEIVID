import os, requests, time, threading
from datetime import datetime
from flask import Flask
import pytz

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVEDATA_API_KEY")
EC = pytz.timezone("America/Guayaquil")
PARES = ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","EUR/JPY","GBP/JPY","USD/CHF","EUR/GBP","USD/CAD","NZD/USD"]

def send(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": text}, timeout=10)
        print(f"Enviado OK")
    except Exception as e:
        print(f"Error send: {e}")

app = Flask(__name__)

@app.route('/')
def home():
    return "BOT V08 SOLO 1 PESO LIVE - OK"

@app.route('/prueba')
def prueba():
    hora = datetime.now(EC).strftime("%H:%M:%S")
    send(f"🔥 PRUEBA BOT DEIVID - Funciona! Hora Ecuador: {hora} - BOT 100% LIVE")
    return f"Prueba enviada a las {hora}!"

def bot_loop():
    print(">>> BOT LOOP INICIADO")
    send("✅ Bot DEIVID V08 iniciado en Render - LIVE")
    while True:
        try:
            print(f"[{datetime.now(EC).strftime('%H:%M:%S')}] Analizando...")
            time.sleep(300)
        except Exception as e:
            print(e)
            time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
