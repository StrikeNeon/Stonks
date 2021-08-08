# Raw Package
import pandas as pd

# Data Source
from binance.client import Client


class binance_api():
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)

    def get_current_data(self, symbol):
        raw_data = self.client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=60)
        data = [{"open": record[1],
                 "high": record[2],
                 "low": record[3],
                 "close": record[4],
                 "volume": record[5],
                 "trades": record[7],
                 "taker_buy_base": record[8],
                 "taker_buy_quote": record[9]} for record in raw_data]
        dataframe = pd.DataFrame(data)
        return dataframe

    def get_data_tick(self, symbol):
        raw_data = self.client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=1)
        data = [{"open": record[1],
                 "high": record[2],
                 "low": record[3],
                 "close": record[4],
                 "volume": record[5],
                 "trades": record[7],
                 "taker_buy_base": record[8],
                 "taker_buy_quote": record[9]} for record in raw_data]
        dataframe = pd.DataFrame(data)
        return dataframe

    def get_last_day(self, symbol):
        raw_data = self.client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, limit=24)
        data = [{"open": record[1],
                 "high": record[2],
                 "low": record[3],
                 "close": record[4],
                 "volume": record[5],
                 "trades": record[7],
                 "taker_buy_base": record[8],
                 "taker_buy_quote": record[9]} for record in raw_data]
        dataframe = pd.DataFrame(data)
        return dataframe

    def get_two_week_history(self, symbol):
        raw_data = self.client.get_historical_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1DAY, limit=14, start_str='2 weeks ago UTC')
        data = [{"open": record[1],
                 "high": record[2],
                 "low": record[3],
                 "close": record[4],
                 "volume": record[5],
                 "trades": record[7],
                 "taker_buy_base": record[8],
                 "taker_buy_quote": record[9]} for record in raw_data]
        dataframe = pd.DataFrame(data)
        return dataframe

    def add_data_tick(self, base_dataframe, data_tick):
        base_dataframe = base_dataframe.append(data_tick, ignore_index=True)
        return base_dataframe


class technical_indicators():

    def get_sma(data):
        short_rolling = data["close"].rolling(window=10).mean()
        long_rolling = data["close"].rolling(window=20).mean()
        return short_rolling, long_rolling

    def get_ema(data):
        ema_short = data["close"].ewm(span=15, adjust=False).mean()
        return ema_short

    def get_rsi(data, periods=14, ema=True):
        """
        Returns a pd.Series with the relative strength index.
        """
        # close_delta = data["close"].diff()

        # Make two series: one for lower closes and one for higher closes
        up = data["high"]
        down = data["low"]
        if ema:
            # Use exponential moving average
            ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
            ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
        else:
            # Use simple moving average
            ma_up = up.rolling(window=periods, adjust=False).mean()
            ma_down = down.rolling(window=periods, adjust=False).mean()  
        rsi = ma_up / ma_down
        rsi = 100 - (100/(1 + rsi))
        return rsi
