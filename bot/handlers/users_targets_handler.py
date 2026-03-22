from aiogram import Router,F
from aiogram.types import CallbackQuery, Message, FSInputFile
from keyboards.inline_keyboards_builder import get_callback_inline_keyboard
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.fsm.context import FSMContext
from handlers.load_every_day_report_handler import start_process
from database.queries import load_target,get_active_targets_query, set_status_target_query
from psycopg import AsyncConnection

targets_router = Router()
class UsersStates(StatesGroup):
    writeTarget = State()

@targets_router.callback_query(F.data == 'Цели')
async def get_target_menu(callback_query: CallbackQuery):
    await callback_query.message.delete()
    await callback_query.bot.send_photo(
        chat_id=callback_query.message.chat.id,
        photo= FSInputFile('/Users/moly/life_style_bot/bot/media/my_targets.png'),
        caption= """В этом разделе собраны все твои цели и намерения, которые ты желаешь воплотить в свою жизнь
        Ты можешь задать новую цель, а также вычеркнуть страю, если чувствуешь, что уже воплотил ее. В
         каждом ежеденвном отчете ментор будет обращать на твои цели внимание""",
        reply_markup=get_callback_inline_keyboard(
            'Активные цели',
            'Новая цель',
            '🔙 В начало'
    )
    )


@targets_router.callback_query(F.data == 'Новая цель')
async def write_new_target(callback_query: CallbackQuery, state: FSMContext, conn:AsyncConnection):
    await callback_query.message.delete()
    await callback_query.message.answer(
        'Отлично бро. Напиши в чат свою цель или намерение, которое ты собираешься влить в свою жизнь. От 5 до 18 символов. Стоп слово - ХВАТИТ'
    )
    await state.set_state(UsersStates.writeTarget)

@targets_router.message(StateFilter(UsersStates.writeTarget), lambda x: 5< len(x.text)<18)
async def filter_new_target(message: Message, state: FSMContext, conn: AsyncConnection):
    if message.text == 'ХВАТИТ':
        await state.clear()
        await message.answer('Добавление новой цели остановлено!')
        await start_process(message,conn)
    else:
        await load_target(conn, message.from_user.id, message.text)
        await state.clear()
        await message.answer('Поздравляю, новая цель успешно добавлена')
        await start_process(message,conn)

@targets_router.message(StateFilter(UsersStates.writeTarget), lambda x: not(5< len(x.text)<18))
async def filter_new_target_bad(message: Message):
    await message.answer('Бро, от 5 до 18 символов')

@targets_router.callback_query(F.data == 'Активные цели')
async def get_active_targets(callback_query: CallbackQuery, conn: AsyncConnection):
    await callback_query.message.delete()
    targets = await get_active_targets_query(conn, callback_query.from_user.id)
    await callback_query.message.answer(
        'Вот все действующие цели. Если какой то цели ты достиг или перестал в ней нуждаться - просто нажми на нее.',
        reply_markup= get_callback_inline_keyboard(
            *targets,
            '🔙 В начало'
        )
    )

@targets_router.callback_query(F.data.startswith('~'))
async def set_target_status(callback_query: CallbackQuery, conn: AsyncConnection):
    target = callback_query.data[2:]
    await set_status_target_query(conn, callback_query.from_user.id, target)
    await callback_query.answer(f'Цель "{target}" была успешно убрана')

