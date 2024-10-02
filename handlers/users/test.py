from datetime import timedelta
from aiogram import types
from loader import dp, db, week_lectures
from utils import parser
from utils.utilities import datetime_now, debug, format_week, escapeMarkdown, formatDate
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

kb = InlineKeyboardMarkup(row_width=2)
kb.add(InlineKeyboardButton(text='⬅️', callback_data="week_back"))
kb.insert(InlineKeyboardButton(text='➡️', callback_data="week_forward"))

current_week = {}

@dp.message_handler(commands=['week_test'])
async def week(message: types.Message):
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
    lectures = await format_week(group)
    await message.answer(lectures, parse_mode="MarkdownV2", reply_markup=kb)
    debug(f"week lectures used by {message.from_user.id} from {group}")

@dp.callback_query_handler(text="week_forward")
async def week_forward(callback: types.CallbackQuery):
    group = db.get_group(callback.from_user.id)

    global current_week
    start = current_week[callback.from_user.id] + timedelta(days=7)
    current_week[callback.from_user.id] = start

    end = start + timedelta(days=6)
    week_days = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)

    day, month, year = formatDate(datetime_now())
    date = f"{day}.{month}.{year}"
    lectures = f"📆 {escapeMarkdown(list(week_days.keys())[0])} \- {escapeMarkdown(list(week_days.keys())[-1])}\n\n"
    for day in week_days:
        if date == day:
            lectures += f"*👉 {week_days[day][0]} {escapeMarkdown(day)} 👈*\n"
        else:
            lectures += f"*{week_days[day][0]} {escapeMarkdown(day)}*:\n"
        if len(week_days[day]) > 1:
            for lecture in week_days[day][1:]:
                lecture_name = escapeMarkdown(lecture.info)
                lectures += f" *{lecture.index}️⃣* ⏰ {lecture.startTime()}\-{lecture.endTime()} 📚 *{lecture_name}* {lecture.f_type}\n"
        else:
            lectures += "В цей день пар немає 🥰\n"
        lectures += "\n"

    await callback.message.edit_text(lectures, parse_mode="MarkdownV2", reply_markup=kb)

@dp.callback_query_handler(text="week_back")
async def week_forward(callback: types.CallbackQuery):
    group = db.get_group(callback.from_user.id)

    global current_week
    start = current_week[callback.from_user.id] - timedelta(days=7)
    current_week[callback.from_user.id] = start

    end = start + timedelta(days=6)
    week_days = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)

    day, month, year = formatDate(datetime_now())
    date = f"{day}.{month}.{year}"
    lectures = f"📆 {escapeMarkdown(list(week_days.keys())[0])} \- {escapeMarkdown(list(week_days.keys())[-1])}\n\n"
    for day in week_days:
        if date == day:
            lectures += f"*👉 {week_days[day][0]} {escapeMarkdown(day)} 👈*\n"
        else:
            lectures += f"*{week_days[day][0]} {escapeMarkdown(day)}*:\n"
        if len(week_days[day]) > 1:
            for lecture in week_days[day][1:]:
                lecture_name = escapeMarkdown(lecture.info)
                lectures += f" *{lecture.index}️⃣* ⏰ {lecture.startTime()}\-{lecture.endTime()} 📚 *{lecture_name}* {lecture.f_type}\n"
        else:
            lectures += "В цей день пар немає 🥰\n"
        lectures += "\n"

    await callback.message.edit_text(lectures, parse_mode="MarkdownV2", reply_markup=kb)