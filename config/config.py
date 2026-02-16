from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str

@dataclass
class Logging:
    level: str
    format: str

@dataclass
class OpenRouter:
    token: str

@dataclass
class Config:
    bot:TgBot
    logging:Logging
    ai:OpenRouter

def get_config(path:str |None= None)->Config:
    env = Env()
    env.read_env(path)
    return Config(
        TgBot(token=env("BOT_TOKEN")),
        Logging(level=env("LOG_LEVEL"), format= env("LOG_FORMAT")),
        OpenRouter(token=env("OPENROUTER_TOKEN"))
    )
