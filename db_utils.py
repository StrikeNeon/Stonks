from pandas import DataFrame
from pymongo import MongoClient, ReturnDocument
import loguru
from data_ops import technical_indicators, binance_api
from passlib.exc import UnknownHashError
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import timedelta, datetime
from settings import ALGORITHM, SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class MongoManager():
    def __init__(self):
        self.active_clients = {}
        self.db_client = MongoClient('127.0.0.1:27017')

        self.db = self.db_client['stonks']
        self.symbols_collection = self.db['symbol_data']
        self.user_collection = self.db['client_data']

        self.db_logger = loguru.logger

    def get_password_hash(self, password):
        return pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
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

    def create_access_token(self, data: dict, expires_delta: timedelta = 30):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def register_client(self, client_data):
        user_check = self.user_collection.find_one({"username": client_data.get("username")})
        if not user_check:
            # TODO encrypt keys and secrets, keep encryption keys local
            added = self.user_collection.insert_one({"username": client_data.get("username"),
                                                     "password": self.get_password_hash(client_data.get("password")),
                                                     "api_key": client_data.get("api_key"),
                                                     "api_secret": client_data.get("api_secret"),
                                                     "bank_data": {}})
            return added
        else:
            return None

    def add_client(self, client: str):
        queried_client = self.user_collection.find_one({"client_name": client})
        if queried_client:
            binance_client = binance_api(queried_client.get("api_key"), queried_client.get("api_secret"))
            # TODO encrypt keys and secrets, keep encryption keys local
            self.active_clients[client] = binance_client
            return self.active_clients[client]
        else:
            return 404

    def setup_symbol(self, symbol: str, client: str):
        if client in self.active_clients.keys():
            start_data = self.active_clients.get(client).get_current_data(symbol)
            added_symbol = self.room_collection.insert_one({"symbol_name": symbol,
                                                            "candlestick_data": start_data,
                                                            "sma_data": {},
                                                            "ema_data": [],
                                                            "rsi_data": []
                                                            }).inserted_id
            self.db_logger.info(f"added new symbol record for {symbol} at {added_symbol}")
            return added_symbol
        else:
            return 403

    def get_current_data(self, symbol: str):
        current_data = self.symbols_collection.find_one({"symbol_name": symbol})
        if not current_data:
            return 404
        else:
            current_candlestick = current_data.get("candlestick_data")
            return current_candlestick

    def add_symbol_tick(self, symbol: str, client: str):
        if client in self.active_clients:
            current_data = self.symbols_collection.find_one({"symbol_name": symbol})
            if not symbol:
                return 404
            else:
                candlestick_data = current_data.get("candlestick_data")
                data_tick = self.active_clients.get(client).get_data_tick(symbol)
                candlestick_data = [{key: value.extend(data_tick[0].get(key)) for key, value in current_candlestick.items()} for current_candlestick in candlestick_data]
            updated_data = self.symbols_collection.update_one({"symbol_name": symbol}, {"$set": {"candlestick_data": current_candlestick}})
            return updated_data.get("candlestick_data")
        return 403

    def recount_sma(self, symbol: str):
        current_data = self.symbols_collection.find_one({"symbol_name": symbol})
        if not current_data:
            return 404
        else:
            short_rolling, long_rolling = technical_indicators.get_sma(DataFrame(current_data.get("candlestick_data")))
            current_sma = self.symbols_collection.update_one({"symbol_name": symbol},
                                                             {"$set": {"sma_data": {"short_rolling": short_rolling.tolist(),
                                                                                    "long_rolling": long_rolling.tolist()}}})
            return current_sma.get("sma_data")

    def recount_ema(self, symbol: str):
        current_data = self.symbols_collection.find_one({"symbol_name": symbol})
        if not current_data:
            return 404
        else:
            ema = technical_indicators.get_ema(DataFrame(current_data.get("candlestick_data")))
            current_ema = self.symbols_collection.update_one({"symbol_name": symbol},
                                                             {"$set": {"ema_data": ema.tolist()}})
            return current_ema.get("ema_data")

    def recount_rsi(self, symbol: str, rsi: list):
        current_data = self.symbols_collection.find_one({"symbol_name": symbol})
        if not current_data:
            return 404
        else:
            rsi = technical_indicators.get_rsi(DataFrame(current_data.get("candlestick_data")))
            current_rsi = self.symbols_collection.update_one({"symbol_name": symbol},
                                                             {"$set": {"rsi_data": rsi.tolist()}})
            return current_rsi.get("rsi_data")

    def gather_data(self, symbol:str, client: str):

        pass

    def record_last_day(self, symbol: str, last_day_data: list):

        pass

    def recount_last_week(self, symbol: str, last_week_data: list):

        pass