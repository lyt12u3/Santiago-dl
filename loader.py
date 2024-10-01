import os

import dotenv
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data import config
from data.database import Links, Database, Subjects, Groups, AllGroups, Notify, Display
from dotenv import load_dotenv

additional_debug = True

load_dotenv()

ADMINS = list(map(int, os.getenv('ADMINS').split(',')))
print(ADMINS)

bot = Bot(token=os.getenv('TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

notify_lectures = {}
week_lectures = {}
today_lectures = {}
tomorrow_lectures = {}

file = "database.db"
db = Database(file)
links = Links(file)
subjects = Subjects(file)
groups = Groups(file)
groups_list = AllGroups("all_groups.db")
notify = Notify(file)
display = Display(file)
db.check_file()
links.check_file()
subjects.check_file()
groups.check_file()
groups_list.check_file()
notify.check_file()
display.check_file()