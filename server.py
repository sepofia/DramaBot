"""
- get the query from the bot
- setup parameters values
- get the actual information from the kinopoiskAPI
- send information to the bot

- *default parameters' values in the config-file (with TOKEN)
"""


import requests
import pandas as pd


def prepare_data(dataset: list, count_elem: int) -> pd.DataFrame:
    data = []
    for elem in dataset:
        if 'names' in elem:
            # check names for RU name
            for name_i in elem['names']:
                if name_i['language'] == 'RU':
                    name = name_i['name']
                    break
            else:
                # don't find RU name
                name = elem['name']
        else:
            # choose the default name
            name = elem['name']

        # rating: kp and imdb
        kp = round(elem['rating']['kp'], 1)
        imdb = round(elem['rating']['imdb'], 1)

        # genres to string
        list_genres = [genre['name'] for genre in elem['genres']]
        genres = ', '.join(list_genres)
        # countries to string
        list_countries = [country['name'] for country in elem['countries']]
        countries = ', '.join(list_countries)

        # release year
        release_year = elem['year']

        # create link
        kp_id = elem['id']
        link = f'https://www.kinopoisk.ru/series/{str(kp_id)}/'  # TODO: set links template in the .yaml

        # creating element of dataset:
        new_elem = {
            'Name': name
            , 'KP rating': kp
            , 'IMDB rating': imdb
            , 'Genres': genres
            , 'Countries': countries
            , 'Release year': release_year
            , 'Link': link
        }
        data.append(new_elem)

    df = pd.DataFrame(data)
    df.sort_values(['Release year', 'KP rating'], ascending=False, inplace=True, ignore_index=True)
    return df[:count_elem]


def load_data(query: dict) -> dict:
    headers = query['headers']
    url = query['url']
    params = query['params']

    response = requests.get(url, headers=headers, params=params, timeout=60)
    return response.json()


def find_serials(query: dict[str, str]) -> pd.DataFrame:
    count_elem = int(query['count_elem'])
    response = load_data(query)
    return prepare_data(response['docs'], count_elem)
