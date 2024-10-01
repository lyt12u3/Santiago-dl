import asyncio
from aiogram import executor
from loader import dp, bot
import handlers
from utils.notify import notify_process
from utils.updater import auto_updater

async def on_startup(dispatcher):
    print("Bot is active!")

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(notify_process(5))
    loop.create_task(auto_updater(60))
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)