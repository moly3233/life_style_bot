from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.handlers.load_every_day_report_handler import start_process


other_router = Router()

@other_router.message()
async def other_message_answer(message: Message):
    await message.answer('Неизвестная команда. Совет - общайтесь по кнопкам!')


@other_router.callback_query(F.data == 'У вас пока нет отчетов')
async def answer_callback(query: CallbackQuery):
    await query.answer('Мы ждем твои отчеты, друг. Ты можешь заполнить его прямо сейчас!')

@other_router.callback_query(F.data=='🔙 В начало')
async def to_begin_process(callback: CallbackQuery,conn):
    await callback.message.delete()
    await start_process(callback.message,conn)