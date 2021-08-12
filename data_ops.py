# Raw Package
import pandas as pd
import numpy as np

# Data Source
from binance.client import Client


class binance_api():
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)

    def get_all_symbols(self):
        exchange_info = self.client.get_exchange_info()
        symbols = [symbol['symbol'] for symbol in exchange_info['symbols']]
        return symbols

    def get_current_data(self, symbol):
        raw_data = self.client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=60)
        data = [{"open": float(record[1]),
                 "high": float(record[2]),
                 "low": float(record[3]),
                 "close": float(record[4]),
                 "volume": float(record[5]),
                 "trades": float(record[7]),
                 "taker_buy_base": float(record[8]),
                 "taker_buy_quote": float(record[9])} for record in raw_data]
        return data

    def get_data_tick(self, symbol):
        raw_data = self.client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=1)
        data = [{"open": float(record[1]),
                 "high": float(record[2]),
                 "low": float(record[3]),
                 "close": float(record[4]),
                 "volume": float(record[5]),
                 "trades": float(record[7]),
                 "taker_buy_base": float(record[8]),
                 "taker_buy_quote": float(record[9])} for record in raw_data]
        return data

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

# TODO Make banker class
# subclass binance api, inherit client data


class binance_banker(binance_api):
    def __init__(self):
        super().__init__()

    def make_test_order(self):

        pass

    def query_order(self):

        pass

    def cancel_order(self):

        pass

    def cancel_all_symbol_order(self):

        pass

    def recount_bank(self):

        pass

    def adjust_bank_value(self):

        pass





class technical_indicators():

    def get_sma(self, data):
        short_rolling = data["close"].rolling(window=20).mean()
        long_rolling = data["close"].rolling(window=40).mean()
        return short_rolling, long_rolling

    def get_ema(self, data):
        ema_short = data["close"].ewm(span=15, adjust=False).mean()
        return ema_short

    def rma(self, x, n, y0):
        a = (n-1) / n
        ak = a**np.arange(len(x)-1, -1, -1)
        return np.r_[np.full(n, np.nan), y0, np.cumsum(ak * x) / ak / n + y0 * a**np.arange(1, len(x)+1)]

    def get_rsi(self, data, periods=14, ema=True):
        """
        Returns a pd.Series with the relative strength index.
        """
        # close_delta = data["close"].diff()

        # Make two series: one for lower closes and one for higher closes

        data['change'] = data['close'].diff()
        data['gain'] = data.change.mask(data.change < 0, 0.0)
        data['loss'] = -data.change.mask(data.change > 0, -0.0)
        data['avg_gain'] = self.rma(data.gain[periods+1:].to_numpy(), periods, np.nansum(data.gain.to_numpy()[:periods+1])/periods)
        data['avg_loss'] = self.rma(data.loss[periods+1:].to_numpy(), periods, np.nansum(data.loss.to_numpy()[:periods+1])/periods)
        data['rs'] = data.avg_gain / data.avg_loss
        data['rsi_14'] = 100 - (100 / (1 + data.rs))
        return data['rsi_14']
