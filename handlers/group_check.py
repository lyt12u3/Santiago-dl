from aiogram import types
from loader import dp, db, groups, groups_list, week_lectures, notify_lectures, bot, FEEDBACK_CHAT

@dp.message_handler(lambda message: message.chat.id == FEEDBACK_CHAT)
async def chat_handler(message: types.Message):
    await message.answer('Мені не дуже зручно виконувати свої основні функціх у груповому чаті. Використовуйте, будь ласка, особистий чат зі мною.')

@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_chat_member(message: types.Message):
    for new_member in message.new_chat_members:
        if new_member.id == (await bot.me).id:
            if message.chat.id != FEEDBACK_CHAT:
                await message.answer("Вибачте, я не можу знаходитись у цьому чаті 😣")
                await bot.leave_chat(message.chat.id)
            else:
                await message.answer("Привіт 👋 \n\nРадий, що нарешті вийшов з особистого чату 😁\nЯ буду автоматично надсилати відгуки від користувачів у цей чат ✍️")