import re
from aiogram import types
from loader import dp
# from keyboards import menu

@dp.message_handler(commands=['keyboard'])
async def keyboard_command(message: types.Message):
    await message.answer('Command keyboard')
    # await message.answer('Появляется клавиатура!', reply_markup=menu)

# @dp.message_handler(lambda message: re.match(r'Кнопка [1-3]{1}', message.text))
# async def button_1(message: types.Message):
#     await message.answer('Кнопка нажата')