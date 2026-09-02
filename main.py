import requests, os, threading, time
from flask import Flask
from datetime import datetime
import pytz

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
app = Flask(__name__)
PARES = ["EURUSD","GBPUSD","USDJPY","AUDUSD","EURJPY","GBPJPY","USDCHF","EURGBP"]

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
        closes = j['chart']['result'][0]['indicators']['quote'][0]['close']
        highs = j['chart']['result'][0]['indicators']['quote'][0]['high']
        lows = j['chart']['result'][0]['indicators']['quote'][0]['low']
        closes = [c for c in closes if c is not None]
        if len(closes) < 30: return None

        precio = closes[-1]
        ema9 = sum(closes[-9:])/9
        ema21 = sum(closes[-21:])/21
        ema50 = sum(closes[-50:])/50

        # RSI
        gains = sum(max(0, closes[i]-closes[i-1]) for i in range(-14,0))
        losses = sum(max(0, closes[i-1]-closes[i]) for i in range(-14,0))
        rs = gains/(losses+0.001)
        rsi = 100 - (100/(1+rs))

        # FILTRO V8: Evitar mechas gigantes y tendencia débil
        body = abs(closes[-1]-closes[-2])
        wick = highs[-1]-lows[-1]
        if wick > body*3: # Vela con mucha mecha = no entrar
            return None

        direccion = None
        conf = 0

        # COMPRA FUERTE - Solo si está por encima de EMA50 y RSI no sobrecomprado
        if ema9 > ema21 and closes[-1] > ema50 and 55 < rsi < 72:
            direccion = "COMPRA 🟢"
            conf = 70 + (5 if rsi>60 else 0) + (5 if ema9>ema50 else 0)

        # VENTA FUERTE - Solo si está por debajo de EMA50 y RSI no sobrevendido
        elif ema9 < ema21 and closes[-1] < ema50 and 28 < rsi < 45:
            direccion = "VENTA 🔴"
            conf = 70 + (5 if rsi<38 else 0) + (5 if ema9<ema50 else 0)

        if direccion and conf >= 70:
            return f"""🔥 SEÑAL V8 {conf}%
{par} - {direccion}

⏰ Hora: {datetime.now(pytz.timezone('America/Guayaquil')).strftime('%H:%M')} EC
⏳ Expira: 5 MINUTOS
💰 Entrada: Próxima vela 5M
📊 RSI: {rsi:.1f} | Tendencia: Fuerte

👉 Entra YA en {par} con 1$
"""
        return None
    except: return None

def bot_loop():
    time.sleep(5)
    tz = pytz.timezone('America/Guayaquil')
    send_telegram(f"✅ BOT V8 PRO 70%+ PRENDIDO {datetime.now(tz).strftime('%H:%M')} EC\nFiltros: Sin mechas, solo tendencia fuerte. Menos señales, más aciertos.")
    while True:
        try:
            for par in PARES:
                senal = analizar(par)
                if senal:
                    send_telegram(senal)
                    time.sleep(3)
            time.sleep(90) # Revisa cada 90 seg, no cada 60 para no spamear
        except: time.sleep(90)

@app.route('/')
def home(): return "Deivid V8 Pro Live"
threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
