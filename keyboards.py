from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from databaes import FastFoodDB


def generate_phone_button():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='Отправить свой контакт', request_contact=True)]
    ])


def generate_main_menu():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='✅ Сделать заказ')],
        [KeyboardButton(text='🗒 История'), KeyboardButton(text='🛒 Корзина'), KeyboardButton(text='⚙ Настройки')]
    ])


def generate_categories():
    categories = FastFoodDB.get_categories()
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for category in categories:
        btn = InlineKeyboardButton(text=category[1], callback_data=f'category_{category[0]}')
        buttons.append(btn)
    markup.add(*buttons)
    return markup


def generate_products_menu(category_id):
    products = FastFoodDB.get_products(category_id)
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for product in products:
        btn = InlineKeyboardButton(text=product[1], callback_data=f'product_{product[0]}')
        buttons.append(btn)
    markup.add(*buttons)
    back_button = InlineKeyboardButton(text='Назад', callback_data='main_menu')
    markup.row(back_button)
    return markup


def generate_count_products(product_id, category_id):
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []
    for num in range(1, 10):
        btn = InlineKeyboardButton(text=str(num), callback_data=f'cart_{product_id}_{num}')
        buttons.append(btn)
    markup.add(*buttons)
    back_button = InlineKeyboardButton(text='Назад', callback_data=f'back_{category_id}')
    markup.row(back_button)
    return markup


def generate_cart_menu(cart_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(text=f'🚀 Оформить заказ', callback_data=f'order_{cart_id}')
    )
    cart_products = FastFoodDB.get_cart_products_for_keyboard(cart_id)
    for cart_product_id, product_name in cart_products:
        markup.row(
            InlineKeyboardButton(text=f'❌ {product_name}', callback_data=f'delete_{cart_product_id}')
        )
    return markup
