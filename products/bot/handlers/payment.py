import types

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove, CallbackQuery, LabeledPrice
from aiogram.filters import CommandStart
from dotenv import dotenv_values

config_token = dotenv_values(".env")
PAYMENT_TOKEN = config_token['CLICK_TOKEN']

payment_router = Router()
PRICE = LabeledPrice(label='Настоящая Машина Времени', amount=4200000)


@payment_router.callback_query(F.data == 'confirm')
async def payment(query: CallbackQuery):
    if PAYMENT_TOKEN.split(':')[1] == "TEST":
        await query.message.answer("Тестовая оплата")
    await query.message.bot.send_invoice(query.from_user.id,
                                         title="qwe",
                                         description="MESSAGES['tm_description']",
                                         provider_token=PAYMENT_TOKEN,
                                         currency='rub',
                                         is_flexible=False,  # True если конечная цена зависит от способа доставки
                                         prices=[PRICE],
                                         start_parameter='time-machine-example',
                                         payload='some-invoice-payload-for-our-internal-use'
                                         )
