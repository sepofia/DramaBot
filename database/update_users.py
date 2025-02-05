"""
- load information about new users
- load information about users commands
- load information about users preferences (`/select` command)
- load information about request status (successful or not)
"""


import yaml
import logging
import psycopg2
from psycopg2 import sql
from contextlib import closing


# load config-file for connection with local Database
with open('C:/Users/пк/Documents/repositories/DoramaBot/configuration/config_database.yaml', 'r') as handle:
    configs = yaml.full_load(handle)

with open('C:/Users/пк/Documents/repositories/DoramaBot/configuration/config_logger.yaml', 'r') as handle:
    logger_config = yaml.full_load(handle)


# logging
log_filename = logger_config['bot_logging']

with open(log_filename, 'a') as handle:
    handle.write('\n\n -- NEW SESSION -- \n')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    , level=logging.INFO
    , filename=log_filename
)
logger = logging.getLogger('my_logs')


# load already existed items in Database
def load_user_id() -> set:
    with closing(psycopg2.connect(**configs)) as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT id from users;')
            result = set([elem[0] for elem in cursor.fetchall()])
            logger.info('Old users loaded from the local database')
            return result


# load new items in the Database
def update_users_database(value: tuple) -> None:
    with closing(psycopg2.connect(**configs)) as conn:
        with conn.cursor() as cursor:
            conn.autocommit = True

            value_sql = sql.SQL(',').join(map(sql.Literal, [value]))
            insert = sql.SQL('INSERT INTO users VALUES {};').format(value_sql)
            cursor.execute(insert)
            logger.info(f'User {value[0]} added in the local database')


def update_command_database(value: tuple, parameters: tuple=()):
    with closing(psycopg2.connect(**configs)) as conn:
        with conn.cursor() as cursor:
            conn.autocommit = True

            # write the command in the `commands` table
            value_sql = sql.SQL(',').join(map(sql.Literal, value))
            insert = sql.SQL(
                'INSERT INTO commands (user_id, command_type, date_time, result) VALUES ({});'
            ).format(value_sql)

            cursor.execute(insert)
            logger.info(f'Command {value[1]} from user {value[0]} added in the database')

    # if the command is `select` - insert parameters in the `commands_select` table
    if value[1] == 'select':
        # put the command_id from the `commands` table
        with closing(psycopg2.connect(**configs)) as conn:
            with conn.cursor() as cursor:
                conn.autocommit = True

                query = f'''
                SELECT id FROM commands 
                WHERE user_id = {value[0]} 
                ORDER BY date_time DESC 
                LIMIT 1;
                '''
                cursor.execute(query)
                command_id = cursor.fetchall()[0][0]

                parameters_sql = sql.SQL(',').join(map(sql.Literal, (command_id, *parameters)))
                insert = sql.SQL(
                    'INSERT INTO commands_select (command_id, genre, min_year, country, count, answer_mode) '
                    'VALUES ({});'
                ).format(parameters_sql)

                cursor.execute(insert)
                logger.info(f'Parameters command `select` {command_id} added in the database')
