import datetime
from . import valid

def timestamp2iso(ts):
    d = datetime.datetime.fromtimestamp(int(ts))
    return d.strftime("%Y-%m-%d")

def _isostr2datetime(isostr):
    if not valid.date(isostr):
        raise ValueError
    return datetime.datetime.strptime(isostr, "%Y-%m-%d")

def _datetime2delta(dt):
    return dt - dt.today()

def isostr2delta(isostr):
    dt = _isostr2datetime(isostr)
    return _datetime2delta(dt)
