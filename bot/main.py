from config.config import Config, get_config
from database.connection import get_pg_connection
from psycopg import AsyncConnection
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import parse_mode
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import os
import asyncio
import logging
from keyboards.commands import get_commands
from handlers.other_handler import other_router
from handlers.load_every_day_report_handler import main_router
from handlers.get_every_day_reports_handler import get_reports_router
from handlers.get_statistics_handler import statistics_router
from handlers.users_targets_handler import targets_router
from handlers.sport_traker_handler import sport_traker
from handlers.get_news_handler import news_handler
from handlers.tracker_imt_handler import tracker_imt_router
from handlers.admins_handler import admin_router
from handlers.integrations_hanler import integrations_router
from utils.reminders import start_reminders

config: Config = get_config()

logging.basicConfig(level=config.logging.level, format=config.logging.format)
logger = logging.getLogger(__name__)


async def main():
    logger.info('Starting bot ...')

    storage = MemoryStorage()

    bot: Bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=parse_mode.ParseMode.HTML)
    )

    dp = Dispatcher(storage=storage)

    conn: AsyncConnection = await get_pg_connection(
        config.pg_settings.database,
        config.pg_settings.user,
        config.pg_settings.password,
        config.pg_settings.host,
        config.pg_settings.port,
    )


    await get_commands(bot)

    dp['conn'] = conn
    dp['bot'] = bot

    dp.include_router(main_router)
    dp.include_router(get_reports_router)
    dp.include_router(statistics_router)
    dp.include_router(targets_router)
    dp.include_router(news_handler)
    dp.include_router(sport_traker)
    dp.include_router(tracker_imt_router)
    dp.include_router(integrations_router)
    dp.include_router(admin_router)
    dp.include_router(other_router)

    start_reminders(bot, conn)


    WEBHOOK_PATH = "/webhook"
    BASE_URL = os.getenv("RENDER_EXTERNAL_URL")

    await bot.delete_webhook(drop_pending_updates=True)
    webhook_url = f"{BASE_URL.rstrip('/')}{WEBHOOK_PATH}"
    await bot.set_webhook(webhook_url)

    app = web.Application()

    async def home(request):
        return web.Response(text="Bot is running")

    async def health(request):
        return web.json_response({"status": "ok"})

    app.router.add_get("/", home)
    app.router.add_get("/health", health)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    port = int(os.getenv("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host='0.0.0.0', port=port)
    await site.start()

    logger.info(f"Bot started on port {port}")
    await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(main())