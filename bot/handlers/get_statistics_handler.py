from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile, FSInputFile
from aiogram.enums import ChatAction
from keyboards.inline_keyboards_builder import get_callback_inline_keyboard
from handlers.load_every_day_report_handler import start_process
from psycopg import AsyncConnection
from utils.generate_chart import generate_mood_chart_image
from database.queries import get_date_mood_for, get_all_day_descriptions_for
from promts.every_day_report import prompt_period_report
from api_openrouter.api_openrouter import get_ai


statistics_router = Router()


@statistics_router.callback_query(F.data== 'Статистика')
async def statistics_menu(callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.message.answer_photo(
        photo = FSInputFile('/Users/moly/life_style_bot/bot/media/statistics.png'),
        caption= '✅ Выбери по каким отчетам ты хочешь получить статистику',
        reply_markup= get_callback_inline_keyboard(
            'По ежедневным отчетам за неделю',
            'По ежедневным отчетам за месяц',
            '🔙 В начало'
        )
    )

@statistics_router.callback_query(F.data == 'По ежедневным отчетам за неделю')
async def get_every_day_report_for_week(callback_query: CallbackQuery,conn: AsyncConnection):
    await callback_query.message.delete()
    dates, moods = await get_date_mood_for(conn, callback_query.from_user.id, days=7)
    chart_bytes = await generate_mood_chart_image(dates, moods)
    data= await get_all_day_descriptions_for(conn, callback_query.from_user.id, days=7)
    if chart_bytes is None:
        await callback_query.answer("Нет данных или ошибка построения графика")
        return

    await callback_query.message.answer_photo(
        photo=BufferedInputFile(file=chart_bytes, filename="mood_chart.png"),
        caption="График настроения за неделю",
        chat_action=ChatAction.TYPING
    )

    await callback_query.message.answer(
        get_ai(prompt_period_report(data, 'неделю')),
    )

    await start_process(callback_query.message, conn)


@statistics_router.callback_query(F.data == 'По ежедневным отчетам за месяц')
async def get_every_day_report_for_month(callback_query: CallbackQuery,conn: AsyncConnection):
    await callback_query.message.delete()
    dates, moods = await get_date_mood_for(conn, callback_query.from_user.id, days=30)
    chart_bytes = await generate_mood_chart_image(dates, moods)
    data = await get_all_day_descriptions_for(conn, callback_query.from_user.id, days=30)


    if chart_bytes is None:
        await callback_query.answer("Нет данных или ошибка построения графика")
        return

    await callback_query.message.answer_photo(
        photo=BufferedInputFile(file=chart_bytes, filename="mood_chart.png"),
        caption="График настроения за месяц",
        chat_action=ChatAction.TYPING
    )

    await callback_query.message.answer(
        get_ai(prompt_period_report(data, 'месяц')),
    )

    await start_process(callback_query.message, conn)


