import os, time, threading, requests, yfinance as yf
from flask import Flask
from datetime import datetime
import pytz

app = Flask(__name__)

PARES = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "NZDUSD=X"]
NOMBRES = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD"]

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
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
        hora_ec = datetime.now(pytz.timezone('America/Guayaquil')).strftime('%I:%M %p')
        mensaje = f"📊 *ESTOCASTICO 13,3,3 | {hora_ec} ECUADOR*\n\n"
        
        for par, nombre in zip(PARES, NOMBRES):
            data = yf.download(par, period="2d", interval="5m", progress=False, auto_adjust=True)
            if len(data) < 30:
                continue
            # aplanar si viene multi-index
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            data = stochastic(data)
            k_actual = float(data['%K'].iloc[-1])
            k_anterior = float(data['%K'].iloc[-2])

            if k_anterior < 20 and k_actual > 20:
                mensaje += f"🟢 *COMPRA {nombre} 5MIN* (Estoc {k_actual:.1f} sube 20)\n"
            elif k_anterior > 80 and k_actual < 80:
                mensaje += f"🔴 *VENTA {nombre} 5MIN* (Estoc {k_actual:.1f} baja 80)\n"
            else:
                mensaje += f"⚪ {nombre} Esperar ({k_actual:.1f})\n"
        
        send_telegram(mensaje)
        print("Mensaje enviado: " + hora_ec)
    except Exception as e:
        print(f"Error analizar: {e}")

def loop_bot():
    while True:
        analizar()
        time.sleep(600) # 10 minutos

@app.route('/')
def home():
    return "Bot DEIVID Estocastico 13,3,3 cada 10 min ACTIVO"

if __name__ == '__main__':
    threading.Thread(target=loop_bot, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
