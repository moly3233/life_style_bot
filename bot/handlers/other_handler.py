from aiogram import Router, F
from aiogram.types import Message, CallbackQuery


other_router = Router()

@other_router.message()
async def other_message_answer(message: Message):
    await message.answer('Неизвестная команда. Совет - общайтесь по кнопкам!')


@other_router.callback_query(F.data == 'У вас пока нет отчетов')
async def answer_callback(query: CallbackQuery):
    await query.answer('Мы ждем твои отчеты, друг. Ты можешь заполнить его прямо сейчас!')