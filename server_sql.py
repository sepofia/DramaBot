"""
- get the query from the bot
- setup parameters values
- get the actual information from my own database
- send information to the bot
"""


import pandas as pd

from database import database_queries as dq


def find_serials(mode: str
                 , parameters: dict = None
                 ) -> pd.DataFrame | pd.Series:
    # DIFFERENT MODES:
    # random drama
    if mode == 'random':
        answer = dq.random()
        return pd.Series(answer)

    # best last dramas
    if mode == 'last':
        answer = dq.last()
        return pd.DataFrame(answer)

    # drama by user's parameters
    if mode == 'user choice':
        answer = dq.select(
            usr_genre=parameters['genres.name']
            , usr_country=parameters['countries.name']
            , usr_year=parameters['year']
            , usr_count=parameters['count']
            , usr_mode=parameters['mode']
        )
        return pd.DataFrame(answer)
