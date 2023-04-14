import logging
import os
from textwrap import dedent

import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from moltin_api import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def get_products_keyboard(update, congext):
    products_descriptions = get_all_products(congext.bot_data['moltin_token'])
    congext.bot_data['products_descriptions'] = products_descriptions
    keyboard = []
    for product in products_descriptions['data']:
        keyboard.append([InlineKeyboardButton(
            product['attributes']['name'],
            callback_data=product['id'])])
    keyboard.append([InlineKeyboardButton('Корзина', callback_data='cart')])
    return InlineKeyboardMarkup(keyboard)


def start(update, context):
    reply_markup = get_products_keyboard(update, context)
    if update.message:
        update.message.reply_text('Выберите продукт:', reply_markup=reply_markup)
    else:
        query = update.callback_query
        query.message.reply_text(
            'Выберите продукт',
            reply_markup=reply_markup
        )
        chat_id = update.effective_chat.id
        context.bot.delete_message(
            chat_id=chat_id,
            message_id=query.message.message_id
        )
    return 'HANDLE_MENU'


def handle_menu(update, context):
    keyboard = [
        [
            InlineKeyboardButton('1 кг', callback_data='1'),
            InlineKeyboardButton('5 кг', callback_data='5'),
            InlineKeyboardButton('10 кг', callback_data='10')
        ],
        [
            InlineKeyboardButton('Назад', callback_data='back'),
            InlineKeyboardButton('Корзина', callback_data='cart')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query
    product_id = query['data']
    context.bot_data['product_id'] = product_id
    moltin_token = context.bot_data.get('moltin_token')
    selected_product = get_product_by_id(moltin_token, product_id)['data']

    product_price = \
        selected_product['meta']['display_price']['without_tax']['formatted']
    product_amount = selected_product['meta']['display_price']['without_tax']['amount']
    product_image_url = get_img_url(moltin_token, product_id)
    chat_id = update.effective_chat.id

    text = dedent(
        f'''
            {selected_product['attributes']['name']}

            Цена: {product_price} за кг.
            Остаток: {product_amount} кг.

            {selected_product['attributes']['description']}
        '''
    )

    if product_image_url:
        context.bot.send_photo(
            photo=product_image_url,
            chat_id=chat_id,
            caption=text,
            reply_markup=reply_markup
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup
        )

    context.bot.delete_message(
        chat_id=chat_id,
        message_id=query.message.message_id, )

    return 'HANDLE_DESCRIPTION'


def handle_description(update, context):
    query = update.callback_query
    cart_id = update.effective_chat.id
    if query['data'] == 'back':
        start(update, context)
        return 'HANDLE_MENU'
    if query['data'] == 'cart':
        return 'HANDLE_CART'
    add_product_to_cart(
        access_token=context.bot_data['moltin_token'],
        cart_id=cart_id,
        product_id=context.bot_data['product_id'],
        quantity=int(query['data'])
    )
    query.answer()
    return 'HANDLE_DESCRIPTION'


def send_cart_contents(update, context, moltin_token, cart_id):
    cart_products = get_cart_products(moltin_token, cart_id)
    message_text = ''
    keyboard = []
    for product in cart_products['data']:
        product_price = \
            product['meta']['display_price']['with_tax']['unit']['formatted']
        total_price = \
            product['meta']['display_price']['with_tax']['value']['formatted']
        message_text += dedent(
            f'''\
                {product['name']}
                {product['description'].strip()}
                {product_price} за 1 кг
                {total_price} за {product['quantity']} кг\n
            '''
        )
        keyboard.append(
            [InlineKeyboardButton(
                f"Убрать из корзины {product['name']}",
                callback_data=product['id']
            )]
        )
    keyboard.append([InlineKeyboardButton('В меню', callback_data='/start')])
    keyboard.append([InlineKeyboardButton('Оплатить', callback_data='payment')])
    message_text += f'Общая стоимость: {get_cart_total(moltin_token, cart_id)}'
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=cart_id,
        text=message_text,
        reply_markup=reply_markup
    )
    context.bot.delete_message(
        chat_id=cart_id,
        message_id=update.callback_query.message.message_id
    )


def handle_cart(update, context):
    query = update.callback_query
    moltin_token = context.bot_data['moltin_token']
    cart_id = update.effective_chat.id
    if query['data'] == 'cart':
        send_cart_contents(update, context, moltin_token, cart_id)
    elif query['data'] == 'payment':
        waiting_email(update, context)
        return 'WAITING_EMAIL'
    else:
        remove_product_from_cart(moltin_token, cart_id, query['data'])
        send_cart_contents(update, context, moltin_token, cart_id)
    return 'HANDLE_CART'


def waiting_email(update, context):
    query = update.callback_query
    if update.message:
        update.message.reply_text(
            text=f'Вы прислали мне эту почту {update.message.text}'
        )
        chat_id = update.effective_chat.id
        user_name = update.message['chat']['username']
        create_customer(
            access_token=context.bot_data['moltin_token'],
            user_name=f'Никнейм: {user_name}, chat_id: {chat_id}',
            user_email=update.message.text
        )
    else:
        query.message.reply_text(
            text='Для формирования заказа сообщите мне ваш e-mail'
        )
    return 'WAITING_EMAIL'


def handle_users_reply(update, context):
    """
    Функция, которая запускается при любом сообщении от пользователя и решает как его обработать.
    Эта функция запускается в ответ на эти действия пользователя:
        * Нажатие на inline-кнопку в боте
        * Отправка сообщения боту
        * Отправка команды боту
    Она получает стейт пользователя из базы данных и запускает соответствующую функцию-обработчик (хэндлер).
    Функция-обработчик возвращает следующее состояние, которое записывается в базу данных.
    Если пользователь только начал пользоваться ботом, Telegram форсит его написать "/start",
    поэтому по этой фразе выставляется стартовое состояние.
    Если пользователь захочет начать общение с ботом заново, он также может воспользоваться этой командой.
    """
    db_connection = context.bot_data['db_connection']
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.effective_chat.id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    elif user_reply == 'cart':
        user_state = 'HANDLE_CART'
    else:
        user_state = db_connection.get(chat_id)

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': waiting_email
    }

    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    db_connection[chat_id] = next_state


def main():
    load_dotenv()
    updater = Updater(os.getenv('TG_TOKEN'))
    dispatcher = updater.dispatcher
    access_token = get_access_token(os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET'))

    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")
    redis_password = os.getenv("REDIS_PASSWORD")
    redis_connection = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=0,
        password=redis_password,
        decode_responses=True
    )

    dispatcher.bot_data['db_connection'] = redis_connection
    dispatcher.bot_data['moltin_token'] = access_token

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
