from aiogram import Router,F
from aiogram.enums import ChatAction
from aiogram.types import Message, CallbackQuery,FSInputFile
from aiogram.filters import Command
from utils.generate_chart import generate_mood_chart_image
from keyboards.inline_keyboards_builder import get_callback_inline_keyboard
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup,StateFilter
from api_openrouter.api_openrouter import get_ai
from promts.every_day_report import promt_every_day_report
from database.queries import load_today_to_db,has_report_today, get_date_mood_for, get_active_targets_query
from psycopg import AsyncConnection

main_router = Router()
class UserStates(StatesGroup):
    mood = State()
    day_desc = State()
    conclusion = State()

@main_router.message(Command(commands='start'))
async def start_process(message: Message, conn: AsyncConnection):
    lines = [
        "<b>Привет, бро! 👊</b>",
        "",
        "Это твой личный бот для ежедневных отчётов — пиши как день прошёл, получай честный разбор от ментора и смотри, как меняется настроение со временем.",
        "",
        "Поддержка и автор — <a href=\"tg://user?id=твой_user_id\">@molypap</a> (пиши туда, если что-то сломалось или есть идеи).",
        "",
        "Давай начинать?",
        "Выбирай, что делаем сегодня:",
        "• <b>Ежедневный отчёт</b> — запиши свой день",
        "• <b>Мои отчёты</b> — глянь старые записи",
        "• <b>Статистика</b> — средний вайб и тренды",
        "• <b>Цели</b> — задай здесь свои цели",
        "• <b>Интеграция с соц сетями</b> — интегрируй этого бота с соц. сетями",
        "",
        "Жду твоего клика 🚀"
    ]

    await message.answer_photo(
                    photo = FSInputFile('/app/bot/media/main_menu.png'),
                    reply_markup= get_callback_inline_keyboard(
                        'Ежедневный отчет',
                        'Физуха',
                        'Мои отчеты',
                        'Статистика',
                        'Цели',
                        'Интеграция с соц сетями',
                    ),
        caption= '\n'.join(lines),
    )


@main_router.callback_query(F.data == 'Ежедневный отчет')
async def every_day_report(callback_query: CallbackQuery,state: FSMContext,conn: AsyncConnection):
    if await has_report_today(conn, callback_query.from_user.id):
        await callback_query.message.answer('❗️ За сегодня уже есть отчет, так что давай дождемся завтрашнего дня!')
    else:
        await callback_query.message.answer(
            'Отлично бро!\n Давай с тобой обсудим новый день. Для начала дай ему оценку от 1 до 10. Стоп слово - ВСЕ')
        await callback_query.message.delete()
        await state.clear()
        await state.set_state(UserStates.mood)


@main_router.message(lambda x: x.text.isdigit() and 0<int(x.text)<=10,StateFilter(UserStates.mood) )
async def get_mood(message: Message, state: FSMContext):
    if message.text != 'ВСЕ':
        await state.update_data(mood = int(message.text))
        await message.answer('Зафиксировали 📌\n Теперь расскажи свой день, а ментор даст тебе совет')
        await state.set_state(UserStates.day_desc)
    else:
        await state.clear()
        await message.answer('Заполение отчета сброшено!')

@main_router.message(lambda x: not x.text.isdigit() or not(0<int(x.text)<=10),StateFilter(UserStates.mood))
async def get_mood_fail(message: Message, state: FSMContext,conn: AsyncConnection):
    if message.text != 'ВСЕ':
        await message.answer('Бро! Напиши только число от 1 до 10')
    else:
        await state.clear()
        await message.answer('Заполение отчета сброшено!')
        await start_process(message,conn)

@main_router.message(lambda x: len(x.text.strip())>50, StateFilter(UserStates.day_desc))
async def get_day_desc(message: Message, state: FSMContext,conn: AsyncConnection):
    if message.text!= 'ВСЕ':
        data = await state.get_data()
        await state.update_data(day_desc = message.text)
        targets = await get_active_targets_query(conn, message.from_user.id)
        day = promt_every_day_report(data['mood'], message.text,targets)
        await message.bot.send_chat_action(
            chat_id= message.chat.id,
            action=ChatAction.TYPING
        )
        mentor_desc = get_ai(day)
        await message.answer(
           mentor_desc,
        )
        await message.answer('Теперь, какой ты вывод сделаешь для себя?')
        await state.update_data(mentor_desc = mentor_desc)
        await state.set_state(UserStates.conclusion)
    else:
        await state.clear()
        await message.answer('Заполение отчета сброшено!')
        await start_process(message, conn)

@main_router.message(lambda x: not len(x.text.strip())>50, StateFilter(UserStates.day_desc))
async def get_day_desc_fail(message: Message, state: FSMContext):
    if message.text!= 'ВСЕ':
        await message.answer('Бро, твой отчет короткий. Минимум 51 символ')
    else:
        await state.clear()
        await message.answer('Заполение отчета сброшено!')



@main_router.message(StateFilter(UserStates.conclusion))
async def get_conclusion(message: Message, state: FSMContext, conn:AsyncConnection):
    data = await state.get_data()
    await load_today_to_db(conn,message.from_user.id, data['mood'], data['day_desc'], data['mentor_desc'],message.text)
    await message.answer(
        'Спасибо за твой отчет! Надеюсь ты вынес из этого свои выводы. Этот отчет сохарнился, ты можешь посмотреть его в любое время',
    )
    await state.clear()
    await start_process(message,conn)