from aiogram.dispatcher.filters.state import State, StatesGroup

class AdminSettings(StatesGroup):
    SettingsMenu = State()
    AddGroup = State()
    DeleteGroup = State()
    DeleteUser = State()
    ChangeNotify = State()
    ChangeGroup_Step1 = State()
    ChangeGroup_Step2 = State()

class AdminPrikoli(StatesGroup):
    MessageWait = State()
    MessageWaitNotify = State()
    GetUsername = State()
    NotifyMyselfWait = State()