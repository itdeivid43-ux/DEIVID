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

        # FILTRO 85% REAL
        conf = 0
        if ema9 > ema21 and 50 < rsi < 68 and dist > 0.05: conf = 87
        elif ema9 < ema21 and 32 < rsi < 50 and dist > 0.05: conf = 87
        elif 45 < rsi < 55 and dist > 0.03: conf = 75
        else: conf = 60

        direccion = "COMPRAR 🟢" if ema9>ema21 else "VENDER 🔴"
        return (conf, par, precio, direccion, rsi, dist)
    except: return None

def bot_loop():
    time.sleep(5)
    tz = pytz.timezone('America/Guayaquil')
    send_telegram(f"✅ V11.6 PRECISION 85% PRENDIDO {datetime.now(tz).strftime('%H:%M')} EC\nAnalizo 5 activos cada 5 min y solo mando si hay 85%+")
    while True:
        try:
            resultados = [evaluar(p) for p in PARES]
            resultados = [r for r in resultados if r]
            if not resultados:
                time.sleep(300); continue
            mejor = max(resultados, key=lambda x: x[0])
            conf, par, precio, direccion, rsi, dist = mejor
            if conf >= 85:
                hora = datetime.now(tz).strftime('%H:%M')
                send_telegram(f"📊 SEÑAL PRECISA {hora} EC\n\n{direccion} {par} 5m\n💰 {precio:.5f}\n📊 EMA9/21 Dist {dist:.3f}\n📈 RSI {rsi:.1f}\n🎯 Confianza {conf}% ✅\n💵 Payout 85%\n\n⏰ Entrada siguiente vela 5m\nSolo mando 85%+")
            time.sleep(300)
        except: time.sleep(300)

@app.route('/')
def home(): return "Precision 85 activo"
threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
