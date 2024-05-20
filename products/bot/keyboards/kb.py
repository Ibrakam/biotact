from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

from products.bot.handlers.some_func import json_loader

ru = json_loader()['menu']['ru']['inline_keyboard_button']
uz = json_loader()['menu']['uz']['inline_keyboard_button']


def get_phone_num(lang='ru'):
    kb = ReplyKeyboardBuilder()
    if lang == 'ru':
        kb.button(text="Отправить свой номер телефона📞", request_contact=True)
    else:
        kb.button(text="Telefon raqamini yuborish📞", request_contact=True)
    return kb.as_markup()


def menu_kb(lang='ru'):
    kb = ReplyKeyboardBuilder()
    kb.button(text=ru['choose_product'] if lang == 'ru' else uz['choose_product'])
    kb.button(text=ru['cart'] if lang == 'ru' else uz['cart'])
    kb.button(text=ru['about_us'] if lang == 'ru' else uz['about_us'])
    kb.button(text="🇺🇿uz" if lang == 'ru' else "🇷🇺ru")
    kb.adjust(2)
    return kb.as_markup()


def stage_order_delivery_kb(lang: str):
    kb = ReplyKeyboardBuilder()
    kb.button(text=ru['delivery'] if lang == 'ru' else uz['delivery'])
    kb.button(text=ru['pickup'] if lang == 'ru' else uz['pickup'])
    kb.button(text=ru['back'] if lang == 'ru' else uz['back'])
    kb.adjust(2)
    return kb.as_markup()


def send_location_kb(lang: str):
    kb = ReplyKeyboardBuilder()
    kb.button(text=ru['send_location'] if lang == 'ru' else uz['send_location'], request_location=True)
    kb.button(text=ru['back'] if lang == 'ru' else uz['back'])
    kb.adjust(1)
    return kb.as_markup()
