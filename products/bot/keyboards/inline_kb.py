from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..handlers.some_func import json_loader
from ...models import Product

ru = json_loader()['menu']['ru']['inline_keyboard_button']
uz = json_loader()['menu']['uz']['inline_keyboard_button']


def choose_lang() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇿 O'zbekcha", callback_data="uz")
    kb.button(text="🇷🇺 Русский", callback_data="ru")
    kb.adjust(2)
    return kb.as_markup()


def menu_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=ru['choose_product'] if lang == 'ru' else uz['choose_product'], callback_data="choose_product")
    kb.button(text=ru['about_us'] if lang == 'ru' else uz['about_us'], callback_data="about_us")
    kb.button(text=ru['public_offer'] if lang == 'ru' else uz['public_offer'], callback_data="public_offer",
              url="https://telegra.ph/Publichnaya-oferta-04-19-4")
    kb.button(text=ru['cart'] if lang == 'ru' else uz['cart'], callback_data="cart")
    kb.adjust(2)
    return kb.as_markup()


def menu_inline_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=ru['about_us'] if lang == 'ru' else uz['about_us'], callback_data="about_us")
    kb.button(text=ru['public_offer'] if lang == 'ru' else uz['public_offer'], callback_data="public_offer",
              url="https://telegra.ph/Publichnaya-oferta-04-19-4")
    kb.adjust(1)
    return kb.as_markup()


def product_kb(lang: str, all_pr: list = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i in all_pr:
        kb.button(text=i.product_name, callback_data=f"product_{i.id}")
    if lang == 'ru':
        kb.button(text="🔙 Назад", callback_data="menu")
        kb.button(text="🏠 Главное меню", callback_data="menu")
    else:
        kb.button(text="🔙 Ortga", callback_data="menu")
        kb.button(text="🏠 Bosh menyu", callback_data="menu")

    kb.adjust(2)
    return kb.as_markup()


def product_menu_kb(current_amount=1, plus_or_minus="", lang="ru") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    count = InlineKeyboardButton(text=f"{current_amount}", callback_data="none")
    plus = InlineKeyboardButton(text="➕", callback_data="increment")
    minus = InlineKeyboardButton(text="➖", callback_data="decrement")
    if plus_or_minus == "increment":
        new_amount = current_amount + 1
        count = InlineKeyboardButton(text=f"{new_amount}", callback_data=str(new_amount))
    elif plus_or_minus == "decrement":
        if current_amount > 1:
            new_amount = current_amount - 1
            count = InlineKeyboardButton(text=f"{new_amount}", callback_data=str(new_amount))
    kb.add(minus, count, plus)
    if lang == 'ru':
        kb.button(text="🛒 В корзину", callback_data="to_cart")
        kb.button(text="🔙 Назад", callback_data="choose_product")
        kb.button(text="🏠 В меню", callback_data="menu")
    else:
        kb.button(text="🛒 Qo'shish", callback_data="to_cart")
        kb.button(text="🔙 Ortga", callback_data="choose_product")
        kb.button(text="🏠 Menyuga", callback_data="menu")
    kb.adjust(3)
    return kb.as_markup()


def about_us_menu_kb(lang: str):
    kb = InlineKeyboardBuilder()
    rus = "📲Отправить сообщение"
    uzb = "📲Xabar yuborish"

    kb.button(text="🗺Локация", url="youtube.com")
    kb.button(text=rus if lang == 'ru' else uzb, url="youtube.com")
    kb.button(text="💬Telegarm", url="youtube.com")
    kb.button(text="📸Instagram", url="youtube.com")
    kb.button(text="🌍Facebook", url="youtube.com")
    kb.button(text="🌐Сайт", url="youtube.com")
    kb.button(text="📹Youtube", url="youtube.com")

    kb.button(text="🏠Главное меню", callback_data="menu")
    kb.adjust(2)
    return kb.as_markup()


def user_cart_edit(lang: str, all_pr: list = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if all_pr:
        for product in all_pr:
            kb.button(text="❌" + " " + product["product_name"], callback_data=f"deleteprod_{product['id']}")
        kb.button(text=ru["promocode"] if lang == 'ru' else uz["promocode"], callback_data="write_promocode")
        kb.button(text=ru["order"] if lang == 'ru' else uz["order"], callback_data="order")
        kb.button(text="🔙Назад" if lang == 'ru' else "🔙Ortga", callback_data="choose_product")
        kb.adjust(1)
        return kb.as_markup()

    kb.button(text="🔙Назад" if lang == 'ru' else "🔙Ortga", callback_data="choose_product")
    kb.adjust(1)
    return kb.as_markup()
