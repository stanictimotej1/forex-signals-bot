"""
State manager - preprečuje pošiljanje duplikat signalov
Shranjuje zadnji signal za vsak par+timeframe kombinacijo
"""
import json
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

STATE_FILE = "signal_state.json"

# Kako dolgo ignoriramo isti signal (v urah) po timeframeu
COOLDOWN_HOURS = {
    "15min": 1,
    "1h": 4,
    "4h": 12,
}


def _load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Napaka pri branju state datoteke: {e}")
        return {}


def _save_state(state: dict):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Napaka pri shranjevanju state datoteke: {e}")


def is_duplicate(pair: str, timeframe: str, signal: str) -> bool:
    """
    Preveri ali je signal duplikat.
    Vrne True če je isti signal že bil poslan v cooldown periodi.
    """
    if signal == "NO SIGNAL":
        return True  # NO SIGNAL nikoli ne pošljemo

    state = _load_state()
    key = f"{pair}_{timeframe}"

    if key not in state:
        return False

    last = state[key]
    if last.get("signal") != signal:
        return False  # Drug signal - ni duplikat

    # Preveri cooldown
    cooldown_h = COOLDOWN_HOURS.get(timeframe, 4)
    last_sent = datetime.fromisoformat(last["sent_at"])
    if datetime.utcnow() - last_sent < timedelta(hours=cooldown_h):
        logger.info(f"Duplikat signal preskočen: {pair} {timeframe} {signal} (cooldown {cooldown_h}h)")
        return True

    return False


def record_signal(pair: str, timeframe: str, signal: str):
    """Zabeleži da je bil signal poslan."""
    state = _load_state()
    key = f"{pair}_{timeframe}"
    state[key] = {
        "signal": signal,
        "sent_at": datetime.utcnow().isoformat(),
    }
    _save_state(state)
    logger.info(f"Signal zabeležen: {pair} {timeframe} {signal}")
