from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline_keyboards_builder import get_callback_inline_keyboard
from environs import Env
import requests

env = Env()
news_handler = Router()

env.read_env()
TOKEN = env.str("NEWSDATAIO_TOKEN")



CATEGORIES = {
    "тема: 🌍 Мир": f"https://newsdata.io/api/1/latest?apikey={TOKEN}&language=ru&category=world",

    "тема: 🇷🇺 Россия / Главное": f"https://newsdata.io/api/1/latest?apikey={TOKEN}&country=ru&language=ru&category=top",

    "тема: 📍 Москва": f"https://newsdata.io/api/1/latest?apikey={TOKEN}&country=ru&language=ru&q=Москва",

    "тема: 🏛 Политика": f"https://newsdata.io/api/1/latest?apikey={TOKEN}&country=ru&language=ru&category=politics",
    "тема: 💰 Экономика": f"https://newsdata.io/api/1/latest?apikey={TOKEN}&country=ru&language=ru&category=business",
    "тема: 🚨 Происшествия": f"https://newsdata.io/api/1/latest?apikey={TOKEN}&country=ru&language=ru&category=crime",
    "тема: 🤖 Технологии": f"https://newsdata.io/api/1/latest?apikey={TOKEN}&country=ru&language=ru&category=technology",
    "тема: 🧪 Наука": f"https://newsdata.io/api/1/latest?apikey={TOKEN}&country=ru&language=ru&category=science",
    "тема: 🏥 Здоровье": f"https://newsdata.io/api/1/latest?apikey={TOKEN}&country=ru&language=ru&category=health",
    "тема: ⚽ Спорт": f"https://newsdata.io/api/1/latest?apikey={TOKEN}&country=ru&language=ru&category=sports",
    "тема: 🎬 Культура": f"https://newsdata.io/api/1/latest?apikey={TOKEN}&country=ru&language=ru&category=entertainment",
    "тема: 🌱 Экология": f"https://newsdata.io/api/1/latest?apikey={TOKEN}&country=ru&language=ru&category=environment",
    "тема: 🎓 Образование": f"https://newsdata.io/api/1/latest?apikey={TOKEN}&country=ru&language=ru&category=education",
    "тема: ✈️ Туризм": f"https://newsdata.io/api/1/latest?apikey={TOKEN}&country=ru&language=ru&category=tourism",
    "тема: 🧘 Стиль жизни": f"https://newsdata.io/api/1/latest?apikey={TOKEN}&country=ru&language=ru&category=lifestyle",
}



@news_handler.callback_query(F.data == 'Новости')
async def get_categories(callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.message.answer(
        'Выберите пожулайста нужную тему и я с радостью выдам тебе новость',
        reply_markup=get_callback_inline_keyboard(*CATEGORIES.keys())
    )


@news_handler.callback_query(F.data.startswith('тема:'))
async def get_news(callback_query: CallbackQuery):
    await callback_query.message.delete()
    link = CATEGORIES[callback_query.data]
    response = requests.get(link).json()
    await callback_query.message.answer(response)