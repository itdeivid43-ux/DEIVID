import os, time, threading
from datetime import datetime
import pandas as pd, pytz, yfinance as yf
from flask import Flask
from ta.momentum import RSIIndicator
import requests

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
ECUADOR_TZ = pytz.timezone("America/Guayaquil")

PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "EUR/JPY", "AUD/USD"]
YAHOO_SYMBOLS = {"EUR/USD":"EURUSD=X","GBP/USD":"GBPUSD=X","USD/JPY":"JPY=X","EUR/JPY":"EURJPY=X","AUD/USD":"AUDUSD=X"}

app = Flask(__name__)
@app.route("/")
def home(): return "BOT ACTIVO - HORA REAL", 200
def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def download_candles(pair: str):
    symbol = YAHOO_SYMBOLS[pair]
    data = yf.download(symbol, period="2d", interval="5m", auto_adjust=False, progress=False, threads=False)
    if data.empty: raise ValueError("Sin datos")
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data.columns = [str(c).title() for c in data.columns]
    data = data.rename(columns={"Adj Close":"Close"})
    data = data[["Open","High","Low","Close"]].apply(pd.to_numeric, errors="coerce").dropna()
    return data

def get_signal(pair: str):
    try:
        df = download_candles(pair)
        if len(df) < 60: return None
        rsi = RSIIndicator(close=df["Close"], window=14).rsi().iloc[-1]
        ema = df["Close"].ewm(span=50).mean().iloc[-1]
        close = df["Close"].iloc[-1]
        direction = None
        if rsi <= 30 and close > ema: direction = "COMPRA 🟢 (CALL)"
        elif rsi >= 70 and close < ema: direction = "VENTA 🔴 (PUT)"
        if direction:
            return {"pair":pair,"dir":direction,"rsi":rsi}
    except Exception as e:
        print(f"Error {pair}: {e}")
    return None

def send_telegram(text: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id":TELEGRAM_CHAT_ID,"text":text,"parse_mode":"HTML"}, timeout=15)
    except Exception as e:
        print(f"Telegram error: {e}")

def main_loop():
    print("Bot iniciado - HORA REAL")
    while True:
        try:
            for pair in PAIRS:
                sig = get_signal(pair)
                if sig:
                    hora = datetime.now(ECUADOR_TZ).strftime('%d/%m/%Y %H:%M:%S')
                    msg = f"🔥 SEÑAL BINARIA 5M 🔥\nPar: {sig['pair']}\nDirección: {sig['dir']}\nExpiración: 5 min\nRSI: {sig['rsi']:.2f}\nHora Ecuador: {hora} - EN VIVO"
                    print(msg)
                    send_telegram(msg)
                    time.sleep(180)
                    break
            time.sleep(300)
        except Exception as e:
            print(f"Error loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    main_loop()
