"""
- send actual dorams by default query
- ask on the query with user's parameters: kind, data or rate
"""


import logging
import yaml
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler


# logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# parsing config-file
with open('config.yaml') as handle:
    configs = yaml.full_load(handle)

TOKEN = configs['token']


# bot actions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f'Hi {update.message.chat.first_name}! Nice to see you here! \nWelcome to the world of doramas 🤍'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def random_dorama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Unfortunately I can't find a good dorama for you now, but I'm still learning 🥺"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def end(update: Update,  context: ContextTypes.DEFAULT_TYPE):
    text = f'Thanks for your politeness! Have a good day, {update.message.chat.first_name}!'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    random_dorama_handler = CommandHandler('random_dorama', random_dorama)
    application.add_handler(random_dorama_handler)

    end_handler = CommandHandler('end', end)
    application.add_handler(end_handler)

    application.run_polling()
