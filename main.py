import os, time, threading, requests
import yfinance as yf
from flask import Flask
app = Flask(__name__)
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PARES = ["EURUSD=X","GBPUSD=X","USDJPY=X"]
def send(m):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":m})
def analizar(ticker):
    df = yf.download(ticker, period="1d", interval="5m", progress=False)
    close = df['Close']
    rsi = 100 - (100/(1+close.diff().where(lambda x: x>0,0).rolling(14).mean() / -close.diff().where(lambda x: x<0,0).rolling(14).mean()))
    r = float(rsi.iloc[-1])
    p = float(close.iloc[-1])
    if r < 40: return f"COMPRAR {ticker} 5m RSI {round(r,1)} precio {p}"
    if r > 60: return f"VENDER {ticker} 5m RSI {round(r,1)} precio {p}"
    return None
def loop():
    time.sleep(10)
    send("BOT 5M ONLINE")
    while True:
        for t in PARES:
            s = analizar(t)
            if s: send(s)
        time.sleep(300)
@app.route("/")
def home(): return "LIVE 5M"
threading.Thread(target=loop, daemon=True).start()
