from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from psycopg import AsyncConnection
from database.queries import get_user_bmi, change_weight_query, change_height_query
from handlers.load_every_day_report_handler import start_process
from promts.sport_tracker_promts import prompt_bmi_simple
from api_openrouter.api_openrouter import get_ai
from keyboards.inline_keyboards_builder import get_callback_inline_keyboard
from aiogram.filters.state import State,StateFilter, StatesGroup
from aiogram.fsm.context import FSMContext

tracker_imt_router = Router()

class user_states(StatesGroup):
    input_weight = State()
    input_height = State()


@tracker_imt_router.callback_query(F.data == 'Трекер ИМТ')
async def bmi_main_menu(callback_query: CallbackQuery, conn: AsyncConnection):
    await callback_query.message.delete()
    data = await get_user_bmi(conn,callback_query.from_user.id)
    if data:
        promt = prompt_bmi_simple(data['height_cm'], data['weight_kg'], data['bmi'])
        lines = [
            f"<b>🕐 Данные от:</b> {data['measured_at']}",
            f"<b>🔝 Твой рост:</b> {data['height_cm']} см",
            f"<b>⚡️ Твой вес:</b> {data['weight_kg']} кг",
            f"<b>📊 Твой ИМТ:</b> {data['bmi']}",
            "<b>🤖 Комментарий от ментора</b>",
            "--------------------------",
            get_ai(promt)
        ]

        await callback_query.message.answer(
            "\n".join(lines),
            parse_mode="HTML",
            reply_markup= get_callback_inline_keyboard(
                'Обновить данные',
                'Статистика',
                '🔙 В начало'
            )
        )
    else:
        await callback_query.message.answer('Данных о вашем росте и весе нет, можете их добавить',
                                            reply_markup=get_callback_inline_keyboard('Обновить данные')
                                            )

@tracker_imt_router.callback_query(F.data == 'Обновить данные')
async def change_parameters(callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.message.answer(
        'Что вы хотите сменить?',
        reply_markup=get_callback_inline_keyboard(
            '🔝Рост',
            '⚖️Вес',
            '🔙 В начало'
        )
    )

@tracker_imt_router.callback_query(F.data == '⚖️Вес')
async def wait_user_weight(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await state.set_state(user_states.input_weight)
    await callback_query.message.answer(
        '⚡️<i>Смена веса. Напиши свой новый вес</i>'
    )


@tracker_imt_router.message(StateFilter(user_states.input_weight), lambda x: x.text.isdigit())
async def change_weight(message: Message, state: FSMContext, conn: AsyncConnection):
    await change_weight_query(conn,
                              message.from_user.id,
                              int(message.text)
                              )
    await message.answer(f'Вес изменен на {message.text} кг')
    await state.clear()
    await start_process(message, conn)

@tracker_imt_router.message(StateFilter(user_states.input_weight), lambda x: not x.text.isdigit())
async def fail_change_weight(message: Message, ):
    await message.answer('Введите только число - ваш новый вес')

@tracker_imt_router.callback_query(F.data == '🔝Рост')
async def wait_user_height(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await state.set_state(user_states.input_height)
    await callback_query.message.answer( '⚡️<i>Смена Роста. Напиши свой новый рост</i>')

@tracker_imt_router.message(StateFilter(user_states.input_height), lambda x:  x.text.isdigit())
async def change_height(message: Message, state: FSMContext, conn: AsyncConnection):
    await change_height_query(conn,message.from_user.id, int(message.text))
    await state.clear()
    await message.answer(f'Рост изменен на {message.text} см')
    await start_process(message,conn)

@tracker_imt_router.message(StateFilter(user_states.input_height), lambda x: not x.text.isdigit())
async def fail_change_height(message: Message, ):
    await message.answer('Введите только число - ваш новый рост')

