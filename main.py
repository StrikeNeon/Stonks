from datetime import datetime
from utils import setup_dirs
from data_sink import get_history_data, get_live_data_yahoo
from plotter import plot_closing, plot_sma, plot_SMAC_signals
from computation import (compute_returns, compute_monthly_returns,
                         compute_sma)
from strata import SMAC, advanced_scalp

setup_dirs()


def history_test():
    # historical data
    aapl = get_history_data('AAPL', datetime(2020, 3, 31),
                            datetime(2021, 3, 31), source="yahoo")
    print(aapl)
    print(compute_returns(aapl))
    print(compute_monthly_returns(aapl))
    sma = [50, 120]
    plot_closing(aapl, "AAPL 1/10/17 - 8/1/19", sma, ewma=True)
    plot_sma(aapl, 50)
    signals = SMAC(aapl)
    plot_SMAC_signals(aapl, signals)


def live_test():
    # live data
    aapl_L = get_live_data_yahoo('AAPL', period="20m", interval="1m")
    print(aapl_L)
    sma_l = [20]
    plot_closing(aapl_L, "AAPL today", sma=sma_l)
    # plot_sma(aapl_L, window=20, live=True)


def scalp_test(symbol: str = 'AAPL',
               start_value: int = 5000,
               start_stocks: int = 5,
               data_index: str = "Adj Close"):
    live_data = get_live_data_yahoo(symbol, period="20m", interval="1m")
    sma = compute_sma(live_data, window=20)
    print(f"current value {live_data[data_index].iloc[-1]}")
    print(f"sma: {sma.iloc[-1]}")
    signal = advanced_scalp(live_data, sma)
    if signal == 0:
        sell_value = None
    elif signal == 2:
        sell_value = live_data[data_index].iloc[0] * 1.010
    elif signal == 1:
        sell_value = live_data[data_index].iloc[0] * 1.007
    print(f"signal: {signal}")
    if sell_value:
        print(f"value bought: {live_data[data_index].iloc[0]},\
               value sold: {sell_value}")
        start_value += sell_value * start_stocks
        start_value -= live_data[data_index].iloc[-1] * start_stocks
    else:
        if live_data[data_index].iloc[0] > live_data[data_index].iloc[-1]:
            start_value -= (live_data[data_index].iloc[0]
                            - live_data[data_index].iloc[-1]) * start_stocks
        elif live_data[data_index].iloc[0] < live_data[data_index].iloc[-1]:
            start_value += (live_data[data_index].iloc[0]
                            - live_data[data_index].iloc[-1]) * start_stocks

    print(f"total value: {start_value}")


live_test()
scalp_test()
