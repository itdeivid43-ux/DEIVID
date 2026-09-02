import os, requests, time, threading
from datetime import datetime
from flask import Flask
import pytz

app = Flask(__name__)
@app.route('/')
def home(): return "BOT BINARIAS 28 PARES 13,3,3 LIVE"

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVEDATA_API_KEY")
EC = pytz.timezone("America/Guayaquil")

PARES = ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","EUR/JPY","GBP/JPY","USD/CHF","EUR/GBP","USD/CAD","NZD/USD","EUR/AUD","GBP/CAD","AUD/CAD","AUD/CHF","AUD/JPY","AUD/NZD","CAD/CHF","CAD/JPY","CHF/JPY","EUR/CAD","EUR/CHF","EURNZD","GBPAUD","GBPCHF","GBPNZD","NZDCAD","NZDCHF","NZDJPY"]

def send(t):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": t}, timeout=15)
    except: pass

def get_stoch(par):
    try:
        url = f"https://api.twelvedata.com/stoch?symbol={par}&interval=5min&apikey={API_KEY}&k_period=13&d_period=3&slowing=3"
        r = requests.get(url, timeout=15).json()
        k = float(r['values'][0]['k'])
        d = float(r['values'][0]['d'])
        return k, d
    except:
        return None, None

def bot_loop():
    send("✅ BOT 28 PARES 13,3,3 CONECTADO\nFiltro 35/65 listo")
    while True:
        try:
            ahora = datetime.now(EC)
            hora = ahora.strftime("%H:%M")
            if 6 <= ahora.hour <= 22:
                for par in PARES:
                    k, d = get_stoch(par)
                    if k is None: continue
                    if k < 35 and d < 40 and k > d and (k - d) > 0.8:
                        send(f"🟢 COMPRA 5M {par}\n⏰ {hora} EC\n📊 Stoch 13,3,3 {k:.1f}/{d:.1f}\n✅ Cruce fuerte")
                    elif k > 65 and d > 60 and k < d and (d - k) > 0.8:
                        send(f"🔴 VENTA 5M {par}\n⏰ {hora} EC\n📊 Stoch 13,3,3 {k:.1f}/{d:.1f}\n✅ Cruce fuerte")
                    time.sleep(8)
            time.sleep(300)
        except:
            time.sleep(10)

threading.Thread(target=bot_loop, daemon=True).start()
