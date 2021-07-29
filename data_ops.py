# Raw Package
import numpy as np
import pandas as pd

# Data Source
import yfinance as yf


def download_symbol():
    # Get Bitcoin data
    data = yf.download(tickers='BTC-USD', period='2h', interval='15m')
    return data


def get_sma(data):
    short_rolling = data.rolling(window=15).mean()
    long_rolling = data.rolling(window=60).mean()
    return short_rolling, long_rolling


def get_ema(data):
    ema_short = data.ewm(span=15, adjust=False).mean()
    return ema_short
