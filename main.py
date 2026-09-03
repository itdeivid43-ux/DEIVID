import os, time, threading, requests
import yfinance as yf
from flask import Flask

app = Flask(__name__)

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PARES = ["EURUSD=X","GBPUSD=X","USDJPY=X"]

def send(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": m, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def analizar(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="5m", progress=False, auto_adjust=True)
        if len(df) < 30: return None
        close = df['Close']
        # RSI simple
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        r = float(rsi.iloc[-1])
        p = float(close.iloc[-1])
        if r < 40:
            return f"*COMPRAR {ticker.replace('=X','')} 5m* RSI {round(r,1)} Precio {p}"
        elif r > 60:
            return f"*VENDER {ticker.replace('=X','')} 5m* RSI {round(r,1)} Precio {p}"
        return None
    except:
        return None

def loop():
    time.sleep(10)
    send("✅ *DEIVID BOT 5M ONLINE*")
    while True:
        for par in PARES:
            s = analizar(par)
            if s:
                send(s)
                time.sleep(2)
        time.sleep(300)

@app.route("/")
def home():
    return "DEIVID BOT LIVE 5M"

threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
