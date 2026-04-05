name: Forex Signal Bot

on:
  schedule:
    # London + New York overlap: 13:00-18:00 UTC = 15:00-20:00 CEST (poletni čas)
    # Vsako uro, ponedeljek-petek
    - cron: '0 13,14,15,16,17,18 * * 1-5'
  workflow_dispatch:

jobs:
  run-bot:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repozitorija
        uses: actions/checkout@v4

      - name: Nastavi Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Namesti odvisnosti
        run: pip install -r requirements.txt

      - name: Zaženi forex signal bota
        env:
          ALPHA_VANTAGE_API_KEY: ${{ secrets.ALPHA_VANTAGE_API_KEY }}
          SENDGRID_API_KEY: ${{ secrets.SENDGRID_API_KEY }}
          EMAIL_FROM: ${{ secrets.EMAIL_FROM }}
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
          LOG_LEVEL: INFO
        run: python main.py --mode once
