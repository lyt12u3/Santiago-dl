from aiogram.utils import exceptions
from aiogram import types
from aiogram.dispatcher import FSMContext
from data import config
from keyboards import menu_buttons, notify_buttons
from states import AdminPrikoli
from utils import parser
from utils.parser import Lecture
from utils.updater import update_lectures_process
from loader import dp, bot, db, links, notify, week_lectures, notify_lectures, subjects, display, ADMINS
from utils.utilities import datetime_now, formatDate, datePrint
import re
from aiogram.utils.markdown import hlink

@dp.message_handler(commands=['delete_user'])
async def command_send_to_igor(message: types.Message):
    if message.from_user.id in ADMINS:
        del_id = message.text.replace("/delete_user ", "")
        if len(del_id) > 1:
            db.delete_user(del_id)
            print(f"[users] Удален пользователь {del_id}")
            links.delete_user(del_id)
            print(f"[links] Удален пользователь {del_id}")
            notify.delete_all_notify(del_id)
            print(f"[notify] Удален пользователь {del_id}")
            display.delete_user(del_id)
            print(f"[display] Удален пользователь {del_id}")
            await message.answer(f"Пользователь {del_id} удален из users, links, notify, display")

@dp.message_handler(commands=['migrate'])
async def migrate(message: types.Message):
    msg = await bot.send_message(message.from_user.id, "Перенос данных про уведомления 🔁\n")
    if message.from_user.id in ADMINS:
        all_users = db.read_all()
        for object in all_users:
            user_id = object[1]
            group = object[2]
            notify_status = object[3]

            if subjects.subjects_exist(group):
                subj_arr_line = subjects.get_subjects(group)
                subj_arr = subj_arr_line.split(',')
            else:
                subj_arr = parser.parseSubjects(group)
                subjects.set_subjects(group, subj_arr)

            for subj in subj_arr:
                if not notify.notify_exist(user_id, group, subj):
                    notify.add_notify(user_id, group, subj, notify_status)
    await bot.edit_message_text("Перенос данных завершен ✅", message.from_user.id, msg.message_id)

@dp.message_handler(commands=['create_lecture'])
async def create_lecture(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer('Ожидание ввода в консоль 🔄️')
        subject = input("Subject: ")
        start = input("Start time (hh:mm): ")
        end = input("End time (hh:mm): ")
        user_id = message.from_user.id
        group = db.get_group(user_id)

        weekdays = {0: "Понеділок", 1: "Вівторок", 2: "Середа", 3: "Четвер", 4: "П'ятниця", 5: "Субота", 6: "Неділя"}

        start_hours, start_minutes = start.split(':')
        end_hours, end_minutes = end.split(':')

        date = datetime_now()
        formatted_date = date.strftime("%d.%m.%Y")
        day, month, year = formatted_date.split(".")
        weekday = weekdays[date.weekday()]

        parsed_week_local = {}
        parsed_week_local[formatted_date] = [weekday]
        parsed_week_local[formatted_date].append(Lecture(1, subject, "Лк", start_hours, start_minutes, end_hours, end_minutes))

        week_lectures[group] = parsed_week_local
        print(week_lectures[group])
        notify_lectures[group] = week_lectures[group][f"{day}.{month}.{year}"][1:]


@dp.message_handler(commands=['notify_test_delete'])
async def notify_test_delete(message: types.Message):
    if message.from_user.id in ADMINS:
        user_id = message.from_user.id
        notify.delete_all_notify(user_id)
        await message.answer("Done ✅")

# @dp.message_handler(commands=['notify_test'])
# async def notify_test(message: types.Message):
#     if message.from_user.id in config.admins:
#         user_id = message.from_user.id
#         await message.answer("Тут ви можете змінити налаштування повідомлень для кожного предмету 😀", parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=notify_buttons(user_id))
#
# @dp.callback_query_handler(lambda call: call.data == "change_all")
# async def callback_change(callback: types.CallbackQuery):
#     user_id = callback.from_user.id
#     notify.update_all_notity(user_id, not notify.has_positive_notify(user_id))
#     await callback.message.edit_text("Тут ви можете змінити налаштування повідомлень для кожного предмету 😀", parse_mode="MarkdownV2", reply_markup=notify_buttons(user_id))
#
# @dp.callback_query_handler(lambda call: re.match(r'change_.+', call.data))
# async def callback_change(callback: types.CallbackQuery):
#     subject = callback.data[7:]
#     user_id = callback.from_user.id
#     print(subject)
#     notify.update_notify(user_id, subject, not notify.get_notify(user_id, subject))
#     await callback.message.edit_text("Тут ви можете змінити налаштування повідомлень для кожного предмету 😀", parse_mode="MarkdownV2", reply_markup=notify_buttons(user_id))


@dp.message_handler(commands=['get_username'])
async def command_send_to_igor(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer('Введите id')
        await AdminPrikoli.GetUsername.set()

@dp.message_handler(state=AdminPrikoli.GetUsername)
async def send_message_to_igor2(message: types.Message, state: FSMContext):
    try:
        # Получаем информацию о пользователе
        user = await bot.get_chat(message.text)
        await message.answer(user.username)
        await message.answer(user.full_name)
    except Exception as e:
        print(f"Не удалось получить username: {e}")
        await message.answer("Can't get username")
    await state.finish()

@dp.message_handler(commands=['text_add_link'])
async def test_add_link(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer('Ожидание ввода в консоль 🔄️')
        subject = input("Subject: ")
        type = input("Type: ")
        code = input("Code: ")
        user_id = message.from_user.id
        group = db.get_group(user_id)
        if (not links.link_exist(user_id, group, subject, type)):
            links.add_link(user_id, group, subject, type, code)
        else:
            links.update_link(user_id, group, subject, type, code)
        await message.answer(f'Ссылка для {subject} {type} добавлена')

@dp.message_handler(commands=['clear_state'], state='*')
async def clear_state(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.finish()
        await message.answer('Состояние очищено ✅')
        day, month, year = formatDate(datetime_now())
        await message.answer(f'📆 Дата: {day}.{month}.{year}\n\nВиберіть дію', reply_markup=menu_buttons(message.from_user.id))

@dp.message_handler(commands=['parse_api'])
async def parse_api_command(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer('Загрузка групп 🔄️')
        parser.parseApiGroups()
        await message.answer('Группы загружены ✅')

@dp.message_handler(commands=['update_lectures'])
async def update_lectures(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer('Загрузка пар 🔄️')
        await update_lectures_process()
        await message.answer('Пары загружены ✅')

# @dp.message_handler(commands=['send_to_igor'])
# async def command_send_to_igor(message: types.Message):
#     if message.from_user.id in config.admins:
#         await bot.send_message(528508962, '🔔 Уведомление 🔔\n\nА твоя мама говорит, что нам не по пути 🛣️\nкогда слышит мой голос в трубке домофона 📞')

@dp.message_handler(commands=['test_markdown'])
async def command_send_to_igor(message: types.Message):
    if message.from_user.id in ADMINS:
        try:
            text = hlink("*СГМтА", "https://googal.com")
            print(text)
            await message.answer(text, parse_mode="HTML")
        except exceptions.CantParseEntities as e:
            await bot.send_message(728227124, f'🚨 Markdown Error 🚨\n\n{e.args[0]}')

@dp.message_handler(commands=['notify_myself'])
async def command_send_to_igor(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer('Введите сообщение для отправки')
        await AdminPrikoli.NotifyMyselfWait.set()

@dp.message_handler(state=AdminPrikoli.NotifyMyselfWait)
async def send_message_to_igor2(message: types.Message, state: FSMContext):
    await bot.send_message(728227124, message.text)
    await state.finish()

@dp.message_handler(commands=['send_to_igor'])
async def command_send_to_igor(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer('Введите сообщение для отправки')
        await AdminPrikoli.MessageWait.set()

@dp.message_handler(state=AdminPrikoli.MessageWait)
async def send_message_to_igor2(message: types.Message, state: FSMContext):
    await bot.send_message(528508962, message.text)
    await state.finish()

@dp.message_handler(commands=['notify'])
async def command_notify(message: types.Message):
    if message.from_user.id in ADMINS:
        await message.answer('Введите сообщение для отправки')
        await AdminPrikoli.MessageWaitNotify.set()

@dp.message_handler(state=AdminPrikoli.MessageWaitNotify)
async def notify_users(message: types.Message, state: FSMContext):
    result = db.get_notify_users()
    if len(result) > 0:
        for el in result:
            try:
                await bot.send_message(el[0], message.text)
            except exceptions.BotBlocked as e:
                datePrint('Ошибка Bot Blocked')
            except Exception as e:
                datePrint(f'Неизвестная ошибка {e.args[0]}')
                await bot.send_message(728227124, f'🚨 Unknown Error 🚨\n\nПользователь: {el[0]}\n\n{e.args[0]}')
    await state.finish()