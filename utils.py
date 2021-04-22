from os import mkdir
from dateutil import tz
from pytz import timezone


def setup_dirs():
    try:
        mkdir("data")
    except FileExistsError:
        pass


def local_to_est(local_dt):
    from_zone = tz.tzlocal()
    to_zone = timezone('US/Eastern')
    return local_dt.replace(tzinfo=from_zone).astimezone(tz=to_zone)