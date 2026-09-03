import time, threading, requests
from flask import Flask

BOT_TOKEN = "8962914647:AAG5pHw1oF-HHIDKNRYD_U4dWxYFbC-WYVk"
CHAT_ID = "5890249548"

def send(msg):
    try:
        r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
        print(f"Telegram: {r.text}")
    except Exception as e:
        print(e)

def bot_loop():
    send("✅ DEIVID BOT CONECTADO - Ya funciona!")
    offset = 0
    while True:
        try:
            resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=10", timeout=15).json()
            for upd in resp.get("result", []):
                offset = upd["update_id"]+1
                txt = upd.get("message",{}).get("text","").lower()
                if "start" in txt or "hola" in txt:
                    send("🚀 Hola Deivid! Bot activo.")
            time.sleep(2)
        except:
            time.sleep(5)

threading.Thread(target=bot_loop, daemon=True).start()
app = Flask(__name__)
@app.route('/')
def home(): return "LIVE"
app.run(host="0.0.0.0", port=10000)
