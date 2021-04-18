from datetime import datetime
from utils import setup_dirs
from data_sink import get_history_data, get_live_data_yahoo
from plotter import plot_closing, plot_sma, plot_SMAC_signals
from computation import compute_returns, compute_monthly_returns, compute_sma
from strata import SMAC, scalp

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
    plot_closing(aapl_L, "AAPL today", sma=sma_l, ewma=False, bbands=False)
    # plot_sma(aapl_L, window=20, live=True)
    sma = compute_sma(aapl_L, 20)
    print(scalp(aapl_L, sma))


live_test()
