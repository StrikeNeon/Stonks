from os import mkdir
from dateutil import tz
from pytz import timezone
from datetime import datetime


def setup_dirs():
    try:
        mkdir("data")
    except FileExistsError:
        pass


def local_to_est(local_dt):
    from_zone = tz.tzlocal()
    to_zone = timezone('US/Eastern')
    return local_dt.replace(tzinfo=from_zone).astimezone(tz=to_zone)


def date_reset():
    local_dt = datetime.now(tz=tz.tzlocal())
    current_est = local_to_est(local_dt)
    return local_dt, current_est


def recount_bank(message, bank_value, start_value, current_value, stock):
    print(message)
    if start_value > current_value:
        bank_value -= (start_value
                       - current_value) * stock
    elif start_value < current_value:
        bank_value += (start_value
                       - current_value) * stock
    return bank_value
