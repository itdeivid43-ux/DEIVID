from flask import Flask
import threading, time, requests, os
app = Flask(__name__)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
def enviar_mensaje(texto):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": texto}, timeout=10)
        print(f"Enviado: {texto}", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)
def bot_loop():
    print("BOT INICIANDO...", flush=True)
    enviar_mensaje("✅ BOT PRO 32 PARES INICIADO - Ya estoy analizando Deivid")
    while True:
        try:
            enviar_mensaje("🔥 SEÑAL TEST - EUR/USD - COMPRA 85% - 5 MIN")
            time.sleep(60)
        except Exception as e:
            print(f"Error loop: {e}", flush=True)
            time.sleep(10)
@app.route('/')
def home():
    return "BOT ACTIVO 24/7 - DEIVID"
if __name__ == "__main__":
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
