import time
from datetime import datetime

import requests
import yfinance as yf

# =========================
# CONFIGURATION
# =========================

DISCORD_WEBHOOK_URL = "COLLE_TON_WEBHOOK_ICI"

# Actions à surveiller
TICKERS = [
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "NVDA",   # Nvidia
    "TSLA",   # Tesla
    "AMZN"    # Amazon
]

# Variation minimale (%) pour alerte
ALERT_THRESHOLD = 2.0

# Vérification toutes les 30 minutes
CHECK_INTERVAL = 1800

# =========================


def get_price(ticker):
    stock = yf.Ticker(ticker)

    data = stock.history(period="1d", interval="1m")

    if data.empty:
        raise Exception(f"Aucune donnée pour {ticker}")

    return float(data["Close"].iloc[-1])


def send_discord(message):
    requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": message},
        timeout=10
    )


def main():
    print("Surveillance démarrée")

    last_prices = {}

    for ticker in TICKERS:
        try:
            last_prices[ticker] = get_price(ticker)
            print(ticker, last_prices[ticker])
        except Exception as e:
            print(e)

    while True:

        for ticker in TICKERS:

            try:
                current = get_price(ticker)
                previous = last_prices[ticker]

                change = ((current - previous) / previous) * 100

                if abs(change) >= ALERT_THRESHOLD:

                    emoji = "📈" if change > 0 else "📉"

                    message = (
                        f"{emoji} **{ticker}**\n"
                        f"Variation : {change:.2f}%\n"
                        f"Prix précédent : {previous:.2f}$\n"
                        f"Prix actuel : {current:.2f}$\n"
                        f"Heure : {datetime.now():%Y-%m-%d %H:%M:%S}"
                    )

                    send_discord(message)
                    print(message)

                last_prices[ticker] = current

            except Exception as e:
                print(f"{ticker}: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()