import asyncio
from datetime import timedelta

from aiogram.types import InputMediaDocument

from loader import groups, week_lectures, notify_lectures, subjects, bot, BACKUP_CHAT, year_lectures
from . import parser
from .utilities import datetime_now, formatDate, debug, datePrint

async def auto_updater(wait_for):
    while True:
        current_time = datetime_now()
        day, month, year = formatDate(current_time)
        hour = current_time.time().hour
        minute = current_time.time().minute

        weekday = current_time.weekday()
        start = current_time - timedelta(days=weekday)
        end = current_time + timedelta(days=6 - weekday)

        if int(hour) == 0 and int(minute) == 0:
            if weekday == 6:
                date = current_time.strftime("%d.%m.%Y")
                media = [
                    InputMediaDocument(media=open("database.db", "rb"), caption=f"Dump {date}"),
                    InputMediaDocument(media=open("all_groups.db", "rb")),
                ]
                await bot.send_media_group(chat_id=BACKUP_CHAT, media=media)
            all_groups = groups.get_groups()
            start_date, end_date = parser.get_semester_dates()
            for group in all_groups:
                debug(f"Автоматическое обновление {group[0]}:")
                try:
                    debug("Получение актуальных предметов группы")
                    current_links_arr = parser.parseSubjects(group[0], start_date, end_date)
                    subjects.set_subjects(group[0], current_links_arr)
                    debug("Получение расписания на год")
                    year_lectures[group[0]] = parser.parseYear(group[0])
                    debug("Получение расписания")
                    week_lectures[group[0]] = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group[0])
                    notify_lectures[group[0]] = week_lectures[group[0]][f"{day}.{month}.{year}"][1:]
                except Exception as e:
                    print(f"Error updating group {group[0]}: {e.args[0]}")
        await asyncio.sleep(wait_for)

async def update_lectures_process():
    current_time = datetime_now()
    day, month, year = formatDate(current_time)


    weekday = current_time.weekday()
    start = current_time - timedelta(days=weekday)
    end = current_time + timedelta(days=6 - weekday)

    all_groups = groups.get_groups()

    start_date, end_date = parser.get_semester_dates()
    for group in all_groups:
        datePrint(f"Загрузка {group[0]}...")
        try:
            debug("Получение актуальных предметов группы")
            current_links_arr = parser.parseSubjects(group[0], start_date, end_date)
            subjects.set_subjects(group[0], current_links_arr)
            debug("Получение расписания на год")
            year_lectures[group[0]] = parser.parseYear(group[0])
            debug("Получение расписания")
            week_lectures[group[0]] = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group[0])
            notify_lectures[group[0]] = week_lectures[group[0]][f"{day}.{month}.{year}"][1:]
        except Exception as e:
            print(f"Error updating group {group[0]}: {e.args[0]}")