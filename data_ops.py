# Raw Package
import numpy as np
import pandas as pd

# Data Source
import yfinance as yf


def download_symbol():
    # Get Bitcoin data
    data = yf.download(tickers='BTC-USD', period = '22h', interval = '15m')
    print(data.describe())
    return data


def get_sma(data):
    short_rolling = data.rolling(window=20).mean()
    long_rolling = data.rolling(window=100).mean()
    return short_rolling, long_rolling
