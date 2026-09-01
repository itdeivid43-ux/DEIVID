import os, time, threading, pytz
from datetime import datetime
import yfinance as yf
import ta
import telebot
from flask import Flask

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(TOKEN) if TOKEN else None
app = Flask(__name__)

PARES = ["EURUSD=X", "GBPUSD=X", "AUDUSD=X", "USDJPY=X", "BTC-USD", "ETH-USD"]
ultima_senal = {}

def obtener_rsi(par):
    try:
        df = yf.download(par, period="1d", interval="5m", progress=False)
        if len(df) < 20: return None, None
        close = df['Close']
        rsi = ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1]
        precio = float(close.iloc[-1])
        return round(rsi,2), precio
    except:
        return None, None

def es_buena_senal(rsi):
    if rsi <= 30: return "COMPRA 🟢", "SOBREVENTA"
    if rsi >= 70: return "VENTA 🔴", "SOBRECOMPRA"
    return None, None

def loop_senales():
    print("Bot 5M iniciado - COMPRA/VENTA")
    while True:
        try:
            for par in PARES:
                rsi, precio = obtener_rsi(par)
                if rsi is None: continue
                tipo, motivo = es_buena_senal(rsi)
                if not tipo: continue
                if par in ultima_senal and time.time() - ultima_senal[par] < 600:
                    continue
                hora_ec = datetime.now(pytz.timezone("America/Guayaquil")).strftime("%H:%M:%S")
                nombre = par.replace("=X","").replace("-USD","/USD")
                mensaje = f"""🚨 SEÑAL 5M - {tipo} 🚨
Par: {nombre}
Acción: {tipo}
Temporalidad: 5M ⏱️
Precio: {precio}
RSI (5m): {rsi}
Motivo: {motivo}
Hora EC: {hora_ec}
Expiración: 5 MINUTOS ✅"""
                if bot and CHAT_ID:
                    bot.send_message(CHAT_ID, mensaje)
                    ultima_senal[par] = time.time()
                    print(f"Señal 5M enviada: {par} {tipo}")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(60)

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "BOT 5M ACTIVO ✅\nSeñales COMPRA/VENTA\nTemporalidad: 5 minutos")

def run_bot():
    if bot: bot.infinity_polling()

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))

@app.route("/")
def home(): return "Bot DEIVID 5M"

if __name__ == "__main__":
    threading.Thread(target=loop_senales, daemon=True).start()
    threading.Thread(target=run_bot, daemon=True).start()
    run_web()
