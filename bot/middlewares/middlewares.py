from aiogram import BaseMiddleware

class DBMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        data['conn'] = data['bot']['conn']
        return handler(event,data)