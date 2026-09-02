import os, time, threading, requests
import pandas as pd
import yfinance as yf
from flask import Flask
from datetime import datetime
import pytz

app = Flask(__name__)

PARES = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "NZDUSD=X"]
NOMBRES = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD"]

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    if not TOKEN or not CHAT_ID:
        print("FALTA TOKEN O CHAT ID")
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)
        print(f"Telegram respuesta: {r.text}")
    except Exception as e:
        print(f"Error telegram: {e}")

def stochastic(df, k=13, d=3, smooth=3):
    low_min = df['Low'].rolling(k).min()
    high_max = df['High'].rolling(k).max()
    df['%K'] = 100 * (df['Close'] - low_min) / (high_max - low_min)
    df['%K'] = df['%K'].rolling(smooth).mean()
    df['%D'] = df['%K'].rolling(d).mean()
    return df

def analizar():
    try:
        print("Analizando mercado...")
        hora_ec = datetime.now(pytz.timezone('America/Guayaquil')).strftime('%I:%M %p')
        mensaje = f"📊 *ESTOCASTICO 13,3,3 | {hora_ec} ECU*\n\n"
        hay_senal = False
        for par, nombre in zip(PARES, NOMBRES):
            try:
                data = yf.download(par, period="2d", interval="5m", progress=False, auto_adjust=True)
                if len(data) < 30: continue
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)
                data = stochastic(data)
                k_actual = float(data['%K'].iloc[-1])
                k_anterior = float(data['%K'].iloc[-2])
                if k_anterior < 20 and k_actual > 20:
                    mensaje += f"🟢 *COMPRA {nombre} 5MIN* (Estoc {k_actual:.1f})\n"
                    hay_senal = True
                elif k_anterior > 80 and k_actual < 80:
                    mensaje += f"🔴 *VENTA {nombre} 5MIN* (Estoc {k_actual:.1f})\n"
                    hay_senal = True
                else:
                    mensaje += f"⚪ {nombre} Esperar ({k_actual:.1f})\n"
            except Exception as e:
                print(f"Error con {nombre}: {e}")
                continue
        if hay_senal:
            mensaje += f"\n⏰ Hora Ecuador: {hora_ec}"
        send_telegram(mensaje)
        print(f"Mensaje enviado OK {hora_ec}")
    except Exception as e:
        print(f"Error analizar general: {e}")

def loop_bot():
    time.sleep(10)
    while True:
        analizar()
        time.sleep(600)

@app.route('/')
def home():
    return "Bot DEIVID ESTOCASTICO ACTIVO"

@app.route('/prueba')
def prueba():
    analizar()
    return "Prueba enviada a Telegram"

threading.Thread(target=loop_bot, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
