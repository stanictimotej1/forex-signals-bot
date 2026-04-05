"""
Scheduler - periodično preverja signale za vse pare in timeframe
"""
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config import PAIRS, TIMEFRAMES, CHECK_INTERVALS

logger = logging.getLogger(__name__)


def run_check(pair: str, timeframe: str):
    """Izvede celoten pipeline za en par in timeframe."""
    from data_fetcher import fetch_ohlcv
    from indicators import add_all_indicators, get_latest_values
    from signal_engine import analyze_signal
    from email_service import send_signal_email
    from state_manager import is_duplicate, record_signal

    logger.info(f"Preverjam: {pair} {timeframe}")

    # 1. Pridobi podatke
    df = fetch_ohlcv(pair, timeframe)
    if df is None:
        logger.warning(f"Ni podatkov za {pair} {timeframe}")
        return

    # 2. Izračunaj indikatorje
    df = add_all_indicators(df)
    if df is None:
        return

    values = get_latest_values(df)
    if not values:
        return

    # 3. Generiraj signal
    result = analyze_signal(values, pair, timeframe)
    signal = result.get("signal")
    logger.info(f"{pair} {timeframe}: {signal}")

    # 4. Preveri duplikat
    if is_duplicate(pair, timeframe, signal):
        return

    # 5. Pošlji email
    success = send_signal_email(result)
    if success:
        record_signal(pair, timeframe, signal)


def run_all_checks():
    """Preveri vse pare in timeframe."""
    logger.info("=== Začenjam preverjanje vseh parov ===")
    for pair in PAIRS:
        for timeframe in TIMEFRAMES:
            try:
                run_check(pair, timeframe)
            except Exception as e:
                logger.error(f"Napaka pri {pair} {timeframe}: {e}")
    logger.info("=== Preverjanje končano ===")


def start_scheduler():
    """Zažene scheduler z ločenimi intervali za vsak timeframe."""
    scheduler = BlockingScheduler(timezone="UTC")

    for pair in PAIRS:
        for timeframe in TIMEFRAMES:
            interval_min = CHECK_INTERVALS.get(timeframe, 15)
            scheduler.add_job(
                func=run_check,
                trigger=IntervalTrigger(minutes=interval_min),
                args=[pair, timeframe],
                id=f"{pair}_{timeframe}",
                name=f"Check {pair} {timeframe}",
                max_instances=1,
                coalesce=True,
            )
            logger.info(f"Dodan job: {pair} {timeframe} vsakih {interval_min} min")

    logger.info("Scheduler zagnan. Ctrl+C za ustavitev.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler ustavljen.")
