import logging
from aiogram import Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command, StateFilter
from psycopg import AsyncConnection
from filters.is_admin_filter import AdminFilter
from aiogram import Bot
from aiogram.filters.state import State,StateFilter, StatesGroup
from aiogram.fsm.context import FSMContext
from database.queries import get_id_users_query

logger = logging.getLogger(__name__)

admin_router = Router()

class all_message(StatesGroup):
    write_message = State()

@admin_router.message(Command('all_message'), AdminFilter())
async def all_message_mode(message:Message, state: FSMContext):
    await state.set_state(all_message.write_message)
    await message.answer('Напиши сообщение, которое будет отправлено всем')

@admin_router.message(AdminFilter(), StateFilter(all_message.write_message))
async def all_message_send(message:Message, state: FSMContext, bot:Bot, conn:AsyncConnection):
    user_ids = await get_id_users_query(conn)

    for user_id in user_ids:
        try:
            await bot.send_message(user_id, message.text)
        except:
            logger.error(f'НЕ УДАЛОСЬ ОТПРАВИТЬ СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЮ {user_id}')
    await state.clear()