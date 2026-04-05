"""
Email service - pošiljanje forex signal emailov via SendGrid SMTP
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from config import SENDGRID_API_KEY, EMAIL_FROM, EMAIL_TO

logger = logging.getLogger(__name__)

DISCLAIMER = """
⚠️ DISCLAIMER / OPOZORILO:
Ta email je zgolj informativne narave in ne predstavlja finančnega nasveta.
Forex trading vključuje visoko tveganje. Pretekli signali ne zagotavljajo
prihodnjih rezultatov. Trgujte odgovorno in vedno upravljajte svoje tveganje.
"""

SIGNAL_EMOJI = {"BUY": "🟢", "SELL": "🔴"}
PAIR_DISPLAY = {
    "EURUSD": "EUR/USD",
    "GBPUSD": "GBP/USD",
    "USDJPY": "USD/JPY",
    "AUDUSD": "AUD/USD",
    "USDCAD": "USD/CAD",
}
TF_DISPLAY = {"15min": "15M", "1h": "1H", "4h": "4H"}


def send_signal_email(signal_data: dict) -> bool:
    """
    Pošlje email za BUY/SELL signal.

    Args:
        signal_data: dict iz signal_engine.analyze_signal()

    Returns:
        True če uspešno poslano, False sicer
    """
    signal = signal_data.get("signal")
    pair = signal_data.get("pair")
    timeframe = signal_data.get("timeframe")

    pair_display = PAIR_DISPLAY.get(pair, pair)
    tf_display = TF_DISPLAY.get(timeframe, timeframe)
    emoji = SIGNAL_EMOJI.get(signal, "⚪")
    timestamp = signal_data.get("timestamp", datetime.utcnow())
    if hasattr(timestamp, "strftime"):
        ts_str = timestamp.strftime("%Y-%m-%d %H:%M UTC")
    else:
        ts_str = str(timestamp)

    subject = f"[FOREX SIGNAL] {emoji} {signal} {pair_display} {tf_display}"

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  body {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }}
  .card {{ background: white; border-radius: 8px; max-width: 560px; margin: 0 auto;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; }}
  .header {{ background: {'#1a6e2e' if signal == 'BUY' else '#8b1a1a'}; color: white;
              padding: 24px 32px; text-align: center; }}
  .header h1 {{ margin: 0; font-size: 28px; }}
  .header p {{ margin: 4px 0 0; opacity: 0.85; font-size: 14px; }}
  .body {{ padding: 28px 32px; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 20px 0; }}
  .box {{ background: #f8f9fa; border-radius: 6px; padding: 14px; }}
  .box .label {{ font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }}
  .box .value {{ font-size: 18px; font-weight: bold; color: #222; margin-top: 4px; }}
  .reason {{ background: #f0f4ff; border-left: 4px solid #3b6fd4; border-radius: 4px;
              padding: 14px 16px; margin: 16px 0; font-size: 14px; color: #444; }}
  .disclaimer {{ background: #fff8e1; border-radius: 6px; padding: 14px 16px; margin-top: 20px;
                  font-size: 12px; color: #666; line-height: 1.6; }}
  .footer {{ background: #f6f8fa; border-top: 1px solid #e1e4e8; padding: 16px 32px;
              text-align: center; font-size: 12px; color: #888; }}
</style>
</head>
<body>
<div class="card">
  <div class="header">
    <h1>{emoji} {signal} {pair_display}</h1>
    <p>Timeframe: {tf_display} &nbsp;|&nbsp; {ts_str}</p>
  </div>
  <div class="body">
    <div class="grid">
      <div class="box">
        <div class="label">Cena vstopa</div>
        <div class="value">{signal_data.get('price', 'N/A')}</div>
      </div>
      <div class="box">
        <div class="label">Stop Loss</div>
        <div class="value" style="color:#c0392b">{signal_data.get('sl', 'N/A')}</div>
      </div>
      <div class="box">
        <div class="label">Take Profit</div>
        <div class="value" style="color:#27ae60">{signal_data.get('tp', 'N/A')}</div>
      </div>
      <div class="box">
        <div class="label">Risk/Reward</div>
        <div class="value">1 : {signal_data.get('rr', 'N/A')}</div>
      </div>
    </div>

    <div class="grid">
      <div class="box">
        <div class="label">RSI</div>
        <div class="value">{signal_data.get('rsi', 'N/A')}</div>
      </div>
      <div class="box">
        <div class="label">Potrditve</div>
        <div class="value">{signal_data.get('confirmations', 'N/A')} / 3</div>
      </div>
      <div class="box">
        <div class="label">EMA 50</div>
        <div class="value">{signal_data.get('ema_fast', 'N/A')}</div>
      </div>
      <div class="box">
        <div class="label">EMA 200</div>
        <div class="value">{signal_data.get('ema_slow', 'N/A')}</div>
      </div>
    </div>

    <div class="reason">
      <strong>📊 Razlog signala:</strong><br/>
      {signal_data.get('reason', 'N/A')}
    </div>

    <div class="disclaimer">
      ⚠️ <strong>Opozorilo:</strong> Ta signal je zgolj informativne narave in ne predstavlja
      finančnega nasveta. Forex trading vključuje visoko tveganje izgube. Pretekli signali
      ne zagotavljajo prihodnjih rezultatov. Vedno upravljajte svoje tveganje.
    </div>
  </div>
  <div class="footer">
    Forex Signal Bot &nbsp;|&nbsp; Samodejno generirano &nbsp;|&nbsp; {ts_str}
  </div>
</div>
</body>
</html>
"""

    text_body = f"""
{emoji} FOREX SIGNAL: {signal} {pair_display}
{'='*40}
Timeframe:    {tf_display}
Čas:          {ts_str}

CENE:
  Vstop:      {signal_data.get('price', 'N/A')}
  Stop Loss:  {signal_data.get('sl', 'N/A')}
  Take Profit:{signal_data.get('tp', 'N/A')}
  R/R Ratio:  1:{signal_data.get('rr', 'N/A')}

INDIKATORJI:
  RSI:        {signal_data.get('rsi', 'N/A')}
  EMA 50:     {signal_data.get('ema_fast', 'N/A')}
  EMA 200:    {signal_data.get('ema_slow', 'N/A')}
  MACD Hist:  {signal_data.get('macd_hist', 'N/A')}
  Potrditve:  {signal_data.get('confirmations', 'N/A')}/3

RAZLOG:
  {signal_data.get('reason', 'N/A')}

{DISCLAIMER}
"""

    return _send_via_sendgrid_smtp(subject, html_body, text_body)


def _send_via_sendgrid_smtp(subject: str, html_body: str, text_body: str) -> bool:
    """Pošlje email preko SendGrid SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP("smtp.sendgrid.net", 587) as server:
            server.ehlo()
            server.starttls()
            server.login("apikey", SENDGRID_API_KEY)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        logger.info(f"✓ Email uspešno poslan: {subject}")
        return True
    except Exception as e:
        logger.error(f"Napaka pri pošiljanju emaila: {e}")
        return False
