import os, time, threading
from datetime import datetime
import pandas as pd
import yfinance as yf
from flask import Flask
from ta.momentum import RSIIndicator
import requests
import telebot
import pytz

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
    try:
        symbol = YAHOO_SYMBOLS.get(pair)
        data = yf.download(symbol, period="2d", interval="1m", progress=False)
        if data.empty: return None
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception as e:
        print(f"Error {pair}: {e}")
        return None

def analizar(pair):
    df = download_candles(pair)
    if df is None or len(df) < 20: return None
    df['RSI'] = RSIIndicator(df['Close']).rsi()
    last_rsi = df['RSI'].iloc[-1]
    price = df['Close'].iloc[-1]
    signal = None
    if last_rsi < 30: signal = "CALL 📈"
    elif last_rsi > 70: signal = "PUT 📉"
    if signal:
        hora_ec = datetime.now(ECUADOR_TZ).strftime("%H:%M:%S")
        return f"🚨 SEÑAL {signal}\nPar: {pair}\nPrecio: {price:.5f}\nRSI: {last_rsi:.2f}\nHora EC: {hora_ec}"
    return None

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN) if TELEGRAM_BOT_TOKEN else None

def send_signal(text):
    if TELEGRAM_CHAT_ID and TELEGRAM_BOT_TOKEN:
        try:
            requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={text}")
        except: pass

def loop_senales():
    while True:
        for pair in PAIRS:
            msg = analizar(pair)
            if msg: send_signal(msg)
            time.sleep(5)
        time.sleep(60)

@bot.message_handler(commands=['start','senales'])
def handle_start(m):
    bot.reply_to(m, "BOT ACTIVO ✅\nTe enviaré señales cada minuto.")

def run_bot():
    print("Bot iniciado - HORA REAL")
    bot.infinity_polling()

if __name__ == "__main__":
    threading.Thread(target=loop_senales, daemon=True).start()
    if bot:
        threading.Thread(target=run_bot, daemon=True).start()
    run_web()
