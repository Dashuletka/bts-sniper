import asyncio
import os
from playwright.async_api import async_playwright
from telegram import Bot

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

last_content = {}


async def check_page(page, item):
    name = item["name"]
    url = item["url"]

    print(f"Checking: {name}")

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        content = await page.content()

        # якщо сторінка блокує доступ
        if "403" in content.lower() or "forbidden" in content.lower():
            print(f"403 blocked: {url}")
            return

        # перший запуск
        if url not in last_content:
            last_content[url] = content
            print(f"Saved first snapshot: {name}")
            return

        # якщо сторінка реально змінилась
        if content != last_content[url]:
            print(f"CHANGE DETECTED: {name}")

            await bot.send_message(
                chat_id=CHAT_ID,
                text=(
                    f"🎟 Зміни на сторінці!\n\n"
                    f"{name}\n"
                    f"{url}"
                )
            )

            last_content[url] = content

    except Exception as e:
        print(f"ERROR ({name}): {e}")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )

        page = await browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )

        while True:
            for item in URLS:
                await check_page(page, item)

            print("Sleep 30 sec...")
            await asyncio.sleep(30)


asyncio.run(main())
