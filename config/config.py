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
class Postgres:
    host: str
    port: int
    user: str
    password: str
    database: str


@dataclass
class Redis:
    host: str
    port: int
    database: str
    password: str
    username: str
@dataclass
class OpenRouter:
    token: str

@dataclass
class Config:
    bot:TgBot
    logging:Logging
    ai:OpenRouter
    pg_settings:Postgres
    redis_settings:Redis

def get_config(path:str |None= None)->Config:
    env = Env()
    env.read_env(path)
    return Config(
        TgBot(token=env("BOT_TOKEN")),
        Logging(level=env("LOG_LEVEL"), format= env("LOG_FORMAT")),
        OpenRouter(token=env("OPENROUTER_TOKEN")),
        Postgres(
            host=env("PG_HOST"),
            port=env.int("PG_PORT"),
            database=env("PG_DB"),
            user=env("PG_USER"),
            password=env("PG_PASS"),
        ),
        Redis(
            host=env("REDIS_HOST"),
            port=env.int("REDIS_PORT"),
            database=env("REDIS_DATABASE"),
            password=env("REDIS_PASSWORD"),
            username=env("REDIS_USERNAME"),
        )
    )
