"""
- get the query from the bot
- setup parameters values
- get the actual information from the kinopoiskAPI
- send information to the bot

- *default parameters' values in the config-file
"""


import yaml
import requests
import pandas as pd
from random import randrange


with open('configuration/config_server.yaml', 'r') as handle:
    config = yaml.full_load(handle)


def load_data(query: dict) -> dict:
    headers = query['headers']
    url = query['url']
    params = query['params']

    response = requests.get(url, headers=headers, params=params, timeout=60)
    response_json = response.json()
    for page in range(2, response_json['pages']):
        params['page'] = page
        add_response = requests.get(url, headers=headers, params=params, timeout=60)
        add_response_json = add_response.json()
        response_json['docs'].extend(add_response_json['docs'])
    return response_json


def prepare_data(dataset: list) -> pd.DataFrame:
    data = []
    for elem in dataset:
        # name and description
        name = elem['name']
        description = elem['description']
        # release year
        release_year = elem['year']
        # rating: kp and imdb
        kp = round(elem['rating']['kp'], 1)
        imdb = round(elem['rating']['imdb'], 1)

        # genres to string
        list_genres = [genre['name'] for genre in elem['genres']]
        genres = ', '.join(list_genres)
        # countries to string
        list_countries = [country['name'] for country in elem['countries']]
        countries = ', '.join(list_countries)

        # create link
        kp_id = elem['id']
        link = f'https://www.kinopoisk.ru/series/{str(kp_id)}/'

        # creating element of dataset:
        new_elem = {
            'Name': name
            , 'Description': description
            , 'KP rating': kp
            , 'IMDB rating': imdb
            , 'Genres': genres
            , 'Country': countries
            , 'Release year': release_year
            , 'Link': link
        }
        data.append(new_elem)

    df = pd.DataFrame(data)
    return df


def random_dramas(df: pd.DataFrame) -> pd.Series:
    random_id = randrange(len(df))
    return df.iloc[random_id]


def slice_list_dramas(df: pd.DataFrame, count_elem: int) -> pd.DataFrame:
    return df[:count_elem]


# --------------------------------------------- THE MAIN PART ---------------------------------------------
def find_serials(mode: str
                 , parameters: dict = None
                 ) -> pd.DataFrame | pd.Series:  # TODO: sending user's parameters
    # DIFFERENT MODES:
    # best last dramas
    if mode == 'last':
        # reading from config-file
        query = config['default_query_last']
        count_elem = int(query['count_elem'])

        response = load_data(query)
        df = prepare_data(response['docs'])
        df.sort_values(['Release year', 'KP rating'], ascending=False, inplace=True, ignore_index=True)
        return slice_list_dramas(df, count_elem)

    # random drama
    if mode == 'random':
        # reading from config-file
        query = config['default_query_random']

        response = load_data(query)
        df = prepare_data(response['docs'])
        return random_dramas(df)

    # drama by user's parameters
    if mode == 'user choose':
        # reading from config-file
        query = config['default_query_user']
        count_elem = parameters['count']
        del parameters['count']
        # adding user's parameters
        query['params'].update(parameters)

        response = load_data(query)
        df = prepare_data(response['docs'])
        df.sort_values(['KP rating', 'Release year'], ascending=False, inplace=True, ignore_index=True)
        return slice_list_dramas(df, count_elem)
