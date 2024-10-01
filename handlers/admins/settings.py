import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from keyboards import admin_settings_buttons, menu_buttons, delete_group_buttons, users_list_buttons
from loader import dp, db, groups, bot
from states import AdminSettings
from utils import parser
from utils.updater import update_lectures_process
from utils.utilities import formatDate, datetime_now, escapeMarkdown


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

@dp.message_handler(text='Список команд', state=AdminSettings.SettingsMenu)
async def change_user_group(message: types.Message):
    await message.answer('Список админ-команд:\n\n/notify - Отправить сообщение всем пользователям\n/notify_myself - Отправить сообщение себе от лица бота\n/send_to_igor - Отправить сообщение Игорю\n/create_lecture - Создать тестовую пару (Опасно, использовать только на тестовом боте)\n/update_lectures - Обновить пары\n/parse_api - Загрузить группы через апи\n/clear_state - Сбросить состояние\n/text_add_link - Я хз там чет в консоли ссылки какиета\n/get_username - Получить ник по ид\n/notify_test - Тестовое меню уведомлений\n/notify_test_delete - Очистить бд на себя с уведомлениями')

# @dp.message_handler(text='Изменить группу', state=MenuState.Admin_SettingsMenu)
# async def change_user_group(message: types.Message):
#     result = db.read_all()
#     markup = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder="Пользователь")
#     if len(result) > 0:
#         for el in result:
#             notify_status = '❌'
#             if el[3] == 1:
#                 notify_status = '✅'
#             markup.add(f'{el[1]} | {el[2]} | {notify_status}')
#         await message.answer('Выберите пользователя', reply_markup=markup)
#         await MenuState.Admin_ChangeGroup_Step1.set()
#     else:
#         await message.answer('В БД пусто 🫤')
#
# @dp.message_handler(lambda message: not re.match(r'(\d+).*', message.text), state=MenuState.Admin_ChangeGroup_Step1)
# async def process_change_user_group_invalid(message: types.Message):
#     await message.answer('Неверно выбран пользователь')
#
# @dp.message_handler(state=MenuState.Admin_ChangeGroup_Step1)
# async def process_delete_user(message: types.Message, state: FSMContext):
#     # user_id = message.text.replace("ID: ", '')
#     user_id = re.search(r'(\d+).*', message.text).group(1)
#     await state.update_data(id = user_id)
#     markup = ReplyKeyboardMarkup(resize_keyboard=True)
#     markup.add('КНТ-22-4').add('ВПВПС-22-3').add('ІТУ-22-1')
#     await message.answer("Выберите новую группу", reply_markup=markup)
#     await MenuState.Admin_ChangeGroup_Step2.set()
#
# @dp.message_handler(lambda message: message.text not in ["КНТ-22-4", "ВПВПС-22-3", "ІТУ-22-1"], state=MenuState.Admin_ChangeGroup_Step2)
# async def process_gender_invalid(message: types.Message):
#     return await message.reply("Указанная группа не поддерживается 🫤\nПожалуйста, выберите группу из предложенных")
#
# @dp.message_handler(state=MenuState.Admin_ChangeGroup_Step2)
# async def process_nure_group(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     group = message.text
#     db.update_nure_group(data['id'], group)
#     await MenuState.Admin_SettingsMenu.set()
#     await message.answer(f'Группа пользователя {data["id"]} была изменена на {group}', reply_markup=admin_settings_markup)
#     # db.update_nure_group()
#     # await message.answer('Вы зарегистрировались!')
#     # day, month, year = formatDate(datetime.now())
#     # await message.answer(f'📆 Дата: {day}.{month}.{year}\n\nВиберіть дію', reply_markup=menu_buttons(message.from_user.id))