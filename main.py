import os, time, threading, requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = Flask(__name__)
@app.route('/')
def home():
    return "DEIVID V10.1 - HORA ECUADOR LIVE"

def hora_ecuador():
    # Ecuador UTC-5 sin horario de verano
    utc_now = datetime.utcnow()
    ecuador = utc_now - timedelta(hours=5)
    return ecuador.strftime("%H:%M:%S - %d/%m/%Y")

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=15)
    except: pass

PARES = {
    "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "USDJPY=X",
    "AUDUSD": "AUDUSD=X", "EURJPY": "EURJPY=X", "GBPJPY": "GBPJPY=X",
    "XAUUSD": "GC=F"
}

def señal_90(df):
    if len(df) < 50: return None
    c = df['Close']
    e9 = c.ewm(span=9).mean().iloc[-1]
    e21 = c.ewm(span=21).mean().iloc[-1]
    e50 = c.ewm(span=50).mean().iloc[-1]
    delta = c.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    rsi = 100 - (100 / (1 + (gain/loss)))
    rsi_last = rsi.iloc[-1]
    last = c.iloc[-1]
    if last > e9 > e21 > e50 and 58 < rsi_last < 78:
        return "COMPRA 📈", round(rsi_last,1)
    if last < e9 < e21 < e50 and 22 < rsi_last < 42:
        return "VENTA 📉", round(rsi_last,1)
    return None

def bot_loop():
    send_telegram(f"✅ *DEIVID V10.1 CONECTADO - HORA ECUADOR*\n\n🕐 Hora: {hora_ecuador()}\n⏰ Señales cada 10 min\n🎯 7 PARES BINARIAS\n\nListo 24/7")
    
    while True:
        try:
            for nombre, symbol in PARES.items():
                try:
                    df = yf.download(symbol, period="1d", interval="1m", progress=False, auto_adjust=True)
                    if df.empty: time.sleep(12); continue
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    res = señal_90(df)
                    if res:
                        dir, rsi = res
                        msg = f"🔔 *SEÑAL {nombre} - {dir}*\n\n⏰ Expira: 5 MIN\n🕐 Hora Ecuador: {hora_ecuador()}\n📊 RSI: {rsi}\n💰 Entrada: AHORA\n\nDEIVID BOT V10.1"
                        send_telegram(msg)
                    time.sleep(12)
                except:
                    time.sleep(15)
            print(f"Ciclo terminado {hora_ecuador()} - esperando 10 min")
            time.sleep(600)
        except:
            time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
