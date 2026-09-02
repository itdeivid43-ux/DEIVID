import os
import time
from flask import Flask
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

# --- CONFIGURACION ---
# Pon estos en Render > Environment
BOT_TOKEN = os.getenv("BOT_TOKEN") # Tu token de @deivid25trading2_bot
CHAT_ID = os.getenv("CHAT_ID") # Tu ID
TD_API_KEY = os.getenv("TD_API_KEY") # API de TwelveData

SYMBOL = "BTC/USD"
INTERVAL = "5min" # <-- AQUI ESTA EL 5M

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def get_hora_ecuador():
    tz = pytz.timezone("America/Guayaquil")
    return datetime.now(tz).strftime("%H:%M:%S")

@app.route('/')
def home():
    return f"BOT V28 SOLO 1 FIJO LIVE - OK - {INTERVAL} - Hora Ecuador: {get_hora_ecuador()} - deivid.onrender.com"

def bot_loop():
    enviar_telegram(f"✅ *Bot DEIVID V08 iniciado en Render - LIVE*\nIntervalo: {INTERVAL}")
    while True:
        try:
            # Aqui va tu logica V28 de EMA 8/21
            # Cuando detecte cruce, llama a enviar_telegram()
            time.sleep(60) 
        except Exception as e:
            print(e)
            time.sleep(10)

# Inicia el bot en segundo plano
import threading
threading.Thread(target=bot_loop).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
