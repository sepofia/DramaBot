"""
- bot messages dictionary with the same phrases in the different languages
"""

import pandas as pd

COLUMNS = {
    'ru': ['Название', 'Описание', 'Рейтинг Кинопоиска', 'Жанры', 'Страна']
    , 'en': ['Name', 'Description', 'KP rating', 'Genres', 'Country']
}

UNSUCCESSFUL_MESSAGE = {
    'ru': 'К сожалению, я не смогла найти подходящие дорамы, попробуй чуть попозже 🥺'
    , 'en': "Unfortunately I can't find a good K-drama for you now, you can try again a little later 🥺"
}


def start(name: str, language: str) -> str:
    if language not in ['ru', 'en']:
        language = 'ru'
    if language == 'en':
        return f"Hello, {name}! 💖 My name is Ji Hyun, and I will help you find the best dramas on Kinopoisk!\n" \
               f"Do you want romance, drama, or something light and funny? I'll pick the perfect list for you! 😎\n\n" \
               f"*What I can do:*\n" \
               f"🔹 /last - I will send links to the 5 best recent dramas;\n" \
               f"🔹 /random - I 'll send you a link to a random drama;\n" \
               f"🔹 /select - I will find the dramas according to your request, " \
               f"taking into account their genre, year and country! 🫶\n\n" \
               f"💭 If you have any suggestions (I'm really looking forward to it! 🤭), " \
               f"questions or complaints 🙄, then you can email my developer: @sepofia2.\n\n" \
               f"Now let's stock up on ramen and enjoy watching! 🍜"
    if language == 'ru':
        return f'Привет, {name}! 💖 Меня зовут Джи Хён, и я помогу тебе найти самые лучшие дорамы на Кинопоиске!\n' \
               f'Хочешь романтики, драмы или что-то лёгкое и смешное? ' \
               f'Я подберу для тебя идеальный список! 😎\n\n' \
               f'*Что я умею: * \n' \
               f'🔹 /last - отправлю ссылки на 5 лучших последних дорам;\n' \
               f'🔹 /random - пришлю ссылку на случайную дораму;\n' \
               f'🔹 /select - найду дорамы по твоему запросу, учитывая их жанр, год и страну! 🫶\n\n' \
               f'💭 Если у тебя возникнут любые пожелания _(очень жду! 🤭)_, вопросы или жалобы 🙄, ' \
               f'то можешь написать на почту моей разработчице: @sepofia2.\n\n' \
               f'_Теперь - запасаемся рамёном и наслаждаемся просмотром!_ 🍜'


def random_drama(drama: pd.DataFrame | pd.Series, language: str) -> str:
    header = {
        'ru': 'Здесь твоя случайная дорама:\n'
        , 'en': 'Here is your random K-drama:\n'
    }
    if language not in ['ru', 'en']:
        language = 'ru'
    text_items = [header[language]]
    for j, col in enumerate(COLUMNS['en']):
        if col == 'Name':
            item = f'[{drama[col]}]({drama["Link"]})'
        else:
            item = f'*{COLUMNS[language][j]}*: _{drama[col]}_'
        text_items.append(item)
    text_items.append('')
    return '\n'.join(text_items)


def last_dramas(dramas_df: pd.DataFrame, language: str) -> str:
    header = {
        'ru': 'Здесь 5 лучших корейских дорам из недавно выпущенных по рейтингу Кинопоиска:\n'
        , 'en': 'Here are 5 best last K-dramas by Kinopoisk rating:\n'
    }

    if language not in ['ru', 'en']:
        language = 'ru'

    if len(dramas_df) == 0:
        return UNSUCCESSFUL_MESSAGE[language]

    text_items = [header[language]]
    for i in range(len(dramas_df)):
        for j, col in enumerate(COLUMNS['en']):
            if col == 'Name':
                item = f'*{i + 1}.* [{dramas_df[col][i]}]({dramas_df["Link"][i]})'
                text_items.append(item)
            else:
                if dramas_df[col][i] != 'None':
                    item = f'*{COLUMNS[language][j]}*: _{dramas_df[col][i]}_'
                    text_items.append(item)
        text_items.append('')
    return '\n'.join(text_items)


def user_dramas(dramas_df: pd.DataFrame | None, language: str) -> str:
    header = {
        'ru': 'Дорамы по твоему запросу:\n'
        , 'en': 'K-dramas for your query:\n'
    }

    if language not in ['ru', 'en']:
        language = 'ru'

    if (dramas_df is None) or (len(dramas_df) == 0):
        return UNSUCCESSFUL_MESSAGE[language]

    text_items = [header[language]]
    text_items_short = [header[language]]
    for i in range(len(dramas_df)):
        for j, col in enumerate(COLUMNS['en']):
            if col == 'Name':
                item = f'*{i + 1}.* [{dramas_df[col][i]}]({dramas_df["Link"][i]})'
                text_items.append(item)
                text_items_short.append(item)
            else:
                if not (dramas_df[col][i] is None):
                    item = f'*{COLUMNS[language][j]}*: _{dramas_df[col][i]}_'
                    text_items.append(item)
                    if col not in ['Description', 'Описание']:
                        text_items_short.append(item)
        text_items.append('')
        text_items_short.append('')
    text = '\n'.join(text_items)
    text_short = '\n'.join(text_items_short)
    return text if len(text) < 4096 else text_short


def select(language: str) -> str:
    text = {
        'ru': 'Давай выберем дораму по твоим пожеланиям! Сначала выбери жанр:'
              '\n_Для прекращения поиска отправь команду_ /cancel.\n'
        , 'en': "Let's choose K-dramas especially for you! First, choose a genre:"
                "\n_Send the_ /cancel _command to stop._"
    }
    if language not in ['ru', 'en']:
        language = 'ru'

    return text[language]


def genre(language: str) -> str:
    text = {
        'ru': 'Запомнила! Теперь укажи минимальный год производства:'
              '\n_Для прекращения поиска отправь команду_ /cancel.\n'
        , 'en': 'Memorize! Now select a minimum production year:'
                '\n_Send the_ /cancel _command to stop._'
    }
    if language not in ['ru', 'en']:
        language = 'ru'

    return text[language]


def year(language: str) -> str:
    text = {
        'ru': 'Отлично! Теперь укажи страну:'
              '\n_Для прекращения поиска отправь команду_ /cancel.\n'
        , 'en': 'Great! Then specify the county:'
                '\n_Send the_ /cancel _command to stop._'
    }
    if language not in ['ru', 'en']:
        language = 'ru'

    return text[language]


def country(language: str) -> str:
    text = {
        'ru': 'Сколько дорам мне нужно найти?'
              '\n_Для прекращения поиска отправь команду_ /cancel.\n'
        , 'en': 'How many K-drams do you want?'
                '\n_Send the_ /cancel _command to stop._'
    }
    if language not in ['ru', 'en']:
        language = 'ru'

    return text[language]


def count(language: str) -> str:
    text = {
        'ru': 'И последний вопрос: ты хочешь получить дорамы с самым высоким рейтингом или просто случайные?'
        , 'en': "And the last question: do you want to get the highest rated K-dramas or just random ones?"
    }
    if language not in ['ru', 'en']:
        language = 'ru'

    return text[language]


def cancel(language: str) -> str:
    text = {
        'ru': 'Не вопрос ;) \nВыберем дорамы для тебя как-нибудь в другой раз!'
        , 'en': "Ok! We can choose K-dramas for you at any time ;)"
    }
    if language not in ['ru', 'en']:
        language = 'ru'

    return text[language]


def incorrect_message(language: str):
    if language == 'en':
        text = "Sorry, I don't understand your message 👀 \nTry to use commands from menu"
    else:
        text = 'Не совсем понимаю, что ты имеешь в виду 👀 \nПопробуй использовать команды из меню'
    return text


def text_message(context: str, language: str):
    if 'спасибо' in context.lower():
        text = 'Рада, что смогла помочь 🫶'
    elif 'thank' in context.lower():
        text = "I was happy to help you 🫶"
    else:
        return incorrect_message(language)
    return text
