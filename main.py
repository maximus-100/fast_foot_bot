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
CLICK_TOKEN = os.getenv('CLICK_TOKEN')
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)


class GetSettingsName(StatesGroup):
    name = State()


@dp.message_handler(commands=['start'])
async def command_start(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, f'Здраствуйте!{message.from_user.full_name} Вас приветствуйт Бот "🍔Fast food🍔" '
                                    f'\nМы достовляем еду по заказу.🚗😁')
    await register_user(message)


async def register_user(message: Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    user = FastFoodDB.first_select_user(chat_id)
    if user:
        await message.answer('Автаризация прошла успешна')
        await show_main_menu(message)
    else:
        FastFoodDB.first_register_user(chat_id, full_name)
        await message.answer('Для регистрации нажмите на кнопку.', reply_markup=generate_phone_button())


@dp.message_handler(content_types=['contact'])
async def finish_register(message: Message):
    chat_id = message.chat.id
    phone = message.contact.phone_number
    FastFoodDB.finish_register(chat_id, phone)
    await create_cart_for_users(message)

    await message.answer('Регестрация прошла успешно')
    await show_main_menu(message)


async def create_cart_for_users(message: Message):
    chat_id = message.chat.id
    try:
        FastFoodDB.insert_to_cart(chat_id)
    except:
        pass


async def show_main_menu(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, 'Выберете напровления', reply_markup=generate_main_menu())


@dp.message_handler(regexp=r'⚙ Настройки')
async def settings(message: Message, state=None):
    await GetSettingsName.name.set()
    await message.answer('Для того чтобы сменить имя напиши его: ', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(content_types=['text'], state=GetSettingsName.name)
async def get_user_name(message: Message, state: FSMContext):
    chat_id = message.chat.id
    full_nam = message.text
    FastFoodDB.update_full_name(chat_id, full_nam)
    await state.finish()
    await show_main_menu(message)


@dp.message_handler(lambda message: '✅ Сделать заказ' in message.text)
async def make_order(message: Message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, 'Выберете категорию: ', reply_markup=generate_categories())


@dp.callback_query_handler(lambda call: 'category' in call.data)
async def show_products(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, category_id = call.data.split('_')
    await bot.edit_message_text(text='Выберите продукт', chat_id=chat_id, message_id=message_id,
                                reply_markup=generate_products_menu(category_id))


@dp.callback_query_handler(lambda call: 'product' in call.data)
async def product_details(call: CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    _, product_id = call.data.split('_')
    product = FastFoodDB.get_product_detail(product_id)
    category_id = FastFoodDB.get_category_this_product(product_id)
    print(product)
    with open(product[6], mode='rb') as image:
        text = f'''{product[2]}

Ингридиенты: {product[4]}

Цена: {product[3]}
'''
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
        await bot.send_photo(chat_id=chat_id, photo=image, caption=text,
                             reply_markup=generate_count_products(product_id, category_id))


@dp.callback_query_handler(lambda call: 'main_menu' in call.data)
async def back_to_main_menu(call: CallbackQuery):
    await bot.edit_message_text(text='Выбериде категорию',
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=generate_categories())


@dp.callback_query_handler(lambda call: 'back' in call.data)
async def back_to_category(call: CallbackQuery):
    _, category_id = call.data.split('_')
    await bot.delete_message(chat_id=call.message.chat.id,
                             message_id=call.message.message_id)
    await bot.send_message(chat_id=call.message.chat.id,
                           text='Выберете продукт: ',
                           reply_markup=generate_products_menu(category_id))


@dp.callback_query_handler(lambda call: call.data.startswith('cart'))
async def add_product_to_cart(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, product_id, quantity = call.data.split('_')
    product_id, quantity = int(product_id), int(quantity)
    cart_id = FastFoodDB.get_cart_id_by_chat_id(chat_id)
    product_name, price = FastFoodDB.get_product_name_price(product_id)
    final_price = quantity * price

    if FastFoodDB.insert_or_update_cart_product(cart_id, product_name, quantity, final_price):
        await bot.answer_callback_query(call.id, 'Продукт успешна добавлен')
    else:
        await bot.answer_callback_query(call.id, 'Количество успешно изменено')


@dp.message_handler(lambda message: '🛒 Корзина' in message.text)
async def show_cart(message: Message, edit_message: bool = False):
    chat_id = message.chat.id
    cart_id = FastFoodDB.get_cart_id_by_chat_id(chat_id)
    try:
        FastFoodDB.sum_quantity_price(cart_id)
    except Exception as e:
        print(e)
        await bot.send_message(chat_id, 'Карзина не даступна')
        return

    total_products, total_price = FastFoodDB.get_total_products_price(cart_id)
    cart_products = FastFoodDB.get_cart_products(cart_id)
    text = 'Ваша карзина: \n\n'
    i = 0
    for product_name, quantity, final_price in cart_products:
        i += 1
        text += f'''{i}. {product_name}
Количество: {quantity}
Общая стоимость: {final_price}\n\n'''
    text += f'''Общее количество товаров: {0 if total_products is None else total_products}
Общая стоимость корзины: {0 if total_price is None else total_price}
'''
    if edit_message:
        await bot.edit_message_text(text, chat_id, message.message_id, reply_markup=generate_cart_menu(cart_id))
    else:
        await bot.send_message(chat_id, text, reply_markup=generate_cart_menu(cart_id))


@dp.callback_query_handler(lambda call: 'delete' in call.data)
async def delete_cart_product(call: CallbackQuery):
    message = call.message
    _, cart_product_id = call.data.split('_')
    cart_product_id = int(cart_product_id)

    FastFoodDB.delete_cart_product(cart_product_id)
    await bot.answer_callback_query(call.id, text='Продукт успешно удолен!')
    await show_cart(message, edit_message=True)

@dp.callback_query_handler(lambda call: 'order' in call.data)
async def create_order(call: CallbackQuery):
    chat_id = call.message.chat.id
    _, cart_id = call.data.split('_')

    total_products, total_price = FastFoodDB.get_total_products_price(cart_id)
    cart_products = FastFoodDB.get_cart_products(cart_id)
    text = 'Ваша заказ: \n\n'
    i = 0
    for product_name, quantity, final_price in cart_products:
        i += 1
        text += f'''{i}. {product_name}
    Количество: {quantity}
    Общая стоимость: {final_price}\n\n'''
    text += f'''Общее количество товаров: {0 if total_products is None else total_products}
    Общая стоимость корзины: {0 if total_price is None else total_price}
    '''

    await bot.send_invoice(
        chat_id=chat_id,
        title=f'Заказ №{cart_id}',
        description=text,
        payload='bot_defined invoice payload',
        provider_token=CLICK_TOKEN,
        currency='UZS',
        prices=[
            LabeledPrice(label='Общая стоемость', amount=int(total_price * 100)),
            LabeledPrice(label='ДОставка', amount=1000000)
        ]
    )
    await bot.send_message(chat_id, 'Заказ оплачен')

executor.start_polling(dp)
