import os, time, threading, requests
from flask import Flask
import yfinance as yf

app = Flask(__name__)

TOKEN = "8141847173:AAFh8Iu5oXB4h2FhIw6Lw5Qv1J2h3K4l5M6N"
CHAT_ID = "7734770893"

def send(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)
    except Exception as e:
        print(e)

def bot():
    send("✅ *DEIVID BOT REAL 10M ONLINE*\n\nEstoy vivo y analizando")
    while True:
        try:
            time.sleep(600)
            send("🔥 *SEÑAL PRUEBA* 🔥\n\nPar: EUR/USD\nDirección: COMPRA 🟢\nConfianza: 87%\nTiempo: 5M")
        except:
            time.sleep(60)

@app.route("/")
def home():
    return "DEIVID BOT ONLINE"

threading.Thread(target=bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
