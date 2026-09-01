import requests
import os
from flask import Flask
import threading
import time

TOKEN = "8962914647:AAHFuFSg14UM4zkdJgVdgiI5n41tr6-5E80"
CHAT_ID = "6273812557"

print(f"BOT INICIANDO... CHAT_ID: {CHAT_ID}")

def send_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mensaje}
        r = requests.post(url, data=data, timeout=10)
        print(f"TELEGRAM -> {r.status_code} | {r.text}")
    except Exception as e:
        print(f"ERROR TELEGRAM: {e}")

def bot_loop():
    print("bot_loop iniciado")
    send_telegram("✅ DEIVID TU BOT YA FUNCIONA!")
    time.sleep(5)
    send_telegram("Si ves esto, Telegram esta conectado. Ahora pondremos el analisis de BTC.")

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot DEIVID activo!"

if __name__ == '__main__':
    t = threading.Thread(target=bot_loop, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=10000)
