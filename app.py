import asyncio
from aiogram import executor
import threading
import uvicorn
from aiogram.types import MenuButtonWebApp, WebAppInfo

from loader import dp, bot, LINK
import handlers
from utils.notify import notify_process
from utils.updater import auto_updater, update_lectures_process
from miniapp_api import app as fastapi_app

async def on_startup(dispatcher):
    print("Bot is active!")
    print("Updating...")
    await update_lectures_process()
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="Розклад",
            web_app=WebAppInfo(
                url=LINK
            )
        )
    )

def run_fastapi():
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == '__main__':
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(notify_process(5))
    loop.create_task(auto_updater(60))
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)