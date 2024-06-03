import os
from datetime import datetime

from aiogram.enums import ContentType
from aiogram.utils.formatting import Text
from asgiref.sync import sync_to_async
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import CommandStart, Command
from django.db.models import Q

from products.models import UserTG, UserCart, Product, Promocode, UsedPromocode, MyOrders
from .some_func import json_loader
from products.bot.keyboards.inline_kb import choose_lang, about_us_menu_kb, menu_inline_kb, user_cart_edit, \
    product_inline_kb, \
    wb_button, product_menu_kb, choose_payment_kb, confirm_order_kb, builder_inline_mk, OrderCallback
from products.bot.keyboards.kb import get_phone_num, menu_kb, stage_order_delivery_kb, send_location_kb, \
    confirm_location_kb, product_kb, category_product_menu, product_edit_menu, product_back_to_category, \
    leave_feedback_kb, settings_kb, phone_number_kb, birthday_kb, choose_time_kb, generate_time_buttons
from products.bot.states import RegistrationState, StageOfOrderState, PromocodeState, LeaveFeedback, PromotionState, \
    SettingsState, TimeState
from products.bot.locator import geolocators
from dotenv import dotenv_values

config_token = dotenv_values(".env")
CLICK_TOKEN = config_token['CLICK_TOKEN']
PAYME_TOKEN = config_token['PAYME_TOKEN']
ADMIN_ID = -4276762392

payment_router = Router()

main_router = Router()
callback_router2 = Router()

ru = json_loader()['menu']['ru']
uz = json_loader()['menu']['uz']

user_location = {}
finally_order = {}
broadcast_router = Router()

admins = [889121031, ADMIN_ID]


@sync_to_async
def get_all_user():
    try:
        user = UserTG.objects.all()
        return list(user)
    except Exception as e:
        print(e)


@sync_to_async
def get_user_by_phone(phone_number):
    try:
        user = UserTG.objects.get(phone_number=phone_number)
        return user
    except Exception as e:
        print(e)


async def broadcast_all_users(message):
    users = await get_all_user()
    for user in users:
        try:
            await message.bot.send_message(user.user_tg_id, message.text.split(" ", 1)[1])
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user.phone_number}: {e}")
            await message.bot.send_message(ADMIN_ID,
                                           f"Не удалось отправить сообщение пользователю {user.phone_number}: {e}")


# Функция для отправки сообщения пользователю по номеру телефона
async def send_message_by_phone(phone_number, message, message_text):
    user = await get_user_by_phone(phone_number)
    if user:
        try:
            await message.bot.send_message(user.user_tg_id, message_text)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user.user_tg_id}: {e}")
            await message.bot.send_message(ADMIN_ID,
                                           f"Не удалось отправить сообщение пользователю {user.phone_number}: {e}")

    else:
        print(f"Пользователь с номером телефона {phone_number} не найден.")
        await message.bot.send_message(ADMIN_ID, f"Пользователь с номером телефона {phone_number} не найден.")


# Пример команды для запуска рассылки всем пользователям
@broadcast_router.message(Command("broadcast"))
async def handle_broadcast_command(message: Message):
    user_id = message.from_user.id
    if user_id in admins:
        await broadcast_all_users(message)
        await message.reply("Рассылка завершена.")
    else:
        await menu(lang=await get_lang(user_id), message=message)


# Пример команды для отправки сообщения по номеру телефона
@broadcast_router.message(Command("send"))
async def handle_send_command(message: Message):
    user_id = message.from_user.id
    if user_id in admins:
        args = message.text.split(' ', 1)

        if len(args) != 2:
            await message.reply("Используйте команду в формате: /send <номер_телефона> <сообщение>")
            return

        print(args[1])
        phone_number, message_text = args[1].split(' ', 1)
        print(phone_number, message_text)
        await send_message_by_phone(phone_number, message, message_text)
        await message.reply("Сообщение отправлено.")
    else:
        await menu(lang=await get_lang(user_id), message=message)


@callback_router2.callback_query(F.data.in_(["cancel", "confirm", "change"]))
async def root(query: CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    lang = await get_lang(user_id)
    data = await state.get_data()
    info = await get_all_info(user_id)
    pay = f"{"💴 Наличные" if lang == "ru" else "💴 Naqd"}" if data["payment"][user_id] == "cash" else "💳" + \
                                                                                                     data["payment"][
                                                                                                         user_id]
    if query.data == "cancel":
        await state.clear()
        await query.message.delete()
        del_cart = await delete_user_cart(user_id)
        finally_order.pop(user_id)
        user_location.pop(user_id)
        await menu(lang=lang, message=query.message)
    elif query.data == "confirm":
        print(user_location)
        await query.message.delete()
        await user_order_conf_menu(user_id, message=query.message, kb=None, payment_method=pay)
        user_id = query.from_user.id
        print(pay)
        if pay in ["💳Click", "💳Payme"]:
            # Пример заказанных продуктов
            ordered_products = await get_user_cart(user_id)

            # Создание списка цен (LabeledPrice) на основе заказанных продуктов
            prices = [LabeledPrice(label=item['product_name'], amount=item['total_price'] * 100) for item in
                      ordered_products]

            # Отправка счета
            await query.message.bot.send_invoice(
                chat_id=user_id,
                title="Оплата заказа",
                description="Пожалуйста, оплатите ваш заказ",
                provider_token=CLICK_TOKEN if pay == "💳Click" else PAYME_TOKEN,
                # Замените на ваш токен платежного провайдера
                currency='UZS',
                prices=prices,
                start_parameter='order-payment',
                payload='order-payment-payload'
            )
        else:
            cart_text = await order_menu(user_id, state)
            await query.message.bot.send_message(ADMIN_ID, cart_text + "\n\nПодтвержден")
            if lang == "ru":
                await query.message.bot.send_message(user_id,
                                                     "Заказ принят. Вам позвонят для уточнения заказа",
                                                     reply_markup=menu_kb(lang))
            else:
                await query.message.bot.send_message(user_id,
                                                     "Buyurtma qabul qilindi. Buyurtmani aniqlashtirish uchun sizga qo'ng'iroq qilishadi",
                                                     reply_markup=menu_kb(lang))

        print("good" if info else "bad")
    elif query.data == "change":
        await user_order_conf_menu(user_id, query=query, kb=choose_payment_kb)


@callback_router2.pre_checkout_query(lambda query: True)
async def pre_check(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def order_menu(user_id, state: FSMContext):
    lang = await get_lang(user_id)
    data = await state.get_data()
    info = await get_all_info(user_id)
    pay = f"{"💴 Наличные" if lang == "ru" else "💴 Naqd"}" if data["payment"][user_id] == "cash" else "💳" + \
                                                                                                     data["payment"][
                                                                                                         user_id]

    delivery_or = f"🚙 Доставка \n📍 {user_location[user_id][0]}" if user_location[user_id][0] else "📦 Самовывоз"
    delivery_or_uz = f"🚙 Yetkazib berish \n📍 {user_location[user_id][0]}" if user_location[
        user_id][0] else "📦 Olib ketish"
    cart_text = ""
    user_cart = await get_user_cart(user_id)
    discount = await get_user_promocode_cart(user_id)
    total_price_all = 0
    for item in user_cart:
        cart_text += f"{item['product_name']} x {item['quantity']} = {item['total_price']} \n"
        total_price_all += item['total_price']
    if discount > 0:
        total_price_all -= total_price_all * (discount / 100)
        cart_text += f"\n\nИтого: {total_price_all:,} сум c учетом скидки {discount}%" if lang == 'ru' else f"\n\nJami: {total_price_all:,} so'm {discount}% skidka bilan"
        cart_text += f"""\n\n{"Имя" if lang == 'ru' else "Ismi"}: {info[1]}
{"Телефон" if lang == "ru" else "Telefon"}: {info[0]}
{(f"Дoполнительные номер:{user_location[user_id][1]}" if lang == "ru" else f"Qo'shimcha raqam:user_location[user_id][1]") if user_location[user_id][1] else ("Дополнительные номер:Нету" if lang == "ru" else f"Qo'shimcha raqam:Yoq")}:
{"Тип заказа" if lang == "ru" else "Turi"}: {delivery_or if lang == 'ru' else delivery_or_uz}
{"Тип оплаты" if lang == "ru" else "To'lov turi"}: 
{pay}: {total_price_all:,}
{(f"Комментарий к заказу: {user_location[user_id][2]}" if lang == "ru" else f"Xabar: {user_location[user_id][2]}") if user_location[user_id][2] else ("Комментарий к заказу: Нету" if lang == "ru" else f"Xabar: Yoq")}

        """
        return cart_text
    else:
        cart_text += f"\n\nИтого: {total_price_all:,} сум" if lang == 'ru' else f"\n\nJami: {total_price_all:,} so'm"
        cart_text += f"""\n\n{"Имя" if lang == 'ru' else "Ismi"}: {info[1]}
{"Телефон" if lang == "ru" else "Telefon"}: {info[0]}
{(f"Дoполнительные номер:{user_location[user_id][1]}" if lang == "ru" else f"Qo'shimcha raqam:user_location[user_id][1]") if user_location[user_id][1] else ("Дополнительные номер:Нету" if lang == "ru" else f"Qo'shimcha raqam:Yoq")}:
{"Тип заказа" if lang == "ru" else "Turi"}: {delivery_or if lang == 'ru' else delivery_or_uz}
{"Тип оплаты" if lang == "ru" else "To'lov turi"}:
{pay}: {total_price_all:,}
{(f"Комментарий к заказу: {user_location[user_id][2]}" if lang == "ru" else f"Xabar: {user_location[user_id][2]}") if user_location[user_id][2] else ("Комментарий к заказу: Нету" if lang == "ru" else f"Xabar: Yoq")}
                        """
        return cart_text


# Оброботчик после(Успешной) оплаты через CLICK
@main_router.message(lambda message: message.successful_payment)
async def got_payment(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    data = await state.get_data()
    info = await get_all_info(user_id)
    pay = f"{"💴 Наличные" if lang == "ru" else "💴 Naqd"}" if data["payment"][user_id] == "cash" else "💳" + \
                                                                                                     data["payment"][
                                                                                                         user_id]

    if lang == "uz":
        response_text = f"Тошган тушунча раҳмат! {message.successful_payment.total_amount / 100} {message.successful_payment.currency} нархидаги заявкани тез ёпамиз! Алоқада туринг!"
    elif lang == "ru":
        response_text = f"Ура! Спасибо за оплату! Мы обработаем ваш заказ на {message.successful_payment.total_amount / 100} {message.successful_payment.currency} как можно быстрее! Оставайтесь на связи!"

    # Отправка сообщения пользователю
    await message.bot.send_message(user_id, response_text)

    # admin_id = -4276762392
    # admin_id = 889121031

    # очистить корзину пользователя
    cart_text = await order_menu(user_id, state)
    # отправим админу сообщение о новом заказе
    try:
        if finally_order[user_id]:
            await message.bot.send_location(chat_id=ADMIN_ID, latitude=finally_order[user_id]['latitude'],
                                            longitude=finally_order[user_id]["longitude"])
    except:
        pass

    data_for_option1 = {"action": "Reject", "user_id": user_id}
    data_for_option2 = {"action": "Accept", "user_id": user_id}
    del_cart = await delete_user_cart(user_id)
    finally_order.pop(user_id)
    user_location.pop(user_id)
    await state.clear()
    await message.bot.send_message(ADMIN_ID, cart_text,
                                   reply_markup=builder_inline_mk(text=['Подтвердить', 'Отклонить'],
                                                                  call_data=[data_for_option2,
                                                                             data_for_option1]))


@main_router.callback_query(OrderCallback.filter())
async def root(query: CallbackQuery, callback_data: OrderCallback):
    lang = await get_lang(callback_data.user_id)
    if callback_data.action == "Accept":
        if lang == "ru":
            await query.message.bot.send_message(callback_data.user_id,
                                                 "Заказ принят. Вам позвонят для уточнения заказа",
                                                 reply_markup=menu_kb(lang))
        else:
            await query.message.bot.send_message(callback_data.user_id,
                                                 "Buyurtma qabul qilindi. Buyurtmani aniqlashtirish uchun sizga qo'ng'iroq qilishadi",
                                                 reply_markup=menu_kb(lang))
    elif callback_data.action == "Reject":
        if lang == "ru":
            await query.message.bot.send_message(callback_data.user_id,
                                                 "Заказ отклонен. Вам позвонят для уточнения заказа",
                                                 reply_markup=menu_kb(lang))
        else:
            await query.message.bot.send_message(callback_data.user_id,
                                                 "Buyurtma qabul qilinmadi. Buyurtmani aniqlashtirish uchun sizga qo'ng'iroq qilishadi",
                                                 reply_markup=menu_kb(lang))


# @main_router.message(ContentType.SUCCESSFUL_PAYMENT)
# async def process_successful_payment(message: Message):
#     print('successful_payment:')
#     pmnt = message.successful_payment.to_python()
#     for key, val in pmnt.items():
#         print(f'{key} = {val}')
#
#     await message.bot.send_message(
#         message.chat.id,
#         ru['successful_payment'].format(
#             total_amount=message.successful_payment.total_amount // 100,
#             currency=message.successful_payment.currency
#         )
#     )

@main_router.message(Command("terms"))
async def terms(message: Message):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    await message.reply(ru['terms_text'] if lang == "ru" else uz['terms_text'], parse_mode="HTML")


# print(product_service.get_all_product())

async def menu(lang, message=None, query=None):
    try:
        user_location.pop(message.from_user.id if message else query.from_user.id)
    except:
        pass
    if lang == 'ru':
        try:
            if message:
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
def get_user_info(user_id):
    user = UserTG.objects.get(user_tg_id=user_id)
    if user:
        return user
    return False


@sync_to_async
def get_lang(user_id):
    return UserTG.objects.get(user_tg_id=user_id).lang


@sync_to_async
def update_lang(user_id, lang):
    try:
        UserTG.objects.filter(user_tg_id=user_id).update(lang=lang)
        return True
    except Exception as e:
        raise e


@sync_to_async
def update_phone(user_id, phone_number):
    try:
        UserTG.objects.filter(user_tg_id=user_id).update(phone_number=phone_number)
        return True
    except Exception as e:
        raise e


@sync_to_async
def update_birthday(user_id, birthday):
    try:
        UserTG.objects.filter(user_tg_id=user_id).update(birthday=birthday)
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
        result = await update_lang(user_id, 'ru')
        if result:
            lang = await get_lang(user_id)
            await menu(message=message, lang=lang)
    elif message.text == "🇺🇿uz":
        result = await update_lang(user_id, 'uz')
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
    try:
        if not user_cart_items.first().promocode:
            return 0

        user_promocode = Promocode.objects.filter(promocode_code=user_cart_items.first().promocode).first().discount
        return user_promocode if user_promocode else 0
    except Exception as e:
        print(e)
        return 0


async def user_cart_menu(lang: str, message=None, query=None):
    print(user_location)
    if message:
        user_cart = await get_user_cart(message.from_user.id)
        if user_cart:
            discount = await get_user_promocode_cart(message.from_user.id)
            print(discount)
            total_price_all = 0
            cart_text = "<b>Корзина:\n\n</b>" if lang == 'ru' else "<b>Savatdagi mahsulotlaringiz:</b>\n\n"
            for item in user_cart:
                cart_text += f"<b>{item['product_name']} </b>- {item['quantity']} шт. - {item['total_price']} сум\n"
                total_price_all += item['total_price']

            if discount > 0:
                total_price_all -= total_price_all * (discount / 100)
                await message.answer(
                    cart_text + f"\n\n<b>Итого: </b> {total_price_all:,} сум c учетом скидки {discount}%" if lang == 'ru' else f"\n\n<b>Jami: </b> {total_price_all:,} so'm {discount}% skidka bilan",
                    reply_markup=user_cart_edit(lang, True if discount > 0 else False, user_cart), parse_mode="HTML")
            else:
                await message.answer(
                    cart_text + f"\n\n<b>Итого:</b> {total_price_all:,} сум" if lang == 'ru' else f"\n\n<b>Jami:</b> {total_price_all:,} so'm",
                    reply_markup=user_cart_edit(lang, True if discount > 0 else False, user_cart), parse_mode="HTML")

        else:
            cart_text = "Ваша корзина пуста" if lang == 'ru' else "Sizning savatingiz bo'sh"

            await message.answer(cart_text,
                                 reply_markup=user_cart_edit(lang, False, user_cart))
    elif query:
        user_cart = await get_user_cart(query.from_user.id)

        if user_cart:
            discount = await get_user_promocode_cart(query.from_user.id)
            total_price_all = 0
            cart_text = "<b>Корзина:\n\n</b>" if lang == 'ru' else "<b>Savatdagi mahsulotlaringiz:</b>\n\n"
            for item in user_cart:
                cart_text += f"- {item['quantity']} шт. - {item['total_price']} сум\n"
                total_price_all += item['total_price']
            if discount > 0:
                total_price_all -= total_price_all * (discount / 100)
                await query.message.edit_text(
                    cart_text + f"\n\n{total_price_all:,} сум c учетом скидки {discount}%" if lang == 'ru' else f"\n\n{total_price_all:,} so'm {discount}% skidka bilan",
                    reply_markup=user_cart_edit(lang, True if discount > 0 else False, user_cart), parse_mode="HTML")
            else:
                await query.message.edit_text(
                    cart_text + f"\n\n {total_price_all:,} сум" if lang == 'ru' else f"\n\n {total_price_all:,} so'm",
                    reply_markup=user_cart_edit(lang, True if discount > 0 else False, user_cart), parse_mode="HTML")
        else:
            cart_text = "Ваша корзина пуста" if lang == 'ru' else "Sizning savatingiz bo'sh"

            await query.message.edit_text(cart_text,
                                          reply_markup=user_cart_edit(lang, False, user_cart))


@main_router.message(F.text.in_([ru['inline_keyboard_button']['cart'], uz['inline_keyboard_button']['cart']]))
async def cart(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    try:
        if user_location[message.from_user.id]:
            await state.set_state(StageOfOrderState.choose_product)
            await message.answer("Ваша корзина" if lang == 'ru' else "Sizning savatingiz",
                                 reply_markup=product_back_to_category(lang))
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


@main_router.message(Command("order"))
@main_router.message(
    F.text.in_([ru['inline_keyboard_button']['choose_product'], uz['inline_keyboard_button']['choose_product']]))
async def choose_product(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    all_pr = await get_all_product()
    print(lang)
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
        user_location[user_id] = ["biotact"]
        # await message.answer("""Закажите через новое удобное меню 👇😉""", reply_markup=wb_button())
        await message.answer(ru['choose_product_menu_1'] if lang == 'ru' else uz['choose_product_menu_1'],
                             parse_mode="HTML",
                             reply_markup=category_product_menu(lang))
        await state.set_state(StageOfOrderState.start_order)
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
        finally_order[user_id] = {"longitude": longitude, "latitude": latitude}
        location = geolocators(latitude, longitude)
        await message.answer(f"Ваш адрес: {location}", reply_markup=confirm_location_kb(lang))
        user_location[user_id] = [location]
    if message.text == 'Подтвердить' or message.text == 'Tasdiqlash':
        all_pr = await get_all_product()

        await message.answer(
            "Укажите удобное для вас время 🕒" if lang == "ru" else "Buyurtmani qabul qilish uchun qulay vaqtni tanlang 🕒",
            reply_markup=choose_time_kb(lang))
        await state.set_state(StageOfOrderState.get_time)
    if message.text == uz['inline_keyboard_button']['back'] or message.text == ru['inline_keyboard_button']['back']:
        await state.clear()
        await menu(lang=lang, message=message)


@main_router.message(StageOfOrderState.get_time)
async def get_time(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    if message.text == uz['inline_keyboard_button']['back'] or message.text == ru['inline_keyboard_button']['back']:
        await message.answer("Пожалуйста, скиньте свой адрес" if lang == 'ru' else "Iltimos, manzilni yuboring",
                             reply_markup=send_location_kb(lang))
        await state.set_state(StageOfOrderState.get_location)
    elif message.text in ["Ближайшее время", "Tez orada"]:
        await message.answer(ru['choose_product_menu_1'] if lang == 'ru' else uz['choose_product_menu_1'],
                             parse_mode="HTML",
                             reply_markup=category_product_menu(lang))
        await state.set_state(StageOfOrderState.start_order)
    elif message.text in ["На время", "Bir muddat"]:
        await message.answer("Выберите время" if lang == "ru" else "Vaqtni tanlang",
                             reply_markup=generate_time_buttons(lang))
        await state.set_state(TimeState.choose_time)


@main_router.message(TimeState.choose_time)
async def choose_time_func(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    selected_time = message.text
    if message.text == uz['inline_keyboard_button']['back'] or message.text == ru['inline_keyboard_button']['back']:
        await message.answer(
            "Укажите удобное для вас время 🕒" if lang == "ru" else "Buyurtmani qabul qilish uchun qulay vaqtni tanlang 🕒",
            reply_markup=choose_time_kb(lang))
        await state.set_state(StageOfOrderState.get_time)
        return
    try:
        datetime.strptime(selected_time, '%H:%M')
        await message.answer(ru['choose_product_menu_1'] if lang == 'ru' else uz['choose_product_menu_1'],
                             parse_mode="HTML",
                             reply_markup=category_product_menu(lang))
        await state.set_state(StageOfOrderState.start_order)
    except ValueError:
        await message.answer("Неправильный формат времени" if lang == 'ru' else "Noto'g'ri vaqtni kiritdingiz",
                             reply_markup=choose_time_kb(lang))


# @main_router.message(F.text == ru['inline_keyboard_button']['back'] or F.text == uz['inline_keyboard_button']['back'])
# async def back_to_menu(message: Message, state: FSMContext):
#     user_id = message.from_user.id
#     lang = await get_lang(user_id)
#     await state.clear()
#     await menu(lang=lang, message=message)


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
    await message.answer(result)
    await user_cart_menu(lang=lang, message=message)


@sync_to_async
def get_all_info(user_id):
    user = UserTG.objects.get(user_tg_id=user_id)
    return [user.phone_number, user.user_name]


@sync_to_async
def delete_user_cart(user_id):
    UserCart.objects.filter(user_id=user_id).delete()
    return True


@main_router.message(StageOfOrderState.user_cart)
async def root(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    if message.text in [ru['inline_keyboard_button']['back'], uz['inline_keyboard_button']['back']]:
        await state.clear()
        await message.delete()
        await user_cart_menu(lang=lang, message=message)
        return
    if message.text in [ru['inline_keyboard_button']['supp_phone_num'], uz['inline_keyboard_button']['supp_phone_num']]:
        await state.set_state(StageOfOrderState.user_payment)
        await user_order_conf_menu(user_id, message=message)
        user_location[user_id].append(None)
        return
    comment = message.text
    user_location[user_id].append(comment)
    await state.set_state(StageOfOrderState.user_payment)
    await user_order_conf_menu(user_id, message=message)


async def user_order_conf_menu(user_id, query=None, message=None, kb=choose_payment_kb, payment_method=""):
    lang = await get_lang(user_id)
    info = await get_all_info(user_id)
    print(user_location)
    delivery_or = "📦 Самовывоз" if user_location[user_id][
                                       0] == "biotact" else f"🚙 Доставка \n📍 {user_location[user_id][0]}"
    delivery_or_uz = "📦 Olib ketish" if user_location[user_id][
                                            0] == "biotact" else f"🚙 Yetkazib berish \n📍 {user_location[user_id][0]}"
    cart_text = ""
    user_cart = await get_user_cart(user_id)
    discount = await get_user_promocode_cart(user_id)
    total_price_all = 0
    for item in user_cart:
        cart_text += f"{item['product_name']} x {item['quantity']} = {item['total_price']} \n"
        total_price_all += item['total_price']
    if discount > 0:
        total_price_all -= total_price_all * (discount / 100)
        cart_text += f"\n\nИтого: {total_price_all:,} сум c учетом скидки {discount}%" if lang == 'ru' else f"\n\nJami: {total_price_all:,} so'm {discount}% skidka bilan"
        cart_text += f"""\n\n{"Имя" if lang == 'ru' else "Ismi"}: {info[1]}
{"Телефон" if lang == "ru" else "Telefon"}: {info[0]}
{"Тип заказа" if lang == "ru" else "Turi"}: {delivery_or if lang == 'ru' else delivery_or_uz}
{"Тип оплаты" if lang == "ru" else "To'lov turi"}: 
{payment_method}:{total_price_all}
"""
        if message:
            await message.answer(cart_text, reply_markup=kb(lang) if kb else None)
        elif query:
            await query.message.edit_text(cart_text, reply_markup=kb(lang) if kb else None)
    else:
        cart_text += f"\n\nИтого: {total_price_all:,} сум" if lang == 'ru' else f"\n\nJami: {total_price_all:,} so'm"
        cart_text += f"""\n\n{"Имя" if lang == 'ru' else "Ismi"}: {info[1]}
{"Телефон" if lang == "ru" else "Telefon"}: {info[0]}
{"Тип заказа" if lang == "ru" else "Turi"}: {delivery_or if lang == 'ru' else delivery_or_uz}
{"Тип оплаты" if lang == "ru" else "To'lov turi"}:
{payment_method}:{total_price_all:,}
            """
        if message:
            await message.answer(cart_text, reply_markup=kb(lang) if kb else None)
        elif query:
            await query.message.edit_text(cart_text, reply_markup=kb(lang) if kb else None)


@main_router.message(StageOfOrderState.user_payment)
async def payment(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    data = await state.get_data()
    print(data)
    payment_data = f"{"💴 Наличные" if lang == "ru" else "💴 Naqd"}" if data["payment"][user_id] == "cash" else "💳" + \
                                                                                                              data[
                                                                                                                  "payment"][
                                                                                                                  user_id]

    if message.text == ru['inline_keyboard_button']['supp_phone_num'] or message.text == uz['inline_keyboard_button'][
        'supp_phone_num']:
        await user_order_conf_menu(message=message, user_id=user_id, kb=confirm_order_kb, payment_method=payment_data)
        user_location[user_id].append(None)
        return
    phone_num = message.text

    user_location[user_id].append(phone_num)
    await user_order_conf_menu(message=message, user_id=user_id, kb=confirm_order_kb, payment_method=payment_data)


@sync_to_async
def get_all_product_by(category):
    if category == "Мерч" or category == "Merch":
        product = list(Product.objects.filter(is_merch=True).all())
        return product
    elif category == "Эксклюзивные сеты" or category == "Ekskluziv Setlar":
        product = list(Product.objects.filter(is_set=True).all())
        return product
    elif category == "Продукция" or category == "Mahsulotlar":
        product = list(Product.objects.filter(is_product=True).all())
        return product
    return False


all_product_dict = {}


@main_router.message(StageOfOrderState.start_order)
# @main_router.message(F.text.in_(["Продукты", "Mahsulotlar", "Сеты", "Setlar", "Мерч", "Merch"]))
async def gain(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    all_product = await get_all_product_by(message.text)
    all_product_dict[user_id] = all_product
    if message.text in ["Продукция", "Mahsulotlar", "Эксклюзивные сеты", "Ekskluziv Setlar", "Мерч", "Merch"]:
        await state.set_state(StageOfOrderState.choose_product)
        await message.answer("Выберите продукт" if lang == "ru" else "Productni tanlang",
                             reply_markup=product_kb(lang, all_product))
    elif message.text in [ru['inline_keyboard_button']['back'], uz['inline_keyboard_button']['back']]:
        await state.set_state(StageOfOrderState.get_delivery)
        if lang == 'ru':
            await message.answer("Заберите свой заказ самостоятельно 🙋 или выберите доставку 🚙",
                                 reply_markup=stage_order_delivery_kb(lang))
            await state.set_state(StageOfOrderState.get_delivery)
        else:
            await message.answer("Buyurtmangizni mustaqil olib keting 🙋‍ yoki yetkazish xizmatini tanlang 🚙",
                                 reply_markup=stage_order_delivery_kb(lang))


@sync_to_async
def get_product(product_id):
    return Product.objects.get(id=product_id)


def get_image(filename):
    try:
        current_path = os.path.abspath(os.getcwd())
        image_path = os.path.join(current_path, 'media', filename)

        with open(image_path, 'rb') as photo:
            return photo.read()

    except Exception as e:
        print(Exception, e)


async def product_menu(message, product_id):
    user_id = message.from_user.id
    product = await get_product(product_id)
    lang = await get_lang(user_id)
    if lang == "ru":
        image = get_image("/Users/ibragimkadamzanov/PycharmProjects/pythonProject19/" + product.product_image.url)
        await message.answer_photo(
            photo=FSInputFile("/Users/ibragimkadamzanov/PycharmProjects/pythonProject19/" + product.product_image.url),
            caption=f"<b>{product.product_name}</b>\n\n"
                    f"{product.price:,} сум\n\n{product.description_ru}",
            parse_mode="HTML", reply_markup=product_menu_kb(lang=lang))
    else:
        await message.answer_photo(
            photo=FSInputFile("/Users/ibragimkadamzanov/PycharmProjects/pythonProject19/" + product.product_image.url),
            caption=f"<b>{product.product_name}</b>\n\n"
                    f"{product.price:,} so'm\n\n{product.description_uz}",
            parse_mode="HTML", reply_markup=product_menu_kb(lang=lang))


@main_router.message(StageOfOrderState.choose_product)
async def product_dec_menu(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    if message.text in [ru['inline_keyboard_button']['back'], uz['inline_keyboard_button']['back']]:
        await state.set_state(StageOfOrderState.start_order)
        await message.answer("Выберите продукт" if lang == "ru" else "Productni tanlang")
        await message.answer(ru['choose_product_menu'] if lang == 'ru' else uz['choose_product_menu'],
                             parse_mode="HTML",
                             reply_markup=category_product_menu(lang))

    all_product = all_product_dict[user_id]
    product_list = [product.product_name for product in all_product]
    if message.text in product_list:
        product_id = all_product[product_list.index(message.text)].id
        await state.set_data({"user": {user_id: {'product_id': product_id, 'pr_count': 1}}})
        await state.set_state(StageOfOrderState.get_product)
        print(all_product[product_list.index(message.text)].id)
        print(message.text)
        await message.answer("Выберите действие", reply_markup=product_edit_menu(lang))
        await product_menu(message, product_id)


@main_router.message(StageOfOrderState.get_product)
async def gain(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    all_product = all_product_dict[user_id]
    product_list = [product.product_name for product in all_product]
    if message.text in [ru['inline_keyboard_button']['back'], uz['inline_keyboard_button']['back']]:
        await state.set_state(StageOfOrderState.choose_product)
        await message.answer("Выберите продукт" if lang == "ru" else "Productni tanlang")
        await message.answer(ru['choose_product_menu'] if lang == 'ru' else uz['choose_product_menu'],
                             parse_mode="HTML",
                             reply_markup=product_kb(lang, all_product))
    elif message.text in ["\uD83D\uDCB3 Корзина", "\uD83D\uDCB3 Savatim"]:
        pass


@main_router.message(Command("feedback"))
@main_router.message(
    F.text.in_([ru['inline_keyboard_button']['leave_feedback'], uz['inline_keyboard_button']['leave_feedback']]))
async def about_us(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    await state.set_state(LeaveFeedback.get_feedback)
    await message.answer(
        "Оставьте свой отзыв. Нам важно ваше мнение." if lang == 'ru' else "Sharhingizni qoldiring. Sizning fikringiz biz uchun muhim.",
        reply_markup=leave_feedback_kb(lang))


@main_router.message(LeaveFeedback.get_feedback)
async def about_us(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    user_info = await get_user_info(user_id)
    if message.text in [ru['inline_keyboard_button']['back'], uz['inline_keyboard_button']['back']]:
        await menu(lang=lang, message=message)
    else:
        await message.bot.send_message(ADMIN_ID, user_info.phone_number + "\n" + message.text)
        await message.answer("Спасибо за ваш отзыв", reply_markup=menu_kb(lang))
        await state.clear()
        await menu(lang=lang, message=message)


@main_router.message(F.text.in_([ru['inline_keyboard_button']['promotion'], uz['inline_keyboard_button']['promotion']]))
async def about_us(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    await message.answer(ru['promotions'] if lang == "ru" else uz['promotion'],
                         reply_markup=menu_kb(lang))
    await state.set_state(PromotionState.get_promotion)


@sync_to_async
def get_user_orders(user_id):
    user_orders = MyOrders.objects.filter(user_id=user_id).all()
    return list(user_orders) if user_orders else None


@main_router.message(F.text.in_([ru['inline_keyboard_button']['my_orders'], uz['inline_keyboard_button']['my_orders']]))
async def about_us(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    user_orders = await get_user_orders(user_id)
    if user_orders:
        await message.answer("Ваши заказы", reply_markup=menu_kb(lang))
        for i in user_orders:
            await message.answer(i.order_text, reply_markup=menu_kb(lang))
    else:
        await message.answer("У вас нет заказов" if lang == "ru" else "Sizda buyurtmalar yo'q",
                             reply_markup=menu_kb(lang))


@main_router.message(PromotionState.get_promotion)
async def about_us(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    if message.text in [ru['inline_keyboard_button']['back'], uz['inline_keyboard_button']['back']]:
        await state.clear()
        await message.delete()
        await menu(lang=lang, message=message)


@sync_to_async
def get_birthday(user_id):
    user = UserTG.objects.get(user_tg_id=user_id)
    if user.birthday:
        return [user.birthday, user.phone_number]
    elif user.phone_number:
        return [None, user.phone_number]
    else:
        return None


async def settings_menu(message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    user_info = await get_birthday(user_id)
    birthday = user_info[0] if user_info else None
    await message.answer("Выберите настройку" if lang == "ru" else "Sozlamani tanlang",
                         reply_markup=settings_kb(lang, birthday))
    await state.set_state(SettingsState.get_settings)


@main_router.message(F.text.in_([ru['inline_keyboard_button']['settings'], uz['inline_keyboard_button']['settings']]))
async def root(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    await settings_menu(message, state)


@main_router.message(SettingsState.get_settings)
async def root(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    user_info = await get_birthday(user_id)
    print(user_info)
    birthday = user_info[0] if user_info else None
    phone_number = user_info[1] if user_info else None
    if message.text in [ru['inline_keyboard_button']['back'], uz['inline_keyboard_button']['back']]:
        await state.clear()
        await message.delete()
        await menu(lang=lang, message=message)
    elif message.text in ["Добавить день рождение", "Tug'ilgan kunini qo'shish"]:
        await message.answer(
            "Введите свой день рождения в формате, похожем на «01-12-2000»" if lang == 'ru' else "Tug'ilgan kunni «01-12-2000» shu formatda kiriting",
            reply_markup=birthday_kb(lang))
        await state.set_state(SettingsState.get_birthday)
    elif message.text in ["Изменить день рождения", "Tug'ilgan kunini o'zgartirish"]:
        await message.answer(
            "Ваша дата рождения:" + birthday + "\n\nНапишите новую дату рождения в формате, похожем на «01-12-2000»" if lang == 'ru' else
            "Sizning tug'ilgan kuni: " + birthday + "\n\nYangi tug'ilgan kunni «01-12-2000» shu formatda kiriting",
            reply_markup=birthday_kb(lang))
        await state.set_state(SettingsState.get_birthday)
    elif message.text in ["Изменить номер телефона", "Telefon raqamini o'zgartirish"]:
        await message.answer("Ваш номер телефона: " + str(
            phone_number) + "\n\nНапишите свой новый номер" if lang == 'ru' else "Sizning telefon raqamingiz: " + str(
            phone_number) + "\n\nTelefon raqamini yozing", reply_markup=phone_number_kb(lang))
        await state.set_state(SettingsState.get_phone)
    elif message.text in ["🇷🇺Поменять на русский", "🇺🇿Ozbekchaga o'zgartirish"]:
        await message.delete()
        if message.text == "🇷🇺Поменять на русский":
            result = await update_lang(user_id, 'ru')
        elif message.text == "🇺🇿Ozbekchaga o'zgartirish":
            result = await update_lang(user_id, 'uz')
        await settings_menu(message, state)


class UserAdress:
    pass


@main_router.message(SettingsState.get_birthday)
async def root(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    if message.text in [ru['inline_keyboard_button']['back'], uz['inline_keyboard_button']['back']]:
        await state.clear()
        await message.delete()
        await settings_menu(message, state)
        return
    birthday = message.text
    try:
        # Проверка формата даты
        datetime.strptime(birthday, '%d-%m-%Y')

        # Сохраните день рождения в базу данных
        result = await update_birthday(user_id, birthday)
        response = "Ваш день рождения успешно сохранен!" if lang == 'ru' else "Tug'ilgan kuningiz muvaffaqiyatli saqlandi!"
        await message.answer(response)
        await state.clear()
        await settings_menu(message, state)
    except ValueError:
        response = "Неверный формат даты. Попробуйте еще раз." if lang == 'ru' else "Noto'g'ri sana formati. Iltimos, qayta urinib ko'ring."
        await message.answer(response, reply_markup=birthday_kb(lang))


@main_router.message(SettingsState.get_phone)
async def root(message: Message, state: FSMContext):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    if message.text in [ru['inline_keyboard_button']['back'], uz['inline_keyboard_button']['back']]:
        await state.clear()
        await message.delete()
        await settings_menu(message, state)
    if message.contact:
        phone = message.contact.phone_number
        result = await update_phone(user_id, phone)
        await message.answer("Ваш номер телефона: " + phone if lang == 'ru' else "Sizning telefon raqamingiz: " + phone)
        await settings_menu(message, state)
