from pandas.core.frame import DataFrame


def compute_sma(data: DataFrame, window: int, data_index: str = "Adj Close"):
    sma = data[data_index].rolling(window=window,
                                   min_periods=1,
                                   center=False).mean()
    return sma


def compute_ewma(data: DataFrame, data_index: str = "Adj Close"):
    ewma = data[data_index].ewm(halflife=0.5, min_periods=20).mean()
    return ewma


def compute_bollinger_bands(data: DataFrame, data_index: str = "Adj Close"):
    middle_band = data[data_index].rolling(window=20).mean()
    upper_band = data[data_index].rolling(window=20).mean() + \
        data[data_index].rolling(window=20).std()*2
    lower_band = data[data_index].rolling(window=20).mean() - \
        data[data_index].rolling(window=20).std()*2

    return upper_band, middle_band, lower_band


def compute_returns(data: DataFrame, data_index: str = "Adj Close"):
    returns = data[data_index].pct_change()
    returns.fillna(0, inplace=True)
    return returns


def compute_monthly_returns(data: DataFrame):
    mdata = data.resample('M').apply(lambda x: x[-1])
    monthly_return = mdata.pct_change()
    return monthly_return
