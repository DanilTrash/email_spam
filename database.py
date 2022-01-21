from loguru import logger
import sqlite3

import pandas as pd


class PandasData:
    def __init__(self):
        self.dataframe = pd.read_excel('UAE.xlsx', sheet_name='Лист1')


class SqliteData:
    def __init__(self, database='email_spam_data.sqlite'):
        self.con = sqlite3.connect(database)
        self.cur = self.con.cursor()
