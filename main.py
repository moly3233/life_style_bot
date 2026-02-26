from config.config import Config, get_config
from database.connection import get_pg_connection
from psycopg import AsyncConnection
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import parse_mode
from redis.asyncio import Redis
import asyncio
import logging


config:Config = get_config()

logging.basicConfig(level=config.logging.level,
                    format = config.logging.format)
logger = logging.getLogger(__name__)
async def main():
    logger.info('Starting bot ...')

    storage = RedisStorage(
        redis = Redis(
            host = config.redis_settings.host,
            port = config.redis_settings.port,
            db = config.redis_settings.database,
            password=config.redis_settings.password,
            username=config.redis_settings.username,
        )
    )
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


asyncio.run(main())
