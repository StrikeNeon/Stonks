from computation import compute_sma
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame


def SMAC(data: DataFrame , windows: list = [50, 120]):
    short_lb, long_lb = windows[0], windows[1]
    signal_df = pd.DataFrame(index=data.index)
    signal_df['signal'] = 0.0
    signal_df['short_mav'] = compute_sma(data, short_lb)
    signal_df['long_mav'] = compute_sma(data, long_lb)
    signal_df['signal'][short_lb:] = np.where(signal_df['short_mav'][short_lb:] > signal_df['long_mav'][short_lb:], 1.0, 0.0)
    signal_df['positions'] = signal_df['signal'].diff()
    signal_df[signal_df['positions'] == -1.0]
    print(signal_df)
    return signal_df
