import os

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404

from products.bot.keyboards.kb import payment_kb
from products.bot.states import RegistrationState, PromocodeState
from products.bot.handlers.some_func import json_loader
from products.bot.keyboards.inline_kb import product_kb, product_menu_kb, about_us_menu_kb, back_promocode
from products.bot.handlers.bot_commands import menu, user_cart_menu
from products.models import UserTG, Product, UserCart

ru = json_loader()['menu']['ru']
uz = json_loader()['menu']['uz']

callback_router = Router()


@sync_to_async
def get_product(product_id):
    return Product.objects.get(id=product_id)


@sync_to_async
def get_lang(user_id):
    return UserTG.objects.get(user_tg_id=user_id).lang


@sync_to_async
def add_to_cart(user_id, product_id, quantity, promocode=None):
    try:
        product = get_object_or_404(Product, id=product_id)
        UserCart.objects.create(user_id=user_id, products=product, quantity=quantity,
                                total_price=+(quantity * product.price),
                                promocode=promocode)
        return True
    except Exception as e:
        print(Exception, e)


def get_image(filename):
    try:
        current_path = os.path.abspath(os.getcwd())
        image_path = os.path.join(current_path, 'media', filename)

        with open(image_path, 'rb') as photo:
            return photo.read()

    except Exception as e:
        print(Exception, e)


async def product_menu(query, product_id):
    user_id = query.from_user.id
    product = await get_product(product_id)
    lang = await get_lang(user_id)
    if lang == "ru":
        await query.message.delete()
        image = get_image("/Users/ibragimkadamzanov/PycharmProjects/pythonProject19/" + product.product_image.url)
        await query.message.answer_photo(
            photo=FSInputFile("/Users/ibragimkadamzanov/PycharmProjects/pythonProject19/" + product.product_image.url),
            caption=f"<b>{product.product_name}</b>\n\n"
                    f"{product.price} сум\n\n{product.description_ru}",
            parse_mode="HTML", reply_markup=product_menu_kb(lang=lang))
    else:
        await query.message.delete()
        await query.message.answer_photo(photo=product.product_image.url,
                                         caption=f"<b>{product.product_name}</b>\n\n"
                                                 f"{product.price} so'm\n\n{product.description_uz}",
                                         parse_mode="HTML", reply_markup=product_menu_kb(lang=lang))


@callback_router.callback_query(F.data.in_(['ru', 'uz']))
async def change_lang(query: CallbackQuery, state: FSMContext):
    await state.set_data({str(query.from_user.id): [query.data]})
    if query.data == 'ru':
        await query.message.edit_text(ru['message_reg_name'])
        await state.set_state(RegistrationState.get_name)
    else:
        await query.message.edit_text(uz['message_reg_name'])
        await state.set_state(RegistrationState.get_name)


@sync_to_async
def get_all_product():
    products = list(Product.objects.all())
    print(products)
    return products


@callback_router.callback_query(F.data == 'choose_product')
async def choose_product(query: CallbackQuery):
    user_id = query.from_user.id
    lang = await get_lang(user_id)
    all_pr = await get_all_product()
    print(lang)
    if lang == 'ru':
        await query.message.delete()
        await query.message.answer(ru['choose_product_menu'], parse_mode="HTML", reply_markup=product_kb(lang, all_pr))
    else:
        await query.message.delete()
        await query.message.answer(uz['choose_product_menu'], parse_mode="HTML", reply_markup=product_kb(lang, all_pr))


@callback_router.callback_query(F.data == "menu")
async def back_to_menu(query: CallbackQuery):
    user_id = query.from_user.id
    lang = await get_lang(user_id)
    await menu(query=query, lang=lang)


@callback_router.callback_query(F.data.in_(['increment', 'decrement', 'to_cart']))
async def get_user_product_count(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = await get_lang(user_id)
    data = await state.get_data()
    users = data['user']
    #     # Если пользователь нажал на +
    if query.data == 'increment':
        actual_count = users[user_id]['pr_count']

        users[user_id]['pr_count'] += 1
        # Меняем значение кнопки
        await query.message.edit_reply_markup(
            reply_markup=product_menu_kb(plus_or_minus='increment', current_amount=actual_count, lang=lang))
    elif query.data == 'decrement':
        actual_count = users[user_id]['pr_count']

        if actual_count > 1:
            users[user_id]['pr_count'] -= 1
            # Меняем значение кнопки
            await query.message.edit_reply_markup(
                reply_markup=product_menu_kb(plus_or_minus='decrement', current_amount=actual_count, lang=lang))
    elif query.data == 'to_cart':
        product_count = users[user_id]['pr_count']
        user_product = users[user_id]['product_id']
        user_id = query.from_user.id
        result = await add_to_cart(user_id=user_id, product_id=user_product, quantity=product_count, promocode=None)
        await query.message.bot.answer_callback_query(query.id, text='Товар добавлен в корзину', show_alert=True)
        await state.clear()
        await choose_product(query)


@callback_router.callback_query(F.data.startswith('product_'))
async def product_menu_call(query: CallbackQuery, state: FSMContext):
    product_id = query.data.split('_')[1]
    await state.set_data({"user": {query.from_user.id: {'product_id': product_id, 'pr_count': 1}}})
    await product_menu(query, int(product_id))


@sync_to_async
def delete_user_cart_product(product_id):
    if UserCart.objects.filter(products_id=product_id).exists():
        UserCart.objects.filter(products_id=product_id).delete()
        return True
    return False


@callback_router.callback_query(F.data.startswith('deleteprod_'))
async def product_menu_call(query: CallbackQuery, state: FSMContext):
    product_id = query.data.split('_')[1]
    result = await delete_user_cart_product(int(product_id))
    lang = await get_lang(query.from_user.id)
    if result:
        await user_cart_menu(lang=lang, query=query)
        await query.message.bot.answer_callback_query(query.id, text='Товар удален из корзины', show_alert=True)
    else:
        await query.message.bot.answer_callback_query(query.id, text='Товар уже удален из корзины', show_alert=True)


@callback_router.callback_query(F.data == "about_us")
async def about_us(query: CallbackQuery):
    user_id = query.from_user.id
    lang = await get_lang(user_id)
    if lang == 'ru':
        await query.message.delete()
        await query.message.answer(ru['about_us_menu'], parse_mode="HTML", reply_markup=about_us_menu_kb(lang='ru'))
    elif lang == 'uz':
        await query.message.delete()
        await query.message.answer(uz['about_us_menu'], parse_mode="HTML", reply_markup=about_us_menu_kb(lang='uz'))


@callback_router.callback_query(F.data == "write_promocode")
async def write_promocode(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = await get_lang(user_id)
    if lang == 'ru':
        await query.message.edit_text(ru['message_promocode'], reply_markup=back_promocode(lang))
    else:
        await query.message.edit_text(uz['message_promocode'], reply_markup=back_promocode(lang))

    await state.set_state(PromocodeState.get_promocode)

@callback_router.callback_query(F.data == "from_promocode")
async def root(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = await get_lang(user_id)
    await state.clear()
    await user_cart_menu(lang=lang, query=query)


@callback_router.callback_query(F.data == "order")
async def root(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = await get_lang(user_id)
    await query.message.delete()
    await query.message.answer(ru["which_payment"] if lang == "ru" else uz["which_payment"], reply_markup=payment_kb(lang))
    await state.clear()
