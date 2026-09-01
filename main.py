from flask import Flask
import threading, time, requests, os

app = Flask(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_mensaje(texto):
    try:
        if not BOT_TOKEN or not CHAT_ID:
            print("❌ FALTA TOKEN O CHAT_ID en Environment de Render!", flush=True)
            return
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": texto}
        r = requests.post(url, data=data, timeout=10)
        print(f"TELEGRAM -> {r.status_code} {r.text[:200]}", flush=True)
    except Exception as e:
        print(f"ERROR: {e}", flush=True)

def bot_loop():
    print(f"TOKEN INICIO: {str(BOT_TOKEN)[:15]}... CHAT: {CHAT_ID}", flush=True)
    print("BOT INICIANDO...", flush=True)
    enviar_mensaje("✅ BOT INICIADO - Deivid si ves esto YA FUNCIONA!")
    time.sleep(2)
    while True:
        try:
            enviar_mensaje("🔥 SEÑAL TEST EUR/USD COMPRA 85% 5MIN")
            time.sleep(60)
        except Exception as e:
            print(f"Loop error: {e}", flush=True)
            time.sleep(10)

@app.route('/')
def home():
    return "BOT ACTIVO"

if __name__ == "__main__":
    threading.Thread(target=bot_loop, daemon=True).start()
    app.run(host='0.0.0.0', port=10000)
