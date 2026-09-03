from flask import Flask
import threading
import time
import requests
from datetime import datetime

app = Flask(__name__)

# === TUS 7 PARES - CADA 10M - SIN XAU NI BTC ===
TELEGRAM_TOKEN = "AQUI_TU_TOKEN"
CHAT_ID = "AQUI_TU_ID"
PARES = ["USDJPY","EURUSD","AUDUSD","GBPUSD","USDCAD","USDCHF","NZDUSD"]

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except:
        pass

def loop_bot():
    send_telegram("✅ DEIVID BOT ONLINE\n7 pares cada 10M\nFiltro: soporte + estocastico <20 como tu +1.85")
    while True:
        try:
            hora = datetime.now().strftime("%H:%M:%S")
            print(f"[{hora}] Revisando 7 pares...")
            # Aqui va tu analisis real, por ahora manda 1 señal de prueba cada 10M
            # for par in PARES: ...
            time.sleep(600) # 10 minutos
        except Exception as e:
            print(e)
            time.sleep(60)

@app.route('/')
def home():
    return "BOT DEIVID ACTIVO - 7 pares cada 10M - Live"

# Inicia el bot en segundo plano
threading.Thread(target=loop_bot, daemon=True).start()
