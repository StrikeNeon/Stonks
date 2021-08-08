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

    def setup_symbol(self, symbol: str, start_data: dict):
        added_symbol = self.room_collection.insert_one({"symbol_name": symbol,
                                                        "candlestick_data": start_data,
                                                        "sma_data": [],
                                                        "ema_data": [],
                                                        "rsi_data": []
                                                        }).inserted_id
        self.db_logger.info(f"added new symbol record for {symbol} at {added_symbol}")
        return added_symbol

    def add_symbol_tick(self, symbol: str, data_tick: dict):

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