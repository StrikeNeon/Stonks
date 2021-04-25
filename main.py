from datetime import datetime
from pytz import timezone
from utils import setup_dirs, date_reset, recount_bank
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


#  TODO cache last closing to check for dupe data
def scalp_operation(symbol: str = 'AAPL',
                    bank_value: int = 500,
                    stock_u_limit: int = 10,
                    stock_l_limit: int = 1,
                    stock: int = 5,
                    data_index: str = "Adj Close"):
    live_data = get_live_data_yahoo(symbol, period="20m", interval="1m")
    sma = compute_sma(live_data, window=20)

    current_value = live_data[data_index].iloc[-1]
    start_value = live_data[data_index].iloc[0]
    signal = scalp(live_data, sma)
    if signal == 0:
        bank_value = recount_bank("hold signal recieved", bank_value,
                                  start_value, current_value, stock)
        sell_value = None
    if signal == 1:
        if stock >= stock_l_limit:
            bank_value = recount_bank("stocks at lower limit, nothing to sell",
                                      bank_value, start_value,
                                      current_value, stock)
            sell_value = None
        else:
            sell_value = current_value * 1.007
            if stock > stock_u_limit:
                to_sell = ((stock - stock_u_limit)+stock_u_limit) // 2
            else:
                to_sell = stock//2
            bank_value, stock_operated = buy_sell_proto(1, bank_value,
                                                        current_value,
                                                        sell_value, to_sell)
        stock -= stock_operated
    elif signal == -1:
        if stock < stock_u_limit:
            bank_value = recount_bank("stocks at upper limit, can't buy",
                                      bank_value, start_value,
                                      current_value, stock)
            sell_value = None
        else:
            sell_value = current_value * 1.005
            bank_value, stock_operated = buy_sell_proto(-1, bank_value,
                                                        current_value,
                                                        sell_value,
                                                        stock_u_limit // 2)
            stock += stock_operated

    return (start_value,  current_value, sma.iloc[-1],
            signal, sell_value, bank_value, stock)


def end_of_day_test(symbol: str):
    data = get_live_data_yahoo(symbol, period="1d", interval="15m")
    print(data)
    sma_l = [20]
    plot_closing(data, f"{symbol} today", sma=sma_l)
    # plot_sma(aapl_L, window=20, live=True)


# live_test()
def trade_routine(symbols: dict):
    report = {key: {"start_value": None,
                    "current_value": None,
                    "current_sma": None,
                    "signal": None,
                    "sell_value": None,
                    "bank_value": value["allocated_bank"],
                    "assets": value["stock"]}
              for key, value in symbols.items()}
    local_dt, current_est = date_reset()
    trade_start = datetime(current_est.year,
                           current_est.month,
                           current_est.day,
                           hour=9,
                           minute=30,
                           tzinfo=timezone('US/Eastern'))
    trade_end = datetime(current_est.year,
                         current_est.month,
                         current_est.day,
                         hour=15,
                         tzinfo=timezone('US/Eastern'))
    intraday = True
    while intraday:
        if trade_end > current_est > trade_start:
            for symbol in symbols.keys():
                if report[symbol]["bank_value"] > symbols[symbol]["allocated_bank"]-(symbols[symbol]["allocated_bank"]//symbols[symbol]["stop_thresh"]):
                    (report[symbol]["start_value"],
                     report[symbol]["current_value"],
                     report[symbol]["current_sma"],
                     report[symbol]["signal"],
                     report[symbol]["sell_value"],
                     report[symbol]["bank_value"],
                     report[symbol]["assets"]) = scalp_operation(symbol=symbol,
                                                                 bank_value=report[symbol]["bank_value"],
                                                                 stock=symbols[symbol]["stock"])
                    print(f"""
                    current est: {current_est}
                    {symbol} report:
                    current value {report[symbol]['current_value']}
                    sma: {report[symbol]['current_sma']}
                    signal: {report[symbol]['signal']}
                    value bought: {report[symbol]['start_value']},
                    value sold: {report[symbol]['sell_value']}
                    assets left: {report[symbol]['assets']}
                    total value: {report[symbol]['bank_value']}
                    """)
                    print("sleeping")
                else:
                    print(f"bank fell below threshold for {symbol}")
                    print(f"""
                    current est: {current_est}
                    {symbol} report:
                    current value {report[symbol]['current_value']}
                    sma: {report[symbol]['current_sma']}
                    signal: {report[symbol]['signal']}
                    value bought: {report[symbol]['start_value']},
                    value sold: {report[symbol]['sell_value']}
                    assets left: {report[symbol]['assets']}
                    total value: {report[symbol]['bank_value']}
                    """)
            sleep(60*20)  # sleep for 20 minutes
        elif trade_start < current_est > trade_end:
            print("trade ended for today, moving to day operations")
            intraday = False
        elif trade_end > current_est < trade_start:
            print(f"sleeping before trade:\
                  {(trade_start-current_est).total_seconds()} seconds")
            sleep((trade_start-current_est).total_seconds())
        local_dt, current_est = date_reset()
    for symbol in symbols.keys():
        end_of_day_test(symbol)


symbols = {"AAPL": {"allocated_bank": 100, "stock": 10, "stop_thresh": 5},
           "UBER": {"allocated_bank": 200, "stock": 5, "stop_thresh": 5}
           }
trade_routine(symbols)
