import os, requests, time, threading
from flask import Flask
import yfinance as yf
from datetime import datetime
import pytz

app = Flask(__name__)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

ultimo_aviso = 0
ultima_senal = {} # para no repetir la misma señal

def send(m):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.get(url, params={"chat_id": CHAT_ID, "text": m}, timeout=10)
        print(f"Enviado: {m}")
    except Exception as e:
        print(f"Error: {e}")

@app.route("/test")
def test():
    send("✅ TEST FINAL VIVO - Bot binarias 14,3,3 listo")
    return "Test enviado"

@app.route("/")
def home():
    return "Bot FINAL Binarias 14,3,3 25/75 Activo - /test para probar"

def calcular_estocastico(df):
    # Estocastico 14,3,3 estandar
    low_min = df['Low'].rolling(14).min()
    high_max = df['High'].rolling(14).max()
    k = ((df['Close'] - low_min) / (high_max - low_min) * 100).rolling(3).mean()
    d = k.rolling(3).mean()
    return k, d

def bot():
    global ultimo_aviso
    pares = ["EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","EURJPY=X","USDCAD=X","GBPJPY=X"]

    send("🚀 BOT FINAL BINARIAS INICIADO\n14,3,3 - Niveles 25/75\n7 pares - Exp 5m\nEsperando cruces...")

    while True:
        senal_enviada_ahora = False
        estado_actual = []

        for par in pares:
            try:
                df = yf.download(par, period="2d", interval="5m", progress=False, auto_adjust=True)
                if len(df) < 30:
                    continue

                # Soporte para MultiIndex de yfinance nuevo
                if isinstance(df.columns, type(df.columns)) and 'Close' in str(df.columns):
                    try:
                        c = df['Close'].iloc[:,0] if len(df['Close'].shape)>1 else df['Close']
                        l = df['Low'].iloc[:,0] if len(df['Low'].shape)>1 else df['Low']
                        h = df['High'].iloc[:,0] if len(df['High'].shape)>1 else df['High']
                    except:
                        c = df['Close']; l = df['Low']; h = df['High']
                else:
                    c = df['Close']; l = df['Low']; h = df['High']

                k, d = calcular_estocastico(df)
                ck = float(k.iloc[-1]); pk = float(k.iloc[-2])
                cd = float(d.iloc[-1]); pd = float(d.iloc[-2])

                estado_actual.append(f"{par.replace('=X','')}: K{ck:.0f} D{cd:.0f}")

                # CONDICION FINAL MAS SENSIBLE PARA BINARIAS
                # Compra cuando cruza hacia arriba en sobreventa 25
                buy = pk < 25 and ck > 25 and ck > cd and pd < 25
                # Venta cuando cruza hacia abajo en sobrecompra 75
                sell = pk > 75 and ck < 75 and ck < cd and pd > 75

                # Evitar repetir misma señal en la misma vela
                key = f"{par}_{df.index[-1]}"
                if key in ultima_senal:
                    continue

                if buy or sell:
                    hora = datetime.now(pytz.timezone('America/Guayaquil')).strftime("%H:%M:%S")
                    tipo = "CALL 📈 COMPRAR" if buy else "PUT 📉 VENDER"
                    par_limpio = par.replace("=X","")
                    msg = f"""🎯 BOT BINARIAS 5m
⏰ {hora} EC - {tipo}
💱 {par_limpio}
📊 Estoc 14,3,3 K:{ck:.1f} D:{cd:.1f}
👉 ENTRAR AHORA prox vela
⏳ EXP 5 MINUTOS"""
                    send(msg)
                    ultima_senal[key] = True
                    senal_enviada_ahora = True
                    time.sleep(2) # para no saturar

            except Exception as e:
                print(f"Error {par}: {e}")

        # Si no hubo señal, avisa cada 30 min que sigue vivo
        if not senal_enviada_ahora:
            ahora = time.time()
            if ahora - ultimo_aviso > 1800: # 1800 = 30 min
                hora = datetime.now(pytz.timezone('America/Guayaquil')).strftime("%H:%M:%S")
                estado_txt = " | ".join(estado_actual[:4])
                send(f"⏳ {hora} EC BOT VIVO - Sin cruces aun\n{estado_txt}\nEsperando 25/75...")
                ultimo_aviso = ahora

        time.sleep(60) # revisa cada 1 min

threading.Thread(target=bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
