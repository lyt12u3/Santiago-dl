import re
from datetime import timedelta

from aiogram import types
from aiogram.types import InputMediaDocument
from aiogram.dispatcher import FSMContext
from keyboards import admin_settings_buttons, menu_buttons, delete_group_buttons, users_list_buttons, editor_types_markup, editor_choose_markup, reply_editor_subjects, editor_automate, editor_finish, marklinks_buttons, subjects_buttons_marks, \
    links_types_delete, links_types, marklinks_types_delete, marklinks_types, cancel_buttons
from loader import dp, db, groups, bot, week_lectures, notify_lectures, all_teachers, subjects, marks, BACKUP_CHAT, \
    subjects_info
from states import AdminSettings
from utils import parser, Lecture
from utils.parser import parse_all_teachers
from utils.updater import update_lectures_process
from utils.utilities import formatDate, datetime_now, escapeMarkdown, formatWeekday, formatChar, make_unique, get_marklinks

@dp.message_handler(text="Сделать бекап", state=AdminSettings.SettingsMenu)
async def backup(message: types.Message):
    date = datetime_now().strftime("%d.%m.%Y")
    media = [
        InputMediaDocument(media=open("database.db", "rb"), caption=f"Dump {date}"),
        InputMediaDocument(media=open("all_groups.db", "rb")),
    ]
    await bot.send_media_group(chat_id=BACKUP_CHAT, media=media)
    await message.answer("Бекап отправлен в чат SantiagoDL Backup", reply_markup=admin_settings_buttons)


#############################  EXPERIMENTAL BLOCK OF CODE  ######################


@dp.message_handler(text="Отметки", state=AdminSettings.SettingsMenu)
async def link_settings(message: types.Message):
    user_id = message.from_user.id
    group = db.get_group(user_id)
    current_links = get_marklinks(user_id)
    await message.answer(current_links, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=marklinks_buttons)

@dp.callback_query_handler(lambda call: call.data in ['add_marklink', 'delete_marklink'], state=AdminSettings.SettingsMenu)
async def callback_add_link1(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_links = get_marklinks(user_id)
    await callback.message.edit_text(current_links, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=subjects_buttons_marks(callback))

@dp.callback_query_handler(text="marklink_cancel", state=AdminSettings.SettingsMenu)
async def callback_link_settings_cancel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_links = get_marklinks(user_id)
    await callback.message.edit_text(current_links, parse_mode="MarkdownV2", reply_markup=marklinks_buttons, disable_web_page_preview=True)

@dp.callback_query_handler(lambda call: re.match(r'mark_delete_.+', call.data), state=AdminSettings.SettingsMenu)
async def callback_type(callback: types.CallbackQuery):
    subject = callback.data[12:]
    await callback.message.edit_text(f'📚 Виберіть тип посилання для видалення {subject}', reply_markup=marklinks_types_delete)
    subj_del_data[callback.from_user.id] = {}
    subj_del_data[callback.from_user.id]["Subject"] = subject

@dp.callback_query_handler(lambda call: call.data in ['lk_del_mark','pz_del_mark','lb_del_mark'], state=AdminSettings.SettingsMenu)
async def callback_links(callback: types.CallbackQuery):
    if callback.data[:2] == "lk":
        type = "Лк"
    elif callback.data[:2] == "pz":
        type = "Пз"
    elif callback.data[:2] == "lb":
        type = "Лб"
    subj_del_data_local = subj_del_data.get(callback.from_user.id)
    subject = subj_del_data_local.get("Subject")
    group = db.get_group(callback.from_user.id)
    if subjects.subjects_exist(group):
        current_links_arr_line = subjects.get_subjects(group)
        current_links_arr = current_links_arr_line.split(',')
    else:
        current_links_arr = list(parser.parseSubjects(group).keys())
        subjects.set_subjects(group, current_links_arr)

        subjects_info.set_subject_info()
    if subject in current_links_arr:
        marks.delete_marklink(group, subject, type)
        await callback.message.answer("Посилання видалено", reply_markup=admin_settings_buttons)
        current_links = get_marklinks(callback.from_user.id)
        await callback.message.answer(current_links, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=marklinks_buttons)

subj_data = {}
subj_del_data = {}

@dp.callback_query_handler(lambda call: re.match(r'mark_add_.+', call.data), state=AdminSettings.SettingsMenu)
async def callback_type(callback: types.CallbackQuery):
    subject = callback.data[9:]
    # await bot.send_message(callback.from_user.id, f'📚 Виберіть тип посилання для {subject}', reply_markup=links_types)
    await callback.message.edit_text(f'📚 Виберіть тип посилання для {subject}',reply_markup=marklinks_types)
    subj_data[callback.from_user.id] = {}
    subj_data[callback.from_user.id]["Subject"] = subject

@dp.callback_query_handler(lambda call: call.data in ['lk_add_mark','pz_add_mark','lb_add_mark'], state=AdminSettings.SettingsMenu)
async def callback_links(callback: types.CallbackQuery):
    if callback.data[:2] == "lk":
        type = "Лк"
    elif callback.data[:2] == "pz":
        type = "Пз"
    elif callback.data[:2] == "lb":
        type = "Лб"
    subj_data_local = subj_data.get(callback.from_user.id)
    subject = subj_data_local.get("Subject")
    subj_data[callback.from_user.id]["Type"] = type
    group = db.get_group(callback.from_user.id)
    if subjects.subjects_exist(group):
        current_links_arr_line = subjects.get_subjects(group)
        current_links_arr = current_links_arr_line.split(',')
    else:
        current_links_arr = list(parser.parseSubjects(group).keys())
        subjects.set_subjects(group, current_links_arr)
    if subject in current_links_arr:
        line = escapeMarkdown(f"Введіть посилання на відвідування для {subject} {type}\n\nПриклад: https://dl.nure.ua/mod/attendance/view.php?id=687645")
        await bot.send_message(callback.from_user.id, f"{line}\n\nЩоб скасувати введення посилання, напишіть *Скасувати*", parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=cancel_buttons)
        await AdminSettings.LinkAdd.set()

@dp.message_handler(lambda message: message.text == "Скасувати", state=AdminSettings.LinkAdd)
async def links_settings_cancel(message: types.Message, state: FSMContext):
    await AdminSettings.SettingsMenu.set()
    await message.answer("Введення посилання скасовано", reply_markup=admin_settings_buttons)

@dp.message_handler(state=AdminSettings.LinkAdd)
async def links_settings_link_wait(message: types.Message, state: FSMContext):
    link = message.text
    user_id = message.from_user.id
    group = db.get_group(user_id)
    subj_data_local = subj_data.get(user_id)
    subject = subj_data_local.get("Subject")
    type = subj_data_local.get("Type")
    if (not marks.marklink_exist(group, subject, type)):
        marks.add_marklink(group, subject, type, link)
    else:
        marks.update_marklink(group, subject, type, link)
    await message.answer(f"Посилання для {subject} {type} встановлене!", reply_markup=admin_settings_buttons)
    current_links = get_marklinks(user_id)
    await message.answer(current_links, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=marklinks_buttons)
    await AdminSettings.SettingsMenu.set()


#################################################################################


@dp.message_handler(text='⬅️ Назад', state=AdminSettings.SettingsMenu)
async def back(message: types.Message, state: FSMContext):
    await state.finish()
    day, month, year = formatDate(datetime_now())
    await message.answer(f'📆 Дата: {day}.{month}.{year}\n\nВиберіть дію', reply_markup=menu_buttons(message.from_user.id))

@dp.message_handler(text='Обновление', state=AdminSettings.SettingsMenu)
async def update_lectures(message: types.Message):
    await message.answer('Загрузка пар 🔄️', reply_markup=admin_settings_buttons)
    await update_lectures_process()
    await message.answer('Пары загружены ✅', reply_markup=admin_settings_buttons)

@dp.message_handler(text='Обновить базу всех групп', state=AdminSettings.SettingsMenu)
async def update_lectures(message: types.Message):
    await message.answer('Загрузка групп 🔄️', reply_markup=admin_settings_buttons)
    parser.parseGroup()
    await message.answer('Группы загружены ✅', reply_markup=admin_settings_buttons)

@dp.message_handler(text='Удалить группу', state=AdminSettings.SettingsMenu)
async def delete_group_from_db(message: types.Message):
    await message.answer('Выберите группу', reply_markup=delete_group_buttons())
    await AdminSettings.DeleteGroup.set()

@dp.callback_query_handler(text="delete_group_cancel", state=AdminSettings.DeleteGroup)
async def process_delete_group_cancel(callback: types.CallbackQuery):
    await AdminSettings.SettingsMenu.set()
    return await callback.message.answer("Выберите действие")
@dp.callback_query_handler(lambda call: call.data not in groups.get_groups_names(), state=AdminSettings.DeleteGroup)
async def process_delete_group_invalid(callback: types.CallbackQuery):
    return await callback.message.answer("Обрана група не підтримується 🫤\nБудь ласка, виберіть групу з представлених")
@dp.callback_query_handler(state=AdminSettings.DeleteGroup)
async def process_delete_group(callback: types.CallbackQuery):
     group = callback.data
     groups.delete_group(group)
     await callback.message.answer(f"Вы удалили группу *{group}*", parse_mode="Markdown")
     await AdminSettings.SettingsMenu.set()

@dp.message_handler(text='Вывести БД', state=AdminSettings.SettingsMenu)
async def show_db(message: types.Message):
    result = db.read_all()
    strokes = ''
    if len(result) > 0:
        for el in result:
            notify_status = '❌'
            if el[3] == 1:
                notify_status = '✅'
            username = ''
            try:
                user = await bot.get_chat(el[1])
                username = '@' + user.username
            except Exception as e:
                print(f"Не удалось получить username от {el[1]}: {e}")
            strokes += f'{el[1]} {el[2]} {notify_status} {username}\n'
        await message.answer(f'Данные БД:\n\n{strokes}\nВсего пользователей: {len(result)}')
    else:
        await message.answer('В БД пусто 🫤')

@dp.message_handler(text='Изменить подписку', state=AdminSettings.SettingsMenu)
async def change_notify_status(message: types.Message):
    result = db.read_all()
    if len(result) > 0:
        await message.answer('Выберите пользователя', reply_markup=users_list_buttons(result))
        await AdminSettings.ChangeNotify.set()
    else:
        await message.answer('В БД пусто 🫤')

@dp.message_handler(lambda message: not re.match(r'(\d+).*', message.text), state=AdminSettings.ChangeNotify)
async def change_notify_status_user_invalid(message: types.Message):
    await message.answer('Неверно выбран пользователь')

@dp.message_handler(state=AdminSettings.ChangeNotify)
async def change_notify_status_user(message: types.Message):
    await AdminSettings.SettingsMenu.set()
    user_id = re.search(r'(\d+).*', message.text).group(1)
    result = db.get_notify_status(user_id)
    if result == 1:
        db.update_notify_status(user_id, False)
        await message.answer(f'Пользователь: {user_id}\nСтатус подписки изменен на Отключено ❌', reply_markup=admin_settings_buttons)
    else:
        db.update_notify_status(user_id, True)
        await message.answer(f'Пользователь: {user_id}\nСтатус подписки изменен на Включено ✅', reply_markup=admin_settings_buttons)

@dp.message_handler(text='Удалить пользователя', state=AdminSettings.SettingsMenu)
async def change_notify_status(message: types.Message):
    result = db.read_all()
    if len(result) > 0:
        await message.answer('Выберите пользователя', reply_markup=users_list_buttons(result))
        await AdminSettings.DeleteUser.set()
    else:
        await message.answer('В БД пусто 🫤')

@dp.message_handler(lambda message: not re.match(r'(\d+).*', message.text), state=AdminSettings.DeleteUser)
async def process_delete_user_invalid(message: types.Message):
    await message.answer('Неверно выбран пользователь')

@dp.message_handler(state=AdminSettings.DeleteUser)
async def process_delete_user(message: types.Message):
    await AdminSettings.SettingsMenu.set()
    user_id = re.search(r'(\d+).*', message.text).group(1)
    if (not db.user_exists(user_id)):
        await message.answer("Пользователь не найден в базе", reply_markup=admin_settings_buttons)
        return
    db.delete_user(user_id)
    await message.answer(f"Пользователь {user_id} был удален", reply_markup=admin_settings_buttons)

@dp.message_handler(text='Изменить группу', state=AdminSettings.SettingsMenu)
async def change_user_group(message: types.Message):
    await message.answer('Не реализовано')

@dp.message_handler(text='Создать пару', state=AdminSettings.SettingsMenu)
async def create_lecture_base(message: types.Message):
    user_id = message.from_user.id
    group = db.get_group(user_id)
    await message.answer('✍️ Создание пары\n\nВыберите или введите название предмета', reply_markup=reply_editor_subjects(user_id, group))
    await AdminSettings.CreateLecture_Name.set()

@dp.message_handler(state=AdminSettings.CreateLecture_Name)
async def create_lecture_name(message: types.Message, state: FSMContext):
    subj_name = message.text
    data = await state.get_data()
    lecture_info = data.get('arr')
    if not lecture_info:
        lecture_info = []
        await state.update_data(arr=lecture_info)
    await state.update_data(subj_name=subj_name)
    await message.answer(f'✍️ Создание пары\n\n📚 Название: {subj_name}\n\nВыберите тип пары', reply_markup=editor_types_markup)
    await AdminSettings.CreateLecture_Type.set()

@dp.message_handler(state=AdminSettings.CreateLecture_Type)
async def create_lecture_type(message: types.Message, state: FSMContext):
    info = await state.get_data()
    subj_type = message.text
    subj_name = info.get('subj_name')
    lecture_info = info.get('arr')
    lecture_info.append([subj_name, subj_type])
    print(f'{lecture_info}')
    await state.update_data(arr=lecture_info)

    arr_information = []
    for description in lecture_info:
        arr_information.append(f'{description[0]} {description[1]}')
    line = ', '.join(arr_information)

    await message.answer(f'✍️ Создание пары\n\n📚 Информация: {line}\n\nДобавить еще один предмет или продолжить?', reply_markup=editor_choose_markup)
    await AdminSettings.CreateLecture_AddOrContinue.set()

@dp.message_handler(text='Добавить', state=AdminSettings.CreateLecture_AddOrContinue)
async def create_lecture_add(message: types.Message):
    user_id = message.from_user.id
    group = db.get_group(user_id)
    await message.answer('✍️ Создание пары\n\nВыберите или введите название предмета', reply_markup=reply_editor_subjects(user_id, group))
    await AdminSettings.CreateLecture_Name.set()

@dp.message_handler(text='Продолжить', state=AdminSettings.CreateLecture_AddOrContinue)
async def create_lecture_time(message: types.Message):
    await message.answer('✍️ Создание пары\n\nВведите время начала или автоматическое определение времени \(Пара начнется через 6 минут после добавления для получения уведомления\)\n\nФормат ввода: *11:15*\n\nВнимание ⚠️ После указания времени пара будет создана\!', parse_mode="MarkdownV2", reply_markup=editor_automate)
    await AdminSettings.CreateLecture_Time.set()

@dp.message_handler(text='Автоматическое определение',state=AdminSettings.CreateLecture_Time)
async def create_lecture_automate(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    group = db.get_group(user_id)

    current_time = datetime_now() + timedelta(minutes=6)
    minute = formatChar(current_time.time().minute)
    hour = formatChar(current_time.time().hour)
    day, month, year = formatDate(current_time)
    date = f"{day}.{month}.{year}"

    info = await state.get_data()
    lecture_info = info.get('arr')

    arr_information = []
    for description in lecture_info:
        arr_information.append(f'{description[0]} {description[1]}')
    line = ', '.join(arr_information)

    weekday_number = current_time.weekday()
    start = current_time - timedelta(days=weekday_number)
    end = current_time + timedelta(days=6 - weekday_number)
    weekday = formatWeekday(current_time.weekday())
    parsed_week = {}
    keys = list(week_lectures.keys())
    if group in keys:
        day_keys = list(week_lectures[group].keys())
        if f"{day}.{month}.{year}" in day_keys:
            week_lectures[group][date].append(Lecture("1", lecture_info, str(hour), str(minute), str(hour), str(minute)))
        else:
            week_lectures[group] = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)
            week_lectures[group][date].append(Lecture("1", lecture_info, str(hour), str(minute), str(hour), str(minute)))
    else:
        week_lectures[group] = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)
        week_lectures[group][date].append(Lecture("1", lecture_info, str(hour), str(minute), str(hour), str(minute)))
    notify_lectures[group] = week_lectures[group][date][1:]
    await message.answer(f'✍️ Создание пары\n\n📚 Информация: {line}\n⏰ Время: {hour}:{minute} - {hour}:{minute}\n\nПара создана ✅', reply_markup=admin_settings_buttons)
    await state.finish()

@dp.message_handler(state=AdminSettings.CreateLecture_Time)
async def create_lecture_time_process(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    group = db.get_group(user_id)

    hour, minute = message.text.split(':')

    info = await state.get_data()
    lecture_info = info.get('arr')

    arr_information = []
    for description in lecture_info:
        arr_information.append(f'{description[0]} {description[1]}')
    line = ', '.join(arr_information)

    current_time = datetime_now()
    day, month, year = formatDate(current_time)
    date = f"{day}.{month}.{year}"
    weekday_number = current_time.weekday()
    start = current_time - timedelta(days=weekday_number)
    end = current_time + timedelta(days=6 - weekday_number)
    weekday = formatWeekday(current_time.weekday())
    parsed_week = {}
    keys = list(week_lectures.keys())
    if group in keys:
        day_keys = list(week_lectures[group].keys())
        if f"{day}.{month}.{year}" in day_keys:
            week_lectures[group][date].append(Lecture("1", lecture_info, str(hour), str(minute), str(hour), str(minute)))
        else:
            week_lectures[group] = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)
            week_lectures[group][date].append(Lecture("1", lecture_info, str(hour), str(minute), str(hour), str(minute)))
    else:
        week_lectures[group] = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, group)
        week_lectures[group][date].append(Lecture("1", lecture_info, str(hour), str(minute), str(hour), str(minute)))
    notify_lectures[group] = week_lectures[group][date][1:]
    await message.answer(f'✍️ Создание пары\n\n📚 Информация: {line}\n⏰ Время: {hour}:{minute} - {hour}:{minute}\n\nПара создана ✅', reply_markup=admin_settings_buttons)
    await state.finish()

@dp.message_handler(text='Сводка по группам', state=AdminSettings.SettingsMenu)
async def groups_info(message: types.Message):
    users = db.read_all()
    groups_list = groups.get_groups()
    strokes = ''
    if len(users) > 0:
        for group in groups_list:
            group_name = escapeMarkdown(group[0])
            users_in_group = ''
            count = 0
            for user in users:
                if user[2] == group[0]:
                    notify_status = '❌'
                    if user[3] == 1:
                        notify_status = '✅'
                    count += 1
                    users_in_group += f'\- {user[1]} {notify_status}\n'
            strokes += f'👥 Группа *{group_name}* \[{count}\]\:\n{users_in_group}\n'
        await message.answer(f'Сводка по группам\:\n\n{strokes}\nВсего пользователей\: {len(users)}', parse_mode="MarkdownV2")
    else:
        await message.answer('В БД пусто 🫤')

@dp.message_handler(text='Обновить преподов', state=AdminSettings.SettingsMenu)
async def update_all_teachers(message: types.Message):
    await message.answer('Parsing...')
    teachers_list = make_unique(parse_all_teachers())
    if len(teachers_list) > 0:
        all_teachers.truncate()
        for teacher in teachers_list:
            all_teachers.add_teacher(teacher[0], teacher[1])
        await message.answer('Added all teachers to database')
    else:
        await message.answer('No teachers parsed')

@dp.message_handler(text='Список команд', state=AdminSettings.SettingsMenu)
async def change_user_group(message: types.Message):
    await message.answer('Список админ-команд:\n\n'
                         '/notify - Отправить сообщение всем пользователям\n'
                         '/notify_myself - Отправить сообщение себе от лица бота\n'
                         '/send_to_igor - Отправить сообщение Игорю\n'
                         '/update_lectures - Обновить пары\n'
                         '/parse_api - Загрузить группы через апи\n'
                         '/clear_state - Сбросить состояние\n'
                         '/text_add_link - Я хз там чет в консоли ссылки какиета\n'
                         '/get_username - Получить ник по ид\n')