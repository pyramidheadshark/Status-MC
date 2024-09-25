import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from mcstatus import JavaServer
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "7753867805:AAFr-XlfnVivR9URMxi0-GEk-PSQFriJBFY"
USER_IDS = [5121976638, 290812347]  # список ID пользователей
SERVER_ADDRESS = "mc.kseoni.ch"
CHECK_INTERVAL = 60  # секунды

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def parse_server_address(address):
    parsed = urlparse(address)
    if parsed.netloc:
        return parsed.netloc
    return parsed.path

async def check_server():
    server_address = parse_server_address(SERVER_ADDRESS)
    try:
        server = JavaServer.lookup(server_address)
        status = await server.async_status()
        return True
    except Exception as e:
        logging.error(f"Ошибка при проверке сервера: {e}")
        return False

async def send_notification(message):
    for user_id in USER_IDS:
        try:
            await bot.send_message(user_id, message)
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

async def monitor_server():
    previous_status = True
    while True:
        current_status = await check_server()
        if previous_status and not current_status:
            await send_notification(f"⚠️ Внимание! Minecraft сервер {SERVER_ADDRESS} недоступен!")
        elif not previous_status and current_status:
            await send_notification(f"✅ Minecraft сервер {SERVER_ADDRESS} снова доступен!")
        previous_status = current_status
        await asyncio.sleep(CHECK_INTERVAL)

async def main():
    await send_notification(f"🟢 Бот запущен и мониторит сервер {SERVER_ADDRESS}.")
    monitoring_task = asyncio.create_task(monitor_server())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())