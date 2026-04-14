from aiogram.types import Message
from aiogram.filters import BaseFilter


class isNumber(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        try:
            int(message.text)
            return True
        except ValueError:
            try:
                float(message.text)
                return True
            except ValueError:
                return False