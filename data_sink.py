import pandas as pd
from pandas.core.frame import DataFrame
import pandas_datareader as pdr
from datetime import datetime


def get_history_data_yahoo(symbol: str, start_date: datetime, end_date: datetime):
    data = pdr.get_data_yahoo(symbol,
                              start=start_date,
                              end=end_date)
    return data


def save_data(data: DataFrame, filename: str):
    data.to_csv(filename)


def load_from_csv(filename: str, index: str = 'Date'):
    df = pd.read_csv(f'data/{filename}', header=0,
                     index_col=index, parse_dates=True)
    return df
