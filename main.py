import os, time, threading, requests
import yfinance as yf
import pandas as pd
from flask import Flask
from datetime import datetime, timedelta

BOT_TOKEN = "8962914647:AAG5pHw1oF-HHIDKNRYD_U4dWxYFbC-WYVk"
CHAT_ID = "5890249548"

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

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)
        print(f"Enviado: {msg[:50]}")
    except Exception as e:
        print(f"Error: {e}")

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
        if rsi_last < 32:
            return f"🟢 *{par}* | RSI: {rsi_last:.1f} | *COMPRA / CALL* 📈\nPrecio: {price:.5f}\nConfianza: 85%\n⏰ Entrada: {(datetime.now()+timedelta(minutes=1)).strftime('%H:%M:%S')} - Expira 10m"
        elif rsi_last > 68:
            return f"🔴 *{par}* | RSI: {rsi_last:.1f} | *VENTA / PUT* 📉\nPrecio: {price:.5f}\nConfianza: 85%\n⏰ Entrada: {(datetime.now()+timedelta(minutes=1)).strftime('%H:%M:%S')} - Expira 10m"
        return None
    except Exception as e:
        print(f"Error {par}: {e}")
        return None

def loop():
    print("Bot 7 pares 10min iniciado")
    time.sleep(3)
    send("✅ *DEIVID BOT 7 PARES CONECTADO* \nEstoy LIVE 24/7\n⏰ Señales cada 10 minutos")
    while True:
        for nombre in PARES:
            sig = get_signal(nombre)
            if sig:
                send(sig)
                time.sleep(2)
        print("Ciclo terminado, esperando 10 min...")
        time.sleep(600)

threading.Thread(target=loop, daemon=True).start()

@app.route('/')
def home(): return "DEIVID 7 PARES 10MIN LIVE"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
