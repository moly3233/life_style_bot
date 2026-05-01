from aiogram.types import BotCommand
from aiogram import Bot

async def get_commands(bot: Bot):
    try:
        commands = [
            BotCommand(command='/start', description='Запустить/перезагрузить бота'),
            BotCommand(command='/getInfo', description='Информация о боте')
        ]
        await bot.set_my_commands(commands)
        print("Команды успешно установлены.")
    except Exception as e:
        print(f"Ошибка при установке команд: {e}")