import os
from asgiref.sync import sync_to_async
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from products.models import UserTG, UserCart, Product
from .some_func import json_loader
from products.bot.keyboards.inline_kb import choose_lang, about_us_menu_kb, menu_inline_kb, user_cart_edit, product_kb
from products.bot.keyboards.kb import get_phone_num, menu_kb
from products.bot.states import RegistrationState, StageOfOrderState
from products.bot.locator import geolocators

main_router = Router()

ru = json_loader()['menu']['ru']
uz = json_loader()['menu']['uz']


# print(product_service.get_all_product())

async def menu(lang, message=None, query=None):
    if lang == 'ru':
        if message:
            # await message.answer_photo(photo=FSInputFile(script_path), caption=ru['message_hello'], parse_mode='HTML',
            #                            reply_markup=menu_kb(lang))
            await message.answer("Главное меню", reply_markup=menu_kb(lang))
            await message.answer(ru['message_hello'], parse_mode='HTML',
                                 reply_markup=menu_inline_kb(lang))
        elif query:
            await query.message.delete()
            # await query.message.answer_photo(photo=FSInputFile(script_path), caption=ru['message_hello'],
            #                                  parse_mode='HTML', reply_markup=menu_kb(lang))
            await query.message.answer("Главное меню", reply_markup=menu_kb(lang))
            await query.message.answer(ru['message_hello'], parse_mode='HTML',
                                       reply_markup=menu_inline_kb(lang))
    elif lang == 'uz':
        if message:
            # await message.answer_photo(photo=FSInputFile(script_path), caption=uz['message_hello'], parse_mode='HTML',
            #                            reply_markup=menu_kb(lang))
            await message.answer("Bosh menyu", reply_markup=menu_kb(lang))
            await message.answer(uz['message_hello'], parse_mode='HTML',
                                 reply_markup=menu_inline_kb(lang))

        elif query:
            await query.message.delete()
            # await query.message.answer_photo(photo=FSInputFile(script_path), caption=uz['message_hello'],
            #                                  parse_mode='HTML', reply_markup=menu_kb(lang))
            await query.message.answer("Bosh menyu", reply_markup=menu_kb(lang))
            await query.message.answer(uz['message_hello'], parse_mode='HTML',
                                       reply_markup=menu_inline_kb(lang))


@sync_to_async
def get_user(user_id):
    user = UserTG.objects.get(user_tg_id=user_id)
    if user:
        return True
    return False


@sync_to_async
def get_lang(user_id):
    return UserTG.objects.get(user_tg_id=user_id).lang


@sync_to_async
def change_lang(user_id, lang):
    try:
        UserTG.objects.filter(user_tg_id=user_id).update(lang=lang)
        return True
    except Exception as e:
        raise e


@main_router.message(CommandStart())
async def start(message: Message):
    try:
        checker = await get_user(message.from_user.id)
        if checker:
            lang = await get_lang(message.from_user.id)
            await menu(lang=lang, message=message)
        else:
            # await message.answer_photo(photo=FSInputFile(photo_path),
            #                            caption=ru['message_hello'] + "\n" + uz['message_hello'], parse_mode='HTML')
            await message.answer(ru['message_hello'] + "\n" + uz['message_hello'], parse_mode='HTML')
            await message.answer("Выберите язык/Tilni tanlang", reply_markup=choose_lang())
    except Exception as e:
        # await message.answer_photo(photo=FSInputFile(photo_path),
        #                            caption=ru['message_hello'] + "\n" + uz['message_hello'], parse_mode='HTML')
        await message.answer(ru['message_hello'] + "\n" + uz['message_hello'], parse_mode='HTML')

        await message.answer("Выберите язык/Tilni tanlang", reply_markup=choose_lang())
        raise e


"""States"""


@main_router.message(RegistrationState.get_name)
async def get_name(message: Message, state: FSMContext):
    data = await state.get_data()
    data[str(message.from_user.id)].append(message.text)
    if data[str(message.from_user.id)][0] == 'ru':
        await message.answer(ru['message_reg_phone'], reply_markup=get_phone_num(data[str(message.from_user.id)][0]))
        await state.set_state(RegistrationState.get_phone)
    else:
        await message.answer(uz['message_reg_phone'], reply_markup=get_phone_num(data[str(message.from_user.id)][0]))
        await state.set_state(RegistrationState.get_phone)


@sync_to_async
def add_user(user_id, name, lang, phone_number):
    UserTG.objects.create(user_tg_id=user_id, user_name=name, lang=lang, phone_number=phone_number)
    return True


@main_router.message(RegistrationState.get_phone)
async def get_phone(message: Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    if message.contact:
        phone_number = message.contact.phone_number
        lang = data[str(message.from_user.id)][0]
        name = data[str(message.from_user.id)][1]
        result = await add_user(user_id, name, lang, phone_number)
        if result:
            await message.answer('Спасибо за регистрацию!', reply_markup=ReplyKeyboardRemove())
            await state.clear()
            await menu(message=message, lang=lang)
    else:
        await message.answer('Пожалуйста, введите свой номер телефона')
        await state.set_state(RegistrationState.get_phone)


@main_router.message(F.text.in_([ru['inline_keyboard_button']['about_us'], uz['inline_keyboard_button']['about_us']]))
async def about_us(message: Message):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    if lang == 'ru':
        await message.answer(ru['about_us_menu'], parse_mode="HTML", reply_markup=about_us_menu_kb(lang='ru'))
    elif lang == 'uz':
        await message.answer(uz['about_us_menu'], parse_mode="HTML", reply_markup=about_us_menu_kb(lang='uz'))


@main_router.message(F.text.in_(["🇷🇺ru", "🇺🇿uz"]))
async def public_offer(message: Message):
    user_id = message.from_user.id
    if message.text == "🇷🇺ru":
        result = await change_lang(user_id, 'ru')
        if result:
            lang = await get_lang(user_id)
            await menu(message=message, lang=lang)
    elif message.text == "🇺🇿uz":
        result = await change_lang(user_id, 'uz')
        if result:
            lang = await get_lang(user_id)
            await menu(message=message, lang=lang)


@sync_to_async
def get_user_cart(user_id):
    user_cart_items = UserCart.objects.filter(user_id=user_id)
    user_cart_dict = {}

    for item in user_cart_items:
        product_name = item.products.product_name
        if product_name in user_cart_dict:
            user_cart_dict[product_name]['quantity'] += item.quantity
            user_cart_dict[product_name]['total_price'] += item.total_price
        else:
            user_cart_dict[product_name] = {
                "id": item.products.id,
                'product_name': product_name,
                'quantity': item.quantity,
                'total_price': item.total_price
            }

    user_cart_list = list(user_cart_dict.values())
    print(user_cart_list)
    return user_cart_list


async def user_cart_menu(lang: str, message=None, query=None):
    if message:
        user_cart = await get_user_cart(message.from_user.id)
        if user_cart:
            total_price_all = 0
            cart_text = "Ваши товары в корзине:\n" if lang == 'ru' else "Savatdagi mahsulotlaringiz:\n"
            for item in user_cart:
                cart_text += f"{item['product_name']} - {item['quantity']} шт. - {item['total_price']} сум\n"
                total_price_all += item['total_price']
            await message.answer(
                cart_text + f"\n\nИтого: {total_price_all} сум" if lang == 'ru' else f"\n\nJami: {total_price_all} so'm",
                reply_markup=user_cart_edit(lang, user_cart))

        else:
            cart_text = "Ваша корзина пуста" if lang == 'ru' else "Sizning savatingiz bo'sh"

            await message.answer(cart_text, reply_markup=user_cart_edit(lang, user_cart))
    elif query:
        user_cart = await get_user_cart(query.from_user.id)
        if user_cart:
            total_price_all = 0
            cart_text = "Ваши товары в корзине:\n" if lang == 'ru' else "Savatdagi mahsulotlaringiz:\n"
            for item in user_cart:
                cart_text += f"{item['product_name']} - {item['quantity']} шт. - {item['total_price']} сум\n"
                total_price_all += item['total_price']
            await query.message.edit_text(
                cart_text + f"\n\nИтого: {total_price_all} сум" if lang == 'ru' else f"\n\nJami: {total_price_all} so'm",
                reply_markup=user_cart_edit(lang, user_cart))
        else:
            cart_text = "Ваша корзина пуста" if lang == 'ru' else "Sizning savatingiz bo'sh"

            await query.message.edit_text(cart_text, reply_markup=user_cart_edit(lang, user_cart))


@main_router.message(F.text.in_([ru['inline_keyboard_button']['cart'], uz['inline_keyboard_button']['cart']]))
async def cart(message: Message):
    lang = await get_lang(message.from_user.id)
    await user_cart_menu(message=message, lang=lang)


@sync_to_async
def get_all_product():
    return list(Product.objects.all())


@main_router.message(
    F.text.in_([ru['inline_keyboard_button']['choose_product'], uz['inline_keyboard_button']['choose_product']]))
async def choose_product(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    all_pr = await get_all_product()
    print(lang)

    if lang == 'ru':
        await message.answer("Заберите свой заказ самостоятельно 🙋 или выберите доставку 🚙")
        await state.set_state(StageOfOrderState.get_delivery)
    else:
        await message.answer("Buyurtmangizni mustaqil olib keting 🙋‍ yoki yetkazish xizmatini tanlang 🚙")
        await state.set_state(StageOfOrderState.get_delivery)


@main_router.message(StageOfOrderState.get_delivery)
async def get_delivery(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    all_pr = await get_all_product()
    if message.text == ru['inline_keyboard_button']['delivery']:
        await message.answer("Пожалуйста, скиньте свой адрес" if lang == 'ru' else "Iltimos, manzilni yuboring")
        await state.set_state(StageOfOrderState.get_location)
    elif message.text == uz['inline_keyboard_button']['pickup']:
        await message.answer(ru['choose_product'] if lang == 'ru' else uz['choose_product'], reply_markup=product_kb(lang, all_pr))
        await state.clear()
