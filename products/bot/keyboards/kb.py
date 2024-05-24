from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from products.bot.handlers.some_func import json_loader

ru = json_loader()['menu']['ru']['inline_keyboard_button']
uz = json_loader()['menu']['uz']['inline_keyboard_button']


def get_phone_num(lang='ru'):
    buttons = [
        [
            KeyboardButton(text="Отправить свой номер телефона📞" if lang == "ru" else "Telefon raqamini yuborish📞",
                           request_contact=True)
        ]
    ]
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
    return kb


def menu_kb(lang='ru', is_order=False):
    order = KeyboardButton(text=ru['re-order'] if lang == 'ru' else uz['re-order'])
    buttons = [
        [
            KeyboardButton(text=ru['choose_product'] if lang == 'ru' else uz['choose_product']),
            KeyboardButton(text=ru['about_us'] if lang == 'ru' else uz['about_us'])
        ],
        [
            KeyboardButton(text=ru['leave_feedback'] if lang == 'ru' else uz['leave_feedback']),
            KeyboardButton(text="🇺🇿uz" if lang == 'ru' else "🇷🇺ru")
        ],

    ]

    if is_order:
        buttons.append([order])
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
    return kb


def stage_order_delivery_kb(lang: str):
    buttons = [
        [
            KeyboardButton(text=ru['delivery'] if lang == 'ru' else uz['delivery']),
            KeyboardButton(text=ru['pickup'] if lang == 'ru' else uz['pickup']),
        ],
        [
            KeyboardButton(text=ru['back'] if lang == 'ru' else uz['back'])
        ]
    ]
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
    return kb


def send_location_kb(lang: str):
    buttons = [
        [
            KeyboardButton(text=ru['send_location'] if lang == 'ru' else uz['send_location'], request_location=True)
        ],
        [
            KeyboardButton(text=ru['back'] if lang == 'ru' else uz['back'])
        ]
    ]
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

    return kb


def confirm_location_kb(lang: str):
    buttons = [
        [
            KeyboardButton(text="Подтвердить" if lang == "ru" else "Tasdiqlash"),
        ],
        [
            KeyboardButton(text=ru['send_location'] if lang == 'ru' else uz['send_location'], request_location=True)
        ]
    ]
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

    return kb


def payment_kb(lang: str):
    buttons = [
        [
            KeyboardButton(text=ru['back'] if lang == 'ru' else uz['back']),
            KeyboardButton(text="Наличные" if lang == 'ru' else "Naqd"),

        ],
        [
            KeyboardButton(text="Теримнал/Карта" if lang == 'ru' else "Terminal/Karta"),
            KeyboardButton(text="Payme")
        ],
        [
            KeyboardButton(text="Click")
        ]
    ]
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)

    return kb


def product_kb(lang: str, all_pr: list = None) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for i in all_pr:
        kb.add(KeyboardButton(text=i.product_name))
    kb.add(KeyboardButton(text=ru['back'] if lang == 'ru' else uz['back']))
    kb.adjust(2)
    return kb.as_markup()


def category_product_menu(lang: str) -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text=ru['back'] if lang == 'ru' else uz['back']),
            KeyboardButton(text=ru['cart'] if lang == 'ru' else uz['cart'])
        ],
        [
            KeyboardButton(text="Продукты" if lang == 'ru' else "Mahsulotlar"),
            KeyboardButton(text="Сеты" if lang == 'ru' else "Setlar")
        ],
        [
            KeyboardButton(text="Продукты" if lang == 'ru' else "Merch")
        ]
    ]

    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=buttons)
    return kb
