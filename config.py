from dataclasses import dataclass

from environs import Env


@dataclass
class Config:
    token: str
    sentry_dsn: str
    admin_id: list
    message_id: int
    channel_id: list


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
            token=env.str("BOT_TOKEN"),
            sentry_dsn=env.str("SENTRY_DSN"),
            admin_id=list(map(int, env.list("ADMIN_ID"))),
            message_id=env.int("MESSAGE_ID"),
            channel_id=list(map(str, env.list("CHANNEL_ID")))
        )
