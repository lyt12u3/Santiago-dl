from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards import cancel_buttons, menu_buttons, choose_group_buttons
from loader import dp, bot, FEEDBACK_CHAT, db
from states import UserWait
from utils.utilities import datetime_now, formatDate, group_check
from data import config
import re

@dp.message_handler(commands=['feedback'])
async def feedback_command(message: types.Message):
    if not group_check(message.from_user.id):
        await UserWait.nure_group.set()
        await message.answer('Для роботи бота потрібно обрати свою групу', reply_markup=choose_group_buttons())
        return
    await UserWait.Feedback.set()
    await message.answer('Напиши свій відгук, проблему або пропозицію для вдосконалення бота ✍️\n\nЩоб скасувати, введіть *Скасувати*', parse_mode="MarkdownV2", reply_markup=cancel_buttons)

@dp.message_handler(lambda message: message.text == "Скасувати", state=UserWait.Feedback)
async def feedback_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Дію скасовано\n\n⚙️ Виберіть дію", reply_markup=menu_buttons(message.from_user.id))

@dp.message_handler(state=UserWait.Feedback)
async def feedback_message(message: types.Message, state: FSMContext):
    try:
        user = await bot.get_chat(message.from_user.id)
        username = f'@{user.username} [{message.from_user.id}]'
    except Exception as e:
        username = f'ID:{message.from_user.id}'
    datetime = datetime_now()
    await bot.send_message(FEEDBACK_CHAT, f"⭐️ Нове повідомлення від користувача ⭐️\n\n<blockquote>{username}:\n{message.text}</blockquote>", parse_mode='HTML')
    await message.answer('Повідомлення було надіслано адміністратору ✅\n\nДякую за відгук, це дійсно важливо 🥰\n\n⚙️ Виберіть дію', reply_markup=menu_buttons(message.from_user.id))
    await state.finish()