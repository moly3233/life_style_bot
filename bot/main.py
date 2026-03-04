from config.config import Config, get_config
from database.connection import get_pg_connection
from psycopg import AsyncConnection
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import parse_mode
from redis.asyncio import Redis
from handlers.other_handler import other_router
from handlers.load_every_day_report_handler import main_router
from handlers.get_every_day_reports_handler import get_reports_router
from utils.reminders import start_reminders, send_daily_remind
import asyncio
import logging


config:Config = get_config()

logging.basicConfig(level=config.logging.level,
                    format = config.logging.format)
logger = logging.getLogger(__name__)





async def main():
    logger.info('Starting bot ...')
    storage = MemoryStorage()
    # storage = RedisStorage(
    #     redis = Redis(
    #         host = config.redis_settings.host,
    #         port = config.redis_settings.port,
    #         db = config.redis_settings.database,
    #         password=config.redis_settings.password,
    #         username=config.redis_settings.username,
    #     )
    # )
    bot:Bot = Bot(token = config.bot.token,
                  default= DefaultBotProperties(parse_mode= parse_mode.ParseMode.HTML))
    dp = Dispatcher(storage = storage)
    conn:AsyncConnection = await get_pg_connection(
        config.pg_settings.database,
        config.pg_settings.user,
        config.pg_settings.password,
        config.pg_settings.host,
        config.pg_settings.port,
    )
    dp['conn'] = conn
    dp.include_router(main_router)
    dp.include_router(get_reports_router)
    dp.include_router(other_router)
    start_reminders(bot,conn)

    await dp.start_polling(bot, disable_notifications=True)
    logger.info('Bot started.')


if __name__ == '__main__':
    asyncio.run(main())
