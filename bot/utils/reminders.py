from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from psycopg import AsyncConnection
from database.queries import get_all_tg_id_query
import logging

scheduler: AsyncIOScheduler = None
logger = logging.getLogger(__name__)

async def send_daily_remind(bot:Bot, conn: AsyncConnection):
    users_id = await get_all_tg_id_query(conn)

    for user_id in users_id:
        try:
            await bot.send_message(
               user_id,
                "Бро, вечер на дворе 🌙\n"
                "Как день прошёл? Жду твой отчёт 👊\n\n"
                "Пиши /start → Ежедневный отчёт"
            )
        except Exception as e:
            logger.error(e)

def start_reminders(bot:Bot,conn:AsyncConnection, timezone: str = 'Europe/Moscow'):
    global scheduler
    scheduler = AsyncIOScheduler(timezone=timezone)

    scheduler.add_job(
        send_daily_remind,
        args = (bot,conn),
        trigger = CronTrigger(hour = 22, minute= 0),
        id = 'send_daily_remind',
        replace_existing = True
    )

    scheduler.start()
    logger.info('Напоминания запущены')