import os
import sys
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from dotenv import dotenv_values
from django.core.wsgi import get_wsgi_application



# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biotact.settings')
print("DJANGO_SETTINGS_MODULE =", os.environ.get('DJANGO_SETTINGS_MODULE'))  # Логирование

application = get_wsgi_application()

# Инициализация бота
config_token = dotenv_values(".env")
bot_token = config_token['BOT_TOKEN']
bot = Bot(token=bot_token)
dp = Dispatcher()
default = DefaultBotProperties(parse_mode='HTML')

from handlers.bot_commands import main_router, callback_router2, broadcast_router
from handlers.callback_queries import callback_router
from handlers.payment import payment_router


async def main():
    dp.include_router(main_router)
    dp.include_router(callback_router)
    dp.include_router(callback_router2)
    dp.include_router(payment_router)
    dp.include_router(broadcast_router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
