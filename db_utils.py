from pandas import DataFrame, date_range
import numpy as np
from pymongo import MongoClient, ReturnDocument
import loguru
from pydantic import BaseModel
from typing import Optional
from zigzag import peak_valley_pivots
from data_ops import technical_indicators, binance_api
from fastapi.security import OAuth2PasswordBearer
from passlib.exc import UnknownHashError
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import timedelta, datetime
from settings import ALGORITHM, SECRET_KEY

indicators = technical_indicators()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class token(BaseModel):
    access_token: str
    token_type: str


class token_data(BaseModel):
    username: Optional[str] = None


class MongoManager():
    def __init__(self):
        self.active_clients = {}
        self.db_client = MongoClient('127.0.0.1:27017')

        self.db = self.db_client['stonks']
        self.symbols_collection = self.db['symbol_data']
        self.user_collection = self.db['client_data']

        self.db_logger = loguru.logger

    def get_password_hash(self, password: str):
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str):
        try:
            verification = pwd_context.verify(plain_password, hashed_password)
            return verification
        except UnknownHashError:
            return 403

    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return 403
        except JWTError:
            return 403
        user = self.user_collection.find_one({"username": username})
        if user is None:
            403
        return user

    def create_access_token(self, data: dict, expires_delta: timedelta = 24):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=12)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def register_client(self, client_data: dict):
        user_check = self.user_collection.find_one({"username": client_data.get("username")})
        if not user_check:
            # TODO encrypt keys and secrets, keep encryption keys local
            # (you need to encode those values before you send them,
            #  you get public keys from a speciffic rest endpoint)
            added = self.user_collection.insert_one({"username": client_data.get("username"),
                                                     "password": self.get_password_hash(client_data.get("password")),
                                                     "api_key": client_data.get("api_key"),
                                                     "api_secret": client_data.get("api_secret"),
                                                     "bank_data": {}}).inserted_id
            return added
        else:
            return None

    def add_client(self, client: str, password: str):
        queried_client = self.user_collection.find_one({"username": client})
        if queried_client:
            if self.verify_password(password, queried_client.get("password")) != 403:
                binance_client = binance_api(queried_client.get("api_key"), queried_client.get("api_secret"))
                # TODO encrypt keys and secrets, keep encryption keys local
                # (you need to encode those values before you send them,
                #  you get public keys from a speciffic rest endpoint, decoding with local private key happens here)
                self.active_clients[client] = binance_client
                return 200
            else:
                return 403
        else:
            return 404

    def setup_symbol(self, symbol: str, client: str):
        if client in self.active_clients.keys():
            self.symbols_collection.find_one_and_delete({"symbol_name": symbol})
            start_data = self.active_clients.get(client).get_current_data(symbol)
            added_symbol = self.symbols_collection.insert_one({"symbol_name": symbol,
                                                            "candlestick_data": start_data,
                                                            "sma_data": {},
                                                            "ema_data": [],
                                                            "rsi_data": []
                                                            }).inserted_id
            self.db_logger.info(f"added new symbol record for {symbol} at {added_symbol}")
            return 200
        else:
            return 403

    def get_current_data(self, symbol: str):
        current_data = self.symbols_collection.find_one({"symbol_name": symbol})
        if not current_data:
            return 404
        else:
            current_candlestick = current_data.get("candlestick_data")
            return current_candlestick

    def add_symbol_tick(self, symbol: str, client: str, interval: int):
        if client in self.active_clients.keys():
            current_data = self.symbols_collection.find_one({"symbol_name": symbol})
            if not symbol:
                return 404
            else:
                candlestick_data = current_data.get("candlestick_data")
                data_tick = self.active_clients.get(client).get_data_tick(symbol, interval)
                candlestick_data.extend(data_tick)
            updated_data = self.symbols_collection.find_one_and_update({"symbol_name": symbol}, {"$set": {"candlestick_data": candlestick_data}}, return_document=ReturnDocument.AFTER)
            return updated_data.get("candlestick_data")
        return 403

    def recount_sma(self, symbol: str):
        current_data = self.symbols_collection.find_one({"symbol_name": symbol})
        if not current_data:
            return 404
        else:
            short_rolling, long_rolling = indicators.get_sma(DataFrame(current_data.get("candlestick_data")))
            current_sma = self.symbols_collection.find_one_and_update({"symbol_name": symbol},
                                                             {"$set": {"sma_data": {"short_rolling": short_rolling.tolist(),
                                                                                    "long_rolling": long_rolling.tolist()}}}, return_document=ReturnDocument.AFTER)
            return current_sma.get("sma_data")

    def recount_ema(self, symbol: str):
        current_data = self.symbols_collection.find_one({"symbol_name": symbol})
        if not current_data:
            return 404
        else:
            ema = indicators.get_ema(DataFrame(current_data.get("candlestick_data")))
            current_ema = self.symbols_collection.find_one_and_update({"symbol_name": symbol},
                                                             {"$set": {"ema_data": ema.tolist()}}, return_document=ReturnDocument.AFTER)
            return current_ema.get("ema_data")

    def recount_rsi(self, symbol: str):
        current_data = self.symbols_collection.find_one({"symbol_name": symbol})
        if not current_data:
            return 404
        else:
            rsi = indicators.get_rsi(DataFrame(current_data.get("candlestick_data")))
            current_rsi = self.symbols_collection.find_one_and_update({"symbol_name": symbol},
                                                             {"$set": {"rsi_data": rsi.tolist()}}, return_document=ReturnDocument.AFTER)
            return current_rsi.get("rsi_data")

    def recount_bbands(self, symbol: str):
        current_data = self.symbols_collection.find_one({"symbol_name": symbol})
        if not current_data:
            return 404
        else:
            sma = indicators.get_sma(DataFrame(current_data.get("candlestick_data")))[1]
            upper_bb, lower_bb = indicators.get_bollinger_bands(DataFrame(current_data.get("candlestick_data")), sma, 20)
            current_rsi = self.symbols_collection.find_one_and_update({"symbol_name": symbol},
                                                             {"$set": {"bband_data":{"upper_bb": upper_bb.tolist(),
                                                                                     "lower_bb": lower_bb.tolist()}}}, return_document=ReturnDocument.AFTER)
            return current_rsi.get("bband_data")

    def recount_pivots(self, symbol: str):
        current_data = self.symbols_collection.find_one({"symbol_name": symbol})
        if not current_data:
            return 404
        else:
            current_dataframe = DataFrame(current_data.get("candlestick_data"))
            current_time = datetime.now()
            start_time = current_time - timedelta(minutes=len(current_dataframe.index))
            date_times = []
            while start_time < current_time:
                start_time += timedelta(minutes=1)
                date_times.append(start_time)
            # dates = date_range(current_time, start_time, freq='M').tolist() # TODO Fix - add proper minute interval generation
            current_dataframe.index = date_times
            pivots = peak_valley_pivots(current_dataframe['close'].values, 0.1, -0.1)
            pivots = [pivot*-1 for pivot in pivots.tolist()]
            current_pivots = self.symbols_collection.find_one_and_update({"symbol_name": symbol},
                                                             {"$set": {"pivot_data": pivots}}, return_document=ReturnDocument.AFTER)
            return current_pivots.get("pivot_data")

    def recount_last_day(self, symbol: str):

        pass

    def recount_last_week(self, symbol: str):

        pass

    def get_sma_cross_signal(self, symbol: str):
        current_data = self.get_current_data(symbol)
        if current_data == 404:
            return 404
        else:
            s_sma_data = self.recount_sma(symbol).get("short_rolling")
            l_sma_data = self.recount_sma(symbol).get("long_rolling")
            last_data, last_s_sma_data, last_l_sma_data = float(current_data[-1].get("close")), s_sma_data[-1], l_sma_data[-1]
            if last_s_sma_data == last_l_sma_data and last_l_sma_data < last_data:
                return 1
            elif last_s_sma_data == last_l_sma_data and last_l_sma_data > last_data:
                return -1
            else:
                return 0

    def get_sma_signal(self, symbol: str, thresh: int):
        current_data = self.get_current_data(symbol)
        if current_data == 404:
            return 404
        else:
            rsi = indicators.get_rsi(DataFrame(current_data))
            last_rsi = rsi.tolist()[-1]
            s_sma_data = self.recount_sma(symbol).get("short_rolling")
            l_sma_data = self.recount_sma(symbol).get("long_rolling")
            last_data, last_s_sma_data, last_l_sma_data = float(current_data[-1].get("close")), s_sma_data[-1], l_sma_data[-1]
            if last_s_sma_data < last_data and last_rsi > rsi.max()-rsi.max()//thresh:
                return 1
            elif last_l_sma_data > last_data and last_rsi < rsi.max()//thresh:
                return -1
            else:
                return 0

    def get_bbands_signal(self, symbol: str):
        current_data = self.get_current_data(symbol)
        if current_data == 404:
            return 404
        else:
            bbands = self.recount_bbands(symbol)
            upper_bb_data = bbands.get("upper_bb")
            lower_bb_data = bbands.get("lower_bb")
            last_data, last_upper_bb_data, last_lower_bb_data = float(current_data[-1].get("close")), upper_bb_data[-1], lower_bb_data[-1]
            if last_data > last_upper_bb_data:
                return 1
            elif last_data < last_lower_bb_data:
                return -1
            else:
                return 0

    def get_pivot_signal(self, symbol: str):
        current_data = self.get_current_data(symbol)
        if current_data == 404:
            return 404
        else:
            pivots = self.recount_pivots(symbol)
            last_pivot = pivots[-1]
            return last_pivot

    def signal_map(self, data, pivot, s_sma, l_sma, rsi, upper_bb, lower_bb, rsi_max, thresh):
        if pivot == 1:
            return 1
        elif pivot == -1:
            return -1
        elif data > upper_bb:
            return 1
        elif s_sma > upper_bb and rsi > rsi_max-rsi_max//thresh:
            return 1
        elif data < lower_bb:
            return -1
        elif l_sma < upper_bb and rsi < rsi_max//thresh:
            return -1
        else:
            return 0

    def get_signal_frame(self, symbol: str, thresh: int):
        current_data = self.get_current_data(symbol)
        if current_data == 404:
            return 404
        else:
            candlestick_closing = DataFrame(current_data)["close"].tolist()
            tech_data = self.symbols_collection.find_one({"symbol_name": symbol})
            sma = tech_data.get("sma_data")
            short_rolling, long_rolling = sma.get("short_rolling"), sma.get("long_rolling")
            rsi = tech_data.get("rsi_data")
            bbands = tech_data.get("bband_data")
            upper_bb, lower_bb = bbands.get("upper_bb"), bbands.get("lower_bb")

            max_rsi = max(rsi)
            pivots = self.recount_pivots(symbol)
            if len(short_rolling) != len(candlestick_closing) or len(pivots) != len(candlestick_closing):
                return 500
            signals = []
            for row in candlestick_closing:
                index = candlestick_closing.index(row)
                signal = self.signal_map(row, pivots[index], short_rolling[index], long_rolling[index], rsi[index], upper_bb[index], lower_bb[index], max_rsi, thresh)
                signals.append(signal)
            return signals

    def write_last_signal(self, symbol: str, rsi_thresh: int):
        sma = self.get_sma_signal(symbol, rsi_thresh)
        bbands = self.get_bbands_signal(symbol)
        if sma == 404 or bbands == 404:
            self.symbols_collection.find_one_and_update({"symbol_name": symbol},
                                                         {"$set": {"sma_sig": sma, "bbands_sig": bbands}})

    def sync_banks(self, symbol: str, client: str):
        if client not in self.active_clients.keys():
            return 403
        bank_data = self.active_clients.get(client).get_symbol_balance(symbol=symbol)
        self.db_logger.debug(f"symbol bank: {bank_data}")
        return bank_data

    def account_status(self, client: str):
        if client not in self.active_clients.keys():
            return 403, None
        status_data = self.active_clients.get(client).get_account_status()
        trade_status_data = self.active_clients.get(client).get_client_trading_status()
        return status_data, trade_status_data

    def get_all_fees(self, client: str):
        if client not in self.active_clients.keys():
            return 403
        fees_data = self.active_clients.get(client).get_fees()
        return fees_data

    def make_test_order(self, client: str, symbol: str, quantity: float, price: float, op_code: int):
        if client not in self.active_clients.keys():
            return 403
        result = self.active_clients.get(client).make_test_order(symbol, quantity, price, op_code)
        return result

    def banking_operate_on_symbol(self, symbol: str, value: float,  client: str, op_code: int):
        """opcode 1 is addition, 0 is substraction"""
        current_value = self.user_collection.find_one({"username": client}).get("bank_data")
        if not current_value:
            current_value = {symbol: value}
            added_value = self.user_collection.find_one_and_update({"username": client},
                                                                   {"$set": {"bank_data": current_value}},
                                                                   return_document=ReturnDocument.AFTER)
            return added_value.get("bank_data").get(symbol)
        if current_value.get(symbol):
            if op_code == 1:
                new_value = (current_value.get(symbol) + value)
            else:
                if current_value.get(symbol) - value < 0:
                    return
                else:
                    new_value = (current_value.get(symbol) - value)
            current_value[symbol] = new_value
            added_value = self.user_collection.find_one_and_update({"username": client},
                                                                   {"$set": {"bank_data": current_value}},
                                                                   return_document=ReturnDocument.AFTER)
            return added_value.get("bank_data").get(symbol)
        else:
            current_value[symbol] = value
            added_value = self.user_collection.find_one_and_update({"username": client},
                                                                   {"$set": {"bank_data": current_value}},
                                                                   return_document=ReturnDocument.AFTER)
            return added_value.get("bank_data").get(symbol)
