from datetime import datetime
from utils import setup_dirs
from data_sink import get_history_data_yahoo
from plotter import plot_closing, plot_sma, plot_SMAC_signals
from computation import compute_returns, compute_monthly_returns
from strata import SMAC

setup_dirs()
aapl = get_history_data_yahoo('AAPL', datetime(2017, 10, 1),
                              datetime(2019, 1, 1))
print(aapl)

print(compute_returns(aapl))
print(compute_monthly_returns(aapl))

# Plot the closing prices for `aapl`
sma = [50, 120]
plot_closing(aapl, "AAPL 1/10/17 - 8/1/19", sma, ewma=True)
#plot_sma(aapl, 50)
signals = SMAC(aapl)
plot_SMAC_signals(aapl, signals)
