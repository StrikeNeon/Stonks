def buy_sell_proto(bank_value, current_value, sell_value, start_stocks):
    bank_value += sell_value * start_stocks
    bank_value -= current_value * start_stocks
    return bank_value
