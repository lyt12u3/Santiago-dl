import re
from datetime import timedelta
from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards import settings_buttons, choose_group_buttons, cancel_buttons, menu_buttons, links_buttons, \
    subjects_buttons, links_types, links_types_delete, notify_buttons, display_buttons, group_users, recieve_interface
from loader import dp, db, groups_list, groups, week_lectures, notify_lectures, subjects, links, bot, notify, display, display_new
from states import Settings
from utils.utilities import debug, datetime_now, formatDate, get_links, escapeMarkdown, datePrint
from utils import parser

@dp.message_handler(text="⬅️ Назад")
async def settings_back(message: types.Message):
    day, month, year = formatDate(datetime_now())
    await message.answer(f'📆 Дата: {day}.{month}.{year}\n\nВиберіть дію', reply_markup=menu_buttons(message.from_user.id))

@dp.message_handler(text="Повідомлення")
async def notify_test(message: types.Message):
    user_id = message.from_user.id
    group = db.get_group(user_id)
    await message.answer("🔔 Тут ви можете змінити налаштування повідомлень для кожного предмету 😀", parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=notify_buttons(user_id, group))

@dp.callback_query_handler(lambda call: call.data == "change_all")
async def callback_change(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    group = db.get_group(user_id)
    notify.update_all_notity(user_id, group, not notify.has_positive_notify(user_id, group))
    await callback.message.edit_text("🔔 Тут ви можете змінити налаштування повідомлень для кожного предмету 😀", parse_mode="MarkdownV2", reply_markup=notify_buttons(user_id, group))

@dp.callback_query_handler(lambda call: re.match(r'change_.+', call.data))
async def callback_change(callback: types.CallbackQuery):
    subject = callback.data[7:]
    user_id = callback.from_user.id
    group = db.get_group(user_id)
    notify.update_notify(user_id, group, subject, not notify.get_notify(user_id, group, subject))
    await callback.message.edit_text("🔔 Тут ви можете змінити налаштування повідомлень для кожного предмету 😀", parse_mode="MarkdownV2", reply_markup=notify_buttons(user_id, group))

@dp.message_handler(text="Відображення")
async def display_setting(message: types.Message):
    user_id = message.from_user.id
    group = db.get_group(user_id)
    await message.answer("🔔 Тут ви можете змінити налаштування відображення предметів в розкладі 😀", parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=display_buttons(user_id, group))

@dp.callback_query_handler(lambda call: re.match(r'display_change_.+', call.data))
async def callback_change(callback: types.CallbackQuery):
    subject = callback.data.replace("display_change_","")
    user_id = callback.from_user.id
    group = db.get_group(user_id)
    display_new.update_display(user_id, group, subject)
    await callback.message.edit_text("🔔 Тут ви можете змінити налаштування відображення предметів в розкладі 😀", parse_mode="MarkdownV2", reply_markup=display_buttons(user_id, group))

# @dp.message_handler(text="Вимкнути повідомлення")
# async def notify_off(message: types.Message):
#     user_id = message.from_user.id
#     db.update_notify_status(user_id, False)
#     await message.answer('Тепер ви не будете отримувати повідомлення 🔕', reply_markup=settings_buttons(user_id))
#     debug(f"notify off by {user_id}")
#
# @dp.message_handler(text="Увімкнути повідомлення")
# async def notify_on(message: types.Message):
#     user_id = message.from_user.id
#     db.update_notify_status(user_id, True)
#     await message.answer('Тепер ви будете отримувати повідомлення 🔔', reply_markup=settings_buttons(user_id))
#     debug(f"notify on by {user_id}")

@dp.message_handler(text="Змінити групу")
async def group_change(message: types.Message):
    await message.answer(f"🎓 Ваша поточна група: {db.get_group(message.from_user.id)}\n\nЩоб змінити її, виберіть потрібний варіант з представлених", reply_markup=choose_group_buttons())
    # await MenuState.SettingsMenu_GroupChange.set()

@dp.callback_query_handler(text="no_group")
async def add_group_start(callback: types.CallbackQuery):
    await Settings.GroupAdd.set()
    await callback.message.answer("🎓 Введіть вашу групу\n\nПриклад: *КНТ-22-4*\nАбо напишіть *Скасувати*", parse_mode="Markdown", reply_markup=cancel_buttons)

@dp.message_handler(text="Скасувати", state=Settings.GroupAdd)
async def process_add_group_invalid(message: types.Message, state: FSMContext):
    await message.answer(f'⚙️ Виберіть дію', reply_markup=settings_buttons(message.from_user.id))
    await state.finish()

@dp.message_handler(lambda message: message.text not in groups_list.get_groups_names(), state=Settings.GroupAdd)
async def process_add_group_invalid(message: types.Message, state: FSMContext):
    print(groups_list.get_groups_names())
    return await message.reply("Обрана група не підтримується 🫤\nБудь ласка, введіть вірну назву або напишіть *Скасувати*", reply_markup=cancel_buttons)

@dp.message_handler(state=Settings.GroupAdd)
async def process_add_group(message: types.Message, state: FSMContext):
    code = groups_list.get_code(message.text)
    groups.add_group(message.text, code)
    db.update_nure_group(message.from_user.id, message.text)

    current_time = datetime_now()
    day, month, year = formatDate(current_time)
    weekday = current_time.weekday()
    start = current_time - timedelta(days=weekday)
    end = current_time + timedelta(days=6 - weekday)
    week_lectures[message.text] = parser.parseWeek(start.day, start.month, start.year, end.day, end.month, end.year, message.text)
    notify_lectures[message.text] = week_lectures[message.text][f"{day}.{month}.{year}"][1:]

    await message.answer(f"Ви обрали групу *{message.text}* та додали її до списку активних груп, тож інші користувачі теж можуть її обрати 🥰\n\n⚙️ Виберіть дію", reply_markup=settings_buttons(message.from_user.id), parse_mode="Markdown")
    await state.finish()
    debug(f"group {message.text} added by {message.from_user.id} on change")

@dp.callback_query_handler(text_contains="group:")
async def process_change_group(callback: types.CallbackQuery, state: FSMContext):
    group = callback.data.replace("group:", "")
    if group in groups.get_groups_names():
        db.update_nure_group(callback.from_user.id, group)
        await callback.message.answer(f"Ви обрали групу *{group}* 🥰\n\n⚙️ Виберіть дію", reply_markup=settings_buttons(callback.from_user.id), parse_mode="Markdown")
        await state.finish()
        debug(f"group {callback.data} selected by {callback.from_user.id} on change")
    else:
        return await callback.message.answer("Обрана група не підтримується 🫤\nБудь ласка, виберіть групу з представлених")

@dp.message_handler(text="Посилання")
async def link_settings(message: types.Message):
    user_id = message.from_user.id
    current_links = get_links(user_id)
    await message.answer(current_links, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=links_buttons)
    debug(f"link list used by {user_id}")

@dp.callback_query_handler(lambda call: call.data in ['add_link', 'delete_link'])
async def callback_add_link1(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_links = get_links(user_id)
    await callback.message.edit_text(current_links, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=subjects_buttons(callback))

@dp.callback_query_handler(text="link_cancel")
async def callback_link_settings_cancel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_links = get_links(user_id)
    await callback.message.edit_text(current_links, parse_mode="MarkdownV2", reply_markup=links_buttons, disable_web_page_preview=True)

@dp.callback_query_handler(lambda call: re.match(r'delete_.+', call.data))
async def callback_type(callback: types.CallbackQuery):
    subject = callback.data[7:]
    # await bot.send_message(callback.from_user.id, f'📚 Виберіть тип посилання для видалення {subject}', reply_markup=links_types_delete)
    await callback.message.edit_text(f'📚 Виберіть тип посилання для видалення {subject}', reply_markup=links_types_delete)
    subj_del_data[callback.from_user.id] = {}
    subj_del_data[callback.from_user.id]["Subject"] = subject

@dp.callback_query_handler(lambda call: call.data in ['lk_del','pz_del','lb_del','all_del'])
async def callback_links(callback: types.CallbackQuery):
    type_raw = callback.data.replace("_del", "")
    if type_raw == "lk":
        type = "Лк"
    elif type_raw == "pz":
        type = "Пз"
    elif type_raw == "lb":
        type = "Лб"
    elif type_raw == "all":
        type = "All"
    subj_del_data_local = subj_del_data.get(callback.from_user.id)
    subject = subj_del_data_local.get("Subject")
    group = db.get_group(callback.from_user.id)
    if subjects.subjects_exist(group):
        current_links_arr_line = subjects.get_subjects(group)
        current_links_arr = current_links_arr_line.split(',')
    else:
        current_links_arr = parser.parseSubjects(group)
        subjects.set_subjects(group, current_links_arr)
    if subject in current_links_arr:
        if type == "All":
            links.delete_link(callback.from_user.id, group, subject, "Лк")
            links.delete_link(callback.from_user.id, group, subject, "Пз")
            links.delete_link(callback.from_user.id, group, subject, "Лб")
        else:
            links.delete_link(callback.from_user.id, group, subject, type)
        await callback.message.answer("Посилання видалено", reply_markup=settings_buttons(callback.from_user.id))
        current_links = get_links(callback.from_user.id)
        await callback.message.answer(current_links, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=links_buttons)
        debug(f"link of {subject} {type} deleted by {callback.from_user.id} from {group}")

subj_data = {}
subj_del_data = {}

@dp.callback_query_handler(lambda call: re.match(r'add_.+', call.data))
async def callback_type(callback: types.CallbackQuery):
    subject = callback.data[4:]
    # await bot.send_message(callback.from_user.id, f'📚 Виберіть тип посилання для {subject}', reply_markup=links_types)
    await callback.message.edit_text(f'📚 Виберіть тип посилання для {subject}',reply_markup=links_types)
    subj_data[callback.from_user.id] = {}
    subj_data[callback.from_user.id]["Subject"] = subject

@dp.callback_query_handler(lambda call: call.data in ['lk_add','pz_add','lb_add','all_add'])
async def callback_links(callback: types.CallbackQuery):
    type_raw = callback.data.replace("_add", "")
    if type_raw == "lk":
        type = "Лк"
    elif type_raw == "pz":
        type = "Пз"
    elif type_raw == "lb":
        type = "Лб"
    elif type_raw == "all":
        type = "All"
    subj_data_local = subj_data.get(callback.from_user.id)
    subject = subj_data_local.get("Subject")
    subj_data[callback.from_user.id]["Type"] = type
    group = db.get_group(callback.from_user.id)
    if subjects.subjects_exist(group):
        current_links_arr_line = subjects.get_subjects(group)
        current_links_arr = current_links_arr_line.split(',')
    else:
        current_links_arr = parser.parseSubjects(group)
        subjects.set_subjects(group, current_links_arr)
    if subject in current_links_arr:
        if type == "All":
            line = escapeMarkdown(f"Введіть посилання для {subject}\n\nПриклад: https://meet.google.com/yjg-qgwj-bwh")
        else:
            line = escapeMarkdown(f"Введіть посилання для {subject} {type}\n\nПриклад: https://meet.google.com/yjg-qgwj-bwh")
        await bot.send_message(callback.from_user.id, f"{line}\n\nЩоб скасувати введення посилання, напишіть *Скасувати*", parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=cancel_buttons)
        await Settings.LinkAdd.set()

@dp.message_handler(lambda message: message.text == "Скасувати", state=Settings.LinkAdd)
async def links_settings_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Введення посилання скасовано\n\n⚙️ Виберіть дію", reply_markup=settings_buttons(message.from_user.id))

@dp.message_handler(state=Settings.LinkAdd)
async def links_settings_link_wait(message: types.Message, state: FSMContext):
    # if "meet.google.com" in message.text:
    #     code = re.search(r"com/(.+)", message.text).group(1)
    # else:
    #     code = message.text
    link = message.text
    user_id = message.from_user.id
    group = db.get_group(user_id)
    subj_data_local = subj_data.get(user_id)
    subject = subj_data_local.get("Subject")
    type = subj_data_local.get("Type")
    if type == "All":
        for new_type in ["Лк","Пз","Лб"]:
            if (not links.link_exist(user_id, group, subject, new_type)):
                links.add_link(user_id, group, subject, new_type, link)
            else:
                links.update_link(user_id, group, subject, new_type, link)
        await message.answer(f"Посилання для {subject} встановлені!", reply_markup=settings_buttons(user_id))
    else:
        if (not links.link_exist(user_id, group, subject, type)):
            links.add_link(user_id, group, subject, type, link)
        else:
            links.update_link(user_id, group, subject, type, link)
        await message.answer(f"Посилання для {subject} {type} встановлене!", reply_markup=settings_buttons(user_id))
    current_links = get_links(user_id)
    await message.answer(current_links, parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=links_buttons)
    await state.finish()
    debug(f"link of {subject} added by {user_id} from {group}")

@dp.message_handler(text="Поділитися посиланнями")
async def notify_test(message: types.Message):
    user_id = message.from_user.id
    group = db.get_group(user_id)

    if subjects.subjects_exist(group):
        current_subj_arr_line = subjects.get_subjects(group)
        current_subj_arr = current_subj_arr_line.split(',')
    else:
        current_subj_arr = parser.parseSubjects(group)
        subjects.set_subjects(group, current_subj_arr)
    links_exist = False
    for subj in current_subj_arr:
        if links_exist:
            break
        for type in ["Лк", "Пз", "Лб", "Конс"]:
            if links.link_exist(user_id, group, subj, type):
                links_exist = True
                break

    if links_exist:
        markup = await group_users(group)
        await message.answer("⚙️ Оберіть користувача, з яким ви хочете поділитися посиланнями\n\nВам представлені користувачі з вашої групи, оберіть одного з них", parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup)
    else:
        await message.answer("Немає посилань, якими ви можете поділитись ⚠️")

@dp.callback_query_handler(lambda call: re.match(r'userid_.+', call.data))
async def callback_userid(callback: types.CallbackQuery):
    user_recieve_id = callback.data.replace("userid_", "")
    user_id = callback.from_user.id
    group = db.get_group(user_id)
    try:
        user_recieve = await bot.get_chat(user_recieve_id)
        user_recieve_username = '@' + user_recieve.username
        sender_username = '@' + escapeMarkdown(callback.from_user.username)
        sender_links = get_links(user_id, False)
        markup = recieve_interface(user_id)
        if len(sender_links) > 1:
            sender_links = f"{sender_links}\n"
        await bot.send_message(user_recieve_id,f"🔗 Користувач {sender_username} хоче поділитися з вами своїми посиланнями на пари\n\n{sender_links}*Зверніть увагу*, після прийняття вказані посилання будуть замінені та не зможуть бути відновлені до попереднього стану",parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup)
        await callback.message.edit_text(f"Ви поділилися посиланнями з користувачем {user_recieve_username} ✅")
    except Exception as e:
        print(e.args[0])

@dp.callback_query_handler(lambda call: re.match(r'accept_senderid_.+', call.data))
async def callback_userid(callback: types.CallbackQuery):
    sender_id = callback.data.replace("accept_senderid_", "")
    user_id = callback.from_user.id
    group = db.get_group(sender_id)
    datePrint(f"links accepted by {user_id}. Sender {sender_id}")
    if subjects.subjects_exist(group):
        current_subj_arr_line = subjects.get_subjects(group)
        current_subj_arr = current_subj_arr_line.split(',')
    else:
        current_subj_arr = parser.parseSubjects(group)
        subjects.set_subjects(group, current_subj_arr)

    for subj in current_subj_arr:
        for type in ["Лк", "Пз", "Лб", "Конс"]:
            if links.link_exist(sender_id, group, subj, type):
                sender_link = links.get_link(sender_id, group, subj, type)
                if links.link_exist(user_id, group, subj, type):
                    links.update_link(user_id, group, subj, type, sender_link)
                else:
                    links.add_link(user_id, group, subj, type, sender_link)
                datePrint(f"Subject {subj} {type} updated")

    message = callback.message
    await message.edit_text("Посилання були замінені ✅")

@dp.callback_query_handler(lambda call: re.match(r'decline_senderid_.+', call.data))
async def callback_userid(callback: types.CallbackQuery):
    sender_id = callback.data.replace("decline_senderid_", "")
    datePrint(f"links declined by {callback.from_user.id}. Sender {sender_id}")
    await bot.delete_message(callback.from_user.id, callback.message.message_id)