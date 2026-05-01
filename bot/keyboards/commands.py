from aiogram.types import BotCommand
from aiogram import Bot

async def get_commands(bot: Bot):
    try:
        commands = [
            BotCommand(command='/start', description='reload bot'),
            BotCommand(command='/info', description='bot info')
        ]
        await bot.set_my_commands(commands)
        print("Команды успешно установлены.")
    except Exception as e:
        print(f"Ошибка при установке команд: {e}")