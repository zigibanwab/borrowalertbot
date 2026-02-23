import requests
from bs4 import BeautifulSoup
import os
import json

# Configuration
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TICKERS = ["AAOI", "BBAI", "FSLR", "MP", "MSTR", "NVDA", "QBTS", "UUUU"]
DATA_FILE = "last_rates.json"

def get_rate(ticker):
    try:
        url = f"https://iborrowdesk.com/report/{ticker}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Scrape the first fee value from the summary table
        fee_row = soup.find("table").find_all("td")[1]
        return float(fee_row.text.replace('%', ''))
    except:
        return None

def send_alert(ticker, change):
    msg = f"Alert: the borrow rate for {ticker} has moved by {change:.2f}%"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}"
    requests.get(url)

# 1. Load previous rates
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        old_rates = json.load(f)
else:
    old_rates = {}

new_rates = {}

# 2. Check each ticker
for t in TICKERS:
    current = get_rate(t)
    if current is not None:
        new_rates[t] = current
        if t in old_rates:
            old = old_rates[t]
            percent_change = ((current - old) / old) * 100
            if abs(percent_change) >= 5.0:
                send_alert(t, percent_change)

# 3. Save current rates for next time
with open(DATA_FILE, "w") as f:
    json.dump(new_rates, f)
