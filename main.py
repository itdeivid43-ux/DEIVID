import requests, os, threading, time, random
from flask import Flask
from datetime import datetime
import pytz

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
app = Flask(__name__)

PARES = ["AUDCAD","AUDCHF","AUDJPY","AUDNZD","AUDUSD","CADCHF","CADJPY","CHFJPY","EURAUD","EURCAD","EURCHF","EURGBP","EURJPY","EURNZD","EURUSD","GBPAUD","GBPCAD","GBPCHF","GBPJPY","GBPNZD","GBPUSD","NZDCAD","NZDCHF","NZDJPY","NZDUSD","USDCAD","USDCHF","USDJPY"]

def send_telegram(mensaje):
    try:
        if not TOKEN or not CHAT_ID: return
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=20)
    except: pass

def analizar(par):
    try:
        symbol = f"{par}=X"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=1d"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15).json()
        closes = r['chart']['result'][0]['indicators']['quote'][0]['close']
        closes = [c for c in closes if c is not None]
        if len(closes) < 50: return None, None
        precio = closes[-1]
        ema9 = sum(closes[-9:])/9
        ema21 = sum(closes[-21:])/21
        ema50 = sum(closes[-50:])/50
        gains, losses = [], []
        for i in range(1,15):
            diff = closes[-i] - closes[-i-1]
            (gains if diff>0 else losses).append(abs(diff))
        rs = (sum(gains)/14 if gains else 0.01)/(sum(losses)/14 if losses else 0.01)
        rsi = 100 - (100/(1+rs))
        separacion = abs(ema9-ema21)/ema21*100
        lateral = separacion < 0.05 and 45 < rsi < 55
        confianza, direccion = 0, None
        if ema9 > ema21 and ema21 > ema50 and 55 < rsi < 68 and precio > ema9:
            direccion="COMPRAR"
            confianza = 80 + min(separacion*100,10) + (68-abs(62-rsi))
        elif ema9 < ema21 and ema21 < ema50 and 32 < rsi < 45 and precio < ema9:
            direccion="VENDER"
            confianza = 80 + min(separacion*100,10) + (45-abs(38-rsi))
        confianza = int(min(max(confianza,0),95))
        if lateral:
            return "LATERAL", par
        if confianza >= 85 and direccion:
            emoji = "🟢" if direccion=="COMPRAR" else "🔴"
            return "SENAL", f"{emoji} *{direccion}* {par} 5m\n💰 {precio:.5f}\n📊 EMA9>EMA21>EMA50\n📈 RSI {rsi:.1f}\n🎯 Confianza {confianza}% ✅\n💵 Payout 85%"
        return None, None
    except: return None, None

def bot_loop():
    send_telegram("🚀 *BOT DEIVID 85% + LATERAL ACTIVO*\n✅ 28 Pares | 5m | Hora Ecuador")
    lateral_count=0
    while True:
        tz_ec = pytz.timezone('America/Guayaquil')
        hora_ec = datetime.now(tz_ec)
        hora_str = hora_ec.strftime("%H:%M")
        if 5 <= hora_ec.hour <= 23:
            senales=0
            laterales=[]
            for par in PARES:
                tipo, msg = analizar(par)
                if tipo=="SENAL":
                    send_telegram(f"📊 *SENAL {hora_str} EC*\n\n{msg}\n\n⏰ Entrar siguiente vela 5m")
                    senales+=1
                    time.sleep(3)
                    if senales>=2: break
                elif tipo=="LATERAL": laterales.append(par)
            if senales==0 and len(laterales)>=15:
                lateral_count+=1
                if lateral_count%2==0:
                    send_telegram(f"⏸️ *MERCADO LATERAL {hora_str} EC*\n{len(laterales)}/28 pares sin direccion\n🚫 NO OPERAR AHORA")
        time.sleep(900)

@app.route('/')
def home(): return "Bot Activo"

threading.Thread(target=bot_loop, daemon=True).start()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
