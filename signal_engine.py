"""
Signal engine - generira BUY / SELL / NO SIGNAL
na podlagi kombinacije indikatorjev
"""
import logging
from config import RSI_OVERBOUGHT, RSI_OVERSOLD, MIN_CONFIRMATIONS

logger = logging.getLogger(__name__)

# SL/TP multiplikatorji ATR
SL_ATR_MULT = 1.5
TP_ATR_MULT = 2.5


def analyze_signal(values: dict, pair: str, timeframe: str) -> dict:
    """
    Analizira indikatorje in vrne signal.

    Logika:
    - BUY:  EMA50 > EMA200 (bullish trend) + RSI < 60 (ni overbought) + MACD hist pozitiven in rastoč
    - SELL: EMA50 < EMA200 (bearish trend) + RSI > 40 (ni oversold)  + MACD hist negativen in padajoč
    - Potrebnih vsaj MIN_CONFIRMATIONS potrditev

    Returns dict z: signal, price, sl, tp, reason, confirmations
    """
    if not values:
        return _no_signal(pair, timeframe, "Ni podatkov")

    close = values["close"]
    ema_fast = values["ema_fast"]
    ema_slow = values["ema_slow"]
    rsi = values["rsi"]
    macd_hist = values["macd_hist"]
    macd_hist_prev = values["macd_hist_prev"]
    atr = values["atr"]
    timestamp = values["timestamp"]

    buy_confirmations = []
    sell_confirmations = []

    # === 1. EMA TREND ===
    if ema_fast > ema_slow:
        buy_confirmations.append("EMA50 > EMA200 (bullish trend)")
    elif ema_fast < ema_slow:
        sell_confirmations.append("EMA50 < EMA200 (bearish trend)")

    # === 2. RSI ===
    if RSI_OVERSOLD < rsi < 60:
        buy_confirmations.append(f"RSI {rsi:.1f} (bullish cona, ni overbought)")
    elif 40 < rsi < RSI_OVERBOUGHT:
        sell_confirmations.append(f"RSI {rsi:.1f} (bearish cona, ni oversold)")
    elif rsi <= RSI_OVERSOLD:
        buy_confirmations.append(f"RSI {rsi:.1f} (oversold - potencialni obrat navzgor)")
    elif rsi >= RSI_OVERBOUGHT:
        sell_confirmations.append(f"RSI {rsi:.1f} (overbought - potencialni obrat navzdol)")

    # === 3. MACD ===
    macd_rising = macd_hist > macd_hist_prev
    if macd_hist > 0 and macd_rising:
        buy_confirmations.append("MACD histogram pozitiven in rastoč")
    elif macd_hist < 0 and not macd_rising:
        sell_confirmations.append("MACD histogram negativen in padajoč")

    # === ODLOČITEV ===
    logger.debug(f"{pair} {timeframe} | BUY: {len(buy_confirmations)} | SELL: {len(sell_confirmations)}")

    if len(buy_confirmations) >= MIN_CONFIRMATIONS:
        sl = round(close - atr * SL_ATR_MULT, 5)
        tp = round(close + atr * TP_ATR_MULT, 5)
        return {
            "signal": "BUY",
            "pair": pair,
            "timeframe": timeframe,
            "price": close,
            "sl": sl,
            "tp": tp,
            "rr": round(TP_ATR_MULT / SL_ATR_MULT, 2),
            "reason": " | ".join(buy_confirmations),
            "confirmations": len(buy_confirmations),
            "rsi": rsi,
            "ema_fast": ema_fast,
            "ema_slow": ema_slow,
            "macd_hist": macd_hist,
            "atr": atr,
            "timestamp": timestamp,
        }

    elif len(sell_confirmations) >= MIN_CONFIRMATIONS:
        sl = round(close + atr * SL_ATR_MULT, 5)
        tp = round(close - atr * TP_ATR_MULT, 5)
        return {
            "signal": "SELL",
            "pair": pair,
            "timeframe": timeframe,
            "price": close,
            "sl": sl,
            "tp": tp,
            "rr": round(TP_ATR_MULT / SL_ATR_MULT, 2),
            "reason": " | ".join(sell_confirmations),
            "confirmations": len(sell_confirmations),
            "rsi": rsi,
            "ema_fast": ema_fast,
            "ema_slow": ema_slow,
            "macd_hist": macd_hist,
            "atr": atr,
            "timestamp": timestamp,
        }

    else:
        reasons = []
        if buy_confirmations:
            reasons.append(f"BUY kandidati ({len(buy_confirmations)}): {', '.join(buy_confirmations)}")
        if sell_confirmations:
            reasons.append(f"SELL kandidati ({len(sell_confirmations)}): {', '.join(sell_confirmations)}")
        reason = " | ".join(reasons) if reasons else "Ni jasnega signala"
        return _no_signal(pair, timeframe, reason)


def _no_signal(pair: str, timeframe: str, reason: str) -> dict:
    return {
        "signal": "NO SIGNAL",
        "pair": pair,
        "timeframe": timeframe,
        "reason": reason,
    }
