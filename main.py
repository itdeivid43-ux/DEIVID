import os, requests, time, threading
from datetime import datetime
from flask import Flask
import pytz
app = Flask(__name__)
@app.route('/')
def home(): return "BOT BINARIAS FOREX VIVO"
TOKEN=os.getenv("TELEGRAM_BOT_TOKEN"); CHAT_ID=os.getenv("TELEGRAM_CHAT_ID"); API_KEY=os.getenv("TWELVEDATA_API_KEY")
EC=pytz.timezone("America/Guayaquil")
PARES=["EUR/USD","GBP/USD","USD/JPY","AUD/USD","EUR/JPY","GBP/JPY","USD/CHF","EUR/GBP","USD/CAD","NZD/USD"]
def send(t):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":t}, timeout=15)
    except: pass
def get_stoch(par):
    try:
        r=requests.get(f"https://api.twelvedata.com/stoch?symbol={par}&interval=5min&apikey={API_KEY}&k_period=13&d_period=3&slowing=3",timeout=10).json()
        return float(r['values'][0]['k']), float(r['values'][0]['d'])
    except: return None,None
def bot_loop():
    send("✅ BOT BINARIAS FOREX CONECTADO\nSin ORO - 13,3,3 - 35/65")
    while True:
        try:
            ahora=datetime.now(EC); hora=ahora.strftime("%H:%M")
            if 6 <= ahora.hour <= 22:
                for par in PARES:
                    k,d=get_stoch(par)
                    if k is None: continue
                    if k<35 and d<40 and k>d: send(f"🟢 COMPRA BINARIAS 5M\n💱 {par}\n⏰ {hora} EC\n📊 {k:.1f}/{d:.1f}")
                    elif k>65 and d>60 and k<d: send(f"🔴 VENTA BINARIAS 5M\n💱 {par}\n⏰ {hora} EC\n📊 {k:.1f}/{d:.1f}")
                    time.sleep(10)
            time.sleep(300)
        except: time.sleep(10)
threading.Thread(target=bot_loop,daemon=True).start()
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
