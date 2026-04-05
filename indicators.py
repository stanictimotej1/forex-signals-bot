"""
Tehnični indikatorji: EMA, RSI, MACD
Vse izračunano ročno z numpy/pandas (brez zewnętrznih TA knjižnic)
"""
import logging
import numpy as np
import pandas as pd
from config import EMA_FAST, EMA_SLOW, RSI_PERIOD, MACD_FAST, MACD_SLOW, MACD_SIGNAL

logger = logging.getLogger(__name__)


def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """Eksponentna drseča sredina."""
    return series.ewm(span=period, adjust=False).mean()


def calculate_rsi(series: pd.Series, period: int = RSI_PERIOD) -> pd.Series:
    """Relative Strength Index (RSI)."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(series: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    MACD indikator.
    Returns: (macd_line, signal_line, histogram)
    """
    ema_fast = calculate_ema(series, MACD_FAST)
    ema_slow = calculate_ema(series, MACD_SLOW)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, MACD_SIGNAL)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range - za izračun SL/TP."""
    high = df["high"]
    low = df["low"]
    close = df["close"]

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Doda vse indikatorje na DataFrame.
    Vrne kopijo z dodatnimi stolpci.
    """
    if df is None or len(df) < EMA_SLOW + 10:
        logger.warning(f"Premalo podatkov za izračun indikatorjev (potrebnih vsaj {EMA_SLOW + 10} svečk)")
        return None

    df = df.copy()
    close = df["close"]

    # EMA
    df["ema_fast"] = calculate_ema(close, EMA_FAST)
    df["ema_slow"] = calculate_ema(close, EMA_SLOW)

    # RSI
    df["rsi"] = calculate_rsi(close, RSI_PERIOD)

    # MACD
    df["macd"], df["macd_signal"], df["macd_hist"] = calculate_macd(close)

    # ATR (za SL/TP izračun)
    df["atr"] = calculate_atr(df)

    # Odstrani vrstice brez vrednosti
    df.dropna(inplace=True)

    return df


def get_latest_values(df: pd.DataFrame) -> dict | None:
    """Vrne zadnjo vrstico indikatorjev kot slovar."""
    if df is None or df.empty:
        return None

    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else last

    return {
        "close": round(last["close"], 5),
        "ema_fast": round(last["ema_fast"], 5),
        "ema_slow": round(last["ema_slow"], 5),
        "rsi": round(last["rsi"], 2),
        "macd": round(last["macd"], 6),
        "macd_signal": round(last["macd_signal"], 6),
        "macd_hist": round(last["macd_hist"], 6),
        "macd_hist_prev": round(prev["macd_hist"], 6),
        "atr": round(last["atr"], 5),
        "timestamp": df.index[-1],
    }
