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


def scalp(data: DataFrame,
          sma: Series,
          index: str = "Adj Close"):
    """ basic scalping method
        0 is a hold signal
        1 is a signal to sell with normal profit %"""
    current_closing = data[index].iloc[-1]
    current_mav = sma.iloc[-1]
    if current_closing > current_mav:
        signal = 1
    else:
        signal = 0
    return signal


def banded_scalp(data: DataFrame,
                 sma: Series,
                 data_index: str = "Adj Close"):
    """ compares latest closing price and bollinger bands
        0 is a hold signal
        1 is a signal to sell with normal profit %
        2 is a signal to sell with increased profit %"""
    current_closing = data[data_index].iloc[-1]
    current_mav = sma.iloc[-1]
    if current_closing > current_mav:
        if (current_mav+(current_closing-current_mav)) > (current_mav+(current_closing-current_mav)) * 2:
            signal = 2
        else:
            signal = 1
    else:
        signal = 0
    return signal


# def day_trade(data: DataFrame,
#                  bands: tuple,
#                  data_index: str = "Adj Close"):
#     """ panic is a point where you dump it in concurrent price falls
#         compares latest closing price and latest moving avg
#         0 is a hold signal
#         1 is a buy signal
#         -1 is a sell signal
#         in case of a rising value, by upper band, hold is advised
#         if the value is higher than 20 min avg,
#             but not higher than the upper bollinger band, sell,
#             as it is unlikely to grow further
#         if the value is falling to a point of panic
#             (lower band being below start of day price),
#             sell it off to buy up later if it bounces back,
#             this will also renew cached value as it was effectively re-entry"""
#     panic = False
#     current_closing = data[data_index].iloc[-1]
#     current_upper_band = bands[1].iloc[-1]
#     current_middle_band = bands[1].iloc[-1]
#     current_lower_band = bands[1].iloc[-1]
#     start_of_day = 144.139999
#     if start_of_day > current_lower_band:
#         panic = True
#     if current_closing > current_upper_band:
#         if panic:
#             signal = 1
#         else:
#             signal = 0
#     elif (current_closing > current_middle_band
#           and current_closing < current_upper_band):
#         signal = -1
#     elif current_closing < current_lower_band:
#         if panic:
#             signal = -1
#         else:
#             signal = 0
#     return signal, panic
