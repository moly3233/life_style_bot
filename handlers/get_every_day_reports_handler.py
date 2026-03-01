from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.inline_keyboards_builder import get_callback_inline_keyboard
from database.queries import get_all_dates_query, get_report_for_date_query
from psycopg import AsyncConnection


get_reports_router = Router()

@get_reports_router.callback_query(F.data == 'Мои отчеты')
async def get_all_dates(callback_query: CallbackQuery, conn: AsyncConnection):
    dates = await get_all_dates_query(conn)
    kb = get_callback_inline_keyboard(*dates)
    await callback_query.message.answer(
        text = 'Вот все даты твоих отчетов.\nНажми на нужную, чтобы получить подробности',
        reply_markup = kb
    )

@get_reports_router.callback_query(F.data.startswith('Отчет за'))
async def get_report_for_date(callback_query: CallbackQuery, conn: AsyncConnection):
    date = callback_query.data[9:]
    report = await get_report_for_date_query(conn, date)
    lines = [
        f"🕐 Дата отчета: {report['date'].strftime('%Y/%m/%d')}",
        f"📊 Ваша оценка дня: {report['mood']}/10",
        f"✏️ Ваше описание дня: {report['day_description'].replace('\n', ' ')}",
        f"🧠 Комментарий ментора: {report['mentor_description'].replace('\n', ' ')}",
        f"📌 Ваш вывод: {report['conclusion'].replace('\n', ' ')}",
    ]

    await callback_query.message.answer("\n".join(lines))