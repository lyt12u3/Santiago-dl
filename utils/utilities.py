from datetime import datetime, timedelta
from data import config
from . import parser
from loader import week_lectures, db, links, additional_debug, subjects, display
from aiogram.utils.markdown import hlink


def formatDate(a_date):
    day = a_date.day
    month = a_date.month
    year = a_date.year
    if len(str(day)) == 1:
        day = "0" + str(day)
    if len(str(month)) == 1:
        month = "0" + str(month)
    return day, month, year

def getMonth():
    current = datetime_now()
    days = []
    for _ in range(30):
        day, month, year = formatDate(current)
        days.append(f"{day}.{month}.{year}")
        current += timedelta(days=1)
    return days

def parse_day(day, month, year, user_id, group = "КНТ-22-4"):
    parsed_lectures = parser.parseDay(day, month, year, group)
    lectures = f"📆 Дата: {day}\.{month}\.{year}\n\n"
    if len(parsed_lectures) > 0:
        lectures += f"📚 Вього пар: {len(parsed_lectures)}\n\n"
    else:
        lectures += "📚 Пар на цю дату немає\n\n"
    for lecture in parsed_lectures:
        # link = links[lecture.name]
        lecture_name = escapeMarkdown(lecture.name)
        link = "Не додано"
        if links.link_exist(user_id, db.get_group(user_id), lecture.name, lecture.f_type):
            link = f"[тик]({escapeMarkdown(links.get_link(user_id, db.get_group(user_id), lecture.name, lecture.f_type))})"
        lectures += f"📚 Назва: *{lecture_name}*\n📖 Тип: {lecture.type}\n⏰ Час: *{lecture.startTime()} \- {lecture.endTime()}*\n🔗 Посилання: {link}\n\n"
    return lectures

def format_lectures(day, month, year, user_id, week_lectures_list):
    group = db.get_group(user_id)

    if subjects.subjects_exist(group):
        current_subj_arr_line = subjects.get_subjects(group)
        current_subj_arr = current_subj_arr_line.split(',')
    else:
        current_subj_arr = parser.parseSubjects(group)
        subjects.set_subjects(group, current_subj_arr)
    if not display.display_exist(user_id, group):
        line = ",".join(current_subj_arr)
        display.set_display(user_id, group, line)

    hidden_counter = 0
    visible_counter = 0
    header_date = f"📆 Дата: {day}.{month}.{year}"
    lectures = ""
    for lecture_info in week_lectures_list:
        lectures_info_list = lecture_info.name
        link = ""
        header_list = []
        types_list = []
        if len(lectures_info_list) > 1:
            for lecture in lectures_info_list:
                lecture_name = lecture[0]
                lecture_type = lecture[1]
                if display.has_display(user_id, group, lecture_name):
                    visible_counter += 1
                    header_list.append(f" <b>{lecture_name}</b>")
                    types_list.append([lecture_name,lecture_type])
                    if links.link_exist(user_id, group, lecture_name, lecture_type):
                        link += f"{hlink(lecture_name, links.get_link(user_id, group, lecture_name, lecture_type))} "
                    if len(link) < 1:
                        link = "Не додано"
                else:
                    hidden_counter += 1
            if len(header_list) > 0:
                types = type_optimize(types_list)
                header = ", ".join(header_list)
                lectures += f"📚 Назва: {header}\n📖 Тип: {types}\n⏰ Час: <b>{lecture_info.startTime()}</b> - <b>{lecture_info.endTime()}</b>\n🔗 Посилання: {link}\n\n"
        else:
            lecture_name = lectures_info_list[0][0]
            lecture_type = type_format(lectures_info_list[0][1])
            if display.has_display(user_id, group, lecture_name):
                visible_counter += 1
                if links.link_exist(user_id, group, lecture_name, lecture_type):
                    link = hlink("[тик]", links.get_link(user_id, group, lecture_name, lecture_type))
                if len(link) < 1:
                    link = "Не додано"
                lectures += f"📚 Назва: <b>{lecture_name}</b>\n📖 Тип: <b>{lecture_type}</b>\n⏰ Час: <b>{lecture_info.startTime()}</b> - <b>{lecture_info.endTime()}</b>\n🔗 Посилання: {link}\n\n"
            else:
                hidden_counter += 1
    if visible_counter > 0:
        header_counter = f"📚 Вього пар: {visible_counter}"
        # if hidden_counter > 0:
        #     header_counter += f" (приховано {hidden_counter})"
        out_text = f"{header_date}\n\n{header_counter}\n\n{lectures}"
    else:
        header_counter = ""
        lectures = "📚 Пар на цю дату немає\n\n"
        out_text = f"{header_date}\n\n{lectures}"
    return out_text

def get_emoji(type):
    emoji = "⚪️"
    if type == "Лк":
        emoji = "🟡"
    elif type == "Пз":
        emoji = "🟢"
    elif type == "Лб":
        emoji = "🟣"
    return emoji

def type_optimize(types):
    notify_type_line_arr = []
    if len(types) > 1:
        for type_in_arr in types:
            subj_name = type_in_arr[0]
            subj_type = type_in_arr[1]
            subj_name = f"        {get_emoji(subj_type)} {subj_name}"
            notify_type_line_arr.append(f"{subj_name} {type_format(subj_type)}")
        notify_type_line = "\n" + "\n".join(notify_type_line_arr)
    else:
        notify_type_line = f"{type_format(types[0][1])}"
    return notify_type_line

def type_format(type):
    result = "Не визначено"
    if type == "Лк":
        result = "Лекція"
    elif type == "Пз":
        result = "Практичне заняття"
    elif type == "Лб":
        result = "Лабораторне заняття"
    elif type == "Конс":
        result = "Консультація"
    return result

async def format_week(user_id, group):
    if subjects.subjects_exist(group):
        current_subj_arr_line = subjects.get_subjects(group)
        current_subj_arr = current_subj_arr_line.split(',')
    else:
        current_subj_arr = parser.parseSubjects(group)
        subjects.set_subjects(group, current_subj_arr)
    if not display.display_exist(user_id, group):
        line = ",".join(current_subj_arr)
        display.set_display(user_id, group, line)

    day, month, year = formatDate(datetime_now())
    date = f"{day}.{month}.{year}"
    week_days = week_lectures[group]
    lectures = f"📆 {list(week_days.keys())[0]} - {list(week_days.keys())[-1]}\n\n"
    for day in week_days:
        visible_counter = 0
        if date == day:
            lectures += f"<b>👉 {week_days[day][0]} {day} 👈</b>\n"
        else:
            lectures += f"<b>{week_days[day][0]} {day}</b>:\n"
        if len(week_days[day]) > 1:
            for lecture in week_days[day][1:]:
                for lecture_info in lecture.name:
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
    return lectures

def get_links(user_id):
    group = db.get_group(user_id)
    if subjects.subjects_exist(group):
        current_links_arr_line = subjects.get_subjects(group)
        current_links_arr = current_links_arr_line.split(',')
    else:
        current_links_arr = parser.parseSubjects(group)
        subjects.set_subjects(group, current_links_arr)
    current_links = "🔗 Ваші посилання:\n\n"
    for el in current_links_arr:
        if links.any_link_exist(user_id, group, el):
            links_types = ""
            if links.link_exist(user_id, group, el, 'Лк'):
                lk_link = f'{links.get_link(user_id, group, el, "Лк")}'
                links_types += f"[Лк]({escapeMarkdown(lk_link)}) "
            if links.link_exist(user_id, group, el, 'Пз'):
                pz_link = f'{links.get_link(user_id, group, el, "Пз")}'
                links_types += f"[Пз]({escapeMarkdown(pz_link)}) "
            if links.link_exist(user_id, group, el, 'Лб'):
                lb_link = f'{links.get_link(user_id, group, el, "Лб")}'
                links_types += f"[Лб]({escapeMarkdown(lb_link)}) "
            # link = links.get_link(user_id, group, el)
            # full_link = f'https://meet.google.com/{link}'
            current_links += f"📚 {escapeMarkdown(el)}: {links_types}\n"
        else:
            current_links += f"📚 {escapeMarkdown(el)}: Не додано\n"
    return current_links


def formatChar(input):
    if len(str(input)) == 1:
        input = "0" + str(input)
    return input

def escapeMarkdown(text):
    characters = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for character in characters:
        text = text.replace(character, f"\\{character}")
    return text

def debug(log):
    if config.debug:
        now = datetime_now()
        message = f'[{formatChar(now.hour)}:{formatChar(now.minute)}:{formatChar(now.second)}]: {log}'
        print(message)

def datePrint(text):
    now = datetime_now()
    message = f'[{formatChar(now.hour)}:{formatChar(now.minute)}:{formatChar(now.second)}]: {text}'
    print(message)

def additionalDebug(text):
    # if additional_debug:
    #     now = datetime_now()
    #     message = f'[{formatChar(now.hour)}:{formatChar(now.minute)}:{formatChar(now.second)}]: {text}'
    #     print(f"{message}"
    now = datetime_now()
    message = f'[{formatChar(now.hour)}:{formatChar(now.minute)}:{formatChar(now.second)}]: {text}'
    print(f"{message}")

def datetime_now():
    return datetime.now()