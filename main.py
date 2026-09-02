import os
import time
import threading
import yfinance as yf
import pandas as pd
from flask import Flask

import requests

app = Flask(__name__)

# TUS PARES
PARES = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "NZDUSD=X"]
NOMBRES = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD"]

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except Exception as e:
        print(e)

def stochastic(df, k=13, d=3, smooth=3):
    low_min = df['Low'].rolling(k).min()
    high_max = df['High'].rolling(k).max()
    df['%K'] = 100 * (df['Close'] - low_min) / (high_max - low_min)
    df['%K'] = df['%K'].rolling(smooth).mean()
    df['%D'] = df['%K'].rolling(d).mean()
    return df

def analizar():
    mensaje = "📊 *SEÑALES ESTOCÁSTICO 13,3,3 - CADA 10 MIN*\n\n"
    hay_senal = False
    
    for par, nombre in zip(PARES, NOMBRES):
        try:
            data = yf.download(par, period="2d", interval="5m", progress=False)
            if len(data) < 30: continue
            data = stochastic(data)
            k_actual = float(data['%K'].iloc[-1])
            k_anterior = float(data['%K'].iloc[-2])
            
            senal = ""
            if k_anterior < 20 and k_actual > 20:
                senal = f"🟢 *COMPRA {nombre} - UP 5 MIN* (Estoc {k_actual:.1f} subiendo 20)"
                hay_senal = True
            elif k_anterior > 80 and k_actual < 80:
                senal = f"🔴 *VENTA {nombre} - DOWN 5 MIN* (Estoc {k_actual:.1f} bajando 80)"
                hay_senal = True
            else:
                senal = f"⚪ {nombre} - Esperar (Estoc {k_actual:.1f})"
            
            mensaje += senal + "\n"
        except Exception as e:
            print(f"Error {nombre}: {e}")

    # Te lo manda CADA 10 minutos aunque no haya compra/venta para que sepas que está vivo
    send_telegram(mensaje)

def loop_bot():
    while True:
        analizar()
        time.sleep(600) # 600 segundos = 10 minutos

@app.route('/')
def home():
    return "Bot Estocástico 13,3,3 activo cada 10 min"

if __name__ == '__main__':
    threading.Thread(target=loop_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
