"""
- find users in my database (by ID)
- in there a new user, then create a new row
"""

import pandas as pd

filepath = 'C:/Users/пк/Documents/repositories/DoramaBot/database/users.csv'


def load_database() -> pd.DataFrame:
    return pd.read_csv(filepath)


def check_user(user: dict):
    users_df = load_database()
    if len(users_df) == 0 or user['id'] not in users_df['id'].tolist():
        user_df = pd.DataFrame([user])
        user_df.to_csv(filepath, header=False, mode='a', index=False)


def find_user(user_id: int) -> pd.DataFrame | pd.Series:
    users_df = load_database()
    return users_df.loc[users_df['id'] == user_id, :]
