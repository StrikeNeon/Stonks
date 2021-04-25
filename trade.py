def buy_sell_proto(signal: int, bank_value, current_value, op_value, stocks):
    if signal == 1:
        bank_value += (op_value-current_value) * stocks
    else:
        bank_value -= (op_value-current_value) * stocks
    return bank_value, stocks
