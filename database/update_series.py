"""
- updating local database from the kinopoiskAPI
- IMPORTANT: I load only new dramas and don't update the rating of already loaded dramas!
"""

import logging
import asyncio
import os
import yaml
import json
import requests
import psycopg2
import time

from psycopg2 import sql
from psycopg2.extras import DictCursor
from contextlib import closing
from googletrans import Translator


WORK_DIR = os.environ.get('PROJECT_PATH', os.getcwd())
# load configurate files
with open(WORK_DIR + '/configuration/config_server_api.yaml', 'r') as handle:
    config = yaml.full_load(handle)

with open(WORK_DIR + '/configuration/config_database.yaml', 'r') as handle:
    configs = yaml.full_load(handle)

with open(WORK_DIR + '/configuration/config_logger.yaml', 'r') as handle:
    logger_config = yaml.full_load(handle)

# load files with translated inscriptions
with open(WORK_DIR + '/database/translate_genres.json', encoding='utf-8') as handle:
    dict_genres = json.load(handle)

with open(WORK_DIR + '/database/translate_countries.json', encoding='utf-8') as handle:
    dict_countries = json.load(handle)


# logging
# log_filename = WORK_DIR + logger_config['series_logging']
# with open(log_filename, 'a') as handle:
#     handle.write(' -- NEW SESSION -- \n')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    , level=logging.INFO
    # , filename=log_filename
)
logger = logging.getLogger('my_logs')


def load_old_data() -> set:
    logger.info('Start loading old dataset from tv_series table')
    with closing(psycopg2.connect(**configs)) as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id FROM tv_series;')
            old_data = set([elem[0] for elem in cursor.fetchall()])
            logger.info('Successful loading old tv_series table')
            return old_data


def load_from_api_by_query(query: dict) -> dict:
    headers = query['headers']
    url = query['url']
    params = query['params']

    response = requests.get(url, headers=headers, params=params)
    response_json = response.json()
    for page in range(2, response_json['pages'] + 1):
        params['page'] = page
        add_response = requests.get(url, headers=headers, params=params)
        add_response_json = add_response.json()
        response_json['docs'].extend(add_response_json['docs'])
    return response_json


def load_all_dataset() -> list:
    # load old series database
    old_data = load_old_data()  # old series dataset from local database

    # load all series from Kinopoisk_API
    logger.info('Start loading new tv_series data from Kinopoisk_API')
    new_data = []  # new series dataset for local database

    # load series from South Korea
    query_1 = config['load_query']
    response = load_from_api_by_query(query_1)['docs']
    for item in response:  # check is the serial is already in database
        if item['id'] not in old_data:
            new_data.append(item)
    count_1 = len(new_data)

    logger.info(f'Loaded {count_1} from country {query_1["params"]["countries.name"]}.')
    logger.info('Successful looking up new tv_series from South Korea')

    # load series from China
    query_2 = query_1
    query_2['params']['page'] = 1
    query_2['params']['countries.name'] = 'Китай'
    response = load_from_api_by_query(query_2)['docs']
    for item in response:  # check is the serial is already in database
        if item['id'] not in old_data:
            new_data.append(item)
    count_2 = len(new_data)

    logger.info(f'Loaded {count_2 - count_1} from country {query_2["params"]["countries.name"]}.')
    logger.info('Successful looking up new tv_series from China')

    # load series from Japan
    query_3 = query_1
    query_3['params']['page'] = 1
    query_3['params']['countries.name'] = 'Япония'
    response = load_from_api_by_query(query_3)['docs']
    for item in response:  # check is the serial is already in database
        if item['id'] not in old_data:
            new_data.append(item)
    count_3 = len(new_data)

    logger.info(f'Loaded {count_3 - count_2} from country {query_3["params"]["countries.name"]}.')
    logger.info('Successful looking up new tv_series from Japan')

    return new_data

def run_async(func, *args, **kwargs):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        return loop.run_until_complete(func(*args, **kwargs))
    else:
        return asyncio.run(func(*args, **kwargs))

def create_different_datasets(dataset: list) -> (list, list, list):
    def translate_text(selected_translator: Translator, ru_texts: str) -> str | None:
        try:
            en_text = run_async(selected_translator.translate, ru_texts, dest='en', src='ru')
            return en_text.text
        except Exception as e:
            logger.info(e)
            return None

    logger.info('Start formatting datasets for local Database')

    series_values, countries_values, genres_values = [], [], []
    pr_key = set()

    # translating
    translator = Translator()
    n = len(dataset)

    for i, elem in enumerate(dataset):
        kp_id = elem['id']
        if kp_id in pr_key:
            continue
        pr_key.add(kp_id)
        # name and description
        name = elem['name']
        if name is None:
            # pass the unknown dramas
            continue

        alternative_name = elem['alternativeName']
        if alternative_name is None:
            alternative_name = name

        description = elem['shortDescription']
        if description is None:
            description = elem['description']

        if description is None:
            description_en = None
        else:
            description_en = translate_text(translator, description) if description else ''

        # release year
        production_year = elem['year']
        # rating: kp and imdb
        kp_rating = round(elem['rating']['kp'], 1)
        imdb_rating = round(elem['rating']['imdb'], 1)

        # genres to string
        list_genres = [genre['name'] for genre in elem['genres']]
        all_genres = ', '.join(list_genres)
        try:
            all_genres_en = ', '.join(
                [' '.join(dict_genres["ru-en"][genre_i].split("_")) for genre_i in list_genres]
            )
        except:
            all_genres_en = translate_text(translator, all_genres)
        # countries to string
        list_countries = [country['name'] for country in elem['countries']]
        all_countries = ', '.join(list_countries)
        try:
            all_countries_en = ', '.join(
                [' '.join(dict_countries["ru-en"][country_i].split("_")) for country_i in list_countries]
            )
        except:
            all_countries_en = translate_text(translator, all_countries)

        # create link
        link = f'https://www.kinopoisk.ru/series/{str(kp_id)}/'

        elem_series = (
            kp_id
            , name
            , alternative_name
            , kp_rating
            , imdb_rating
            , production_year
            , link
            , description
            , description_en
            , all_countries
            , all_countries_en
            , all_genres
            , all_genres_en
        )

        elem_countries_bools = [country in list_countries for country in dict_countries['ru-en']]
        elem_countries = (kp_id, *elem_countries_bools)

        elem_genres_bools = [genre in list_genres for genre in dict_genres['ru-en']]
        elem_genres = (kp_id, *elem_genres_bools)

        series_values.append(elem_series)
        countries_values.append(elem_countries)
        genres_values.append(elem_genres)

        if i % 10 == 0:
            logger.info(f'{round(i / n * 100, 2)}%')

    logger.info('Successful formatting datasets for local database')
    return series_values, countries_values, genres_values


def create_series_databases(
        values_series: list, values_countries: list, values_genres: list
) -> None:
    logger.info('Connect for local database')
    with closing(psycopg2.connect(**configs)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            conn.autocommit = True

            values_series_sql = sql.SQL(',').join(map(sql.Literal, values_series))
            insert = sql.SQL(
                'INSERT INTO tv_series '
                'VALUES {}').format(values_series_sql)
            cursor.execute(insert)

            values_countries_sql = sql.SQL(',').join(map(sql.Literal, values_countries))
            insert = sql.SQL(
                'INSERT INTO countries '
                'VALUES {}').format(values_countries_sql)
            cursor.execute(insert)

            values_genres_sql = sql.SQL(',').join(map(sql.Literal, values_genres))
            insert = sql.SQL(
                'INSERT INTO genres '
                'VALUES {}').format(values_genres_sql)
            cursor.execute(insert)

            logger.info('Successful updating series tables\n\n')


# launch --------------------------------------------------------------------------------------------------------
def launch_creating_datasets() -> None:
    start_time = time.time()
    data_from_api = load_all_dataset()

    kp_time = time.time()
    logger.info(f'The loading from KinoPoisk takes {kp_time - start_time} seconds')

    series, countries, genres = create_different_datasets(data_from_api)
    if not series:
        logger.info('There is no new date to add to the local database\n\n')
    else:
        create_series_databases(series, countries, genres)

    db_time = time.time()
    logger.info(f'The preparing and saving to the database take {db_time - kp_time} seconds')
    logger.info(f'All actions take {db_time - start_time} seconds')
