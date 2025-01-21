"""
- send actual K-drams by default query
- ask on the query with user's parameters: genre, year or rate
"""


import logging

import yaml
import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder
    , ContextTypes
    , CommandHandler
    , CallbackContext
    , ConversationHandler
    , MessageHandler
    , filters
)

from datetime import datetime as dt
from server_sql import find_serials
from utils import messages
from database import update_users


# logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# parsing config-file
with open('configuration/config_bot.yaml', 'r') as handle:
    configs = yaml.full_load(handle)
# parsing file with buttons names
with open('utils/buttons.json', encoding='utf-8') as handle:
    BUTTONS = json.load(handle)

# bot unique token from config-file
TOKEN = configs['token']
GENRE, YEAR, COUNTRY, COUNT, MODE = range(5)

# load already existed users
all_users = update_users.load_user_id()
commands = {}


# bot actions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = (
        update.message.from_user.id
        , update.message.from_user.username
        , update.message.from_user.first_name
        , update.message.from_user.language_code
        , update.message.from_user.is_premium
        , update.message.from_user.is_bot
    )

    if user[0] not in all_users:  # add user in local database
        all_users.add(user[0])
        update_users.update_users_database(user)

    new_command = (
        update.message.from_user.id
        , 'start'
        , dt.now()
        , None
    )
    update_users.update_command_database(new_command)

    text = messages.start(user[2], user[3])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    drama = find_serials('random')
    text = messages.random_drama(drama, update.message.from_user.language_code)

    new_command = (
        update.message.from_user.id
        , 'random'
        , dt.now()
        , None
    )
    update_users.update_command_database(new_command)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='Markdown')


async def last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dramas_df = find_serials('last')
    text = messages.last_dramas(dramas_df, update.message.from_user.language_code)

    new_command = (
        update.message.from_user.id
        , 'last'
        , dt.now()
        , None
    )
    update_users.update_command_database(new_command)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='Markdown')


# USER'S K-DRAMAS -----------------------------------------------------------------------------------------------------
async def select(update: Update, context: CallbackContext) -> int:
    reply_keyboard = BUTTONS['genres']
    text = messages.select(update.message.from_user.language_code)
    commands[update.message.chat.id] = {}

    await update.message.reply_text(
        text=text,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Genre',
            resize_keyboard=True
        ),
        parse_mode='Markdown'
    )

    return GENRE


async def genre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Genre of %s: %s", user.first_name, update.message.text)

    reply_keyboard = BUTTONS['years']
    text = messages.genre(update.message.from_user.language_code)
    commands[update.message.chat.id]['genres.name'] = update.message.text

    await update.message.reply_text(
        text=text,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Year',
            resize_keyboard=True
        ),
        parse_mode='Markdown'
    )

    return YEAR


async def year(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Year of %s: %s", user.first_name, update.message.text)

    reply_keyboard = BUTTONS['countries']
    text = messages.year(update.message.from_user.language_code)
    commands[update.message.chat.id]['year'] = update.message.text

    await update.message.reply_text(
        text=text,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Country',
            resize_keyboard=True
        ),
        parse_mode='Markdown'
    )

    return COUNTRY


async def country(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Country of %s: %s", user.first_name, update.message.text)

    reply_keyboard = BUTTONS['counts']
    text = messages.country(update.message.from_user.language_code)
    commands[update.message.chat.id]['countries.name'] = update.message.text

    await update.message.reply_text(
        text=text,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Count',
            resize_keyboard=True
        ),
        parse_mode='Markdown'
    )

    return COUNT


async def count(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Count of %s: %s", user.first_name, update.message.text)

    reply_keyboard = BUTTONS['modes']
    text = messages.count(update.message.from_user.language_code)
    commands[update.message.chat.id]['count'] = int(update.message.text)

    await update.message.reply_text(
        text=text,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Mode',
            resize_keyboard=True
        ),
        parse_mode='Markdown'
    )

    return MODE


async def mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Mode of %s: %s", user.first_name, update.message.text)

    commands[update.message.chat.id]['mode'] = update.message.text

    try:
        dramas_df = find_serials('user choice', commands[update.message.chat.id])
        text = messages.user_dramas(dramas_df, update.message.from_user.language_code)

        new_command = (
            update.message.from_user.id
            , 'select'
            , dt.now()
            , ', '.join(map(str, commands[update.message.chat.id].values()))
        )
        update_users.update_command_database(new_command)
    except Exception as ex:
        text = messages.user_dramas(None, update.message.from_user.language_code)
        logger.warning(ex)

    await update.message.reply_text(text=text, parse_mode='Markdown')

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)

    text = messages.cancel(update.message.from_user.language_code)
    del commands[update.message.chat.id]
    new_command = (
        update.message.from_user.id
        , 'cancel'
        , dt.now()
        , None
    )
    update_users.update_command_database(new_command)

    await update.message.reply_text(text=text, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


if __name__ == '__main__':
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .read_timeout(10)
        .write_timeout(10)
        .concurrent_updates(True)
        .build()
    )

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    last_handler = CommandHandler('last', last)
    application.add_handler(last_handler)

    random_handler = CommandHandler('random', random)
    application.add_handler(random_handler)

    genre_names = "^(мелодрама|драма|комедия|детектив|триллер|история|ужасы|любой)$"
    year_names = "^(2000|2008|2014|2020|любой)$"
    country_names = "^(Корея Южная|Китай|Япония)$"
    count_names = "^(1|3|5|10)$"
    mode_names = "^(лучшие|случайные)$"
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("select", select)],
        states={
            GENRE: [MessageHandler(filters.Regex(genre_names), genre)],
            YEAR: [MessageHandler(filters.Regex(year_names), year)],
            COUNTRY: [MessageHandler(filters.Regex(country_names), country)],
            COUNT: [MessageHandler(filters.Regex(count_names), count)],
            MODE: [MessageHandler(filters.Regex(mode_names), mode)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)

    application.run_polling()
