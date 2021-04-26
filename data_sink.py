import pandas as pd
from pandas.core.frame import DataFrame
from pandas_datareader import data as data_reader
from datetime import datetime
import yfinance as yf


def get_history_data(symbol: str, start_date: datetime,
                     end_date: datetime, source: str = "yahoo"):
    data = data_reader.DataReader(symbol,
                                  start=start_date,
                                  end=end_date,
                                  data_source=source)
    return data


def get_live_data_yahoo(symbol: str, period: str = "1d", interval: str = "5m"):
    data = yf.download(tickers=symbol, period=period, interval=interval)
    return data


def save_data(data: DataFrame, filename: str):
    data.to_csv(f'data/{filename}')


def load_from_csv(filename: str, index: str = 'Date'):
    df = pd.read_csv(f'data/{filename}', header=0,
                     index_col=index, parse_dates=True)
    return df
