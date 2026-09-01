import requests
import os
from flask import Flask
import threading
import time

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print(f"BOT INICIANDO... TOKEN existe: {bool(TOKEN)} CHAT_ID: {CHAT_ID}")

def send_telegram(mensaje):
    print(f"Enviando: {mensaje[:30]}...")
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mensaje}
        r = requests.post(url, data=data, timeout=15)
        print(f"TELEGRAM -> {r.status_code} | {r.text[:200]}")
    except Exception as e:
        print(f"ERROR: {e}")

def bot_loop():
    print("bot_loop iniciado")
    time.sleep(3)
    send_telegram("✅ DEIVID TU BOT YA FUNCIONA! Token nuevo correcto!")
    while True:
        send_telegram("🤖 Bot vivo - prueba cada 60 seg")
        time.sleep(60)

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot DEIVID activo - vFINAL"

if __name__ == '__main__':
    t = threading.Thread(target=bot_loop, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=10000)
