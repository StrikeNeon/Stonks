from pymongo import MongoClient, ReturnDocument
import loguru
from data_ops import binance_api


class MongoManager():
    def __init__(self):
        self.client = MongoClient('127.0.0.1:27017')

        self.db = self.client['stonks']
        self.symbols_collection = self.db['symbol_data']
        self.user_collection = self.db['client_data']

        self.db_logger = loguru.logger

    def setup_symbol(self, symbol: str, start_data: list):

        pass

    def add_symbol_tick(self, symbol:str, data_tick: list):

        pass

    def recount_sma(self, symbol: str):

        pass

    def recount_ema(self, symbol: str):

        pass

    def recount_rsi(self, symbol: str):

        pass

    def record_last_day(self, symbol: str):

        pass

    def recount_last_week(self, symbol: str):

        pass