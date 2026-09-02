import requests, os, threading, time
from flask import Flask
from datetime import datetime
import pytz
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
app = Flask(__name__)
PARES = ["EURUSD","GBPUSD","USDJPY","AUDUSD","XAUUSD"]

def send_telegram(m):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": m}, timeout=15)
    except: pass

def evaluar(par):
    try:
        symbol = "GC=F" if par=="XAUUSD" else f"{par}=X"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        closes = [c for c in requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()['chart']['result'][0]['indicators']['quote'][0]['close'] if c is not None]
        if len(closes)<30: return None
        precio = closes[-1]
        ema9 = sum(closes[-9:])/9
        ema21 = sum(closes[-21:])/21
        gains = sum(max(0, closes[i]-closes[i-1]) for i in range(-14,0))
        losses = sum(max(0, closes[i-1]-closes[i]) for i in range(-14,0))
        rsi = 100 - (100/(1+gains/(losses+0.001)))
        dist = abs(ema9-ema21)/precio*1000

        if ema9 > ema21 and 52 < rsi < 67 and dist > 0.06: conf = 87
        elif ema9 < ema21 and 33 < rsi < 48 and dist > 0.06: conf = 87
        elif 48 < rsi < 68 and dist > 0.04 or 32 < rsi < 52 and dist > 0.04: conf = 72
        else: conf = 55

        direccion = "COMPRAR 🟢" if ema9>ema21 else "VENDER 🔴"
        if conf >= 85: tag = "🔥 85%+ PREMIUM"
        elif conf >= 70: tag = "✅ 70% BUENA"
        else: return None

        return (conf, f"{tag} {datetime.now(pytz.timezone('America/Guayaquil')).strftime('%H:%M')} EC\n\n{direccion} {par} 5m\n💰 {precio:.5f}\n📈 RSI {rsi:.1f}\n🎯 Confianza {conf}%\n\n⏰ Entrada siguiente vela")
    except: return None

def bot_loop():
    time.sleep(5)
    tz = pytz.timezone('America/Guayaquil')
    send_telegram(f"✅ V11.8 70% y 85% PRENDIDO {datetime.now(tz).strftime('%H:%M')} EC\nCada 5 min analizo 5 activos\n70% = entrada normal\n85% = entrada premium")
    while True:
        try:
            res = [evaluar(p) for p in PARES]
            res = [r for r in res if r]
            if res:
                mejor = max(res, key=lambda x: x[0])
                send_telegram(mejor[1])
            time.sleep(300)
        except: time.sleep(300)

@app.route('/')
def home(): return "70 y 85"
threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
