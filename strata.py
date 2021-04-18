from computation import compute_sma
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
from pandas.core.series import Series


def SMAC(data: DataFrame, windows: list = [50, 120]):
    short_lb, long_lb = windows[0], windows[1]
    signal_df = pd.DataFrame(index=data.index)
    signal_df['signal'] = 0.0
    signal_df['short_mav'] = compute_sma(data, short_lb)
    signal_df['long_mav'] = compute_sma(data, long_lb)
    signal_df['signal'][short_lb:] =\
        np.where(signal_df['short_mav'][short_lb:] >
                 signal_df['long_mav'][short_lb:], 1.0, 0.0)
    signal_df['positions'] = signal_df['signal'].diff()
    signal_df[signal_df['positions'] == -1.0]
    return signal_df


def scalp(data: DataFrame, sma: Series):
    # compares latest closing price and latest moving avg
    # returns true if closing price is above mav
    current_closing = data["Close"].iloc[-1]
    current_mav = sma.iloc[-1]
    if current_closing > current_mav:
        return True
    return False
