from aiogram.fsm.state import State, StatesGroup

class CalcState(StatesGroup):
    DLZKA = State()
    SIRKA = State()
    SHOW_RESULT = State()
    PICK_METHOD = State()       # výber kanála kontaktu
    ASK_PHONE = State()         # zadanie / zdieľanie čísla
    ASK_NAME = State()          # meno
    ASK_PREFER_TIME = State()   # preferovaný čas kontaktu (voliteľné)
    ASK_COMMENT = State()       # poznámka (voliteľné)
    CONFIRM_SAVE = State()      # potvrdenie a ukladanie
