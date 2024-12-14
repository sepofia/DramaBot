"""
it might be reasonable to add choosing language:
- in the separate function with the global LANGUAGE parameter for this file
- create dictionary with the same phrases in the different languages
"""

import pandas as pd

COLUMNS = {
    'ru': ['Название', 'Описание', 'Рейтинг Кинопоиска', 'Жанры', 'Страна']
    , 'en': ['Name', 'Description', 'KP rating', 'Genres', 'Countries']
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
    columns = {
        'ru': ['Название', 'Описание', 'Рейтинг Кинопоиска', 'Жанры', 'Страна']
        , 'en': ['Name', 'Description', 'KP rating', 'Genres', 'Countries']
    }
    text_items = [header[language]]
    for j, col in enumerate(['Name', 'Description', 'KP rating', 'Genres', 'Countries']):
        if col == 'Name':
            item = f'[{drama[col]}]({drama["Link"]})'
        else:
            item = f'*{columns[language][j]}*: _{drama[col]}_'
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
        for j, col in enumerate(['Name', 'KP rating', 'Genres', 'Countries']):
            if col == 'Name':
                item = f'*{i + 1}.* [{dramas_df[col][i]}]({dramas_df["Link"][i]})'
            else:
                item = f'*{COLUMNS[language][j]}*: _{dramas_df[col][i]}_'
            text_items.append(item)
        text_items.append('')
    return '\n'.join(text_items)


def user_dramas(dramas_df: pd.DataFrame | None, language: str) -> str:

    unsuccessful = {
        'ru': 'К сожалению, я не смогла найти подходящую дораму по твоим рекомендациям...\n'
              'Пример запроса: `/user_dramas genres.name мелодрама rating.kp 7.8-10 year 2019-2024`'
        , 'en': "Unfortunately I can't find good K-dramas for you by your recommendations...\n"
                "Example of query: `/user_dramas genres.name мелодрама rating.kp 7.8-10 year 2019-2024`"
    }
    header = {
        'ru': 'Здесь 5 лучших корейских дорам по твоему запросу:\n'
        , 'en': 'Here are best K-dramas for your query:\n'
    }

    if (dramas_df is None) or (len(dramas_df) == 0):
        return unsuccessful[language]

    text_items = [header[language]]
    for i in range(len(dramas_df)):
        for j, col in enumerate(['Name', 'KP rating', 'Genres', 'Countries']):
            if col == 'Name':
                item = f'*{i + 1}.* [{dramas_df[col][i]}]({dramas_df["Link"][i]})'
            else:
                item = f'*{COLUMNS[language][j]}*: _{dramas_df[col][i]}_'
            text_items.append(item)
        text_items.append('')
    return '\n'.join(text_items)
