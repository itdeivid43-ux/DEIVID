from flask import Flask
import threading, time, requests

app = Flask(__name__)

@app.route('/')
def home():
    return "BOT DEIVID ACTIVO - 7 pares cada 10M"

# TU BOT DE 7 PARES CADA 10M AQUI
def bot_loop():
    while True:
        print("Revisando señales 7 pares...")
        # aqui va tu funcion de señales
        time.sleep(600)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
