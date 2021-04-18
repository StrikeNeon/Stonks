from datetime import datetime
from utils import setup_dirs
from data_sink import get_history_data, get_live_data_yahoo
from plotter import plot_closing, plot_sma, plot_SMAC_signals
from computation import compute_returns, compute_monthly_returns
from strata import SMAC

setup_dirs()

# historical data
# aapl = get_history_data('AAPL', datetime(2020, 3, 31),
#                         datetime(2021, 3, 31), source="yahoo")
# print(aapl)

# print(compute_returns(aapl))
# print(compute_monthly_returns(aapl))
# sma = [50, 120]
# plot_closing(aapl, "AAPL 1/10/17 - 8/1/19", sma, ewma=True)
# plot_sma(aapl, 50)
# signals = SMAC(aapl)
# plot_SMAC_signals(aapl, signals)

#live data
aapl_L = get_live_data_yahoo('AAPL')
print(aapl_L)
sma = [5, 12]
plot_closing(aapl_L, "AAPL today", sma=sma, ewma=False)
plot_sma(aapl_L, 5, live=True)
signals = SMAC(aapl_L, windows=sma)
print(signals)
plot_SMAC_signals(aapl_L, signals)
