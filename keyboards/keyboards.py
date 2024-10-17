from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from data import config
from loader import groups, db, subjects, notify, display, ADMINS, bot
from utils import parser
from utils.utilities import getMonth


def menu_buttons(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('Пари на сьогодні').insert('Пари на завтра').insert('Пари на тиждень')
    markup.add('Обрати дату')
    markup.add('⚙️ Налаштування')
    if user_id in ADMINS:
        markup.insert('⚙️ Админка')
    return markup

def settings_buttons(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Посилання")
    # if db.get_notify_status(user_id) == 1:
    #     markup.insert("Вимкнути повідомлення")
    # else:
    #     markup.insert("Увімкнути повідомлення")
    markup.insert("Повідомлення")
    markup.insert("Змінити групу")
    markup.add("Відображення")
    markup.add("Поділитися посиланнями")
    markup.add("⬅️ Назад")
    return markup

def month_buttons():
    days = getMonth()
    markup = InlineKeyboardMarkup(row_width=3)
    for num in range(30):
        markup.insert(InlineKeyboardButton(text=f'{days[num]}', callback_data=f'day_{days[num]}'))
    return markup

def choose_group_buttons():
    markup = InlineKeyboardMarkup(row_width=3)
    all_groups = groups.get_groups()
    for group in all_groups:
        markup.insert(InlineKeyboardButton(group[0], callback_data=f'group:{group[0]}'))
    markup.add(InlineKeyboardButton("Моєї групи немає 😖", callback_data="no_group"))
    return markup

def subjects_buttons(callback):
    user_id = callback.from_user.id
    group = db.get_group(user_id)
    if subjects.subjects_exist(group):
        current_links_arr_line = subjects.get_subjects(group)
        current_links_arr = current_links_arr_line.split(',')
    else:
        current_links_arr = parser.parseSubjects(group)
        subjects.set_subjects(group, current_links_arr)

    markup = InlineKeyboardMarkup(row_width=3)
    for el in current_links_arr:
        if callback.data == "add_link":
            markup.insert(InlineKeyboardButton(text=f"📚 {el}", callback_data=f"add_{el}"))
        else:
            markup.insert(InlineKeyboardButton(text=f"📚 {el}", callback_data=f"delete_{el}"))
    markup.add(InlineKeyboardButton(text="❌ Назад", callback_data="link_cancel"))

    return markup

def notify_buttons(user_id, group):
    if subjects.subjects_exist(group):
        current_subj_arr_line = subjects.get_subjects(group)
        current_subj_arr = current_subj_arr_line.split(',')
    else:
        current_subj_arr = parser.parseSubjects(group)
        subjects.set_subjects(group, current_subj_arr)

    markup = InlineKeyboardMarkup(row_width=3)
    for subj in current_subj_arr:
        if not notify.notify_exist(user_id, group, subj):
            notify.add_notify(user_id, group, subj, db.get_notify_status(user_id))
        emojis = {0: "❌", 1: "✅"}
        emoji = emojis[notify.get_notify(user_id, group, subj)]
        markup.insert(InlineKeyboardButton(text=f"{subj} {emoji}", callback_data=f"change_{subj}"))
    if notify.has_positive_notify(user_id, group):
        markup.add(InlineKeyboardButton(text="Вимкнути всі повідомлення", callback_data="change_all"))
    else:
        markup.add(InlineKeyboardButton(text="Увімкнути всі повідомлення", callback_data="change_all"))

    return markup

def display_buttons(user_id, group):
    if subjects.subjects_exist(group):
        current_subj_arr_line = subjects.get_subjects(group)
        current_subj_arr = current_subj_arr_line.split(',')
    else:
        current_subj_arr = parser.parseSubjects(group)
        subjects.set_subjects(group, current_subj_arr)

    markup = InlineKeyboardMarkup(row_width=3)
    for subj in current_subj_arr:
        emojis = {0: "❌", 1: "✅"}
        if not display.display_exist(user_id, group):
            line = ",".join(current_subj_arr)
            display.set_display(user_id, group, line)
        emoji = emojis[display.has_display(user_id, group, subj)]
        markup.insert(InlineKeyboardButton(text=f"{subj} {emoji}", callback_data=f"display_change_{subj}"))

    return markup

def delete_group_buttons():
    markup = InlineKeyboardMarkup(row_width=3)
    all_groups = groups.get_groups()
    for group in all_groups:
        markup.insert(InlineKeyboardButton(group[0], callback_data=group[0]))
    markup.add(InlineKeyboardButton('Отмена', callback_data="delete_group_cancel"))
    return markup

def users_list_buttons(list):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Пользователь")
    for el in list:
        notify_status = '❌'
        if el[3] == 1:
            notify_status = '✅'
        markup.add(f'{el[1]} | {el[2]} | {notify_status}')
    return markup

links_buttons = InlineKeyboardMarkup(row_width=2)
links_buttons.add(InlineKeyboardButton(text="Додати/змінити", callback_data="add_link"))
links_buttons.insert(InlineKeyboardButton(text="Видалити посилання", callback_data="delete_link"))

links_types = InlineKeyboardMarkup(row_width=3)
links_types.add(InlineKeyboardButton(text='📖 Лк', callback_data="lk_add"))
links_types.insert(InlineKeyboardButton(text='📖 Пз', callback_data="pz_add"))
links_types.insert(InlineKeyboardButton(text='📖 Лб', callback_data="lb_add"))
links_types.add(InlineKeyboardButton(text="❌ Назад", callback_data="link_cancel"))

links_types_delete = InlineKeyboardMarkup(row_width=3)
links_types_delete.add(InlineKeyboardButton(text='📖 Лк', callback_data="lk_del"))
links_types_delete.insert(InlineKeyboardButton(text='📖 Пз', callback_data="pz_del"))
links_types_delete.insert(InlineKeyboardButton(text='📖 Лб', callback_data="lb_del"))
links_types_delete.add(InlineKeyboardButton(text="❌ Назад", callback_data="link_cancel"))

admin_settings_buttons = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Действие")
admin_settings_buttons.add('Обновить базу всех групп')
admin_settings_buttons.insert('Обновление')
admin_settings_buttons.add('Вывести БД')
admin_settings_buttons.add('Удалить пользователя')
admin_settings_buttons.add('Изменить подписку')
admin_settings_buttons.insert('Удалить группу')
admin_settings_buttons.add('Создать пару')
admin_settings_buttons.add('Сводка по группам')
admin_settings_buttons.add('Список команд')
admin_settings_buttons.add('⬅️ Назад')

editor_types_markup = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Тип")
editor_types_markup.add('Лк')
editor_types_markup.insert('Пз')
editor_types_markup.add('Лб')
editor_types_markup.insert('Конс')

editor_choose_markup = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Действие")
editor_choose_markup.add('Добавить')
editor_choose_markup.insert('Продолжить')

def reply_editor_subjects(user_id, group):
    if subjects.subjects_exist(group):
        current_subj_arr_line = subjects.get_subjects(group)
        current_subj_arr = current_subj_arr_line.split(',')
    else:
        current_subj_arr = parser.parseSubjects(group)
        subjects.set_subjects(group, current_subj_arr)

    insert = False
    markup = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Название")
    for subj in current_subj_arr:
        if insert:
            markup.insert(subj)
            insert = False
        else:
            markup.add(subj)
            insert = True
    return markup

editor_automate = ReplyKeyboardMarkup(resize_keyboard=True).add('Автоматическое определение')

editor_finish = ReplyKeyboardMarkup(resize_keyboard=True).add('Сохранить').insert('Отменить')

another_day_buttons = InlineKeyboardMarkup(row_width=1)
another_day_buttons.add(InlineKeyboardButton(text="Інша дата", callback_data="another_day"), InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))


cancel_buttons = ReplyKeyboardMarkup(resize_keyboard=True).add('Скасувати')

async def group_users(group):
    markup = InlineKeyboardMarkup(row_width=3)
    users_list = db.get_users_in_group(group)
    insert = False
    for user_obj in users_list:
        user_id = user_obj[0]
        username = str(user_id) ###### ЗАМЕНИТЬ НА ПУСТУЮ СТРОКУ
        try:
            user = await bot.get_chat(user_id)
            username = '@' + user.username
        except Exception as e:
            pass
        if len(username) > 1:
            markup.insert(InlineKeyboardButton(username, callback_data=f"userid_{user_id}"))
    return markup

def recieve_interface(user_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton("Прийняти ✅", callback_data=f"accept_senderid_{user_id}"))
    markup.insert(InlineKeyboardButton("Відхилити ❌", callback_data=f"decline_senderid_{user_id}"))
    return markup