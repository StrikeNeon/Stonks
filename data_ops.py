# Raw Package
import numpy as np
import pandas as pd

# Data Source
import yfinance as yf


def download_symbol():
    # Get Bitcoin data
    data = yf.download(tickers='BTC-USD', period='2h', interval='1m')
    return data


def get_sma(data):
    short_rolling = data.rolling(window=20).mean()
    long_rolling = data.rolling(window=40).mean()
    short_rolling.fillna(0, inplace=True), long_rolling.fillna(0, inplace=True)
    print(long_rolling)
    return short_rolling, long_rolling


def get_ema(data):
    ema_short = data.ewm(span=15, adjust=False).mean()
    return ema_short
