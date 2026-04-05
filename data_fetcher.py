"""
Pridobivanje OHLCV podatkov iz Alpha Vantage API
"""
import logging
import requests
import pandas as pd
from config import ALPHA_VANTAGE_API_KEY

logger = logging.getLogger(__name__)

BASE_URL = "https://www.alphavantage.co/query"

# Mapiranje naših timeframov na Alpha Vantage funkcije/intervale
TIMEFRAME_MAP = {
    "15min": {"function": "FX_INTRADAY", "interval": "15min"},
    "1h":    {"function": "FX_INTRADAY", "interval": "60min"},
    "4h":    {"function": "FX_INTRADAY", "interval": "60min"},  # 4h bomo resamplirani iz 1h
}


def fetch_ohlcv(pair: str, timeframe: str, outputsize: str = "compact") -> pd.DataFrame | None:
    """
    Pridobi OHLCV podatke za forex par in timeframe.

    Args:
        pair: npr. "EURUSD"
        timeframe: "15min", "1h", "4h"
        outputsize: "compact" (100 svečk) ali "full" (do 5000)

    Returns:
        DataFrame z stolpci: open, high, low, close, volume
        ali None ob napaki
    """
    from_symbol = pair[:3]
    to_symbol = pair[3:]

    tf_config = TIMEFRAME_MAP.get(timeframe)
    if not tf_config:
        logger.error(f"Neznan timeframe: {timeframe}")
        return None

    params = {
        "function": tf_config["function"],
        "from_symbol": from_symbol,
        "to_symbol": to_symbol,
        "interval": tf_config["interval"],
        "outputsize": outputsize,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }

    try:
        logger.debug(f"Fetching {pair} {timeframe} ...")
        response = requests.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Poišči pravi ključ v odgovoru
        time_series_key = None
        for key in data.keys():
            if "Time Series" in key:
                time_series_key = key
                break

        if not time_series_key:
            error_msg = data.get("Note") or data.get("Information") or data.get("Error Message", "Neznan odgovor API")
            logger.warning(f"{pair} {timeframe}: {error_msg}")
            return None

        time_series = data[time_series_key]
        df = pd.DataFrame.from_dict(time_series, orient="index")
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        # Preimenuj stolpce
        df.columns = [col.split(". ")[1] for col in df.columns]
        df = df.rename(columns={"open": "open", "high": "high", "low": "low", "close": "close"})
        df = df.astype(float)

        # Za 4h resampliraj iz 1h podatkov
        if timeframe == "4h":
            df = df.resample("4h").agg({
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
            }).dropna()

        logger.info(f"✓ {pair} {timeframe}: {len(df)} svečk pridobljenih")
        return df

    except requests.exceptions.RequestException as e:
        logger.error(f"Network napaka pri {pair} {timeframe}: {e}")
        return None
    except Exception as e:
        logger.error(f"Napaka pri obdelavi {pair} {timeframe}: {e}")
        return None


def get_current_price(pair: str) -> float | None:
    """Pridobi trenutno ceno para."""
    from_symbol = pair[:3]
    to_symbol = pair[3:]

    params = {
        "function": "CURRENCY_EXCHANGE_RATE",
        "from_currency": from_symbol,
        "to_currency": to_symbol,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        rate = data["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
        return float(rate)
    except Exception as e:
        logger.error(f"Napaka pri pridobivanju cene {pair}: {e}")
        return None
