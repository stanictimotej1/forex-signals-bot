"""
Configuration loader - vse vrednosti iz .env datoteke
"""
import os
from dotenv import load_dotenv

load_dotenv()

# === FOREX PARI IN TIMEFRAMI ===
PAIRS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]
TIMEFRAMES = ["15min", "1h", "4h"]

# === ALPHA VANTAGE API ===
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# === EMAIL (SendGrid SMTP) ===
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")

# === INDIKATORJI ===
EMA_FAST = 50
EMA_SLOW = 200
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# === SIGNAL LOGIKA ===
# Koliko indikatorjev se mora ujemati za signal
MIN_CONFIRMATIONS = 3  # od 3 možnih (EMA trend, RSI, MACD)

# === SCHEDULER ===
# Kako pogosto preverimo (v minutah) - po timeframeu
CHECK_INTERVALS = {
    "15min": 15,
    "1h": 60,
    "4h": 240,
}

# === LOGGING ===
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = "forex_bot.log"

def validate_config():
    """Preveri da so vse obvezne vrednosti nastavljene."""
    required = {
        "ALPHA_VANTAGE_API_KEY": ALPHA_VANTAGE_API_KEY,
        "SENDGRID_API_KEY": SENDGRID_API_KEY,
        "EMAIL_FROM": EMAIL_FROM,
        "EMAIL_TO": EMAIL_TO,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(f"Manjkajo .env spremenljivke: {', '.join(missing)}")
