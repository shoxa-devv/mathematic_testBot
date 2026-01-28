"""Reply keyboardlar"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_phone_keyboard():
    """Telefon raqamini yuborish uchun keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Telefon raqamini yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard
