import asyncio
import logging

import sentry_sdk
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import load_config, Config

logger = logging.getLogger(__name__)


async def send_message_to_channel(bot: Bot):
    config: Config = bot.get("config")
    for channel_id in config.channel_id:
        try:
            await bot.copy_message(from_chat_id=config.admin_id, message_id=bot.get("config"), chat_id=channel_id)
            await asyncio.sleep(0.5)
        except:
            pass


async def get_mess(m: Message):
    config: Config = m.bot.get("config")
    if m.from_user.id in config.admin_id:
        m.bot['msg_id'] = m.message_id
        await m.answer("O'zgartirildi ✅")


def set_scheduled_jobs(scheduler, bot):
    scheduler.add_job(send_message_to_channel, "interval", args=[bot], hours=1, timezone="Asia/Tashkent")


async def main():
    logging.basicConfig(
        level=logging.WARNING,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config: Config = load_config(".env")
    sentry_sdk.init(
        dsn=config.sentry_dsn,
        traces_sample_rate=1.0
    )

    bot = Bot(token=config.token, parse_mode='HTML')
    bot['config'] = config
    dp = Dispatcher(bot, storage=MemoryStorage())
    dp.register_message_handler(get_mess)
    scheduler = AsyncIOScheduler()
    set_scheduled_jobs(scheduler, bot)

    # start
    try:
        scheduler.start()
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
