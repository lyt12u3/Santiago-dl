import asyncio
from datetime import datetime, timedelta
from aiogram.types import ReplyKeyboardMarkup
from loader import db, links, bot, notify_lectures, notify, display, display_new, subjects, ADMINS, marks
from aiogram.utils import exceptions
from aiogram.utils.markdown import hlink
from utils.utilities import datetime_now, additionalDebug, datePrint, type_optimize

async def notify_process(wait_for):
    while True:
        for group in notify_lectures:
            if len(notify_lectures[group]) > 0:
                lecture = notify_lectures[group][0]

                # Lecture name get
                lectures_list = lecture.info
                # lecture_name2 = escapeMarkdown(lecture.name2)

                # Time get
                current_time = datetime_now()
                year = current_time.year
                month = current_time.month
                day = current_time.day
                hour = current_time.time().hour

                # Creating target time to notify
                target_time = datetime.strptime(f"{year}.{month}.{day} {lecture.startTime()}", "%Y.%m.%d %H:%M")
                left_time = target_time - current_time
                additionalDebug(f"TARGET: {lecture.info} {group} {target_time} LEFT: {left_time}")

                # Deleting if lecture already processed
                if left_time < timedelta(minutes=4):
                    datePrint(f"{lecture.info[0][0]} у {group} уже была в {lecture.startTime()}. Удаление")
                    notify_lectures[group].pop(0)
                elif left_time <= timedelta(minutes=5):
                    group_userlist = db.get_users_in_group(group)
                    # print(f"group_list:")
                    for userlist in group_userlist:
                        send = False

                        notify_message_header_list = []
                        notify_message_types_list = []
                        notify_message_links = ""
                        marklinks = ""

                        user = userlist[0]
                        # print(user)

                        for lecture_info in lectures_list:
                            lecture_name = lecture_info[0]
                            lecture_type = lecture_info[1]
                            if not notify.notify_exist(user, group, lecture_name):
                                notify.add_notify(user, group, lecture_name, db.get_notify_status(user))
                            if notify.get_notify(user, group, lecture_name):
                                # print(f"user {user} has notify for {lecture_name}")
                                if not display_new.display_exist(user, group, lecture_name):
                                    display_new.add_display(user, group, lecture_name)
                                if display_new.has_positive_display(user, group, lecture_name):
                                    # print(f"user {user} has display for {lecture_name}")
                                    send = True
                                    # print(f"send = {send}\n\n")
                                    notify_message_header_list.append(f"<b>{lecture_name}</b>")
                                    notify_message_types_list.append([lecture_name, lecture_type])
                                    placeholder = lecture_name
                                    if len(lectures_list) == 1:
                                        placeholder = 'тик'
                                    if links.link_exist(user, group, lecture_name, lecture_type):
                                        notify_message_links = notify_message_links + f"{hlink(placeholder, links.get_link(user, group, lecture_name, lecture_type))} "
                                    if marks.marklink_exist(group, lecture_name, lecture_type):
                                        marklinks = marklinks + f"{hlink(placeholder, marks.get_marklink(group, lecture_name, lecture_type))} "
                        if send:
                            notify_message_header = ", ".join(notify_message_header_list)
                            types = type_optimize(notify_message_types_list)
                            if len(notify_message_links) < 1:
                                notify_message_links = "Не додано"
                            marklinks_line = ""
                            if len(marklinks) > 0:
                                marklinks_line = f"\n📌 Відмітитись: {marklinks}\n"
                            await sendNotify(user, group,f'🔔 <b>{notify_message_header}</b> через <b>5</b> хвилин! 🔔\n\n⏰ Час: {lecture.startTime()} - {lecture.endTime()}\n📖 Тип: {types}\n🔗 Посилання: {notify_message_links}{marklinks_line}')
                    notify_lectures[group].pop(0)

        try:
            await asyncio.sleep(wait_for)
        except:
            break

async def sendNotify(user, group, text):
    try:
        await bot.send_message(user, text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=menu_buttons(user))
        datePrint(f'Уведомление {group} отправлено в чат {user}')
    except exceptions.ChatNotFound:
        datePrint(f'Чат {user} не найден. Уведомление не отправлено')
        # await bot.send_message(728227124, f'🚨 ChatNotFound 🚨\n\nПользователь: {user}')
    except exceptions.CantParseEntities as e:
        datePrint('Ошибка Markdown')
        username = ''
        try:
            us = await bot.get_chat(user)
            username = '@' + us.username
        except Exception as e:
            username = "Unknown"
        await bot.send_message(728227124, f'🚨 Markdown Error 🚨\n\nПользователь: {user} {username}\n\n{e.args[0]}')
    except exceptions.BotBlocked as e:
        datePrint('Ошибка Bot Blocked')
        # await bot.send_message(728227124, f'🚨 Bot Blocked 🚨\n\nПользователь: {el[0]}\n\n{e.args[0]}')
    except Exception as e:
        datePrint(f'Неизвестная ошибка {e.args[0]}')
        await bot.send_message(728227124, f'🚨 Unknown Error 🚨\n\nПользователь: {user}\n\n{e.args[0]}')


def menu_buttons(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Пари на сьогодні').insert('Пари на завтра').insert('Пари на тиждень')
    markup.add('Обрати дату')
    markup.add('Розклад викладача')
    markup.add('⚙️ Налаштування')
    if user_id in ADMINS:
        markup.insert('⚙️ Админка')
    return markup