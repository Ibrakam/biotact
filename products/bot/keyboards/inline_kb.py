from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..handlers.some_func import json_loader
import random
from ...models import Product

print(json_loader())
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
    kb.button(text=ru['public_offer'] if lang == 'ru' else uz['public_offer'], callback_data="public_offer",
              url="https://telegra.ph/Publichnaya-oferta-04-19-4")
    kb.adjust(1)
    return kb.as_markup()


def product_inline_kb(lang: str, all_pr: list = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    rand_item = random.sample(all_pr, 3)
    for i in rand_item:
        kb.button(text=i.product_name, callback_data=f"product_{i.id}")
    if lang == 'ru':
        kb.button(text=ru['back'], callback_data="back_to_category")
    else:
        kb.button(text=uz['back'], callback_data="back_to_category")

    kb.adjust(1)
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
    else:
        kb.button(text="🛒 Qo'shish", callback_data="to_cart")
    kb.adjust(3)
    return kb.as_markup()


def about_us_menu_kb(lang: str):
    kb = InlineKeyboardBuilder()
    rus = "📲Отправить сообщение"
    uzb = "📲Xabar yuborish"

    kb.button(text="🗺Локация",
              url="https://www.google.com/maps/place/41°20'56.8%22N+69°10'45.1%22E/@41.349118,69.1766051,17z/data=!3m1!4b1!4m4!3m3!8m2!3d41.349118!4d69.17918?entry=ttu")
    kb.button(text=rus if lang == 'ru' else uzb, url="https://t.me/@biotact_deutschland_uz")
    kb.button(text="💬Telegarm", url="https://t.me/BiotactDeutschland_uz")
    kb.button(text="📸Instagram", url="https://www.instagram.com/biotactdeutschland_uz")
    kb.button(text="🌍Facebook", url="https://www.facebook.com/BiotactDeutschlandUz")
    kb.button(text="🌐Сайт", url="biotact.uz")
    kb.button(text="📹Youtube", url="https://www.youtube.com/@biotactdeutschland")

    kb.button(text="🏠Главное меню", callback_data="menu")
    kb.adjust(2)
    return kb.as_markup()


def user_cart_edit(lang: str, promo_code: bool = False, all_pr: list = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if all_pr:
        for product in all_pr:
            kb.button(text="❌" + " " + product["product_name"], callback_data=f"deleteprod_{product['id']}")
        if not promo_code:
            kb.button(text=ru["promocode"] if lang == 'ru' else uz["promocode"], callback_data="write_promocode")
        kb.button(text="Продолжить заказ" if lang == "ru" else "Zakazni davom etish", callback_data="continue")
        kb.button(text=ru["order"] if lang == 'ru' else uz["order"], callback_data="order")
        kb.button(text="🔙Назад" if lang == 'ru' else "🔙Ortga", callback_data="back_to_category")
        kb.adjust(1)
        return kb.as_markup()

    kb.button(text="🔙Назад" if lang == 'ru' else "🔙Ortga", callback_data="back_to_category")
    kb.adjust(1)
    return kb.as_markup()


def back_promocode(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙Назад" if lang == 'ru' else "🔙Ortga", callback_data="from_promocode")
    kb.adjust(1)
    return kb.as_markup()


def wb_button() -> InlineKeyboardMarkup:
    web_app_url = 'http://127.0.0.1:8000/'  #
    buttons = [
        [
            InlineKeyboardButton(text="Go to shop", web_app=WebAppInfo(url=web_app_url))
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


def choose_payment_kb(lang: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="Наличные" if lang == 'ru' else "Naqd", callback_data="cash")
    kb.button(text="Terminal", callback_data="Terminal")
    kb.button(text="Payme", callback_data="Payme")
    kb.button(text="Click", callback_data="Click")

    kb.adjust(2)
    return kb.as_markup()


def confirm_order_kb(lang: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="❌Отменить" if lang == "ru" else "❌Bekor qilish", callback_data="cancel")
    kb.button(text="✅Подтвердить" if lang == "ru" else "✅Tasdiqlash", callback_data="confirm")
    kb.button(text="🔄Изменить" if lang == "ru" else "🔄Tahrirlash", callback_data="change")
    kb.adjust(2)
    return kb.as_markup()


from aiogram.filters.callback_data import CallbackData


class OrderCallback(CallbackData, prefix="order"):
    action: str
    user_id: int


def builder_inline_mk(text, call_data):
    kb = InlineKeyboardBuilder()
    for i, j in zip(text, call_data):
        kb.button(text=i, callback_data=OrderCallback(action=j["action"], user_id=j["user_id"]).pack())
    return kb.as_markup()


