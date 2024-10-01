from datetime import datetime, timedelta
from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards import choose_group_buttons, menu_buttons, cancel_buttons
from loader import dp, db, groups, groups_list, week_lectures, notify_lectures, bot
from states import UserWait
from utils import parser
from utils.utilities import formatDate, datetime_now, debug

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    if (not db.user_exists(message.from_user.id)):
        debug(f"/start used by non-registered user {message.from_user.id}")
        print(message.from_user.id)
        await UserWait.nure_group.set()
        await message.answer('Привіт 👋\nДля роботи бота потрібно обрати свою групу', reply_markup=choose_group_buttons())
    else:
        debug(f"/start used by registered user {message.from_user.id}")
        day, month, year = formatDate(datetime_now())
        await message.answer(f'📆 Дата: {day}.{month}.{year}\n\nВиберіть дію', reply_markup=menu_buttons(message.from_user.id))

@dp.callback_query_handler(text="no_group", state=UserWait.nure_group)
async def add_group_start(callback: types.CallbackQuery):
    await UserWait.add_group.set()
    await callback.message.answer("🎓 Введіть вашу групу\n\nПриклад: *КНТ-22-4*\nАбо напишіть *Скасувати*", parse_mode="Markdown", reply_markup=cancel_buttons)

@dp.message_handler(text="Скасувати", state=UserWait.add_group)
async def process_add_group_invalid(message: types.Message):
    await message.answer("Дію скасовано")
    await message.answer('Для роботи бота потрібно обрати свою групу', reply_markup=choose_group_buttons())
    await UserWait.nure_group.set()

@dp.message_handler(lambda message: message.text in groups_list.get_groups()[0], state=UserWait.add_group)
async def process_add_group_invalid(message: types.Message):
    return await message.reply("Обрана група не підтримується 🫤\nБудь ласка, введіть вірну назву або напишіть *Скасувати*", reply_markup=cancel_buttons)

@dp.message_handler(state=UserWait.add_group)
async def process_add_group(message: types.Message, state: FSMContext):
    code = groups_list.get_code(message.text)
    groups.add_group(message.text, code)
    db.add_user(message.from_user.id, message.text, True)
    all_users = len(db.read_all())

    current_time = datetime_now()
    day, month, year = formatDate(current_time)
    weekday = current_time.weekday()
    start = current_time - timedelta(days=weekday)
    end = current_time + timedelta(days=6 - weekday)
    week_lectures[message.text] = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, message.text)
    notify_lectures[message.text] = week_lectures[message.text][f"{day}.{month}.{year}"][1:]

    await message.answer(f"Доступ надано ✅\n\nВи обрали групу *{message.text}* та додали її до списку активних груп, тож інші користувачі теж можуть її обрати 🥰\n\n🎓 Тепер ви можете дивитись розклад та отримувати повідомлення перед початком пари!", parse_mode="Markdown")
    await message.answer(f'📆 Дата: {day}.{month}.{year}\n\nВиберіть дію', reply_markup=menu_buttons(message.from_user.id))
    await state.finish()
    debug(f"group {message.text} added by {message.from_user.id} on register")
    await bot.send_message(728227124, f"📈 Новий користувач: {message.from_user.full_name} [{message.from_user.id}]\n🎓 Група: {message.text}\n\n👥 Всього користувачів: {all_users}")

@dp.callback_query_handler(text_contains="group:", state=UserWait.nure_group)
async def process_nure_group(callback: types.CallbackQuery, state: FSMContext):
    group = callback.data.replace("group:", "")
    if group in groups.get_groups_names():
        db.add_user(callback.from_user.id, group, True)
        all_users = len(db.read_all())

        await callback.message.answer('Доступ надано ✅\n\n🎓 Тепер ви можете дивитись розклад та отримувати повідомлення перед початком пари!', parse_mode="Markdown")
        day, month, year = formatDate(datetime_now())
        await callback.message.answer(f'📆 Дата: {day}.{month}.{year}\n\nВиберіть дію', reply_markup=menu_buttons(callback.from_user.id))
        await state.finish()
        debug(f"group {group} selected by {callback.from_user.id} on register")
        await bot.send_message(728227124, f"📈 Новий користувач: {callback.from_user.full_name} [{callback.from_user.id}]\n🎓 Група: {group}\n\n👥 Всього користувачів: {all_users}")
    else:
        return await callback.message.answer("Обрана група не підтримується 🫤\nБудь ласка, виберіть групу з представлених")