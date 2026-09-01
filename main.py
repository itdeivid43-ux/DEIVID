import os
import time
import threading
import requests
from flask import Flask

# --- ARREGLA EL TOKEN ---
token_raw = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_TOKEN = token_raw.strip().replace(" ", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()

print(f"TOKEN INICIO: {TELEGRAM_TOKEN[:10]}...{TELEGRAM_TOKEN[-5:]} CHAT: {CHAT_ID}")
print("BOT INICIANDO...")

# --- TU BOT DE TRADING ---
def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text}
        r = requests.post(url, data=data, timeout=10)
        print(f"TELEGRAM -> {r.status_code} {r.text[:100]}")
    except Exception as e:
        print(f"Error telegram: {e}")

def bot_loop():
    send_telegram("✅ Bot DEIVID conectado y funcionando en Render!")
    while True:
        try:
            # Aquí va tu lógica de trading, por ahora solo avisa que está vivo
            # send_telegram("Señal de prueba...")
            time.sleep(60)
        except Exception as e:
            print(f"Error en loop: {e}")
            time.sleep(10)

# --- SERVIDOR PARA RENDER ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot DEIVID activo!"

if __name__ == '__main__':
    t = threading.Thread(target=bot_loop, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=10000)
