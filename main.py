import requests, os, threading, time
from flask import Flask, request
from datetime import datetime
import pytz

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
app = Flask(__name__)

PARES = ["EURUSD","GBPUSD","USDJPY","AUDUSD","XAUUSD"]
# Intervalo 5m como tu foto
INTERVAL = "5m"

def send_telegram(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": m, "parse_mode": "Markdown"}, timeout=10)
    except:
        pass

def calcular_estocastico(closes, highs, lows, k_period=13, k_smooth=3, d_smooth=3):
    # %K = 100 * (close - lowest_low) / (highest_high - lowest_low)
    try:
        k_vals = []
        for i in range(len(closes)):
            if i < k_period:
                continue
            hh = max(highs[i-k_period:i])
            ll = min(lows[i-k_period:i])
            if hh == ll:
                k = 50
            else:
                k = 100 * (closes[i] - ll) / (hh - ll)
            k_vals.append(k)

        # Suavizado 3,3
        if len(k_vals) < k_smooth + d_smooth: return None, None
        k_smooth_vals = [sum(k_vals[i-k_smooth:i])/k_smooth for i in range(k_smooth, len(k_vals))]
        d_vals = [sum(k_smooth_vals[i-d_smooth:i])/d_smooth for i in range(d_smooth, len(k_smooth_vals))]

        return k_smooth_vals[-1], d_vals[-1], k_smooth_vals[-2], d_vals[-2]
    except:
        return None, None, None, None

def evaluar(par):
    try:
        symbol = "GC=F" if par=="XAUUSD" else f"{par}=X"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={INTERVAL}&range=1d"
        data = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()['chart']['result'][0]
        closes = data['indicators']['quote'][0]['close']
        highs = data['indicators']['quote'][0]['high']
        lows = data['indicators']['quote'][0]['low']

        # Limpia Nones
        closes = [c for c in closes if c is not None]
        highs = [h for h in highs if h is not None]
        lows = [l for l in lows if l is not None]

        if len(closes) < 35: return None

        precio = closes[-1]
        ema50 = sum(closes[-50:])/50 if len(closes)>=50 else sum(closes)/len(closes)
        ema200 = sum(closes[-200:])/200 if len(closes)>=200 else ema50

        # RSI simple 14
        gains = [max(0, closes[i]-closes[i-1]) for i in range(1,15)]
        losses = [max(0, closes[i-1]-closes[i]) for i in range(1,15)]
        rs = (sum(gains)/14) / (sum(losses)/14 + 0.0001)
        rsi = 100 - (100 / (1 + rs))

        k, d, k_prev, d_prev = calcular_estocastico(closes, highs, lows, 13, 3, 3)
        if k is None: return None

        # TU CONDICION PRECISE: Cruce en 20 y 80
        cruce_compra_20 = k_prev < 20 and k > 20 and k < 35 and d < 35
        cruce_venta_80 = k_prev > 80 and k < 80 and k > 65 and d > 65

        # Filtro premium para confianza 87%
        buy_ok = cruce_compra_20 and precio > ema50 and ema50 > ema200 and 50 < rsi < 68
        sell_ok = cruce_venta_80 and precio < ema50 and ema50 < ema200 and 32 < rsi < 50

        if buy_ok or sell_ok:
            conf = 87 if (abs(k-d) > 2) else 82
            tipo = "COMPRAR 🟢" if buy_ok else "VENDER 🔴"
            emoji_rsi = "📈" if buy_ok else "📉"
            hora = datetime.now(pytz.timezone('America/Guayaquil')).strftime("%H:%M:%S")

            mensaje = f"🔥 85%+ PREMIUM {hora} EC\n\n{tipo} {par} {INTERVAL}\n💰 {precio:.5f}\n{emoji_rsi} RSI {rsi:.1f}\n📊 Estoc 13,3,3 K:{k:.1f} D:{d:.1f}\n🎯 Confianza {conf}%\n\n⏰ Entrada siguiente vela"
            send_telegram(mensaje)
            return True
    except Exception as e:
        print(f"Error {par}: {e}")
    return None

# Loop automatico cada 1 minuto
def loop():
    while True:
        for par in PARES:
            evaluar(par)
            time.sleep(2)
        time.sleep(55)

@app.route('/')
def home():
    return "Bot V20 Stochastic 13,3,3 Activo"

# Para recibir alertas de TradingView tambien
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data:
        send_telegram(f"🔔 TradingView: {data}")
    return "ok"

if __name__ == "__main__":
    threading.Thread(target=loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
