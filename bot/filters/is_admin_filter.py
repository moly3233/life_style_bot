from aiogram.types import Message
from aiogram.filters import BaseFilter


class AdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        admins = ['960517920']
        return str(message.from_user.id) in admins