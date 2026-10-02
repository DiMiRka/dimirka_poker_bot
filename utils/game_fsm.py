from aiogram.fsm.state import State, StatesGroup


class ChangePurchase(StatesGroup):
    change = State()


class ResultGame(StatesGroup):
    result_bank = State()
