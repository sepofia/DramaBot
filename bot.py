"""
- send actual K-drams by default query
- ask on the query with user's parameters: genre, year or rate
"""


import logging

import pandas as pd
import yaml
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder
    , ContextTypes
    , CommandHandler
    , CallbackContext
    , CallbackQueryHandler
    , ConversationHandler
    , MessageHandler
    , filters
)
from server import find_serials

from utils import messages, database


# logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# parsing config-file
with open('configuration/config_bot.yaml', 'r') as handle:
    configs = yaml.full_load(handle)

# bot unique token from config-file
TOKEN = configs['token']


# bot actions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = {'id': update.message.chat.id
            , 'name': update.message.chat.first_name
            , 'language': update.message.from_user.language_code}
    database.check_user(user)

    text = messages.start(user['name'], user['language'])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def random_drama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    drama = find_serials('random')
    text = messages.random_drama(drama, update.message.from_user.language_code)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='Markdown')


async def last_dramas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dramas_df = find_serials('last')
    text = messages.last_dramas(dramas_df, update.message.from_user.language_code)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='Markdown')


async def user_dramas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_message = user_message.replace('/user_dramas', '')
    user_message = user_message.split()
    user_params = {}
    for i in range(0, len(user_message) - 1, 2):
        user_params[user_message[i].replace(' ', '')] = user_message[i + 1].replace(' ', '')

    try:
        dramas_df = find_serials('user choose', user_params)
        text = messages.user_dramas(dramas_df, update.message.from_user.language_code)
    except Exception as _:
        text = messages.user_dramas(None, update.message.from_user.language_code)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='Markdown')


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    last_dramas_handler = CommandHandler('last_dramas', last_dramas)
    application.add_handler(last_dramas_handler)

    random_drama_handler = CommandHandler('random_drama', random_drama)
    application.add_handler(random_drama_handler)

    user_dramas_handler = CommandHandler('user_dramas', user_dramas)
    application.add_handler(user_dramas_handler)

    application.run_polling()
