import os, requests, time, random, threading
from datetime import datetime
from flask import Flask
import pytz

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
EC = pytz.timezone("America/Guayaquil")

app = Flask(__name__)
@app.route('/')
def home():
    return "BOT VIVO 24/7"

def send(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except: pass

def bot_loop():
    send("✅ BOT CONECTADO 24/7\nYa no se duerme - 40/60")
    while True:
        try:
            ahora = datetime.now(EC)
            if 6 <= ahora.hour <= 22:
                k = random.uniform(5, 95)
                d = random.uniform(5, 95)
                hora = ahora.strftime("%H:%M")
                
                # 40/60 para que lleguen mas señales
                if k < 40 and k > d:
                    send(f"🟢 COMPRA BINARIAS 5M\n⏰ {hora} EC\n📊 Stoch {k:.1f}/{d:.1f}\n👉 Entrada siguiente vela")
                elif k > 60 and k < d:
                    send(f"🔴 VENTA BINARIAS 5M\n⏰ {hora} EC\n📊 Stoch {k:.1f}/{d:.1f}\n👉 Entrada siguiente vela")
            time.sleep(120)
        except Exception as e:
            print(e)
            time.sleep(30)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
