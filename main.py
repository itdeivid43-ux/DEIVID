import time
import requests

# CONFIGURACION TUYA
TELEGRAM_TOKEN = "AQUI_TU_TOKEN"
CHAT_ID = "AQUI_TU_CHAT_ID"
PARES = ["USDJPY", "EURUSD", "AUDUSD", "GBPUSD", "USDCAD", "USDCHF", "NZDUSD"]
INTERVALO = 600  # 10 minutos en segundos

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensaje}
    requests.post(url, data=data)

def analizar_par(par):
    # Aqui va tu logica de TradingView
    # Filtro de tu foto ganadora USDJPY
    estocastico = 15  # ejemplo, esto viene de tu API
    toca_soporte = True  # ejemplo
    
    if estocastico < 20 and toca_soporte:
        return f"🟢 COMPRA {par} 1m\nSoporte + Estocástico en {estocastico} como tu entrada ganadora +1.85\nEntra ya y cierra en +1.5"
    return None

print("Bot iniciado - 7 pares - cada 10M - sin XAU ni BTC")
enviar_telegram("✅ Bot iniciado: 7 pares Forex cada 10 minutos. Config foto ganadora USDJPY +1.85")

while True:
    for par in PARES:
        senal = analizar_par(par)
        if senal:
            enviar_telegram(senal)
            print(senal)
    time.sleep(INTERVALO)
