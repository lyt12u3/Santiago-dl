from aiogram.dispatcher.filters.state import State, StatesGroup

class Settings(StatesGroup):
    GroupChange = State()
    GroupAdd = State()
    LinkAdd = State()
    LinkTypeSelect = State()

class UserWait(StatesGroup):
    nure_group = State()
    add_group = State()
    Feedback = State()