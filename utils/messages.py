"""
it might be reasonable to add choosing language:
- in the separate function with the global LANGUAGE parameter for this file
- create dictionary with the same phrases in the different languages
"""

import pandas as pd

# TODO: move to the json-file
COLUMNS = {
    'ru': ['Название', 'Описание', 'Рейтинг Кинопоиска', 'Жанры', 'Страна']
    , 'en': ['Name', 'Description', 'KP rating', 'Genres', 'Country']
}


def start(name: str, language: str) -> str:
    if language == 'en':
        return f'Hi {name}! Nice to see you here! \nWelcome to the world of K-dramas 🤍'
    if language == 'ru':
        return f'Привет, {name}, рада видеть тебя здесь! \nДобро пожаловать в мир дорам 🤍'


def help_message():
    pass


def random_drama(drama: pd.DataFrame | pd.Series, language: str) -> str:
    header = {
        'ru': 'Здесь твоя случайная дорама не старше 2016 года и с рейтингом кинопоиска выше 7.1:\n'
        , 'en': 'Here is your random K-drama from 2016 to 2024 and with a kinopoisk rating of over 7.1:\n'
    }
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
        'ru': 'Здесь 5 лучших корейских дорам за последние 2 года по рейтингу Кинопоиска:\n'
        , 'en': 'Here are 5 best last K-dramas by Kinopoisk rating:\n'
    }
    unsuccessful = {
        'ru': 'К сожалению, я не смогла найти подходящую дораму для тебя, но я ещё учусь 🥺'
        , 'en': "Unfortunately I can't find a good K-drama for you now, but I'm still learning 🥺"
    }

    if len(dramas_df) == 0:
        return unsuccessful[language]

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

    unsuccessful = {
        'ru': 'К сожалению, я не смогла найти подходящую дораму по твоим рекомендациям...'
        , 'en': "Unfortunately I can't find good K-dramas for you by your recommendations..."
    }
    header = {
        'ru': 'Дорамы по твоему запросу:\n'
        , 'en': 'K-dramas for your query:\n'
    }

    if (dramas_df is None) or (len(dramas_df) == 0):
        return unsuccessful[language]

    text_items = [header[language]]
    for i in range(len(dramas_df)):
        for j, col in enumerate(COLUMNS['en']):
            if col == 'Name':
                item = f'*{i + 1}.* [{dramas_df[col][i]}]({dramas_df["Link"][i]})'
                text_items.append(item)
            else:
                if not (dramas_df[col][i] is None):
                    item = f'*{COLUMNS[language][j]}*: _{dramas_df[col][i]}_'
                    text_items.append(item)
        text_items.append('')
    return '\n'.join(text_items)


def select(language: str) -> str:
    text = {
        'ru': 'Давай выберем дораму по твоим пожеланиям! Сначала выбери жанр:'
              '\n_Для прекращения поиска отправь команду_ /cancel.\n'
        , 'en': "Let's choose K-dramas especially for you! First, choose a genre:"
                "\n_Send the_ /cancel _command to stop._"
    }
    return text[language]


def genre(language: str) -> str:
    # TODO: change the message - "select the minimum year" or in some similar way
    text = {
        'ru': 'Запомнила! Теперь укажи минимальную оценку Кинопоиска:'
              '\n_Для прекращения поиска отправь команду_ /cancel.\n'
        , 'en': 'Memorize! Now select a minimum Kinopoist rating:'
                '\n_Send the_ /cancel _command to stop._'
    }
    return text[language]


def rating(language: str) -> str:
    text = {
        'ru': 'Запомнила! Теперь укажи минимальный год производства:'
              '\n_Для прекращения поиска отправь команду_ /cancel.\n'
        , 'en': 'Memorize! Now select a minimum production year:'
                '\n_Send the_ /cancel _command to stop._'
    }
    return text[language]


def year(language: str) -> str:
    text = {
        'ru': 'Отлично! Теперь укажи страну:'
              '\n_Для прекращения поиска отправь команду_ /cancel.\n'
        , 'en': 'Great! Then specify the county:'
                '\n_Send the_ /cancel _command to stop._'
    }
    return text[language]


def country(language: str) -> str:
    text = {
        'ru': 'Сколько дорам мне нужно найти?'
              '\n_Для прекращения поиска отправь команду_ /cancel.\n'
        , 'en': 'How many K-drams do you want?'
                '\n_Send the_ /cancel _command to stop._'
    }
    return text[language]


def count(language: str) -> str:
    text = {
        'ru': 'И последний вопрос: ты хочешь получить дорамы с самым высоким рейтингом или просто случайные?'
        , 'en': "And the last question: do you want to get the highest rated K-dramas or just random ones?"
    }
    return text[language]


# def mode(language: str) -> str:
#     text = {
#         'ru': 'Всё записала! Сейчас найду для тебя подходящие дорамы ^-^'
#         , 'en': "Noted! Let's see what I can find for you ^-^"
#     }
#     return text[language]


def cancel(language: str) -> str:
    text = {
        'ru': 'Не вопрос ;) \nВыберем дорамы для тебя как-нибудь в другой раз!'
        , 'en': "Ok! We can choose K-dramas for you at any time ;)"
    }
    return text[language]
