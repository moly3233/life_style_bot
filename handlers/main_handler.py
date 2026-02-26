from aiogram import Router,F
from aiogram.types import Message
from aiogram.filters import Command


main_router = Router()

@main_router.message(Command('Start'))
async def start_process(message: Message):
    await message.answer('Привет, пока идет разработка,функционала нет')

