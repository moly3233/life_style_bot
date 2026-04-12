from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.fsm.context import FSMContext
from keyboards.inline_keyboards_builder import get_callback_inline_keyboard
from psycopg import AsyncConnection
from utils.validate_tokens import validate_notion_token
from database.queries import input_notion_token_query, insert_user_to_users_integrations
from handlers.load_every_day_report_handler import start_process



integrations_router = Router()

class InputNotionToken(StatesGroup):
    wait_token = State()

@integrations_router.callback_query(F.data == 'Интеграция с соц сетями')
async def integrations_menu(callback_query: CallbackQuery, conn: AsyncConnection):
    await callback_query.message.delete()
    await insert_user_to_users_integrations(conn, callback_query.from_user.id)
    await callback_query.message.answer(
        "Здесь ты сможешь интегрировать бота с другими сервисами.\n Выбери один из доступных!",
        reply_markup= get_callback_inline_keyboard(
            "Notion",
            "🔙 В начало"
        )
    )

@integrations_router.callback_query(F.data == 'Notion')
async def wait_notion_token(callback_query: CallbackQuery, state: FSMContext):
    text = (
        "🔌 Подключение Notion\n\n"
        "Чтобы бот мог записывать твои ежедневные отчёты, тренировки и вес прямо в твой Notion-календарь, нужно подключить интеграцию.\n\n"
        "Как это сделать:\n"
        "1. Перейди по ссылке: https://www.notion.so/my-integrations\n"
        "2. Нажми \"New integration\"\n"
        "3. Дай любое название (например \"Life Style Bot\")\n"
        "4. Выбери нужный workspace\n"
        "5. Скопируй Internal Integration Token (начинается с secret_...)\n\n"
        "Отправь мне этот токен одним сообщением."
        "Если передумал - пиши СТОП"
    )
    await callback_query.message.delete()
    await callback_query.message.answer(
        text = text,
    )
    await state.set_state(InputNotionToken.wait_token)

@integrations_router.message(StateFilter(InputNotionToken.wait_token))
async def input_notion_token(message: Message, state: FSMContext, conn: AsyncConnection):
    token = message.text.strip()

    if token.lower() == 'стоп':
        await state.clear()
        await message.answer("Отмена операции")
        await start_process(message, conn)
        return

    if not validate_notion_token(token):
        await message.answer("Токен невалидный или истёк.")
        return

    try:
        await input_notion_token_query(conn, str(message.from_user.id), token)
        await message.answer("✅ Notion токен привязан")
        await state.clear()
        await start_process(message, conn)
    except Exception as err:
        await message.answer("Возникла ошибка с привязкой токена")

