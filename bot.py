import requests
import time
import hashlib
import json
import os
from bs4 import BeautifulSoup
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CHECK_INTERVAL = 30

URLS = {
    "Ticketmaster BTS Munich": "https://www.ticketmaster.de/artist/bts-tickets/958687",
    "TicketSwap": "https://www.ticketswap.com/"
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
}

POSITIVE_HINTS = [
    "available",
    "find tickets",
    "limited availability",
    "resale",
    "1 ticket",
]

NEGATIVE_HINTS = [
    "few or no tickets available",
    "sold out",
    "not available",
]

STATE = {}

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text[:4000],
        "disable_web_page_preview": True,
    }

    requests.post(url, data=payload, timeout=20)

def normalize(html):
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)
    text = " ".join(text.split())

    return text.lower()

def fingerprint(text):
    return hashlib.sha256(text.encode()).hexdigest()

def analyze(text):
    positive = [x for x in POSITIVE_HINTS if x in text]
    negative = [x for x in NEGATIVE_HINTS if x in text]

    return {
        "positive": positive,
        "negative": negative,
        "has_positive": len(positive) > 0,
        "has_negative": len(negative) > 0,
    }

def fetch(url):
    r = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
        allow_redirects=True,
    )

    r.raise_for_status()

    return r.text

def check(name, url):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {name}")

    try:
        html = fetch(url)
    except Exception as e:
        print(e)
        return

    text = normalize(html)

    fp = fingerprint(text)
    flags = analyze(text)

    old = STATE.get(name)

    STATE[name] = {
        "fp": fp,
        "negative": flags["has_negative"],
    }

    if old is None:
        return

    changed = old["fp"] != fp

    # найважливіший сигнал
    if old["negative"] and not flags["has_negative"]:
        message = (
            f"🚨 МОЖЛИВО BTS КВИТКИ З'ЯВИЛИСЯ\\n\\n"
            f"{name}\\n"
            f"{url}"
        )

        print(message)
        send_telegram(message)

        return

    if changed and flags["has_positive"]:
        message = (
            f"✨ Сторінка змінилась\\n\\n"
            f"{name}\\n"
            f"{url}"
        )

        print(message)
        send_telegram(message)

def main():
    send_telegram("🤖 BTS sniper started")

    while True:
        for name, url in URLS.items():
            try:
                check(name, url)
            except Exception as e:
                print(e)

            time.sleep(5)

        print(f"Sleep {CHECK_INTERVAL} sec...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
