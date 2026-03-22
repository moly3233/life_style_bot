from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from psycopg import AsyncConnection
from bot.keyboards.inline_keyboards_builder import get_callback_inline_keyboard
from aiogram.filters.state import State, StatesGroup,StateFilter
from aiogram.fsm.context import FSMContext
from handlers.load_every_day_report_handler import start_process
from bot.api_openrouter.api_openrouter import get_ai
from bot.promts.sport_tracker_promts import prompt_training_mentor
from bot.database.queries import load_user_training_query,get_trainings_dates,get_training_info_query



sport_traker = Router()
class user_states(StatesGroup):
    input_training_name = State()
    input_mood_before = State()
    input_training_log = State()
    input_mood_after = State()
    input_feelings_after = State()

@sport_traker.callback_query(F.data == 'Физуха')
async def sport_traker_menu(callback_query: CallbackQuery):
   await callback_query.message.delete()
   await callback_query.bot.send_photo(
       chat_id=callback_query.message.chat.id,
       photo= FSInputFile('/Users/moly/life_style_bot/bot/media/pe.png'),
       caption= 'Здесь ты полностью можешь сосредоточиться на одной из твоих форм жизни - теле. Тренируй его, следи за ним.',
       reply_markup=get_callback_inline_keyboard(
           'Добавить тренировку',
           'Мои тренировки',
           'Трекер ИМТ',
           '🔙 В начало'
       )
   )


@sport_traker.callback_query(F.data == 'Добавить тренировку')
async def start_fsm_sport_traker(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    await callback_query.message.answer(
        'Я рад, что ты провел тренировку. Теперь расскажи как оно было.\n Сейчас напиши ее название, например "Силовая верх" или "Бег на улице". Стоп слово - ВСЕ'
    )
    await state.set_state(user_states.input_training_name)

@sport_traker.message(StateFilter(user_states.input_training_name), lambda x: len(x.text) >=5)
async def input_training_name_process(message: Message, state: FSMContext,):
    await state.update_data(training_name=message.text)
    await state.set_state(user_states.input_mood_before)
    await message.answer('Отлично бро 😎! Давай продолжим. Как ты оценивал свое состояние до тренировки? Введи только число от 1 до 10')

@sport_traker.message(StateFilter(user_states.input_training_name), lambda x: len(x.text)<5)
async def fail_input_name(message: Message, state: FSMContext,conn:AsyncConnection):
    if message.text == 'ВСЕ':
        await state.clear()
        await start_process(message, conn)
        await message.answer('Заполнение тренировки прервано!')
    else:
        await message.answer('Бро, название меньше 5 букв не подходит, нужно больше 5')

@sport_traker.message(StateFilter(user_states.input_mood_before), lambda x: x.text.isdigit() and 1<=int(x.text)<=10)
async def input_mood_before_process(message:Message, state:FSMContext):
    await state.update_data(mood_before = int(message.text))
    await state.set_state(user_states.input_training_log)
    await message.answer('🔥 Переходим дальше. Теперь распиши свою тренировку. Пример: жим лежа 4x10, бег 2 км')

@sport_traker.message(StateFilter(user_states.input_mood_before), lambda x: not(x.text.isdigit()) or not(1<=int(x.text)<=10))
async def fail_input_mood_before(message:Message, state:FSMContext,conn:AsyncConnection):
    if message.text == 'ВСЕ':
        if message.text == 'ВСЕ':
            await state.clear()
            await start_process(message, conn)
            await message.answer('Заполнение тренировки прервано!')
    else:
        await message.answer('Бро напиши ТОЛЬКО ЦИФРУ')

@sport_traker.message(StateFilter(user_states.input_training_log), lambda x: len(x.text)>=5)
async def input_training_log_process(message:Message, state:FSMContext):
    await state.update_data(training_log=message.text)
    await state.set_state(user_states.input_mood_after)
    await message.answer('Спасибо за описание! Теперь напиши оценку своего состояния после тренировки')

@sport_traker.message(StateFilter(user_states.input_training_log), lambda x: len(x.text)<5)
async def fail_input_training_log(message:Message, state:FSMContext,conn:AsyncConnection):
    if message.text == 'ВСЕ':
        if message.text == 'ВСЕ':
            await state.clear()
            await start_process(message, conn)
            await message.answer('Заполнение тренировки прервано!')
    else:
        await message.answer('Бро, описание меньше 5 букв не подходит, нужно больше 5')

@sport_traker.message(StateFilter(user_states.input_mood_after), lambda x: lambda x: x.text.isdigit() and 1<=int(x.text)<=10)
async def input_mood_after_process(message:Message, state:FSMContext):
    await state.update_data(mood_after = int(message.text))
    await state.set_state(user_states.input_feelings_after)
    await message.answer('Осталось чуть - чуть. Напиши свои ощущения после тренировки. Например, что то болит, есть сомнения или эмоции')

@sport_traker.message(StateFilter(user_states.input_mood_after), lambda x: not(x.text.isdigit()) or not(1<=int(x.text)<=10))
async def fail_input_mood_after(message:Message, state:FSMContext,conn:AsyncConnection):
    if message.text == 'ВСЕ':
        if message.text == 'ВСЕ':
            await state.clear()
            await start_process(message, conn)
            await message.answer('Заполнение тренировки прервано!')
    else:
        await message.answer('Бро напиши ТОЛЬКО ЦИФРУ')

@sport_traker.message(StateFilter(user_states.input_feelings_after), lambda x: len(x.text)>=5)
async def input_feelings_after_process(message:Message, state:FSMContext,conn:AsyncConnection):
    await state.update_data(feelings_after = message.text)
    await message.answer('Спасибо за твою сводку! Твой наставник уже получил данные, жди ответа')

    data = await state.get_data()
    promt = prompt_training_mentor(
        data['mood_before'],
        data['training_name'],
        data['training_log'],
        data['mood_after'],
        data['feelings_after'],
        )
    response = get_ai(promt)

    await load_user_training_query(
        conn,
        message.from_user.id,
        data['training_name'],
        data['mood_before'],
        data['training_log'],
        data['mood_after'],
        data['feelings_after'],
        response
    )

    await message.answer(response)
    await state.clear()
    await start_process(message, conn)

@sport_traker.message(StateFilter(user_states.input_feelings_after), lambda x: len(x.text)<5)
async def fail_input_feelings_after(message:Message, state:FSMContext,conn:AsyncConnection):
    if message.text == 'ВСЕ':
        await state.clear()
        await start_process(message, conn)
        await message.answer('Заполнение тренировки прервано!')
    else:
        await message.answer('Бро, описание меньше 5 букв не подходит, нужно больше 5')

@sport_traker.callback_query(F.data == 'Мои тренировки')
async def get_my_trainings(callback_query:CallbackQuery, conn:AsyncConnection):
    await callback_query.message.delete()
    data = await get_trainings_dates(conn,callback_query.from_user.id)
    await callback_query.bot.send_photo(
        chat_id=callback_query.message.chat.id,
        photo=FSInputFile('/Users/moly/life_style_bot/bot/media/my_trainings.png'),
        caption= '🏋️ Вот все твои тренировки',
        reply_markup= get_callback_inline_keyboard(
            *data,
            '🔙 В начало'
        )
    )


@sport_traker.callback_query(F.data.startswith('Тренировка за '))
async def get_training_info(callback_query:CallbackQuery, conn:AsyncConnection):
    await callback_query.message.delete()
    data = await get_training_info_query(conn,
                                         callback_query.from_user.id,
                                         callback_query.data[14:]
                                         )
    lines = [
        f"🕐 <strong>Дата тренировки</strong>: {data['date']}",
        f"🏋️<strong> Название</strong>: {data['training_name']}",
        f"😌<strong> Настроение до </strong>: {data['mood_before']}/10",
        f"📝<strong> Что делал:</strong>",
        f"{data['training_log']}",
        f"🔥<strong> Настроение / ощущения после </strong>: {data['mood_after']}/10",
        f"<i>{data['feelings_after'] or 'Не указано'}</i>",
        "",
        "🤖<strong> Комментарий ментора </strong>:",
        "--------------------------",
        data['mentor_comment'] or "Ментор пока не прокомментировал"
    ]

    await callback_query.message.answer("\n".join(lines),
                                        parse_mode='HTML',
                                        reply_markup=get_callback_inline_keyboard('🔙 В начало'))