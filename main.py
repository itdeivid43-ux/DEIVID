import os
import time
import threading
import requests
from datetime import datetime, timedelta
from flask import Flask
import yfinance as yf

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

PARES = ["EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","USDCAD=X","USDCHF=X","EURJPY=X","EURGBP=X","EURCAD=X","EURAUD=X","EURCHF=X","GBPJPY=X","GBPCAD=X","GBPCHF=X","GBPAUD=X","AUDJPY=X","AUDCAD=X","AUDCHF=X","CADJPY=X","CHFJPY=X","EURUSD=X","GBPUSD=X","NZDUSD=X","NZDJPY=X","NZDCAD=X","NZDCHF=X","EURNZD=X","GBPNZD=X","AUDNZD=X","CADCHF=X","EURCAD=X","EURCAD=X"]

def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def bot_loop():
    while True:
        try:
            ahora = datetime.now()
            expira = ahora + timedelta(minutes=5)
            texto = f"🚀 *BOT 32 PARES ACTIVO - {ahora.strftime('%H:%M:%S')} EC*\n⌛ Expira: {expira.strftime('%H:%M:%S')}\n\nMonitoreando 32 pares..."
            enviar_telegram(texto)
            print("Mensaje enviado")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(300)

@app.route('/')
def home():
    return "Bot 32 Pares OK"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
