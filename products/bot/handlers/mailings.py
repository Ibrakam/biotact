from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async

from products.models import UserTG

