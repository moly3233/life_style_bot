from aiogram import Router
from aiogram.types import Message


other_router = Router()

@other_router.message()
async def other_message_answer(message: Message):
    await message.answer('Неизвестная команда. Совет - общайтесь по кнопкам!')