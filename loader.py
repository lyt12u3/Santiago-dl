import os

import dotenv
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data import config
from data.database import Links, Users, Subjects, Groups, AllGroups, Teachers, AllTeachers, Notify, Display, DisplayNew, Marks
from dotenv import load_dotenv

additional_debug = True

load_dotenv()

ADMINS = list(map(int, os.getenv('ADMINS').split(',')))
MASTER_ADMIN = int(os.getenv('MASTER_ADMIN'))
FEEDBACK_CHAT = int(os.getenv('FEEDBACK_CHAT'))
BACKUP_CHAT = int(os.getenv('BACKUP_CHAT'))

bot = Bot(token=os.getenv('TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

notify_lectures = {}
week_lectures = {}
today_lectures = {}
tomorrow_lectures = {}

file = "database.db"
db = Users(file)
links = Links(file)
subjects = Subjects(file)
groups = Groups(file)
all_teachers = AllTeachers(file)
teachers = Teachers(file)
groups_list = AllGroups("all_groups.db")
notify = Notify(file)
display = Display(file)
display_new = DisplayNew(file)
marks = Marks(file)
db.check_file()
links.check_file()
subjects.check_file()
groups.check_file()
all_teachers.check_file()
teachers.check_file()
groups_list.check_file()
notify.check_file()
display.check_file()
display_new.check_file()
marks.check_file()