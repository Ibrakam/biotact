import os
from asgiref.sync import sync_to_async
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from django.db.models import Q

from products.models import UserTG, UserCart, Product, Promocode, UsedPromocode
from .some_func import json_loader
from products.bot.keyboards.inline_kb import choose_lang, about_us_menu_kb, menu_inline_kb, user_cart_edit, product_inline_kb, \
    wb_button
from products.bot.keyboards.kb import get_phone_num, menu_kb, stage_order_delivery_kb, send_location_kb, \
    confirm_location_kb, product_kb
from products.bot.states import RegistrationState, StageOfOrderState, PromocodeState
from products.bot.locator import geolocators

main_router = Router()

ru = json_loader()['menu']['ru']
uz = json_loader()['menu']['uz']

user_location = {}


# print(product_service.get_all_product())

async def menu(lang, message=None, query=None):
    if lang == 'ru':
        try:
            if message:
                is_order = True if user_location[message.from_user.id] else False
                print(message.text)
                # await message.answer_photo(photo=FSInputFile(script_path), caption=ru['message_hello'], parse_mode='HTML',
                #                            reply_markup=menu_kb(lang))
                await message.answer("Главное меню", reply_markup=menu_kb(lang, is_order))
                await message.answer(ru['message_hello'], parse_mode='HTML',
                                     reply_markup=menu_inline_kb(lang))
            elif query:
                is_order = True if user_location[query.from_user.id] else False

                await query.message.delete()
                # await query.message.answer_photo(photo=FSInputFile(script_path), caption=ru['message_hello'],
                #                                  parse_mode='HTML', reply_markup=menu_kb(lang))
                await query.message.answer("Главное меню", reply_markup=menu_kb(lang, is_order))
                await query.message.answer(ru['message_hello'], parse_mode='HTML',
                                           reply_markup=menu_inline_kb(lang))
        except Exception as e:
            if message:
                print(e)

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
        try:

            if message:
                is_order = True if user_location[message.from_user.id] else False
                # await message.answer_photo(photo=FSInputFile(script_path), caption=uz['message_hello'], parse_mode='HTML',
                #                            reply_markup=menu_kb(lang))
                await message.answer("Bosh menyu", reply_markup=menu_kb(lang, is_order))
                await message.answer(uz['message_hello'], parse_mode='HTML',
                                     reply_markup=menu_inline_kb(lang))

            elif query:
                is_order = True if user_location[query.from_user.id] else False
                await query.message.delete()
                # await query.message.answer_photo(photo=FSInputFile(script_path), caption=uz['message_hello'],
                #                                  parse_mode='HTML', reply_markup=menu_kb(lang))
                await query.message.answer("Bosh menyu", reply_markup=menu_kb(lang, is_order))
                await query.message.answer(uz['message_hello'], parse_mode='HTML',
                                           reply_markup=menu_inline_kb(lang))
        except Exception as e:
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


@sync_to_async
def get_user_promocode_cart(user_id):
    user_cart_items = UserCart.objects.filter(user_id=user_id)
    if not user_cart_items.first().promocode:
        return 0
    user_promocode = Promocode.objects.filter(promocode_code=user_cart_items.first().promocode).first().discount
    return user_promocode if user_promocode else 0


async def user_cart_menu(lang: str, message=None, query=None):
    if message:
        user_cart = await get_user_cart(message.from_user.id)
        if user_cart:
            discount = await get_user_promocode_cart(message.from_user.id)
            print(discount)
            total_price_all = 0
            cart_text = "Ваши товары в корзине:\n" if lang == 'ru' else "Savatdagi mahsulotlaringiz:\n"
            for item in user_cart:
                cart_text += f"{item['product_name']} - {item['quantity']} шт. - {item['total_price']} сум\n"
                total_price_all += item['total_price']

            if discount > 0:
                total_price_all -= total_price_all * (discount / 100)
                await message.answer(
                    cart_text + f"\n\nИтого: {total_price_all} сум c учетом скидки {discount}%" if lang == 'ru' else f"\n\nJami: {total_price_all} so'm {discount}% skidka bilan",
                    reply_markup=user_cart_edit(lang, True if discount > 0 else False, user_cart))
            else:
                await message.answer(
                    cart_text + f"\n\nИтого: {total_price_all} сум" if lang == 'ru' else f"\n\nJami: {total_price_all} so'm",
                    reply_markup=user_cart_edit(lang, True if discount > 0 else False, user_cart))

        else:
            cart_text = "Ваша корзина пуста" if lang == 'ru' else "Sizning savatingiz bo'sh"

            await message.answer(cart_text,
                                 reply_markup=user_cart_edit(lang, False, user_cart))
    elif query:
        user_cart = await get_user_cart(query.from_user.id)

        if user_cart:
            discount = await get_user_promocode_cart(query.from_user.id)
            total_price_all = 0
            cart_text = "Ваши товары в корзине:\n" if lang == 'ru' else "Savatdagi mahsulotlaringiz:\n"
            for item in user_cart:
                cart_text += f"{item['product_name']} - {item['quantity']} шт. - {item['total_price']} сум\n"
                total_price_all += item['total_price']
            if discount > 0:
                total_price_all -= total_price_all * (discount / 100)
                await query.message.edit_text(
                    cart_text + f"\n\nИтого: {total_price_all} сум c учетом скидки {discount}%" if lang == 'ru' else f"\n\nJami: {total_price_all} so'm {discount}% skidka bilan",
                    reply_markup=user_cart_edit(lang, True if discount > 0 else False, user_cart))
            else:
                await query.message.edit_text(
                    cart_text + f"\n\nИтого: {total_price_all} сум" if lang == 'ru' else f"\n\nJami: {total_price_all} so'm",
                    reply_markup=user_cart_edit(lang, True if discount > 0 else False, user_cart))
        else:
            cart_text = "Ваша корзина пуста" if lang == 'ru' else "Sizning savatingiz bo'sh"

            await query.message.edit_text(cart_text,
                                          reply_markup=user_cart_edit(lang, False, user_cart))


@main_router.message(F.text.in_([ru['inline_keyboard_button']['cart'], uz['inline_keyboard_button']['cart']]))
async def cart(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    try:
        if user_location[message.from_user.id]:
            await user_cart_menu(message=message, lang=lang)
        else:
            await message.answer("Давайте начнем заказ" if lang == 'ru' else "Buyurtmani boshlaymiz",
                                 reply_markup=stage_order_delivery_kb(lang))
            await state.set_state(StageOfOrderState.get_delivery)
    except Exception as e:
        print(e)
        await message.answer("Давайте начнем заказ" if lang == 'ru' else "Buyurtmani boshlaymiz",
                             reply_markup=stage_order_delivery_kb(lang))
        await state.set_state(StageOfOrderState.get_delivery)


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
    try:
        is_order = True if user_location[user_id] else False
        if is_order:
            if lang == 'ru':
                await message.answer("Выберите продукт", reply_markup=menu_kb(lang, is_order=True))
                await message.answer(ru['choose_product_menu'], parse_mode="HTML",
                                     reply_markup=product_kb(lang, all_pr))
            else:
                await message.answer("Выберите продукт", reply_markup=menu_kb(lang, is_order=True))
                await message.answer(uz['choose_product_menu'], parse_mode="HTML",
                                     reply_markup=product_kb(lang, all_pr))
            return
        else:
            if lang == 'ru':
                await message.answer("Заберите свой заказ самостоятельно 🙋 или выберите доставку 🚙",
                                     reply_markup=stage_order_delivery_kb(lang))
                await state.set_state(StageOfOrderState.get_delivery)
            else:
                await message.answer("Buyurtmangizni mustaqil olib keting 🙋‍ yoki yetkazish xizmatini tanlang 🚙",
                                     reply_markup=stage_order_delivery_kb(lang))
                await state.set_state(StageOfOrderState.get_delivery)
    except KeyError:
        pass
    if lang == 'ru':
        await message.answer("Заберите свой заказ самостоятельно 🙋 или выберите доставку 🚙",
                             reply_markup=stage_order_delivery_kb(lang))
        await state.set_state(StageOfOrderState.get_delivery)
    else:
        await message.answer("Buyurtmangizni mustaqil olib keting 🙋‍ yoki yetkazish xizmatini tanlang 🚙",
                             reply_markup=stage_order_delivery_kb(lang))
        await state.set_state(StageOfOrderState.get_delivery)


@main_router.message(StageOfOrderState.get_delivery)
async def get_delivery(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    all_pr = await get_all_product()
    if message.text == ru['inline_keyboard_button']['delivery'] or message.text == uz['inline_keyboard_button'][
        'delivery']:
        await message.answer("Пожалуйста, скиньте свой адрес" if lang == 'ru' else "Iltimos, manzilni yuboring",
                             reply_markup=send_location_kb(lang))
        await state.set_state(StageOfOrderState.get_location)
    elif message.text == uz['inline_keyboard_button']['pickup'] or message.text == ru['inline_keyboard_button'][
        'pickup']:
        user_location[user_id] = "biotact"
        # await message.answer("""Закажите через новое удобное меню 👇😉""", reply_markup=wb_button())
        await message.answer("Выберите продукт" if lang == 'ru' else "Productni tanlang",
                             reply_markup=menu_kb(lang, is_order=True))
        await message.answer(ru['choose_product_menu'] if lang == 'ru' else uz['choose_product_menu'],
                             parse_mode="HTML",
                             reply_markup=product_kb(lang, all_pr))
        await state.clear()
    elif message.text == uz['inline_keyboard_button']['back'] or message.text == ru['inline_keyboard_button']['back']:
        await menu(lang=lang, message=message)
        await state.clear()


@main_router.message(StageOfOrderState.get_location)
async def get_location(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    if message.location:
        longitude = message.location.longitude
        latitude = message.location.latitude
        location = geolocators(latitude, longitude)
        await message.answer(f"Ваш адрес: {location}", reply_markup=confirm_location_kb(lang))
        user_location[user_id] = location
    if message.text == 'Подтвердить' or message.text == 'Tasdiqlash':
        all_pr = await get_all_product()

        if lang == 'ru':
            await message.answer("Выберите продукт", reply_markup=menu_kb(lang))
            await message.answer(ru['choose_product_menu'], parse_mode="HTML",
                                 reply_markup=product_kb(lang, all_pr))
        else:
            await message.answer("Выберите продукт", reply_markup=menu_kb(lang))
            await message.answer(uz['choose_product_menu'], parse_mode="HTML",
                                 reply_markup=product_kb(lang, all_pr))
        await state.clear()
    if message.text == uz['inline_keyboard_button']['back'] or message.text == ru['inline_keyboard_button']['back']:
        await state.clear()
        await menu(lang=lang, message=message)


@main_router.message(F.text == ru['inline_keyboard_button']['back'] or F.text == uz['inline_keyboard_button']['back'])
async def back_to_menu(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    await state.clear()
    await menu(lang=lang, message=message)


@main_router.message(F.text.in_(["Начать заказ заново", "Buyurtma qayta boshlash"]))
async def back_to_menu(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    print(lang, user_id)
    user_location.pop(user_id)
    await menu(lang=lang, message=message)


@sync_to_async
def get_user_promocode(user_id=None, lang=None, promocode=None):
    # Проверка, что промокод существует
    if not Promocode.objects.filter(promocode_code=promocode).exists():
        return "Такого промокода нету" if lang == 'ru' else 'Bu promokod mavjud emas'

    # Проверка, что промокод уже был использован данным пользователем
    if UsedPromocode.objects.filter(Q(promocode=promocode) & Q(user_id=user_id)).exists():
        return "Такой промокод уже использован" if lang == 'ru' else 'Bu promokod avval foydalanilgan'

    # Получение данных о промокоде
    promocode_user = Promocode.objects.filter(promocode_code=promocode)
    if promocode_user.exists():
        UserCart.objects.filter(user_id=user_id).update(promocode=promocode_user.first().promocode_code)
        return "Промокод активирован" if lang == 'ru' else 'Promokod aktivlashtirildi'
    else:
        return False


@sync_to_async
def update_user_cart(user_id, promocode):
    UserCart.objects.filter(user_id=user_id).update(promocode=promocode)


@main_router.message(PromocodeState.get_promocode)
async def get_promocode(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    result = await get_user_promocode(user_id, lang, message.text)
    await state.clear()
    await message.answer(result, reply_markup=menu_kb(lang, True))
    await user_cart_menu(lang=lang, message=message)


@sync_to_async
def get_all_info(user_id):
    user = UserTG.objects.get(user_tg_id=user_id)
    return [user.phone_number, user.user_name]


@sync_to_async
def delete_user_cart(user_id):
    UserCart.objects.filter(user_id=user_id).delete()
    return True


@main_router.message(F.text.in_(["Click", "Payme", "Теримнал/Карта", "Terminal/Karta",
                                 "Наличные", "Naqd", ru['inline_keyboard_button']['back'],
                                 uz['inline_keyboard_button']['back']]))
async def payment(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    info = await get_all_info(user_id)
    delivery_or = f"🚙 Доставка \n📍 {user_location[user_id]}\n\n" if user_location[user_id] else "📦 Самовывоз"
    cart_text = f"""Имя: {info[1]}
Телефон: {info[0]}
Способ оплаты: 💳{message.text}
Тип заказа: {delivery_or}"""
    user_cart = await get_user_cart(message.from_user.id)
    discount = await get_user_promocode_cart(message.from_user.id)
    total_price_all = 0
    for item in user_cart:
        cart_text += f"{item['quantity']} x {item['product_name']} \n"
        total_price_all += item['total_price']
    if discount > 0:
        total_price_all -= total_price_all * (discount / 100)
        await message.answer(
            cart_text + f"\n\nИтого: {total_price_all} сум c учетом скидки {discount}%" if lang == 'ru' else f"\n\nJami: {total_price_all} so'm {discount}% skidka bilan")
    else:
        await message.answer(
            cart_text + f"\n\nИтого: {total_price_all} сум" if lang == 'ru' else f"\n\nJami: {total_price_all} so'm",
            reply_markup=menu_kb(lang, False))
    await message.bot.send_message(889121031,
                                   cart_text + f"\n\nИтого: {total_price_all} сум" if lang == 'ru' else f"\n\nJami: {total_price_all} so'm")
    user_location.pop(user_id)
    info = await delete_user_cart(user_id)
    print("good" if info else "bad")
    await menu(lang, message)
    if message.text == ru['inline_keyboard_button']['back'] or message.text == uz['inline_keyboard_button']['back']:
        await state.clear()
        await user_cart_menu(lang=lang, message=message)
