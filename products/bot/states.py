from aiogram.fsm.state import State, StatesGroup


class RegistrationState(StatesGroup):
    get_name = State()
    get_phone = State()




class StageOfOrderState(StatesGroup):
    get_delivery = State()
    get_location = State()