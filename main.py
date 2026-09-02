import os, requests, time, threading
from flask import Flask
import yfinance as yf
from datetime import datetime
import pytz

app = Flask(__name__)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send(m):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.get(url, params={"chat_id": CHAT_ID, "text": m}, timeout=10)
        print(f"Telegram status: {r.status_code} {r.text}")
        return r.text
    except Exception as e:
        print(f"Error telegram: {e}")
        return str(e)

@app.route("/test")
def test():
    result = send("✅ PRUEBA BOT BINARIAS - Si ves esto en Telegram, TODO esta bien conectado")
    return f"Enviado: {result}"

def bot():
    pares = ["EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","EURJPY=X"]
    while True:
        for par in pares:
            try:
                df = yf.download(par, period="2d", interval="5m", progress=False)
                if len(df) < 30: continue
                c = df['Close']; l = df['Low']; h = df['High']
                low_min = l.rolling(13).min()
                high_max = h.rolling(13).max()
                k = ((c - low_min) / (high_max - low_min) * 100).rolling(3).mean()
                d = k.rolling(3).mean()
                ck = float(k.iloc[-1]); pk = float(k.iloc[-2]); cd = float(d.iloc[-1])
                buy = pk < 20 and ck > 20 and ck > cd
                sell = pk > 80 and ck < 80 and ck < cd
                if buy or sell:
                    hora = datetime.now(pytz.timezone('America/Guayaquil')).strftime("%H:%M:%S")
                    tipo = "CALL COMPRAR" if buy else "PUT VENDER"
                    send(f"BOT BINARIAS 5m {hora} EC {tipo} {par} Estoc 13,3,3 K:{ck:.1f} D:{cd:.1f} ENTRAR AHORA sig vela EXP 5m")
            except Exception as e:
                print(e)
        time.sleep(60)

threading.Thread(target=bot, daemon=True).start()

@app.route("/")
def home():
    return "Bot V20 Binarias 5m 13,3,3 Activo - usa /test para probar Telegram"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
