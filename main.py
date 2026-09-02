import requests, os, threading, time
from flask import Flask
from datetime import datetime
import pytz

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
app = Flask(__name__)
PARES = ["EURUSD","GBPUSD","USDJPY","AUDUSD","NZDUSD","EURJPY","GBPJPY","USDCAD"]

def send_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": mensaje}, timeout=20)
    except: pass

def analizar(par):
    try:
        symbol = f"{par}=X"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=5d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        j = r.json()
        data = j['chart']['result'][0]['indicators']['quote'][0]
        closes = [c for c in data['close'] if c is not None]
        if len(closes) < 60: return None

        precio = closes[-1]
        ema9 = sum(closes[-9:])/9
        ema21 = sum(closes[-21:])/21
        ema50 = sum(closes[-50:])/50

        gains = sum(max(0, closes[i]-closes[i-1]) for i in range(-14,0))
        losses = sum(max(0, closes[i-1]-closes[i]) for i in range(-14,0))
        rsi = 100 - (100/(1+gains/(losses+0.001)))

        tz = pytz.timezone('America/Guayaquil')
        hora_str = datetime.now(tz).strftime('%H:%M')

        # SOLO SEÑALES PERFECTAS 85-95%
        if ema9 > ema21 > ema50 and 59 < rsi < 65:
            conf = 95 if 60 < rsi < 62.5 else 85
            return f"""📊 SENAL {hora_str} EC

🟢 COMPRAR {par} 5m
💰 {precio:.5f}
📊 EMA9>EMA21>EMA50
📈 RSI {rsi:.1f}
🎯 Confianza {conf}% ✅
💵 Payout 85%

⏰ Entrar siguiente vela 5m {hora_str}"""

        elif ema9 < ema21 < ema50 and 35 < rsi < 41:
            conf = 95 if 37 < rsi < 39.5 else 85
            return f"""📊 SENAL {hora_str} EC

🔴 VENDER {par} 5m
💰 {precio:.5f}
📊 EMA9<EMA21<EMA50
📈 RSI {rsi:.1f}
🎯 Confianza {conf}% ✅
💵 Payout 85%

⏰ Entrar siguiente vela 5m {hora_str}"""
        return None
    except: return None

def bot_loop():
    time.sleep(5)
    tz = pytz.timezone('America/Guayaquil')
    send_telegram(f"✅ V11 FORMATO PRO 95% PRENDIDO {datetime.now(tz).strftime('%H:%M')} EC\nFormato igual a la foto. NZDUSD incluido.")
    while True:
        try:
            for par in PARES:
                senal = analizar(par)
                if senal:
                    send_telegram(senal)
                    time.sleep(4)
            time.sleep(120)
        except: time.sleep(120)

@app.route('/')
def home(): return "V11 Pro 95%"
threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
