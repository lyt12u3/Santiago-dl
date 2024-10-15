import datetime
import re
from datetime import timedelta
from aiogram import types
from data import config
from keyboards import menu_buttons, month_buttons, another_day_buttons, settings_buttons, admin_settings_buttons, choose_group_buttons
from loader import dp, db, week_lectures, ADMINS, display
from states import AdminSettings, UserWait
from utils import parser
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.utilities import datetime_now, formatDate, format_lectures, debug, format_week, group_check


@dp.message_handler(text='Пари на сьогодні')
async def today(message: types.Message):
    if not group_check(message.from_user.id):
        await UserWait.nure_group.set()
        await message.answer('Для роботи бота потрібно обрати свою групу', reply_markup=choose_group_buttons())
        return
    group = db.get_group(message.from_user.id)
    now = datetime_now()
    day, month, year = formatDate(now)
    weekday = now.weekday()
    start = now - timedelta(days=weekday)
    end = now + timedelta(days=6 - weekday)
    keys = list(week_lectures.keys())
    if group in keys:
        day_keys = list(week_lectures[group].keys())
        if f"{day}.{month}.{year}" in day_keys:
            week_lectures_to_send = week_lectures[group]
        else:
            week_lectures_to_send = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)
    else:
        week_lectures_to_send = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)

    lectures = format_lectures(day, month, year, message.from_user.id, week_lectures_to_send[f"{day}.{month}.{year}"][1:])
    try:
        await message.answer(lectures, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        await message.answer(f'🚨 Unknown Error 🚨\n\n{e.args[0]}')
    debug(f"today lectures used by {message.from_user.id} from {group}")

@dp.message_handler(text='Пари на завтра')
async def tomorrow(message: types.Message):
    if not group_check(message.from_user.id):
        await UserWait.nure_group.set()
        await message.answer('Для роботи бота потрібно обрати свою групу', reply_markup=choose_group_buttons())
        return
    date = datetime_now() + timedelta(days=1)
    day, month, year = formatDate(date)
    weekday = date.weekday()
    start = date - timedelta(days=weekday)
    end = date + timedelta(days=6 - weekday)
    group = db.get_group(message.from_user.id)
    keys = list(week_lectures.keys())
    if group in keys:
        day_keys = list(week_lectures[group].keys())
        if f"{day}.{month}.{year}" in day_keys:
            week_lectures_to_send = week_lectures[group]
        else:
            week_lectures_to_send = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)
    else:
        week_lectures_to_send = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)

    lectures = format_lectures(day, month, year, message.from_user.id, week_lectures_to_send[f"{day}.{month}.{year}"][1:])
    try:
        await message.answer(lectures, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        await message.answer(f'🚨 Unknown Error 🚨\n\n{e.args[0]}')
    debug(f"tomorrow lectures used by {message.from_user.id} from {group}")

kb = InlineKeyboardMarkup(row_width=2)
kb.add(InlineKeyboardButton(text='⬅️', callback_data="week_back"))
kb.insert(InlineKeyboardButton(text='➡️', callback_data="week_forward"))

current_week = {}

@dp.message_handler(text='Пари на тиждень')
async def week(message: types.Message):
    if not group_check(message.from_user.id):
        await UserWait.nure_group.set()
        await message.answer('Для роботи бота потрібно обрати свою групу', reply_markup=choose_group_buttons())
        return
    group = db.get_group(message.from_user.id)
    now = datetime_now()
    weekday = now.weekday()
    start = now - timedelta(days=weekday)
    end = now + timedelta(days=6 - weekday)
    global current_week
    current_week[message.from_user.id] = start
    keys = list(week_lectures.keys())
    if group not in keys:
        week_lectures[group] = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)
    lectures = await format_week(message.from_user.id, group)
    await message.answer(lectures, parse_mode="HTML", reply_markup=kb)
    debug(f"week lectures used by {message.from_user.id} from {group}")

@dp.callback_query_handler(text="week_forward")
async def week_forward(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    group = db.get_group(user_id)

    global current_week
    start = current_week[user_id] + timedelta(days=7)
    current_week[user_id] = start

    end = start + timedelta(days=6)
    week_days = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)

    day, month, year = formatDate(datetime_now())
    date = f"{day}.{month}.{year}"
    lectures = f"📆 {list(week_days.keys())[0]} - {list(week_days.keys())[-1]}\n\n"
    for day in week_days:
        visible_counter = 0
        if date == day:
            lectures += f"<b>👉 {week_days[day][0]} {day} 👈</b>\n"
        else:
            lectures += f"<b>{week_days[day][0]} {day}</b>:\n"
        if len(week_days[day]) > 1:
            for lecture in week_days[day][1:]:
                for lecture_info in lecture.info:
                    lecture_name = lecture_info[0]
                    lecture_type = lecture_info[1]
                    if display.has_display(user_id, group, lecture_name):
                        lectures += f" {lecture.index}️⃣ ⏰ {lecture.startTime()}-{lecture.endTime()} 📚 <b>{lecture_name}</b> {lecture_type}\n"
                        visible_counter += 1
        else:
            lectures += "В цей день пар немає 🥰\n"
            visible_counter += 1
        if visible_counter < 1:
            lectures += "В цей день пар немає 🥰\n"
        lectures += "\n"

    await callback.message.edit_text(lectures, parse_mode="HTML", reply_markup=kb)

@dp.callback_query_handler(text="week_back")
async def week_forward(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    group = db.get_group(user_id)

    global current_week
    start = current_week[user_id] - timedelta(days=7)
    current_week[user_id] = start

    end = start + timedelta(days=6)
    week_days = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)

    day, month, year = formatDate(datetime_now())
    date = f"{day}.{month}.{year}"
    lectures = f"📆 {list(week_days.keys())[0]} - {list(week_days.keys())[-1]}\n\n"
    for day in week_days:
        visible_counter = 0
        if date == day:
            lectures += f"<b>👉 {week_days[day][0]} {day} 👈</b>\n"
        else:
            lectures += f"<b>{week_days[day][0]} {day}</b>:\n"
        if len(week_days[day]) > 1:
            for lecture in week_days[day][1:]:
                for lecture_info in lecture.info:
                    lecture_name = lecture_info[0]
                    lecture_type = lecture_info[1]
                    if display.has_display(user_id, group, lecture_name):
                        lectures += f" {lecture.index}️⃣ ⏰ {lecture.startTime()}-{lecture.endTime()} 📚 <b>{lecture_name}</b> {lecture_type}\n"
                        visible_counter += 1
        else:
            lectures += "В цей день пар немає 🥰\n"
            visible_counter += 1
        if visible_counter < 1:
            lectures += "В цей день пар немає 🥰\n"
        lectures += "\n"

    await callback.message.edit_text(lectures, parse_mode="HTML", reply_markup=kb)

@dp.message_handler(text='Обрати дату')
async def choose_date(message: types.Message):
    if not group_check(message.from_user.id):
        await UserWait.nure_group.set()
        await message.answer('Для роботи бота потрібно обрати свою групу', reply_markup=choose_group_buttons())
        return
    if (not db.user_exists(message.from_user.id)):
        return
    await message.answer('📆 Виберіть дату\n\nДоступні наступні 30 днів', reply_markup=month_buttons())

@dp.callback_query_handler(lambda call: re.match(r'day_(.+)', call.data))
async def callback_day(callback: types.CallbackQuery):
    callback_date = callback.data.replace('day_', '')
    day, month, year = callback_date.split('.')
    date = datetime.datetime(int(year), int(month), int(day))
    weekday = date.weekday()
    start = date - timedelta(days=weekday)
    end = date + timedelta(days=6 - weekday)
    group = db.get_group(callback.from_user.id)
    keys = list(week_lectures.keys())
    if group in keys:
        day_keys = list(week_lectures[group].keys())
        if f"{day}.{month}.{year}" in day_keys:
            week_lectures_to_send = week_lectures[group]
        else:
            week_lectures_to_send = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)
    else:
        week_lectures_to_send = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)

    lectures = format_lectures(day, month, year, callback.from_user.id,week_lectures_to_send[f"{day}.{month}.{year}"][1:])
    try:
        await callback.message.edit_text(lectures, parse_mode="HTML", disable_web_page_preview=True, reply_markup=another_day_buttons)
    except Exception as e:
        await callback.message.edit_text(f'🚨 Unknown Error 🚨\n\n{e.args[0]}', reply_markup=another_day_buttons)
    debug(f"date lectures used by {callback.from_user.id} from {group} on {day}.{month}.{year}")

@dp.callback_query_handler(text='another_day')
async def callback_another_day(callback: types.CallbackQuery):
    await callback.message.answer('📆 Виберіть дату\n\nДоступні наступні 30 днів', reply_markup=month_buttons())

@dp.callback_query_handler(text='back')
async def callback_back(callback: types.CallbackQuery):
    day, month, year = formatDate(datetime_now())
    await callback.message.answer(f'📆 Дата: {day}.{month}.{year}\n\nВиберіть дію', reply_markup=menu_buttons(callback.from_user.id))

@dp.message_handler(text='⚙️ Налаштування')
async def settings(message: types.Message):
    if not group_check(message.from_user.id):
        await UserWait.nure_group.set()
        await message.answer('Для роботи бота потрібно обрати свою групу', reply_markup=choose_group_buttons())
        return
    await message.answer("⚙️ Виберіть дію", reply_markup=settings_buttons(message.from_user.id))

@dp.message_handler(text='⚙️ Админка')
async def admin_settings(message: types.Message):
    if message.from_user.id in ADMINS:
        if not group_check(message.from_user.id):
            await UserWait.nure_group.set()
            await message.answer('Для роботи бота потрібно обрати свою групу', reply_markup=choose_group_buttons())
            return
        await AdminSettings.SettingsMenu.set()
        await message.answer("Виберіть дію", reply_markup=admin_settings_buttons)