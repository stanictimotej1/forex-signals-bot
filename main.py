"""
Forex Signal Bot - Vstopna točka
"""
import logging
import argparse
import sys
from config import validate_config, LOG_LEVEL, LOG_FILE


def setup_logging():
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)

    # File handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logging.basicConfig(level=level, handlers=[console, file_handler])


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="Forex Signal Bot")
    parser.add_argument(
        "--mode",
        choices=["run", "test", "once"],
        default="run",
        help="run=scheduler, test=testni email, once=enkratno preverjanje"
    )
    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("   FOREX SIGNAL BOT - ZAGANJAM")
    logger.info("=" * 50)

    # Preveri konfiguracijo
    try:
        validate_config()
        logger.info("✓ Konfiguracija OK")
    except ValueError as e:
        logger.error(f"Napaka konfiguracije: {e}")
        sys.exit(1)

    if args.mode == "test":
        # Pošlji testni email
        logger.info("Pošiljam testni email...")
        from email_service import send_signal_email
        test_signal = {
            "signal": "BUY",
            "pair": "EURUSD",
            "timeframe": "1h",
            "price": 1.08542,
            "sl": 1.08100,
            "tp": 1.09200,
            "rr": 1.67,
            "rsi": 45.2,
            "ema_fast": 1.08300,
            "ema_slow": 1.07800,
            "macd_hist": 0.00023,
            "atr": 0.00295,
            "confirmations": 3,
            "reason": "EMA50 > EMA200 (bullish trend) | RSI 45.2 (bullish cona) | MACD histogram pozitiven in rastoč",
            "timestamp": __import__("datetime").datetime.utcnow(),
        }
        success = send_signal_email(test_signal)
        if success:
            logger.info("✓ Testni email poslan!")
        else:
            logger.error("✗ Napaka pri pošiljanju testnega emaila")

    elif args.mode == "once":
        # Enkratno preverjanje vseh parov
        logger.info("Enkratno preverjanje vseh parov...")
        from scheduler import run_all_checks
        run_all_checks()

    else:
        # Zaženi scheduler
        logger.info("Zaganjam scheduler...")
        from scheduler import start_scheduler
        start_scheduler()


if __name__ == "__main__":
    main()
