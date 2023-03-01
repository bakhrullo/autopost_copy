import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import load_config, Config

import sentry_sdk


logger = logging.getLogger(__name__)


async def send_message_to_channel(bot: Bot, config: Config):
    for channel_id in config.channel_id:
        try:
            await bot.copy_message(from_chat_id=config.admin_id, message_id=config.message_id, chat_id=channel_id)
            await asyncio.sleep(0.5)
            print("succes")
        except Exception as e:
            print(e)
    print("end")


def set_scheduled_jobs(scheduler, bot, config):
    scheduler.add_job(send_message_to_channel, "interval", args=(bot, config),
                      seconds=10, timezone="Asia/Tashkent")


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

    storage = MemoryStorage()
    bot = Bot(token=config.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)
    scheduler = AsyncIOScheduler()
    set_scheduled_jobs(scheduler, bot, config)

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
