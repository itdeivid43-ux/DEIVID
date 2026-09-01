import os
import time
import threading
import requests
from datetime import datetime, timedelta
from flask import Flask
import yfinance as yf
import pytz

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 32 PARES FOREX PARA QUOTEX / BINARIAS
PARES = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X",
    "EURJPY=X", "EURGBP=X", "EURCAD=X", "EURAUD=X", "EURCHF=X", "GBPJPY=X",
    "GBPCAD=X", "GBPAUD=X", "GBPCHF=X", "AUDJPY=X", "AUDCAD=X", "AUDCHF=X",
    "CADJPY=X", "CADCHF=X", "CHFJPY=X", "NZDUSD=X", "EURCHF=X", "EURNZD=X",
    "GBPNZD=X", "AUDNZD=X", "NZDJPY=X", "NZDCAD=X", "NZDCHF=X", "EURUSD=X",
    "USDJPY=X", "GBPUSD=X"
]
# Limpiamos duplicados y dejamos 32
PARES = list(dict.fromkeys(PARES))[:32]

ZONA_EC = pytz.timezone("America/Guayaquil")

def enviar_telegram(msg):
    try:
        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            print("Falta TOKEN o CHAT_ID")
            return
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
        r = requests.post(url, data=data, timeout=15)
        print(f"Telegram enviado: {r.status_code}")
    except Exception as e:
        print(f"Error telegram: {e}")

def calcular_rsi(precios, period=14):
    try:
        deltas = [precios[i] - precios[i-1] for i in range(1, len(precios))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period-1) + gains[i]) / period
            avg_loss = (avg_loss * (period-1) + losses[i]) / period
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    except:
        return 50

def analizar_par(par):
    try:
        ticker = yf.Ticker(par)
        hist = ticker.history(period="1d", interval="5m")
        if len(hist) < 20:
            return None
        closes = hist['Close'].tolist()
        rsi = calcular_rsi(closes)
        precio = closes[-1]
        tendencia = "ALCISTA" if closes[-1] > closes[-5] else "BAJISTA"

        senal = None
        confianza = 0
        if rsi < 30:
            senal = "COMPRA 🟢"
            confianza = 85 if rsi < 25 else 75
        elif rsi > 70:
            senal = "VENTA 🔴"
            confianza = 85 if rsi > 75 else 75

        if senal:
            return {"par": par.replace("=X",""), "senal": senal, "rsi": round(rsi,1), "precio": round(precio,5), "tendencia": tendencia, "conf": confianza}
    except Exception as e:
        print(f"Error {par}: {e}")
    return None

def bot_loop():
    print("BOT PRO 32 PARES INICIADO")
    enviar_telegram("🚀 *BOT PRO 32 PARES ACTIVO*\nAnalizando mercado cada 5 min... ⏳")
    while True:
        try:
            ahora = datetime.now(ZONA_EC)
            expira = ahora + timedelta(minutes=5)
            hora_str = ahora.strftime("%H:%M:%S")
            expira_str = expira.strftime("%H:%M:%S")

            oportunidades = []
            for par in PARES:
                res = analizar_par(par)
                if res:
                    oportunidades.append(res)
                time.sleep(0.5) # para no saturar yfinance

            if oportunidades:
                # Ordenar por confianza
                oportunidades.sort(key=lambda x: x['conf'], reverse=True)
                top = oportunidades[:3] # solo las 3 mejores

                msg = f"📊 *SEÑALES 5M - {hora_str} EC*\n"
                msg += f"⌛ Expira: {expira_str} EC\n"
                msg += f"━━━━━━━━━━━━━━━\n"
                for op in top:
                    msg += f"\n💱 *{op['par']}* - {op['senal']}\n"
                    msg += f" RSI: {op['rsi']} | {op['tendencia']}\n"
                    msg += f" Confianza: {op['conf']}% | Precio: {op['precio']}\n"
                msg += f"\n🎯 Entrada: {hora_str} - {expira_str} (5m)"
                enviar_telegram(msg)
            else:
                # Si no hay señales claras, avisa que sigue monitoreando
                if ahora.minute % 30 == 0: # cada 30 min avisa
                    enviar_telegram(f"⏳ *Monitoreando... {hora_str} EC*\n32 pares sin señal clara ahora. Esperando RSI extremo.")

            time.sleep(300) # 5 minutos

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
