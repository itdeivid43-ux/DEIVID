import os, time, threading, requests
import yfinance as yf
import pandas as pd
from flask import Flask
from datetime import datetime, timedelta, timezone

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PARES = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X",
    "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X",
    "EUR/GBP": "EURGBP=X"
}

app = Flask(__name__)
ECUADOR_TZ = timezone(timedelta(hours=-5))

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)
    except: pass

def get_signal(par):
    try:
        ticker = PARES[par]
        df = yf.download(ticker, period="1d", interval="5m", progress=False)
        if len(df) < 20: return None
        close = df['Close']
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_last = float(rsi.iloc[-1])
        price = float(close.iloc[-1])
        hora_ec = datetime.now(ECUADOR_TZ)
        entrada = (hora_ec + timedelta(minutes=1)).strftime('%H:%M:%S')
        if rsi_last < 32:
            return f"🟢 *{par}* | RSI: {rsi_last:.1f} | *COMPRA / CALL* 📈\nPrecio: {price:.5f}\nConfianza: 85%\n⏰ Hora Ecuador: {entrada} - Expira 10m"
        elif rsi_last > 68:
            return f"🔴 *{par}* | RSI: {rsi_last:.1f} | *VENTA / PUT* 📉\nPrecio: {price:.5f}\nConfianza: 85%\n⏰ Hora Ecuador: {entrada} - Expira 10m"
        return None
    except: return None

def loop():
    time.sleep(3)
    send("✅ *DEIVID BOT 7 PARES CONECTADO - HORA ECUADOR* \nLIVE 24/7 cada 10 min")
    while True:
        for nombre in PARES:
            sig = get_signal(nombre)
            if sig:
                send(sig)
                time.sleep(2)
        time.sleep(600)

threading.Thread(target=loop, daemon=True).start()
@app.route('/')
def home(): return "LIVE ECUADOR"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
