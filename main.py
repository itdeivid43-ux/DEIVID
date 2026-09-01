import os
import time
import threading
import requests
from datetime import datetime
from flask import Flask
import yfinance as yf
import pytz

app = Flask(__name__)

# CONFIGURACION TELEGRAM - de Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")

# 32 PARES FOREX
PARES = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X",
    "EURJPY=X", "EURGBP=X", "EURCAD=X", "EURAUD=X", "EURCHF=X", "GBPJPY=X",
    "GBPCAD=X", "GBPAUD=X", "GBPCHF=X", "AUDJPY=X", "AUDCAD=X", "AUDCHF=X",
    "CADJPY=X", "CADCHF=X", "CHFJPY=X", "NZDUSD=X", "EURNZD=X", "GBPNZD=X",
    "AUDNZD=X", "NZDJPY=X", "NZDCAD=X", "NZDCHF=X", "EURCHF=X", "USDNOK=X",
    "USDSEK=X", "USDSGD=X"
]

ZONA_EC = pytz.timezone("America/Guayaquil")

def enviar_telegram(mensaje):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("FALTA TOKEN O CHAT_ID")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "HTML"}
        r = requests.post(url, data=data, timeout=10)
        print(f"Telegram: {r.status_code}")
    except Exception as e:
        print(f"Error telegram: {e}")

def calcular_rsi(precios, periodo=14):
    try:
        deltas = [precios[i] - precios[i-1] for i in range(1, len(precios))]
        ganancias = [d if d > 0 else 0 for d in deltas]
        perdidas = [-d if d < 0 else 0 for d in deltas]
        if len(ganancias) < periodo: return 50
        avg_gan = sum(ganancias[-periodo:]) / periodo
        avg_per = sum(perdidas[-periodo:]) / periodo
        if avg_per == 0: return 100
        rs = avg_gan / avg_per
        return 100 - (100 / (1 + rs))
    except:
        return 50

def analizar_par(par):
    try:
        data = yf.download(par, period="1d", interval="5m", progress=False, auto_adjust=True)
        if len(data) < 20: return None
        cierres = data['Close'].tolist()
        rsi = calcular_rsi(cierres)
        precio = cierres[-1]
        if rsi < 30:
            return f"🟢 <b>COMPRA</b> {par} - RSI {rsi:.1f}"
        elif rsi > 70:
            return f"🔴 <b>VENTA</b> {par} - RSI {rsi:.1f}"
        return None
    except Exception as e:
        print(f"Error {par}: {e}")
        return None

def bot_loop():
    enviar_telegram("✅ <b>BOT PRO 32 PARES INICIADO EN RENDER</b>\nAnalizando cada 5 min")
    while True:
        try:
            hora_str = datetime.now(ZONA_EC).strftime("%H:%M:%S")
            print(f"Analizando {hora_str}")
            senales = 0
            for par in PARES:
                senal = analizar_par(par)
                if senal:
                    enviar_telegram(f"{senal}\n⏰ {hora_str} EC\n📊 Quotex")
                    senales += 1
                time.sleep(2)
            if senales == 0:
                print(f"Sin señales {hora_str}")
            time.sleep(300)
        except Exception as e:
            print(f"Error loop: {e}")
            time.sleep(60)

@app.route('/')
def home():
    return "BOT PRO 32 PARES LIVE - OK", 200

if __name__ == "__main__":
    threading.Thread(target=bot_loop, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
