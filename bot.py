"""
- processing users commands and messages
- receiving datas from the server (API or local database)
- sending answering messages for users (from the `utils.messages.py` file)
"""


import nest_asyncio
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
from server.sql import find_serials
from utils import messages
from database import update_users, update_series


nest_asyncio.apply()

# logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    , level=logging.WARNING
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

# create a dict for saving users parameters (for the /select command)
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
        , True
    )
    update_users.update_command_database(new_command)

    # send a message to the user
    text = messages.start(user[2], user[3])
    await update.message.reply_text(text=text, parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = messages.info(update.message.from_user.language_code)

    new_command = (
        update.message.from_user.id
        , 'info'
        , dt.now()
        , True
    )
    update_users.update_command_database(new_command)

    await update.message.reply_text(text=text, parse_mode='Markdown', reply_markup=ReplyKeyboardRemove())


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    drama = find_serials('random')
    text = messages.random_drama(drama, update.message.from_user.language_code)

    new_command = (
        update.message.from_user.id
        , 'random'
        , dt.now()
        , ord(text[-1]) != 129402
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
        , ord(text[-1]) != 129402
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
    commands[update.message.chat.id]['mode'] = update.message.text
    try:
        dramas_df = find_serials('user choice', commands[update.message.chat.id])
        text = messages.user_dramas(dramas_df, update.message.from_user.language_code)
        # values for the `commands` table
        new_command = (
            update.message.from_user.id
            , 'select'
            , dt.now()
            , ord(text[-1]) != 129402
        )
        # parameters for the `commands_select` table
        parameters = list(commands[update.message.chat.id].values())
        # check the data type of year
        if parameters[1].startswith('люб'):
            parameters[1] = None

        # update tables
        update_users.update_command_database(new_command, tuple(parameters))

    except Exception as ex:
        text = messages.user_dramas(None, update.message.from_user.language_code)
        logger.warning(ex)

    await update.message.reply_text(
        text=text, parse_mode='Markdown', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    text = messages.cancel(update.message.from_user.language_code)
    del commands[update.message.chat.id]
    new_command = (
        update.message.from_user.id
        , 'cancel'
        , dt.now()
        , True
    )
    update_users.update_command_database(new_command)

    await update.message.reply_text(text=text, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# secret bot command
async def update_database(update: Update, context: ContextTypes.DEFAULT_TYPE):

    flag_access = update.message.from_user.id == 7761512780
    if flag_access:
        update_series.launch_creating_datasets()
    text = messages.update_database_message(flag_access)

    new_command = (
        update.message.from_user.id
        , 'update_database'
        , dt.now()
        , flag_access
    )
    update_users.update_command_database(new_command)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='Markdown')


# USER'S MESSAGES -----------------------------------------------------------------------------------------------------
async def message(update: Update, context: CallbackContext):
    if isinstance(update.message.text, str):
        text = messages.text_message(update.message.text, update.message.from_user.language_code)
    else:
        text = messages.incorrect_message(update.message.from_user.language_code)
    await update.message.reply_text(text=text)


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

    info_handler = CommandHandler('info', info)
    application.add_handler(info_handler)

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

    database_handler = CommandHandler("update_database", update_database)
    application.add_handler(database_handler)

    message_handler = MessageHandler(None, message)
    application.add_handler(message_handler)

    application.run_polling()
