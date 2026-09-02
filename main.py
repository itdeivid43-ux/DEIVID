import os, requests, time, threading
from datetime import datetime
from flask import Flask
import pytz

app = Flask(__name__)

@app.route('/')
def home():
    return "BOT V08 SOLO 1 PESO LIVE - OK"

@app.route('/prueba')
def prueba():
    send("🔥 PRUEBA BOT DEIVID - Funciona! Si ves esto en Telegram, el bot está 100% LIVE. Hora: " + datetime.now(pytz.timezone("America/Guayaquil")).strftime("%H:%M:%S"))
    return "Mensaje de prueba enviado a Telegram!"

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVEDATA_API_KEY")
EC = pytz.timezone("America/Guayaquil")

PARES = ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","EUR/JPY","GBP/JPY","USD/CHF","EUR/GBP","USD/CAD","NZD/USD"]

def send(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": text, "parse_mode":"Markdown"}, timeout=10)
        print(f"Enviado: {text[:30]}")
    except Exception as e:
        print(f"Error send: {e}")

def bot_loop():
    print(">>> BOT LOOP INICIADO - Buscando señales cada 5 min")
    send("✅ Bot DEIVID V08 iniciado en Render - LIVE y buscando señales cada 5 min")
    while True:
        try:
            print(f"[{datetime.now(EC).strftime('%H:%M:%S')}] Analizando mercado...")
            # AQUI VA TU LOGICA DE ANALISIS - por ahora manda señal de prueba cada hora para validar
            # Pon tu logica real aquí
            time.sleep(300) # 5 minutos
        except Exception as e:
            print(f"Error loop: {e}")
            time.sleep(60)

# INICIAR BOT EN SEGUNDO PLANO - ESTO ES LO QUE TE FALTABA
threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
