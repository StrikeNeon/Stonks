import pandas as pd
from pandas.core.frame import DataFrame
from pandas_datareader import data as data_reader
from datetime import datetime
import yfinance as yf


class abstract_eye():

    def __init__(self, source: str, symbol:str):
        self.source = source,
        self.symbol = symbol

    def get_history_data(self, start_date: datetime,
                         end_date: datetime, source: str = "yahoo"):
        data = data_reader.DataReader(symbol,
                                      start=start_date,
                                      end=end_date,
                                      data_source=source)
        return data

    def save_data(self, data: DataFrame, filename: str):
        data.to_csv(f'data/{filename}')

    def load_from_csv(self, filename: str, index: str = 'Date'):
        df = pd.read_csv(f'data/{filename}', header=0,
                        index_col=index, parse_dates=True)
        return df


class YF_eye(abstract_eye):
    def __init__(self, symbol: str):
        super.__init__(self, "yahoo", symbol)
        self.ticks = []

    def get_live_tick(self, symbol: str, period: str = "20m", interval: str = "1m"):
        data = yf.download(self.symbol, period=period, interval=interval)
        current_value = data["Adj Close"].iloc[-1]
        if self.ticks != [] or current_value != self.ticks[-1]:
            self.ticks.append(data)
            print("tick added")
        return data

    def get_ticks(self):
        return self.ticks
