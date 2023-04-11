import logging
import os

import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from moltin_api import get_access_token, get_all_products, get_product_by_id, get_img_url


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

_database = None


def get_products_keyboard(update, congext):
    products_descriptions = get_all_products(congext.bot_data['moltin_token'])
    congext.bot_data['products_descriptions'] = products_descriptions
    keyboard = []
    for product in products_descriptions['data']:
        keyboard.append([InlineKeyboardButton(
            product['attributes']['name'],
            callback_data=product['id'])])
    return InlineKeyboardMarkup(keyboard)


def start(update, context):
    reply_markup = get_products_keyboard(update, context)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)
    return 'HANDLE_MENU'


def handle_menu(update, context):
    query = update.callback_query
    product_id = query['data']
    moltin_token = context.bot_data.get('moltin_token')
    selected_product = get_product_by_id(moltin_token, product_id)['data']

    product_price = \
        selected_product['meta']['display_price']['without_tax']['formatted']
    product_amount = selected_product['meta']['display_price']['without_tax']['amount']
    product_image_url = get_img_url(moltin_token, product_id)
    chat_id = update.effective_chat.id

    text = f'''
{selected_product['attributes']['name']}

Цена: {product_price} за кг.
Остаток: {product_amount} кг.

{selected_product['attributes']['description']}
        '''

    if product_image_url:
        context.bot.send_photo(
            photo=product_image_url,
            chat_id=chat_id,
            caption=text,
        )
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
        )

    return 'START'


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
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'
    else:
        user_state = db_connection.get(chat_id)

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
    }

    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    db_connection[chat_id] = next_state


def main():
    load_dotenv()
    updater = Updater(os.getenv('TG_TOKEN'))
    dispatcher = updater.dispatcher
    moltin_token = get_access_token(os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET'))

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
    dispatcher.bot_data['moltin_token'] = moltin_token

    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
