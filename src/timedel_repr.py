import math
import datetime

def timedel_repr(dt):
    minute = 60
    hour = 60 * 60
    day = hour * 24
    month = day * 30

    def get_mins(x):
        return int(math.floor(x.total_seconds() / 60))
    def get_hrs(x):
        return int(math.floor(x.total_seconds() / hour))
    def get_days(x):
        return int(math.floor(x.total_seconds() / day))
    def get_months(x):
        return int(math.floor(x.total_seconds() / month))

    if dt.total_seconds() < minute:
        return "{} s.".format(str(dt.seconds))
    elif dt.total_seconds() < hour:
        return "{} m.".format(str(get_mins(dt)))
    elif dt.total_seconds() < day:
        return "{} h.".format(str(get_hrs(dt)))
    elif dt.total_seconds() < month:
        return "{} d.".format(str(get_days(dt)))
    else:
        return "{} M.".format(str(get_months(dt)))
