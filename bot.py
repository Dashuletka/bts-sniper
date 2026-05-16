import asyncio
from playwright.async_api import async_playwright
from telegram import Bot
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=BOT_TOKEN)

URLS = [
    {
        "name": "Ticketmaster BTS Munich",
        "url": "https://www.ticketmaster.de/artist/bts-tickets/958687"
    },

    {
        "name": "BTS Munich 11 July 2026",
        "url": "https://www.ticketswap.com/concert-tickets/bts-munich-allianz-arena-2026-07-11-CX6shmt4gwPx9g8nDxRcf"
    },

    {
        "name": "BTS Munich 12 July 2026",
        "url": "https://www.ticketswap.com/concert-tickets/bts-munich-allianz-arena-2026-07-12-CXNexsCWNaYDBiWKZnpGw"
    }
]

GOOD_WORDS = [
    "available",
    "tickets",
    "buy",
    "from",
    "vip",
    "resale"
]


async def check_page(page_info):
    print(f"\nChecking: {page_info['name']}")

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        page = await browser.new_page()

        await page.set_extra_http_headers({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0 Safari/537.36"
            )
        })

        try:
            await page.goto(
                page_info["url"],
                timeout=60000,
                wait_until="networkidle"
            )

            content = (await page.content()).lower()

            found = []

            for word in GOOD_WORDS:
                if word in content:
                    found.append(word)

            if found:

                text = (
                    f"🚨 BTS КВИТКИ МОЖЛИВО З'ЯВИЛИСЬ!\n\n"
                    f"{page_info['name']}\n"
                    f"{page_info['url']}\n\n"
                    f"Знайдено слова:\n"
                    f"{', '.join(found)}"
                )

                print(text)

                await bot.send_message(
                    chat_id=CHAT_ID,
                    text=text
                )

            else:
                print("Нічого не знайдено")

        except Exception as e:
            print(f"Помилка: {e}")

        await browser.close()


async def main():

    await bot.send_message(
        chat_id=CHAT_ID,
        text="🤖 BTS sniper bot запущений!"
    )

    while True:

        for page_info in URLS:
            await check_page(page_info)

        print("\nSleep 30 sec...\n")

        await asyncio.sleep(30)


asyncio.run(main())
