import os, time, threading, requests
from flask import Flask
from datetime import datetime
import pytz
app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TD_API_KEY = os.getenv("TD_API_KEY")
SYMBOL = "BTC/USD"
INTERVAL = "5min"
ultima_senal = ""
def hora_ec():
    return datetime.now(pytz.timezone("America/Guayaquil")).strftime("%H:%M:%S")
def send(msg):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
def get_emas():
    try:
        r = requests.get(f"https://api.twelvedata.com/ema?symbol={SYMBOL}&interval={INTERVAL}&apikey={TD_API_KEY}&period=21&series_type=close").json()
        ema21 = float(r["values"][0]["ema"])
        r2 = requests.get(f"https://api.twelvedata.com/ema?symbol={SYMBOL}&interval={INTERVAL}&apikey={TD_API_KEY}&period=8&series_type=close").json()
        ema8 = float(r2["values"][0]["ema"])
        return ema8, ema21
    except: return None, None
@app.route("/")
def home(): return f"BOT V28 5M LIVE - {hora_ec()}"
def loop_v28():
    global ultima_senal
    while True:
        try:
            ema8, ema21 = get_emas()
            if not ema8: time.sleep(60); continue
            senal = "COMPRA" if ema8 > ema21 else "VENTA"
            if senal!= ultima_senal:
                ultima_senal = senal
                send(f"🔥 V28 {INTERVAL} - {senal} - {hora_ec()}")
            time.sleep(60)
        except: time.sleep(30)
threading.Thread(target=loop_v28, daemon=True).start()
