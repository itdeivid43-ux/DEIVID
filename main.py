import requests
import os
from flask import Flask
import threading
import time

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(mensaje):
    print(f"Intentando enviar a {CHAT_ID}: {mensaje}")
    try:
        if not TOKEN or not CHAT_ID:
            print(f"FALTA TOKEN O CHAT_ID! TOKEN:{bool(TOKEN)} CHAT:{CHAT_ID}")
            return
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mensaje}
        r = requests.post(url, data=data, timeout=15)
        print(f"RESPUESTA TELEGRAM: {r.status_code} - {r.text[:500]}")
    except Exception as e:
        print(f"ERROR EXCEPCION: {e}")

print("=== INICIO BOT DEIVID ===")
print(f"TOKEN existe: {bool(TOKEN)} CHAT_ID: {CHAT_ID}")
send_telegram("🚀 BOT DEIVID CONECTADO - PRUEBA INSTANTANEA")

def bot_loop():
    print("bot_loop iniciado - esperando 60 seg")
    while True:
        time.sleep(60)
        send_telegram("✅ DEIVID sigo vivo - bot cada 60 seg")

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot DEIVID activo"

t = threading.Thread(target=bot_loop, daemon=True)
t.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
