import time
import threading
import requests
from flask import Flask

# --- CONFIGURACION REAL DE DEIVID ---
BOT_TOKEN = "8962914647:AAHFuFSg14UM4zkdJgVdgi15n4ltr6-5E80"
CHAT_ID = "5890249548"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
        requests.post(url, data=data, timeout=10)
        print(f"Mensaje enviado: {msg}")
    except Exception as e:
        print(f"Error telegram: {e}")

def bot_loop():
    send_telegram("✅ <b>DEIVID BOT REAL ONLINE</b>\n\nEl bot ya está funcionando con tu ID real 5890249548\nTe enviaré las señales de ORO XAUUSD aquí.")
    while True:
        try:
            # Aquí va tu lógica de trading
            time.sleep(60)
        except Exception as e:
            print(e)
            time.sleep(5)

# Iniciar bot en segundo plano
threading.Thread(target=bot_loop, daemon=True).start()

# Servidor web para que Render no se apague
app = Flask(__name__)
@app.route('/')
def home():
    return "DEIVID BOT LIVE - OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
