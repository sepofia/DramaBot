"""
- sql-queries for a local database by users commands
"""


import sys
import yaml
import json
import psycopg2
from psycopg2.extras import DictCursor
from contextlib import closing


WORK_DIR = sys.path[0]
# load configurate files
with open(WORK_DIR + '/configuration/config_database.yaml', 'r') as handle:
    configs = yaml.full_load(handle)

# load files with translated inscriptions
with open(WORK_DIR + '/database/translate_genres.json', encoding='utf-8') as handle:
    dict_genres = json.load(handle)

with open(WORK_DIR + '/database/translate_countries.json', encoding='utf-8') as handle:
    dict_countries = json.load(handle)


def prepare_one_drama(row) -> dict:
    # parsing the output from the database
    (_, name, alternative_name, kp, imdb, production_year, link,
     description, description_en, countries, countries_en, genres, genres_en) = row
    return {
        'Name': name
        , 'Alternative name': alternative_name
        , 'Description': description
        , 'Description_en': description_en
        , 'KP rating': kp
        , 'IMDB rating': imdb
        , 'Genres': genres
        , 'Genres_en': genres_en
        , 'Country': countries
        , 'Country_en': countries_en
        , 'Release year': production_year
        , 'Link': link
    }


# QUERY -> DATABASE -> OUTPUT
def random() -> dict:
    # create database session
    with (closing(psycopg2.connect(**configs)) as conn):
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('SELECT t.* '
                           'FROM tv_series AS t '
                           'INNER JOIN countries AS c '
                           'ON t.id = c.id '
                           'WHERE (t.kp_rating >= 7 OR t.imdb_rating >= 9) AND c.south_korea = TRUE '
                           'ORDER BY RANDOM() '
                           'LIMIT 1;')

            row = cursor.fetchall()
            if len(row) == 0 or row is None:
                return {}
            return prepare_one_drama(row[0])


def last() -> list[dict]:
    with closing(psycopg2.connect(**configs)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute('SELECT t.* '
                           'FROM tv_series AS t '
                           'JOIN countries AS c '
                           'ON t.id = c.id '
                           'WHERE c.south_korea = TRUE and t.kp_rating >= 7 '
                           'ORDER BY t.production_year DESC, t.kp_rating DESC '
                           'LIMIT 5;')
            answer = []
            for row in cursor:
                answer.append(prepare_one_drama(row))
            return answer


def select(
        usr_genre: str, usr_country: str, usr_year: str, usr_count: str
        , usr_mode: str  # best or random
) -> list[dict]:
    # formulate conditions
    condition_genre = ''
    if usr_genre != 'любой':
        genre = dict_genres['ru-en'][usr_genre]
        condition_genre = f' AND g.{genre} = TRUE '

    condition_year = ''
    if usr_year != 'любой':
        condition_year = f' AND t.production_year >= {usr_year} '

    country_column = f'{dict_countries["ru-en"][usr_country]}'
    count = int(usr_count)

    condition_order = 'ORDER BY t.kp_rating DESC' if usr_mode == 'лучшие' else 'ORDER BY RANDOM()'

    with closing(psycopg2.connect(**configs)) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = f"""
                SELECT t.* 
                FROM tv_series AS t 
                JOIN countries c ON t.id = c.id 
                JOIN genres AS g ON t.id = g.id 
                WHERE c.{country_column} = TRUE AND t.kp_rating >= 7 
                {condition_genre} {condition_year}
                {condition_order} 
                LIMIT {count};
            """
            cursor.execute(query)

            answer = []
            for row in cursor:
                answer.append(prepare_one_drama(row))
            return answer
