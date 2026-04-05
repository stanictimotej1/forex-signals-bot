# 📈 Forex Signal Bot

Python bot ki samodejno analizira forex trg in pošilja email alertove za BUY/SELL signale.

> ⚠️ **DISCLAIMER:** Ta bot je zgolj za izobraževalne namene. Ne predstavlja finančnega nasveta.
> Forex trading vključuje visoko tveganje izgube kapitala. Pretekli signali ne zagotavljajo
> prihodnjih rezultatov. Trgujte odgovorno.

---

## 🚀 Setup

### 1. Zahteve
- Python 3.11+
- Brezplačen [Alpha Vantage API ključ](https://www.alphavantage.co/support/#api-key)
- [SendGrid](https://sendgrid.com) račun z verificiranim emailom

### 2. Namestitev
```bash
git clone <repo>
cd forex-signal-bot
pip install -r requirements.txt
```

### 3. Konfiguracija
```bash
cp .env.example .env
# Uredi .env z tvojimi podatki
```

### 4. Zagon

**Testni email** (preveri da vse deluje):
```bash
python main.py --mode test
```

**Enkratno preverjanje** vseh parov:
```bash
python main.py --mode once
```

**Scheduler** (neprekinjeno delovanje):
```bash
python main.py --mode run
```

---

## 📊 Strategija

| Indikator | BUY pogoj | SELL pogoj |
|-----------|-----------|------------|
| EMA 50/200 | EMA50 > EMA200 | EMA50 < EMA200 |
| RSI | 30–60 (ni overbought) | 40–70 (ni oversold) |
| MACD | Histogram pozitiven in rastoč | Histogram negativen in padajoč |

Signal se pošlje samo če se **vsaj 3 od 3 indikatorjev ujemajo**.

---

## 📁 Struktura projekta

```
forex-signal-bot/
├── main.py           # Vstopna točka
├── config.py         # Konfiguracija iz .env
├── data_fetcher.py   # Alpha Vantage API
├── indicators.py     # EMA, RSI, MACD, ATR
├── signal_engine.py  # BUY/SELL logika
├── email_service.py  # SendGrid email
├── state_manager.py  # Preprečevanje duplikatov
├── scheduler.py      # APScheduler
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⏱️ Intervali preverjanja

| Timeframe | Interval |
|-----------|----------|
| 15M | vsakih 15 min |
| 1H | vsakih 60 min |
| 4H | vsakih 4 ure |

---

## 📬 Primer email signala

```
Subject: [FOREX SIGNAL] 🟢 BUY EUR/USD 1H

Vstop:       1.08542
Stop Loss:   1.08100
Take Profit: 1.09200
R/R Ratio:   1:1.67

RSI:         45.2
EMA 50:      1.08300
EMA 200:     1.07800
Potrditve:   3/3

Razlog: EMA50 > EMA200 | RSI bullish cona | MACD pozitiven
```

---

## ⚠️ Omejitve Alpha Vantage (brezplačni plan)

- 25 klicev / dan
- 5 parov × 3 timeframe = 15 klicev na preverjanje
- Priporočilo: preverjaj maks 1-2x na dan ali nadgradi plan

---

## 🔒 Varnost

- Nikoli ne commitaj `.env` v git
- Dodaj `.env` v `.gitignore`
- API ključe rotiraj redno
