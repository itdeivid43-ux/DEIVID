import requests, os, threading, time
from flask import Flask
from datetime import datetime
import pytz

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
app = Flask(__name__)

PARES = ["AUDCAD","AUDCHF","AUDJPY","AUDNZD","AUDUSD","CADCHF","CADJPY","CHFJPY","EURAUD","EURCAD","EURCHF","EURGBP","EURJPY","EURNZD","EURUSD","GBPAUD","GBPCAD","GBPCHF","GBPJPY","GBPNZD","GBPUSD","NZDCAD","NZDCHF","NZDJPY","NZDUSD","USDCAD","USDCHF","USDJPY"]

lateral_count = 0

def send_telegram(mensaje):
    try:
        if not TOKEN or not CHAT_ID:
            print("ERROR: FALTA TOKEN O CHAT_ID EN RENDER")
            return
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
        r = requests.post(url, data=data, timeout=20)
        print(f"Telegram -> {r.status_code} {r.text[:100]}")
    except Exception as e:
        print(f"Error telegram: {e}")

def analizar(par):
    try:
        symbol = f"{par}=X"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=1d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()
        closes = r['chart']['result'][0]['indicators']['quote'][0]['close']
        closes = [c for c in closes if c is not None]
        if len(closes) < 50:
            return None, None
        precio = closes[-1]
        ema9 = sum(closes[-9:])/9
        ema21 = sum(closes[-21:])/21
        ema50 = sum(closes[-50:])/50

        if ema9 > ema21 > ema50 and precio > ema9:
            return "SENAL", f"🟢 *{par} COMPRA* - Tendencia Alcista"
        elif ema9 < ema21 < ema50 and precio < ema9:
            return "SENAL", f"🔴 *{par} VENTA* - Tendencia Bajista"
        else:
            return "LATERAL", par
    except Exception as e:
        print(f"Error {par}: {e}")
        return None, None

def bot_loop():
    global lateral_count
    time.sleep(5)
    send_telegram(f"✅ *BOT DEIVID V7 PRENDIDO* ✅\n\nEstoy LIVE en Render\nHora EC: {datetime.now(pytz.timezone('America/Guayaquil')).strftime('%H:%M')}\n\nBuscando señales cada 2 min...")

    while True:
        try:
            tz_ec = pytz.timezone('America/Guayaquil')
            hora_ec = datetime.now(tz_ec)
            hora_str = hora_ec.strftime("%H:%M")
            print(f"--- Analizando {hora_str} EC ---")

            if 5 <= hora_ec.hour <= 23:
                senales = 0
                laterales = []
                for par in PARES:
                    tipo, msg = analizar(par)
                    if tipo == "SENAL":
                        send_telegram(f"🔥 *SEÑAL {hora_str} EC*\n\n{msg}\n\n⏰ Entrar siguiente vela 5m")
                        senales += 1
                        time.sleep(3)
                        if senales >= 2:
                            break
                    elif tipo == "LATERAL":
                        laterales.append(par)

                if senales == 0:
                    lateral_count += 1
                    print(f"Sin señales. Laterales: {len(laterales)} - Contador: {lateral_count}")
                    if lateral_count >= 5:
                        send_telegram(f"📊 *MERCADO LATERAL {hora_str} EC*\n\n{len(laterales)}/28 pares sin dirección. Esperando tendencia...")
                        lateral_count = 0
                else:
                    lateral_count = 0
            else:
                print("Fuera de horario")

            time.sleep(120)
        except Exception as e:
            print(f"Error loop: {e}")
            time.sleep(60)

@app.route('/')
def home():
    return "Bot Activo - Deivid V7 - LIVE"

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
