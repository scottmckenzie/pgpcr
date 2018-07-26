import datetime
from . import valid

def timestamp2iso(ts):
    d = datetime.datetime.fromtimestamp(int(ts))
    return d.strftime("%Y-%m-%d")

def _isostr2datetime(isostr):
    if not valid.date(isostr):
        raise ValueError
    dl = isostr.split("-")
    i = 0
    for t in dl:
        dl[i] = int(t)
        i += 1
    return datetime.date(*dl)

def _datetime2delta(dt):
    return dt - dt.today()

def isostr2delta(isostr):
    dt = _isostr2datetime(isostr)
    return _datetime2delta(dt)
