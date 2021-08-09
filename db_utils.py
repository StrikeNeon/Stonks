from pandas import DataFrame
from pymongo import MongoClient, ReturnDocument
import loguru
from data_ops import technical_indicators


class MongoManager():
    def __init__(self):
        self.db_client = MongoClient('127.0.0.1:27017')

        self.db = self.db_client['stonks']
        self.symbols_collection = self.db['symbol_data']
        self.user_collection = self.db['client_data']

        self.db_logger = loguru.logger

    def setup_symbol(self, symbol: str, start_data: dict):
        added_symbol = self.room_collection.insert_one({"symbol_name": symbol,
                                                        "candlestick_data": start_data,
                                                        "sma_data": {},
                                                        "ema_data": [],
                                                        "rsi_data": []
                                                        }).inserted_id
        self.db_logger.info(f"added new symbol record for {symbol} at {added_symbol}")
        return added_symbol

    def add_symbol_tick(self, symbol: str, data_tick: dict):
        current_data = self.symbols_collection.find_one({"symbol_name":symbol})
        if not symbol:
            return 404
        else:
            current_candlestick = current_data.get("candlestick_data")
            current_candlestick = {key: value.extend(data_tick.get(key)) for key, value in current_candlestick.items()}
        updated_data = self.symbols_collection.update_one({"symbol_name": symbol}, {"$set": {"candlestick_data": current_candlestick}})
        return updated_data

    def recount_sma(self, symbol: str, short_rolling: list, long_rolling: list):
        current_data = self.symbols_collection.find_one({"symbol_name":symbol})
        if not current_data:
            return 404
        else:
            current_sma = self.symbols_collection.update_one({"symbol_name": symbol},
                                                             {"$set": {"sma_data": {"short_rolling": short_rolling,
                                                                                    "long_rolling": long_rolling.}}})
            return current_sma

    def recount_ema(self, symbol: str, ema: list):
        current_data = self.symbols_collection.find_one({"symbol_name":symbol})
        if not current_data:
            return 404
        else:
            current_ema = self.symbols_collection.update_one({"symbol_name": symbol},
                                                             {"$set": {"ema_data": ema}})
            return current_ema

    def recount_rsi(self, symbol: str, rsi: list):
        current_data = self.symbols_collection.find_one({"symbol_name":symbol})
        if not current_data:
            return 404
        else:
            current_rsi = self.symbols_collection.update_one({"symbol_name": symbol},
                                                             {"$set": {"rsi_data": "rsi": rsi}})
            return current_rsi

    def record_last_day(self, symbol: str, last_day_data: list):

        pass

    def recount_last_week(self, symbol: str, last_week_data: list):

        pass