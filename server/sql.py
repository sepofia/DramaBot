"""
- get the query from the bot
- setup parameters values for the SQL-query to a local database
  * all SQL-queries in the `database/queries.py` file
- get the result from my local database
- send information to the bot
"""


import pandas as pd

from database import queries as dq


# launch the necessary function from `queries.py`, depending on the user's command
def find_serials(mode: str
                 , parameters: dict = None
                 ) -> pd.DataFrame | pd.Series:
    # DIFFERENT MODES -> for different commands:
    if mode == 'random':        # random drama
        answer = dq.random()
        return pd.Series(answer)

    if mode == 'last':          # best last dramas
        answer = dq.last()
        return pd.DataFrame(answer)

    if mode == 'user choice':   # drama by user's parameters
        answer = dq.select(
            usr_genre=parameters['genres.name']
            , usr_country=parameters['countries.name']
            , usr_year=parameters['year']
            , usr_count=parameters['count']
            , usr_mode=parameters['mode']
        )
        return pd.DataFrame(answer)

    return None
