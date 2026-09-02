import requests, os, threading, time
from flask import Flask
from datetime import datetime
import pytz

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
app = Flask(__name__)
PARES = ["EURUSD","GBPUSD","USDJPY","AUDUSD","NZDUSD","EURJPY","GBPJPY"]

def send_telegram(m):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": m}, timeout=15)
    except: pass

def analizar(par):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{par}=X?interval=5m&range=5d"
        closes = [c for c in requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()['chart']['result'][0]['indicators']['quote'][0]['close'] if c is not None]
        if len(closes) < 60: return None
        precio = closes[-1]
        ema9 = sum(closes[-9:])/9
        ema21 = sum(closes[-21:])/21
        ema50 = sum(closes[-50:])/50
        gains = sum(max(0, closes[i]-closes[i-1]) for i in range(-14,0))
        losses = sum(max(0, closes[i-1]-closes[i]) for i in range(-14,0))
        rsi = 100 - (100/(1+gains/(losses+0.001)))

        # FILTRO NUEVO: si esta pegado a soporte/resistencia no manda
        if precio > max(closes[-20:])*0.999 or precio < min(closes[-20:])*1.001:
            return None

        hora = datetime.now(pytz.timezone('America/Guayaquil')).strftime('%H:%M')
        if ema9 > ema21 > ema50 and 60 < rsi < 64:
            conf = 95 if 61 < rsi < 62.5 else 85
            return f"📊 SENAL {hora} EC\n\n🟢 COMPRAR {par} 5m\n💰 {precio:.5f}\n📊 EMA9>EMA21>EMA50\n📈 RSI {rsi:.1f}\n🎯 Confianza {conf}% ✅\n💵 Payout 85%\n\n⏰ Entrar siguiente vela 5m {hora}"
        if ema9 < ema21 < ema50 and 36 < rsi < 40:
            conf = 95 if 37 < rsi < 39 else 85
            return f"📊 SENAL {hora} EC\n\n🔴 VENDER {par} 5m\n💰 {precio:.5f}\n📊 EMA9<EMA21<EMA50\n📈 RSI {rsi:.1f}\n🎯 Confianza {conf}% ✅\n💵 Payout 85%\n\n⏰ Entrar siguiente vela 5m {hora}"
        return None
    except: return None

def bot_loop():
    time.sleep(5)
    tz = pytz.timezone('America/Guayaquil')
    send_telegram(f"✅ V11.5 SIGUE MANDANDO {datetime.now(tz).strftime('%H:%M')} EC\nSigue activo toda la noche con filtro anti-soporte.")
    while True:
        try:
            for par in PARES:
                s = analizar(par)
                if s:
                    send_telegram(s)
                    time.sleep(4)
            time.sleep(120)
        except: time.sleep(120)

@app.route('/')
def home(): return "V11.5 activo"
threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
