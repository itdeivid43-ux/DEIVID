import os, time, threading, requests
import yfinance as yf
from flask import Flask

app = Flask(__name__)

# TUS DATOS REALES - YA ARREGLADO
TOKEN = "8141847173:AAFh8Iu5oXB4h2FhIw6Lw5Qv1J2h3K415M6N"
CHAT_ID = "7734770893"
PARES = ["EURUSD=X", "GBPUSD=X", "USDJPY=X"]

def send(m):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": m, "parse_mode": "Markdown"}, timeout=15)
    except Exception as e:
        print(f"Error send: {e}")

def analizar(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="5m", progress=False, auto_adjust=True)
        if len(df) < 30: return None
        close = df['Close']
        delta = close.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        r = float(rsi.iloc[-1])
        p = float(close.iloc[-1])
        nombre = ticker.replace("=X","")
        if r < 40:
            return f"📈 *COMPRAR {nombre} 5m*\n💰 Precio: {round(p,5)}\n📊 RSI: {round(r,1)}\n⏰ 5 min"
        if r > 60:
            return f"📉 *VENDER {nombre} 5m*\n💰 Precio: {round(p,5)}\n📊 RSI: {round(r,1)}\n⏰ 5 min"
        return None
    except Exception as e:
        print(e)
        return None

def loop():
    print("Iniciando bot...")
    time.sleep(10)
    send("✅ *DEIVID BOT REAL ONLINE*\nEl bot ya está funcionando y te mandará señales cada 5 minutos")
    while True:
        for par in PARES:
            senal = analizar(par)
            if senal:
                send(senal)
                time.sleep(2)
        time.sleep(300)

@app.route("/")
def home():
    return "DEIVID BOT LIVE - OK"

threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
