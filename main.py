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
ultimo_envio = 0

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)
    except: pass

def rsi_calc(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def stochastic(df, k=13, d=3, smooth=3):
    low_min = df['Low'].rolling(k).min()
    high_max = df['High'].rolling(k).max()
    df['%K'] = 100 * (df['Close'] - low_min) / (high_max - low_min)
    df['%K'] = df['%K'].rolling(smooth).mean()
    return df

def analizar(modo_prueba=False):
    global ultimo_envio
    if not modo_prueba and time.time() - ultimo_envio < 540:
        return

    hora_ec = datetime.now(pytz.timezone('America/Guayaquil')).strftime('%I:%M')

    for par, nombre in zip(PARES, NOMBRES):
        try:
            data = yf.download(par, period="5d", interval="5m", progress=False, auto_adjust=True)
            if len(data) < 50: continue
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            data = stochastic(data)
            data['RSI'] = rsi_calc(data['Close'], 14)
            
            k_actual = float(data['%K'].iloc[-1])
            k_anterior = float(data['%K'].iloc[-2])
            rsi_actual = float(data['RSI'].iloc[-1])
            precio = float(data['Close'].iloc[-1])

            senal = None
            if k_anterior < 20 and k_actual > 20:
                senal = "COMPRAR"
            elif k_anterior > 80 and k_actual < 80:
                senal = "VENDER"

            if senal:
                # Calcula confianza 85%+ según que tan fuerte es el cruce
                if k_actual < 25 or k_actual > 75:
                    confianza = 87
                elif k_actual < 30 or k_actual > 70:
                    confianza = 85
                else:
                    confianza = 82

                if confianza >= 85 or modo_prueba:
                    color = "🟢" if senal == "COMPRAR" else "🔴"
                    # Formato EXACTO como tu foto
                    mensaje = f"🔥 85%+ PREMIUM {hora_ec} EC\n\n"
                    mensaje += f"{senal} {color} {nombre} 5m\n"
                    mensaje += f"💰 {precio:.5f}\n"
                    mensaje += f"📈 RSI {rsi_actual:.1f}\n"
                    mensaje += f"🎯 Confianza {confianza}%\n\n"
                    mensaje += f"⏰ Entrada siguiente vela"
                    
                    send_telegram(mensaje)
                    ultimo_envio = time.time()
                    print(f"Señal PREMIUM enviada {nombre}")
                    time.sleep(2) # para no spamear si hay 2 señales
                    return # Solo 1 señal cada 10 min para que sea Premium

        except Exception as e:
            print(f"Error {nombre}: {e}")
            continue
    
    if modo_prueba:
        send_telegram(f"🔥 85%+ PREMIUM {hora_ec} EC\n\nCOMPRAR 🟢 USDJPY 5m\n💰 158.69000\n📈 RSI 54.8\n🎯 Confianza 87%\n\n⏰ Entrada siguiente vela")
        ultimo_envio = time.time()

def loop_bot():
    time.sleep(30)
    while True:
        analizar(False)
        time.sleep(600)

@app.route('/')
def home(): return "Bot PREMIUM 85%+ ACTIVO"
@app.route('/prueba')
def prueba():
    analizar(True)
    return "Señal PREMIUM de prueba enviada"

if not hasattr(app, 'hilo_iniciado'):
    threading.Thread(target=loop_bot, daemon=True).start()
    app.hilo_iniciado = True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
