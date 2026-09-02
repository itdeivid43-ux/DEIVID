import requests, os, threading, time
from flask import Flask
from datetime import datetime
import pytz

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
app = Flask(__name__)
PARES = ["EURUSD","GBPUSD","USDJPY","AUDUSD","EURJPY","GBPJPY","USDCHF"]

def send_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": mensaje}, timeout=20)
    except: pass

def analizar(par):
    try:
        symbol = f"{par}=X"
        # FIX: Pedimos 5 días para tener 300+ velas
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=5d"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=15)
        j = r.json()
        closes = j['chart']['result'][0]['indicators']['quote'][0]['close']
        closes = [c for c in closes if c is not None]

        if len(closes) < 30:
            return None

        precio = closes[-1]
        ema9 = sum(closes[-9:])/9
        ema21 = sum(closes[-21:])/21
        # RSI simple
        ganancias = sum(max(0, closes[i]-closes[i-1]) for i in range(-14,0))
        perdidas = sum(max(0, closes[i-1]-closes[i]) for i in range(-14,0))
        rsi = 100 - (100/(1+ganancias/(perdidas+0.001)))

        direccion = None
        conf = 0
        if ema9 > ema21 and rsi > 50 and rsi < 75:
            direccion = "COMPRA 🟢"
            conf = 65 + (10 if rsi>60 else 0)
        elif ema9 < ema21 and rsi < 50 and rsi > 25:
            direccion = "VENTA 🔴"
            conf = 65 + (10 if rsi<40 else 0)

        if direccion and conf >= 65:
            return f"""🔥 SEÑAL {conf}%
{par} - {direccion}

⏰ Hora: {datetime.now(pytz.timezone('America/Guayaquil')).strftime('%H:%M')} EC
⏳ Expira: 5 MINUTOS
💰 Entrada: Próxima vela 5M
📊 RSI: {rsi:.1f}

👉 Entra YA en {par}
"""
        return None
    except Exception as e:
        print(e)
        return None

def bot_loop():
    time.sleep(5)
    tz = pytz.timezone('America/Guayaquil')
    send_telegram(f"✅ BOT V7.3 FIX PRENDIDO {datetime.now(tz).strftime('%H:%M')} EC\nAhora si, con datos suficientes. Esperando señales 65%+")

    while True:
        try:
            for par in PARES:
                senal = analizar(par)
                if senal:
                    send_telegram(senal)
                    time.sleep(2)
            time.sleep(60)
        except: time.sleep(60)

@app.route('/')
def home(): return "Deivid V7.3 Live"
threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
