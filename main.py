from flask import Flask
from threading import Thread
app = Flask('')
@app.route('/')
def home():
    return "¡Bot de señales 24/7 ACTIVO!"
def run_web():
    app.run(host='0.0.0.0', port=8080)
Thread(target=run_web, daemon=True).start()
"""World Binary signal bot.

This bot only produces trading signals. It never places or manages trades.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Final
from zoneinfo import ZoneInfo

import matplotlib
import mplfinance as mpf
import pandas as pd
import yfinance as yf
from telegram import Bot
from telegram.error import Forbidden, InvalidToken, NetworkError
from flask import Flask
from threading import Thread

app = Flask('')
@app.route('/')
def home():
    return "BOT ACTIVO - World Binary Bot funcionando!"

def run_web():
    app.run(host='0.0.0.0', port=8080)
matplotlib.use("Agg")


LOGGER = logging.getLogger("world-binary-bot")
ECUADOR_TZ: Final = ZoneInfo("America/Guayaquil")
SCAN_INTERVAL_SECONDS: Final = 3 * 60
TIMEFRAME: Final = "5m"
HISTORY_PERIOD: Final = "5d"
STATE_PATH: Final = Path("signal_state.json")

# GBPUSD appeared twice in the requested list. dict.fromkeys keeps the original
# order while removing the duplicate.
REQUESTED_PAIRS: Final = tuple(
    dict.fromkeys(
        (
            "EURUSD",
            "GBPUSD",
            "USDJPY",
            "GBPJPY",
            "EURJPY",
            "AUDUSD",
            "USDCAD",
            "NZDUSD",
            "EURGBP",
            "GBPCHF",
            "XAUUSD",
            "BTCUSD",
            "ETHUSD",
            "EURAUD",
            "GBPAUD",
            "AUDJPY",
            "CADJPY",
            "CHFJPY",
            "EURCAD",
            "GBPCAD",
            "AUDCAD",
            "NZDCAD",
            "EURCHF",
            "GBPUSD",
            "USDCHF",
        )
    )
)

# Yahoo Finance symbols do not use the same names as the symbols shown to the
# user. Gold uses a liquid futures proxy because XAUUSD=X is not consistently
# available from Yahoo Finance.
YAHOO_SYMBOLS: Final = {
    **{pair: f"{pair}=X" for pair in REQUESTED_PAIRS if pair not in {"XAUUSD", "BTCUSD", "ETHUSD"}},
    "XAUUSD": "GC=F",
    "BTCUSD": "BTC-USD",
    "ETHUSD": "ETH-USD",
}


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    telegram_chat_id: str
    rsi_buy_min: float = 50.0
    rsi_sell_max: float = 50.0

    @classmethod
    def from_environment(cls) -> Settings:
        token = os.getenv("TELEGRAM_TOKEN", "").strip()
        chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
        if not token or not chat_id:
            missing = [
                name
                for name, value in (
                    ("TELEGRAM_TOKEN", token),
                    ("TELEGRAM_CHAT_ID", chat_id),
                )
                if not value
            ]
            raise RuntimeError(
                f"Faltan Secrets requeridos: {', '.join(missing)}. "
                "Añádelos antes de iniciar el bot."
            )

        return cls(
            telegram_token=token,
            telegram_chat_id=chat_id,
            rsi_buy_min=float(os.getenv("RSI_BUY_MIN", "50")),
            rsi_sell_max=float(os.getenv("RSI_SELL_MAX", "50")),
        )


@dataclass(frozen=True)
class Signal:
    pair: str
    direction: str
    rsi: float
    candle_time: pd.Timestamp
    yahoo_symbol: str

    @property
    def dedupe_key(self) -> str:
        return f"{self.pair}:{self.direction}:{self.candle_time.isoformat()}"


class TelegramConfigurationError(RuntimeError):
    """Telegram credentials or destination need to be corrected."""


class SignalState:
    """Small JSON-backed store so a restart cannot resend the same crossover."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.sent_keys = self._load()

    def _load(self) -> set[str]:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            keys = raw.get("sent_signal_keys", [])
            return {str(key) for key in keys}
        except FileNotFoundError:
            return set()
        except (json.JSONDecodeError, OSError, AttributeError):
            LOGGER.warning("No se pudo leer el estado anterior; se iniciará vacío.")
            return set()

    def contains(self, key: str) -> bool:
        return key in self.sent_keys

    def add(self, key: str) -> None:
        self.sent_keys.add(key)
        # Keep the file bounded while retaining enough recent history to survive
        # restarts during the intraday data retention window.
        recent = list(self.sent_keys)[-500:]
        self.sent_keys = set(recent)
        self.path.write_text(
            json.dumps({"sent_signal_keys": recent}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _normalise_yahoo_columns(data: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Return a normal OHLCV frame for both yfinance column formats."""

    if not isinstance(data.columns, pd.MultiIndex):
        return data

    for level in range(data.columns.nlevels):
        values = set(data.columns.get_level_values(level))
        if symbol in values:
            return data.xs(symbol, level=level, axis=1, drop_level=True)

    # With a single ticker, yfinance can still return a two-level frame where
    # the ticker label is not exactly the requested symbol. Select OHLCV fields
    # by name instead of relying on the label.
    flattened: dict[str, pd.Series] = {}
    for field in ("Open", "High", "Low", "Close", "Volume"):
        for column in data.columns:
            if field in column:
                flattened[field] = data[column]
                break
    return pd.DataFrame(flattened, index=data.index)


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
    data = _normalise_yahoo_columns(data, symbol)
    required = ["Open", "High", "Low", "Close"]
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError(f"Yahoo Finance no devolvió {', '.join(missing)} para {symbol}")

    data = data[required + (["Volume"] if "Volume" in data.columns else [])].copy()
    data = data.apply(pd.to_numeric, errors="coerce").dropna(subset=required)
    if len(data) < 80:
        raise ValueError(f"Datos insuficientes para {symbol}: {len(data)} velas")

    # The newest M5 candle can still be forming when the 3-minute scan runs.
    # Excluding it prevents a crossover from disappearing before candle close.
    return data.iloc[:-1]


def calculate_indicators(data: pd.DataFrame) -> pd.DataFrame:
    enriched = data.copy()
    close = enriched["Close"]
    enriched["EMA20"] = close.ewm(span=20, adjust=False, min_periods=20).mean()
    enriched["EMA50"] = close.ewm(span=50, adjust=False, min_periods=50).mean()

    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    average_gain = gain.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    average_loss = loss.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
    relative_strength = average_gain / average_loss.replace(0, pd.NA)
    enriched["RSI14"] = 100 - (100 / (1 + relative_strength))
    enriched.loc[(average_loss == 0) & (average_gain > 0), "RSI14"] = 100
    return enriched.dropna(subset=["EMA20", "EMA50", "RSI14"])


def detect_signal(pair: str, data: pd.DataFrame, settings: Settings) -> Signal | None:
    if len(data) < 2:
        return None

    previous = data.iloc[-2]
    latest = data.iloc[-1]
    bullish_cross = previous["EMA20"] <= previous["EMA50"] and latest["EMA20"] > latest["EMA50"]
    bearish_cross = previous["EMA20"] >= previous["EMA50"] and latest["EMA20"] < latest["EMA50"]
    rsi = float(latest["RSI14"])

    if bullish_cross and rsi >= settings.rsi_buy_min:
        direction = "COMPRA"
    elif bearish_cross and rsi <= settings.rsi_sell_max:
        direction = "VENTA"
    else:
        return None

    candle_time = data.index[-1]
    if not isinstance(candle_time, pd.Timestamp):
        candle_time = pd.Timestamp(candle_time)
    return Signal(pair, direction, rsi, candle_time, YAHOO_SYMBOLS[pair])


def build_chart(data: pd.DataFrame, signal: Signal) -> str:
    chart_data = data.tail(80).copy()
    marker = pd.Series(index=chart_data.index, dtype="float64")
    marker.iloc[-1] = chart_data.iloc[-1]["High"] * 1.0015
    marker_style = {
        "marker": "^" if signal.direction == "COMPRA" else "v",
        "markersize": 120,
        "color": "#19d3ae" if signal.direction == "COMPRA" else "#ff6b7a",
    }

    addplots = [
        mpf.make_addplot(chart_data["EMA20"], color="#4da3ff", width=1.2),
        mpf.make_addplot(chart_data["EMA50"], color="#f4b942", width=1.2),
        mpf.make_addplot(marker, type="scatter", panel=0, **marker_style),
        mpf.make_addplot(
            chart_data["RSI14"],
            panel=1,
            color="#c084fc",
            ylim=(0, 100),
            ylabel="RSI 14",
            width=1.1,
        ),
    ]

    style = mpf.make_mpf_style(
        base_mpf_style="nightclouds",
        gridstyle=":",
        facecolor="#0b1220",
        edgecolor="#344054",
        figcolor="#070b14",
        rc={
            "font.size": 8,
            "axes.labelcolor": "#d0d5dd",
            "xtick.color": "#98a2b3",
            "ytick.color": "#98a2b3",
        },
    )
    label = "Compra" if signal.direction == "COMPRA" else "Venta"
    with tempfile.NamedTemporaryFile(
        prefix=f"{signal.pair}_",
        suffix=".png",
        delete=False,
    ) as temporary:
        chart_path = temporary.name

    mpf.plot(
        chart_data,
        type="candle",
        style=style,
        addplot=addplots,
        panel_ratios=(3, 1),
        volume=False,
        ylabel="Precio",
        title=f"{signal.pair} · Cruce EMA 20/50 · {label}",
        datetime_format="%d/%m %H:%M",
        xrotation=0,
        tight_layout=True,
        savefig=dict(fname=chart_path, dpi=140, bbox_inches="tight"),
    )
    return chart_path


def format_caption(signal: Signal) -> str:
    ecuador_time = signal.candle_time
    if ecuador_time.tzinfo is None:
        ecuador_time = ecuador_time.tz_localize("UTC")
    ecuador_time = ecuador_time.tz_convert(ECUADOR_TZ)
    return (
        "🔥 SEÑAL BINARIA 5M 🔥\n"
        f"Par: {signal.pair}\n"
        f"Dirección: {signal.direction}\n"
        "Expiración: 5 min\n"
        f"World Binary RSI: {signal.rsi:.2f}\n"
        f"Hora Ecuador: {ecuador_time.strftime('%d/%m/%Y %H:%M')}"
    )


async def send_signal(
    bot: Bot,
    chat_id: str,
    signal: Signal,
    chart_path: str,
) -> None:
    try:
        with open(chart_path, "rb") as chart:
            try:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=chart,
                    caption=format_caption(signal),
                )
            except InvalidToken as error:
                raise TelegramConfigurationError(
                    "Telegram rechazó TELEGRAM_TOKEN. Genera un token nuevo "
                    "con @BotFather y actualiza el Secret."
                ) from error
            except Forbidden as error:
                raise TelegramConfigurationError(
                    "Telegram rechazó el destino. Verifica que TELEGRAM_CHAT_ID "
                    "sea el ID de un chat, grupo o canal donde el bot sea miembro."
                ) from error
    finally:
        try:
            os.remove(chart_path)
        except OSError:
            LOGGER.warning("No se pudo borrar el gráfico temporal %s", chart_path)


async def scan_once(
    bot: Bot,
    settings: Settings,
    state: SignalState,
) -> None:
    LOGGER.info("Escaneando %d pares en M5...", len(REQUESTED_PAIRS))
    for pair in REQUESTED_PAIRS:
        try:
            candles = await asyncio.to_thread(download_candles, pair)
            indicators = calculate_indicators(candles)
            signal = detect_signal(pair, indicators, settings)
            if signal is None:
                continue
            if state.contains(signal.dedupe_key):
                LOGGER.info("Señal ya enviada: %s", signal.dedupe_key)
                continue

            chart_path = await asyncio.to_thread(build_chart, indicators, signal)
            await send_signal(bot, settings.telegram_chat_id, signal, chart_path)
            state.add(signal.dedupe_key)
            LOGGER.info(
                "Señal enviada: %s %s RSI %.2f",
                signal.pair,
                signal.direction,
                signal.rsi,
            )
        except TelegramConfigurationError as error:
            LOGGER.error("%s Se pausará el envío hasta corregir Secrets.", error)
            return
        except NetworkError:
            LOGGER.warning(
                "Telegram no respondió durante el envío de %s; se reintentará "
                "en el siguiente escaneo.",
                pair,
            )
        except Exception:
            LOGGER.exception("Error al procesar %s; se continúa con el siguiente par.", pair)


def seconds_to_next_scan() -> float:
    now = datetime.now(timezone.utc)
    next_minute = now.minute - (now.minute % 3) + 3
    next_scan = now.replace(second=5, microsecond=0)
    if next_minute >= 60:
        next_scan = (now + timedelta(hours=1)).replace(
            minute=next_minute % 60,
            second=5,
            microsecond=0,
        )
    else:
        next_scan = next_scan.replace(minute=next_minute)
    return max(5.0, (next_scan - now).total_seconds())


async def run_bot() -> None:
    settings = Settings.from_environment()
    state = SignalState(STATE_PATH)
    LOGGER.info(
        "Bot iniciado: %d pares únicos, M5, escaneo cada 3 minutos. "
        "RSI compra >= %.1f / venta <= %.1f.",
        len(REQUESTED_PAIRS),
        settings.rsi_buy_min,
        settings.rsi_sell_max,
    )

    # python-telegram-bot v22 exposes Bot as an async context manager.
    async with Bot(settings.telegram_token) as bot:
        while True:
            started = time.monotonic()
            await scan_once(bot, settings, state)
            elapsed = time.monotonic() - started
            delay = seconds_to_next_scan()
            LOGGER.info(
                "Escaneo terminado en %.1fs. Próximo escaneo en %.1fs.",
                elapsed,
                delay,
            )
            await asyncio.sleep(delay)


def main() -> None:
    # https/httpcore otherwise log the full Telegram API URL, which may contain
    # the bot token. Keep third-party request details out of workflow logs.
    for logger_name in ("httpx", "httpcore", "telegram", "telegram.ext"):
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    Thread(target=run_web, daemon=True).start()
    LOGGER.info("Servidor web iniciado para UptimeRobot")
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        LOGGER.info("Bot detenido por el usuario.")
    except Exception:
        LOGGER.exception("El bot no pudo iniciar.")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
