from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_callback_inline_keyboard(*args, width:int=1) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    buttons:list[InlineKeyboardButton] = []
    if args:
        for btn in args:
            buttons.append(InlineKeyboardButton(
                text = btn,
                callback_data=btn
            ))
    kb.row(*buttons, width=width)
    return kb.as_markup()

