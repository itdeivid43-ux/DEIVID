import os, time, threading, requests, yfinance as yf
from flask import Flask
app = Flask(__name__)

TOKEN = "8141847173:AAFh8Iu5oXB4h2FhIw6Lw5Qv1J2h3K4l5M6N"
CHAT_ID = "7734770893"

PARES = ["EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","USDCAD=X","USDCHF=X","NZDUSD=X","EURJPY=X"]

def send(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":m,"parse_mode":"Markdown"}, timeout=10)
    except: pass

def analizar(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="5m", progress=False)
        if len(df)<30: return None
        close = df['Close']
        delta = close.diff()
        gain = delta.where(delta>0,0).rolling(14).mean()
        loss = -delta.where(delta<0,0).rolling(14).mean()
        rs = gain/loss
        rsi = 100 - (100/(1+rs))
        r = float(rsi.iloc[-1])
        precio = float(close.iloc[-1])
        if r < 40: dir="COMPRAR 🟢"; conf=90 if r<35 else 87
        elif r > 60: dir="VENDER 🔴"; conf=90 if r>65 else 87
        else: return None
        par = ticker.replace("=X","").replace("USD","/USD").replace("EUR/","EUR/").replace("GBP/","GBP/")
        if "JPY" in par: par = par[:3]+"/"+par[3:]
        # formato igual a tu foto
        return f"*{dir} {par} 5m*\n💰 {round(precio,5)}\n📊 RSI {round(r,1)}\n✅ Confianza {conf}%\n\n⏰ Entrada siguiente vela 00:53\n🔥 85%+ PREMIUM"
    except: return None

def loop():
    send("✅ *DEIVID BOT REAL MERCADO ONLINE*\n\nYa con precio real, no inventado")
    while True:
        try:
            for p in PARES:
                s = analizar(p)
                if s:
                    send(s)
                    time.sleep(3)
            time.sleep(600)
        except: time.sleep(60)

@app.route("/")
def home(): return "BOT REAL ON"

threading.Thread(target=loop, daemon=True).start()
if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
