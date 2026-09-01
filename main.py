import yfinance as yf
import requests
import time
import os
from flask import Flask
import threading

TOKEN = "8962914647:AAHFuFSg14UM4zkdJgVdgiI5n41tr6-5E80"
CHAT_ID = "6273812557"

print(f"TOKEN INICIO: {TOKEN[:10]}...")
print(f"CHAT_ID: {CHAT_ID}")
print("BOT INICIANDO...")

def send_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mensaje}
        r = requests.post(url, data=data, timeout=10)
        print(f"TELEGRAM -> {r.status_code} | {r.text[:100]}")
        return r
    except Exception as e:
        print(f"ERROR TELEGRAM: {e}")

def analizar():
    try:
        btc = yf.Ticker("BTC-USD").history(period="1d", interval="1m")
        precio = btc['Close'].iloc[-1]
        return f"BTC: ${precio:.2f} - Bot de prueba funcionando!"
    except Exception as e:
        return f"Error: {e}"

def bot_loop():
    send_telegram("✅ Bot DEIVID conectado y funcionando en Render!")
    while True:
        try:
            msg = analizar()
            send_telegram(msg)
            time.sleep(60)
        except Exception as e:
            print(f"Error loop: {e}")
            time.sleep(10)

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot DEIVID activo!"

if __name__ == '__main__':
    t = threading.Thread(target=bot_loop, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=10000)
