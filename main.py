import os
import threading
import time
import requests
from flask import Flask

BOT_TOKEN = "8962914647:AAG5pHw1oF-HHIDKNRYD_U4dWxYFbC-WYVk"  # <--- TU TOKEN NUEVO
CHAT_ID = "5890249548"

app = Flask(__name__)

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print(f"Error send: {e}")

def trading_loop():
    time.sleep(5)
    send("✅ DEIVID BOT CONECTADO - Ya estoy LIVE 24/7")
    while True:
        try:
            # Aqui va tu logica de trading, por ahora solo vive
            time.sleep(60)
        except:
            time.sleep(10)

# Inicia el bot en segundo plano
threading.Thread(target=trading_loop, daemon=True).start()

@app.route('/')
def home():
    return "DEIVID BOT LIVE"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
