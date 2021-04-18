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


def cached_scalp(data: DataFrame, bands: tuple):
    """compares latest closing price and latest moving avg
       1 is a positive signal of a rising value, sell
       0 is a signal that the value is higher than 20 min avg,
         but not higher than the upper bollinger band, so hold
       -1 is warning signal - this means the value is falling,
         buy if you have spare allocated bank % and if fall signal number in
         cache is not above panic sell level"""
    panic = False
    current_closing = data["Close"].iloc[-1]
    current_upper_band = bands[1].iloc[-1]
    current_middle_band = bands[1].iloc[-1]
    current_lower_band = bands[1].iloc[-1]
    if current_closing > current_upper_band:
        signal = 1
    if current_closing > current_middle_band and \
       current_closing < current_upper_band:
        signal = 0
    if current_closing < current_lower_band:
        signal = -1
    return signal, panic
