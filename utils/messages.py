"""
- bot messages dictionary with the same phrases in the different languages
"""

import pandas as pd

MESSAGE_COLUMNS = {
    'ru': ['Название', 'Описание', 'Рейтинг Кинопоиска', 'Жанры', 'Страна']
    , 'en': ['Name', 'Description', 'KP rating', 'Genres', 'Country']
}
DATABASE_COLUMNS = {'ru': ['Name', 'Description', 'KP rating', 'Genres', 'Country']
                    , 'en': ['Alternative name', 'Description_en', 'KP rating', 'Genres_en', 'Country_en']}

UNSUCCESSFUL_MESSAGE = {
    'ru': 'К сожалению, я не смогла найти подходящие дорамы, попробуй чуть попозже 🥺'
    , 'en': "Unfortunately I can't find a good K-drama for you now, you can try again a little later 🥺"
}


def start(name: str, language: str) -> str:
    if language == 'en':
        return f"I'm glad to see you here, {name}! 💖\n\n" \
               f"*What I can do:*\n" \
               f"🔹 /last - I'll send links to the 5 best recent dramas\n" \
               f"🔹 /random - I'll send you a link to a random drama\n" \
               f"🔹 /select - I'll find the dramas according to your request, " \
               f"taking into account their genre, year and country\n" \
               f"🔹 /info - developer's contact  ✍️\n\n"
    else:
        return f'Рада видеть тебя здесь, {name}! 💖 \n\n' \
               f'*Что я умею: * \n' \
               f'🔹 /last - отправлю ссылки на 5 лучших последних дорам\n' \
               f'🔹 /random - пришлю ссылку на случайную дораму\n' \
               f'🔹 /select - найду дорамы по твоему запросу, учитывая их жанр, год и страну\n' \
               f'🔹 /info - контакт разработчицы ✍️\n\n'


def info(language: str) -> str:
    if language == 'en':
        return f"I hope my Ji Hyun was helpful!\n" \
               f"If you have any suggestions _(I'm really looking forward to it)_, " \
               f"questions or complaints, then you can text me here: @sepofia2.\n\n" \
               f"_Now let's stock up on ramen and enjoy watching the best K-dramas!_ 🍜💛"
    else:
        return f'Надеюсь моя Джи Хён оказалась полезной!\n' \
               f'Ну а если у тебя возникли любые пожелания _(очень буду рада)_, ' \
               f'вопросы или жалобы, то можешь написать мне в тг: @sepofia2\n\n' \
               f'_Теперь - запасаемся рамёном и наслаждаемся лучшими дорамами! Приятного просмотра!_ 🍜💛'


def get_text_item(drama: pd.DataFrame, language: str, flag_short: bool=False) -> list[str]:
    items = []
    for j, (mes_col, db_col) in enumerate(zip(MESSAGE_COLUMNS['en'], DATABASE_COLUMNS[language])):
        if mes_col == 'Name':
            item = f'[{drama[db_col]}]({drama["Link"]})'
        else:
            if drama[db_col] is None or (flag_short and db_col.startswith('Desc')):
                continue
            item = f'*{MESSAGE_COLUMNS[language][j]}*: _{drama[db_col]}_'
        items.append(item)
    return items


def random_drama(drama: pd.DataFrame | pd.Series, language: str) -> str:
    if (drama is None) or (len(drama) == 0):
        return UNSUCCESSFUL_MESSAGE[language]

    header = {
        'ru': 'Здесь твоя случайная дорама:\n'
        , 'en': 'Here is your random K-drama:\n'
    }

    if language not in ['ru', 'en']:
        language = 'ru'

    text_items = [header[language]]
    text_items.extend(get_text_item(drama, language))
    text_items.append('')
    return '\n'.join(text_items)


def last_dramas(dramas_df: pd.DataFrame, language: str) -> str:
    if len(dramas_df) == 0:
        return UNSUCCESSFUL_MESSAGE[language]

    header = {
        'ru': 'Здесь 5 лучших корейских дорам из недавно выпущенных по рейтингу Кинопоиска:\n'
        , 'en': 'Here are 5 best last K-dramas by Kinopoisk rating:\n'
    }

    if language not in ['ru', 'en']:
        language = 'ru'

    text_items = [header[language]]
    for ind in dramas_df.index:
        text_items.extend(get_text_item(dramas_df.iloc[ind], language))
        text_items.append('')
    return '\n'.join(text_items)


def user_dramas(dramas_df: pd.DataFrame | None, language: str) -> str:
    if (dramas_df is None) or (len(dramas_df) == 0):
        return UNSUCCESSFUL_MESSAGE[language]

    header = {
        'ru': 'Дорамы по твоему запросу:\n'
        , 'en': 'K-dramas for your query:\n'
    }

    if language not in ['ru', 'en']:
        language = 'ru'

    text_items = [header[language]]
    text_items_short = [header[language]]

    for i, ind in enumerate(dramas_df.index):
        text_items.extend(get_text_item(dramas_df.iloc[ind], language))
        text_items_short.extend(get_text_item(dramas_df.iloc[ind], language, True))
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


def update_database_message(flag_access: bool):
    if flag_access:
        return "Database is successfully updated!"
    return "You are not my developer 💅"
