"""
- get the query from the bot and the config file
- create a query to the kinopoiskAPI
- get the actual information from the kinopoiskAPI
- send information to the bot

- *default parameters values in the config-file
"""


from datetime import date
import yaml
import requests
import pandas as pd
from random import randrange


# load the year for the correct query to the kinopoiskAPI
TODAY_YEAR = date.today().year

# load configs
with open('../configuration/config_server_api.yaml', 'r') as handle:
    config = yaml.full_load(handle)


# send queries to the kinopoiskAPI (for all pages)
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


# convert response into a pd.DataFrame with necessary information
def prepare_data(dataset: list) -> pd.DataFrame:
    data = []
    for elem in dataset:
        # name and description
        name = elem['name']
        if name is None:
            continue
        description = elem['shortDescription']
        if description is None:
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


# return the random element from the DataFrame
def random_dramas(df: pd.DataFrame) -> pd.Series:
    random_id = randrange(len(df))
    return df.iloc[random_id]


# return the necessary count of DataFrame top elements
def slice_list_dramas(df: pd.DataFrame, count_elem: int) -> pd.DataFrame:
    return df[:count_elem]


# --------------------------------------------- THE MAIN PART ---------------------------------------------
# formatting the result, depending on the user's query
def find_serials(mode: str
                 , parameters: dict = None
                 ) -> pd.DataFrame | pd.Series:  # TODO: sending user's parameters
    # DIFFERENT MODES -> for different commands:
    # best last dramas
    if mode == 'last':
        query = config['default_query_last']  # reading from config-file
        count_elem = int(query['count_elem'])

        response = load_data(query)
        df = prepare_data(response['docs'])
        df.sort_values(['Release year', 'KP rating'], ascending=False, inplace=True, ignore_index=True)
        return slice_list_dramas(df, count_elem)

    # random drama
    if mode == 'random':
        query = config['default_query_random']  # reading from config-file

        response = load_data(query)
        df = prepare_data(response['docs'])
        return random_dramas(df)

    # drama by user's parameters
    if mode == 'user choice':
        query = config['default_query_user']  # reading from config-file

        # additional params
        count_elem = parameters['count']
        del parameters['count']
        flag_best = parameters['mode'] == 'лучшие'
        del parameters['mode']

        parameters['year'] += f'-{TODAY_YEAR}'

        if parameters['year'].startswith('люб'):
            del parameters['year']
        if parameters['genres.name'].startswith('люб'):
            del parameters['genres.name']

        # adding user's parameters
        query['params'].update(parameters)

        response = load_data(query)
        df = prepare_data(response['docs'])

        # filtered by mode
        if flag_best:
            df.sort_values(['KP rating', 'Release year'], ascending=False, inplace=True, ignore_index=True)
        else:
            # shuffled dataframe
            df = df.sample(frac=1, ignore_index=True)
        return slice_list_dramas(df, count_elem)
