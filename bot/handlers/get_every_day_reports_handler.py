from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline_keyboards_builder import get_callback_inline_keyboard
from database.queries import get_all_dates_query, get_report_for_date_query
from psycopg import AsyncConnection


get_reports_router = Router()

@get_reports_router.callback_query(F.data == 'Мои отчеты')
async def get_all_dates(callback_query: CallbackQuery, conn: AsyncConnection):
    dates = await get_all_dates_query(conn, callback_query.from_user.id)
    kb = get_callback_inline_keyboard(*dates)
    await callback_query.message.answer(
        text = 'Вот все даты твоих отчетов.\nНажми на нужную, чтобы получить подробности',
        reply_markup = kb
    )

@get_reports_router.callback_query(F.data.startswith('Отчет за'))
async def get_report_for_date(callback_query: CallbackQuery, conn: AsyncConnection):
    date = callback_query.data[9:]
    report = await get_report_for_date_query(conn, date, callback_query.from_user.id)
    lines = [
        f"🕐 <strong>Дата отчета: </strong> {report['date'].strftime('%Y/%m/%d')}",
        f"📊 <strong>Ваша оценка дня: </strong> {report['mood']}/10",
        f"✏️ <strong>Ваше описание дня: </strong> {report['day_description'].replace('\n', ' ')}",
        f"🧠 <strong>Комментарий ментора: </strong> <i>{report['mentor_description'].replace('\n', ' ')}</i>",
        f"📌 <strong>Ваш вывод: </strong> {report['conclusion'].replace('\n', ' ')}",
    ]

    await callback_query.message.answer("\n".join(lines), parse_mode='HTML')