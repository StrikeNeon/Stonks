from pandas.core.frame import DataFrame
import matplotlib.pyplot as plt
from computation import compute_sma, compute_ewma, compute_bollinger_bands


def plot_closing(data: DataFrame, title: str,
                 sma: list = None, ewma: bool = False,
                 bbands: bool = False, data_index: str = "Adj Close"):
    save_state = data  # not to skrew with the actual data
    plt.figure(figsize=(10, 10))
    plt.plot(save_state.index, save_state[data_index], label="Closing price")
    if sma:
        for item in sma:
            save_state[f"SMA{sma.index(item)}"] = compute_sma(data, item)
            plt.plot(save_state[f"SMA{sma.index(item)}"],
                     'r--', label=f"SMA {item}")
    if ewma:
        save_state["EWMA"] = compute_ewma(data)
        plt.plot(save_state["EWMA"], 'g--', label="EWMA")
    if bbands:
        (save_state['upper_band'],
         save_state['middle_band'],
         save_state['lower_band']) = compute_bollinger_bands(data)
        plt.plot(save_state['upper_band'], 'c--', label="upper band")
        plt.plot(save_state['middle_band'], 'm--', label="middle band")
        plt.plot(save_state['lower_band'], 'y--', label="lower band")
    plt.xlabel("date")
    plt.ylabel("$ price")
    plt.title(title)
    plt.legend()
    plt.show()


def plot_sma(data: DataFrame, window: int = 50, live: bool = False):
    sma = compute_sma(data, window)
    plt.figure(figsize=(10, 10))
    plt.plot(sma.index, sma,
             label=f"{window} day window" if not live
             else f"{window} minute window")
    plt.xlabel("date")
    plt.ylabel("$ price")
    plt.title(f"{window} day window" if not live
              else f"{window} minute window")
    plt.legend()
    plt.show()


def plot_SMAC_signals(data: DataFrame,
                      signals: DataFrame, data_index: str = "Adj Close"):
    fig = plt.figure()
    plt1 = fig.add_subplot(111,  ylabel='$ price')
    data[data_index].plot(ax=plt1, color='r', lw=2.)
    signals[['short_mav', 'long_mav']].plot(ax=plt1, lw=2., figsize=(12, 8))
    plt1.plot(signals.loc[signals.positions == -1.0].index,
              signals.short_mav[signals.positions == -1.0],
              'v', markersize=10, color='k')

    plt1.plot(signals.loc[signals.positions == 1.0].index,
              signals.short_mav[signals.positions == 1.0],
              '^', markersize=10, color='m')

    plt.show()
