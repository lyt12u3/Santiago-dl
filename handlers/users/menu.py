import datetime
import re
from datetime import timedelta
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from data import config
from keyboards import menu_buttons, month_buttons, another_day_buttons, settings_buttons, admin_settings_buttons, choose_group_buttons, select_teachers, cancel_buttons
from loader import dp, db, week_lectures, ADMINS, display, display_new, teachers, all_teachers, bot, year_lectures
from states import AdminSettings, UserWait
from utils import parser, updater
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.parser import parse_teacher_week
from utils.utilities import datetime_now, formatDate, format_lectures, debug, format_week, group_check, format_teachers_schedule


@dp.message_handler(Text(contains='Пари на сьогодні'))
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

@dp.message_handler(Text(contains='Пари на завтра'))
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

@dp.message_handler(Text(contains='Пари на тиждень'))
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
    groups = list(year_lectures.keys())
    if group not in groups:
        await updater.update_lectures_process()

    dates = []
    current = start

    while current <= end:
        dates.append(current.strftime("%d.%m.%Y"))
        current += timedelta(days=1)

    result = set(dates).issubset(set(list(year_lectures[group].keys())))
    if not result:
        week_days = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)
    else:
        week_days = {}
        for date in dates:
            week_days[date] = (year_lectures[group][date])

    # week_days = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)

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
                    if display_new.has_positive_display(user_id, group, lecture_name):
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
async def week_backward(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    group = db.get_group(user_id)

    global current_week
    start = current_week[user_id] - timedelta(days=7)
    current_week[user_id] = start

    end = start + timedelta(days=6)
    groups = list(year_lectures.keys())
    if group not in groups:
        await updater.update_lectures_process()

    dates = []
    current = start

    while current <= end:
        dates.append(current.strftime("%d.%m.%Y"))
        current += timedelta(days=1)

    result = set(dates).issubset(set(list(year_lectures[group].keys())))
    if not result:
        week_days = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)
    else:
        week_days = {}
        for date in dates:
            week_days[date] = (year_lectures[group][date])

    # week_days = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)

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
                    if display_new.has_positive_display(user_id, group, lecture_name):
                        lectures += f" {lecture.index}️⃣ ⏰ {lecture.startTime()}-{lecture.endTime()} 📚 <b>{lecture_name}</b> {lecture_type}\n"
                        visible_counter += 1
        else:
            lectures += "В цей день пар немає 🥰\n"
            visible_counter += 1
        if visible_counter < 1:
            lectures += "В цей день пар немає 🥰\n"
        lectures += "\n"

    await callback.message.edit_text(lectures, parse_mode="HTML", reply_markup=kb)

@dp.message_handler(Text(contains='Обрати дату'))
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

@dp.message_handler(Text(contains='Розклад викладача'))
async def teacher_schedule(message: types.Message):
    if not group_check(message.from_user.id):
        await UserWait.nure_group.set()
        await message.answer('Для роботи бота потрібно обрати свою групу', reply_markup=choose_group_buttons())
        return
    requested_teachers = teachers.get_teachers()
    keyboard = select_teachers(requested_teachers)
    await message.answer('📅 Щоб отримати розклад, оберіть одного з викладачів зі списку\n\nЯкщо в списку немає потрібного викладача, натисніть <b>Додати</b>', parse_mode='HTML', reply_markup=keyboard)

@dp.callback_query_handler(text='teacher_add')
async def callback_add_teacher(callback: types.CallbackQuery):
    await callback.message.answer('🥰 Введіть прізвище викладача і я подивлюсь його розклад', reply_markup=cancel_buttons)
    await UserWait.TeacherName.set()

@dp.message_handler(lambda message: message.text == "Скасувати", state=UserWait.TeacherName)
async def callback_add_teacher_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    day, month, year = formatDate(datetime_now())
    await message.answer(f'📆 Дата: {day}.{month}.{year}\n\nВиберіть дію', reply_markup=menu_buttons(message.from_user.id))

@dp.message_handler(state=UserWait.TeacherName)
async def callback_add_teacher_process(message: types.Message, state: FSMContext):
    await state.finish()

    target_teacher = message.text

    all_teachers_list = all_teachers.get_teachers()

    result = []
    for teacher in all_teachers_list:
        if target_teacher in teacher[0]:
            result.append(teacher)

    amount = len(result)
    if amount > 0:
        if amount > 1:
            keyboard = select_teachers(result, True)
            await message.answer(f"Знайдено декілька викладачів, оберіть одного з них", reply_markup=keyboard)
        else:
            teachers.add_teacher(result[0][0], result[0][1])
            await message.answer(f"✅ Викладача додано", reply_markup=menu_buttons(message.from_user.id))
            await week_result_process(message, message.from_user.id, result[0][1])
    else:
        await message.answer(f"😥 На жаль, такого викладача немає в базі")
        day, month, year = formatDate(datetime_now())
        await message.answer(f'📆 Дата: {day}.{month}.{year}\n\nВиберіть дію', reply_markup=menu_buttons(message.from_user.id))

@dp.callback_query_handler(lambda call: re.match(r'add_teacher_.+', call.data))
async def callback_teacher(callback: types.CallbackQuery):
    teacher_code = callback.data.replace("add_teacher_", "")

    name = all_teachers.get_name(teacher_code)
    teachers.add_teacher(name, teacher_code)

    await callback.message.answer(f"✅ Викладача додано", reply_markup=menu_buttons(callback.from_user.id))
    await week_result_process(callback.message, callback.from_user.id, teacher_code)

@dp.callback_query_handler(lambda call: re.match(r'^teacher_.+', call.data))
async def callback_teacher(callback: types.CallbackQuery):
    teacher_code = callback.data.replace("teacher_", "")

    await week_result_process(callback.message, callback.from_user.id, teacher_code)

current_teachers_week = {}

async def week_result_process(message, user_id, code):
    now = datetime_now()
    weekday = now.weekday()
    start = now - timedelta(days=weekday)
    end = now + timedelta(days=6 - weekday)

    global current_teachers_week
    current_teachers_week[user_id] = start

    teachers_kb = InlineKeyboardMarkup(row_width=2)
    teachers_kb.add(InlineKeyboardButton(text='⬅️', callback_data=f"teachers_week_back_{code}"))
    teachers_kb.insert(InlineKeyboardButton(text='➡️', callback_data=f"teachers_week_forward_{code}"))

    result = parse_teacher_week(start.day, start.month, start.year, end.day, end.month, end.year, code)
    teacher_name = all_teachers.get_name(code)
    line = format_teachers_schedule(result, teacher_name)
    debug(f"teachers schedule used by {user_id}")
    await message.answer(line, parse_mode="HTML", reply_markup=teachers_kb)

@dp.callback_query_handler(lambda call: re.match(r'^teachers_week_forward_.+', call.data))
async def callback_teacher(callback: types.CallbackQuery):
    code = callback.data.replace("teachers_week_forward_", "")
    user_id = callback.from_user.id

    global current_teachers_week
    start = current_teachers_week[user_id] + timedelta(days=7)
    current_teachers_week[user_id] = start
    end = start + timedelta(days=6)

    teachers_kb = InlineKeyboardMarkup(row_width=2)
    teachers_kb.add(InlineKeyboardButton(text='⬅️', callback_data=f"teachers_week_back_{code}"))
    teachers_kb.insert(InlineKeyboardButton(text='➡️', callback_data=f"teachers_week_forward_{code}"))

    result = parse_teacher_week(start.day, start.month, start.year, end.day, end.month, end.year, code)
    teacher_name = all_teachers.get_name(code)
    line = format_teachers_schedule(result, teacher_name)
    debug(f"teachers schedule used by {user_id}")
    await callback.message.edit_text(line, parse_mode="HTML", reply_markup=teachers_kb)

@dp.callback_query_handler(lambda call: re.match(r'^teachers_week_back_.+', call.data))
async def callback_teacher(callback: types.CallbackQuery):
    code = callback.data.replace("teachers_week_back_", "")
    user_id = callback.from_user.id

    global current_teachers_week
    start = current_teachers_week[user_id] - timedelta(days=7)
    current_teachers_week[user_id] = start
    end = start + timedelta(days=6)

    teachers_kb = InlineKeyboardMarkup(row_width=2)
    teachers_kb.add(InlineKeyboardButton(text='⬅️', callback_data=f"teachers_week_back_{code}"))
    teachers_kb.insert(InlineKeyboardButton(text='➡️', callback_data=f"teachers_week_forward_{code}"))

    result = parse_teacher_week(start.day, start.month, start.year, end.day, end.month, end.year, code)
    teacher_name = all_teachers.get_name(code)
    line = format_teachers_schedule(result, teacher_name)
    debug(f"teachers schedule used by {user_id}")
    await callback.message.edit_text(line, parse_mode="HTML", reply_markup=teachers_kb)

@dp.callback_query_handler(lambda call: re.match(r'^teachers_week_back_.+', call.data))
async def callback_teacher(callback: types.CallbackQuery):
    code = callback.data.replace("teachers_week_back_", "")
    user_id = callback.from_user.id

    global current_teachers_week
    start = current_week[user_id] - timedelta(days=7)
    current_week[user_id] = start
    end = start + timedelta(days=6)

    teachers_kb = InlineKeyboardMarkup(row_width=2)
    teachers_kb.add(InlineKeyboardButton(text='⬅️', callback_data=f"teachers_week_back_{code}"))
    teachers_kb.insert(InlineKeyboardButton(text='➡️', callback_data=f"teachers_week_forward_{code}"))

    result = parse_teacher_week(start.day, start.month, start.year, end.day, end.month, end.year, code)
    teacher_name = all_teachers.get_name(code)
    line = format_teachers_schedule(result, teacher_name)
    await callback.message.edit_text(line, parse_mode="HTML", reply_markup=teachers_kb)

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