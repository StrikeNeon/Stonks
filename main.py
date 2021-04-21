from datetime import datetime
import asyncio
from utils import setup_dirs
from data_sink import get_history_data, get_live_data_yahoo
from plotter import plot_closing, plot_sma, plot_SMAC_signals
from computation import (compute_returns, compute_monthly_returns,
                         compute_sma)
from strata import SMAC, scalp
from trade import buy_sell_proto
from time import sleep


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
               bank_value: int = 5000,
               start_stocks: int = 5,
               data_index: str = "Adj Close"):
    live_data = get_live_data_yahoo(symbol, period="20m", interval="1m")
    sma = compute_sma(live_data, window=20)

    current_value = live_data[data_index].iloc[-1]
    start_value = live_data[data_index].iloc[0]
    signal = scalp(live_data, sma)
    if signal == 0:
        sell_value = None
    elif signal == 1:
        sell_value = current_value * 1.007
    if sell_value:
        bank_value = buy_sell_proto(bank_value, current_value,
                                    sell_value, start_stocks)
    else:
        if start_value > current_value:
            bank_value -= (start_value
                           - current_value) * start_stocks
        elif start_value < current_value:
            bank_value += (start_value
                           - current_value) * start_stocks

    return (start_value,  current_value, sma.iloc[-1],
            signal, sell_value, bank_value)


# live_test()
def trade_routine(symbols: dict):
    hours = 3
    report = {key: {"start_value": None,
                    "current_value": None,
                    "current_sma": None,
                    "signal": None,
                    "sell_value": None,
                    "bank_value": value["allocated_bank"]}
              for key, value in symbols.items()}
    for i in range(hours*3):
        for symbol in symbols.keys():
            if report[symbol]["bank_value"] > symbols[symbol]["allocated_bank"]-(symbols[symbol]["allocated_bank"]//symbols[symbol]["stop_thresh"]):
                (report[symbol]["start_value"],
                 report[symbol]["current_value"],
                 report[symbol]["current_sma"],
                 report[symbol]["signal"],
                 report[symbol]["sell_value"],
                 report[symbol]["bank_value"]) = scalp_test(symbol=symbol,
                                                            bank_value=report[symbol]["bank_value"],
                                                            start_stocks=symbols[symbol]["start_stocks"])
                print(f"""{report[symbol]} report:
                            current value {report[symbol]['current_value']}
                            sma: {report[symbol]['current_sma']}
                            signal: {report[symbol]['signal']}
                            value bought: {report[symbol]['start_value']}, value sold: {report[symbol]['sell_value']}
                            total value: {report[symbol]['bank_value']}""")
                print("sleeping")
                sleep(60*20)  # sleep for 20 minutes
            else:
                print(f"bank fell below threshold for {symbol}")
                print(f"""{report[symbol]} report:
                            current value {report[symbol]['current_value']}
                            sma: {report[symbol]['current_sma']}
                            signal: {report[symbol]['signal']}
                            value bought: {report[symbol]['start_value']}, value sold: {report[symbol]['sell_value']}
                            total value: {report[symbol]['bank_value']}""")


symbols = {"AAPL": {"allocated_bank": 1000, "start_stocks": 10, "stop_thresh": 10},
           "UBER": {"allocated_bank": 1500, "start_stocks": 5, "stop_thresh": 10}
           }
trade_routine(symbols)
