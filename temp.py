from aiogram import Dispatcher, executor, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, ReplyKeyboardRemove
from keyboards import *
from dotenv import load_dotenv
import os
from databaes import FastFoodDB
from aiogram.dispatcher import FSMContext

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

load_dotenv()

storage = MemoryStorage()

TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)


class Oprostnic(StatesGroup):
    age = State()
    nationality = State()
    location = State()


@dp.message_handler(commands=['start'], state=None)
async def command_start(message: Message):
    await Oprostnic.age.set()
    await message.answer('Введите свой возрост: ')

@dp.message_handler(content_types=['text'], state=Oprostnic.age)
async def ask_nation(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = message.text
    # await Oprostnic.nationality.set()
    await Oprostnic.next()
    await message.answer('Введите свою национальность: ')

@dp.message_handler(content_types=['text'], state=Oprostnic.nationality)
async def ask_location(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['nationality'] = message.text

    await Oprostnic.next()
    await message.answer('Введите свою локацию: ')

@dp.message_handler(content_types=['text'], state=Oprostnic.location)
async def save_location(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['location'] = message.text

    await message.answer(f'''Ваш возраст: {data["age"]}
Ваша национальносить: {data["nationality"]}
Ваш адрис: {data["location"]}
''')
    await state.finish()

executor.start_polling(dp)
