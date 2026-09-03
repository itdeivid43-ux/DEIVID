import os, time, threading, requests
import yfinance as yf
from flask import Flask

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = Flask(__name__)
@app.route('/')
def home():
    return "DEIVID BOT V8 ANTI-BAN LIVE"

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
        print("Telegram -> OK")
    except Exception as e:
        print(f"Error telegram: {e}")

PARES = ["EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","USDCAD=X","EURJPY=X"]

def bot_loop():
    send_telegram("✅ *DEIVID V8 CONECTADO*\nYahoo me había bloqueado, ya lo arreglé. Analizando 1 por 1 para no ser baneado...")
    while True:
        try:
            for par in PARES:
                try:
                    print(f"Descargando {par}...")
                    data = yf.download(par, period="1d", interval="1m", progress=False)
                    print(f"{par} OK: {len(data)} velas")
                    time.sleep(10)  # 10 segundos de descanso entre cada par
                except Exception as e:
                    print(f"Error {par}: {e}")
                    time.sleep(20)
            
            print("Ciclo terminado, descanso 2 min...")
            time.sleep(120)
        except Exception as e:
            print(f"Error loop: {e}")
            time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
