import os
import time
from datetime import datetime
from typing import Dict, List
import pandas as pd
import pytz
import yfinance as yf
from flask import Flask
from ta.momentum import RSIIndicator

# ==============================
# CONFIG
# ==============================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
ECUADOR_TZ = pytz.timezone("America/Guayaquil")

PAIRS: List[str] = ["EUR/USD", "GBP/USD", "USD/JPY", "EUR/JPY", "AUD/USD"]
YAHOO_SYMBOLS: Dict[str, str] = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "EUR/JPY": "EURJPY=X",
    "AUD/USD": "AUDUSD=X",
}
TIMEFRAME = "5m"
HISTORY_PERIOD = "2d"
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
EMA_PERIOD = 50
CANDLE_INTERVAL_SECONDS = 300
PAUSE_SECONDS = 180

app = Flask(__name__)
@app.route("/")
def home():
    return "BOT ACTIVO - HORA REAL", 200

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

class Signal:
    def __init__(self, pair: str, direction: str, rsi: float):
        self.pair = pair
        self.direction = direction
        self.rsi = rsi

def _normalise_yahoo_columns(data: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if isinstance(data.columns, pd.MultiIndex):
        if symbol in data.columns.get_level_values(1):
            data = data.xs(symbol, axis=1, level=1)
        else:
            data.columns = data.columns.get_level_values(0)
    data.columns = [str(col).strip().title() for col in data.columns]
    data = data.rename(columns={"Adj Close": "Close"})
    return data

def download_candles(pair: str) -> pd.DataFrame:
    symbol = YAHOO_SYMBOLS[pair]
    data = yf.download(
        tickers=symbol,
        period=HISTORY_PERIOD,
        interval=TIMEFRAME,
        auto_adjust=False,
        progress=False,
        threads=False,
        group_by="column",
    )
    if data.empty:
        raise ValueError(f"Sin datos para {symbol}")
    data = _normalise_yahoo_columns(data, symbol)
    required = ["Open", "High", "Low", "Close"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(f"Yahoo no devolvió {', '.join(missing)} para {symbol}")
    data = data[required + (["Volume"] if "Volume" in data.columns else [])].copy()
    data = data.apply(pd.to_numeric, errors="coerce").dropna(subset=required)
    if len(data) < 80:
        raise ValueError(f"Datos insuficientes para {symbol}: {len(data)} velas")
    return data # <-- ARREGLADO, SIN iloc

def calculate_indicators(data: pd.DataFrame) -> pd.DataFrame:
    enriched = data.copy()
    enriched["RSI"] = RSIIndicator(close=enriched["Close"], window=RSI_PERIOD).rsi()
    enriched["EMA"] = enriched["Close"].ewm(span=EMA_PERIOD, adjust=False).mean()
    return enriched

def detect_signal(pair: str) -> Signal | None:
    try:
        df = download_candles(pair)
        df = calculate_indicators(df)
        rsi = float(df["RSI"].iloc[-1])
        last_close = float(df["Close"].iloc[-1])
        last_ema = float(df["EMA"].iloc[-1])
        direction = None
        if rsi <= RSI_OVERSOLD and last_close > last_ema:
            direction = "COMPRA 🟢 (CALL)"
        elif rsi >= RSI_OVERBOUGHT and last_close < last_ema:
            direction = "VENTA 🔴 (PUT)"
        if direction:
            return Signal(pair, direction, rsi)
    except Exception as e:
        print(f"[{pair}] Error: {e}")
    return None

def send_telegram(message: str):
    import requests
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Error Telegram: {e}")

def format_caption(signal: Signal) -> str:
    ecuador_time = datetime.now(ECUADOR_TZ)
    return (
        "🔥 SEÑAL BINARIA 5M 🔥\n"
        f"Par: {signal.pair}\n"
        f"Dirección: {signal.direction}\n"
        "Expiración: 5 min\n"
        f"World Binary RSI: {signal.rsi:.2f}\n"
        f"Hora Ecuador: {ecuador_time.strftime('%d/%m/%Y %H:%M:%S')} - EN VIVO"
    )

def main_loop():
    print("Bot iniciado - HORA REAL")
    while True:
        for pair in PAIRS:
            sig = detect_signal(pair)
            if sig:
                msg = format_caption(sig)
                print(msg)
                send_telegram(msg)
                time.sleep(PAUSE_SECONDS)
                break
        time.sleep(CANDLE_INTERVAL_SECONDS)

if __name__ == "__main__":
    import threading
    threading.Thread(target=run_web, daemon=True).start()
    main_loop()
