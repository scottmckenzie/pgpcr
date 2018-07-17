import logging
import traceback
import sys
from snack import SnackScreen

def init():
    log = logging.getLogger("pgpcr")
    log.setLevel(logging.INFO)
    fh = logging.FileHandler("pgpcr.log")
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    fh.setFormatter(formatter)
    log.addHandler(fh)

def _excepthook(t, v, tb):
    SnackScreen().finish()
    traceback.print_exception(t, v, tb)
    exc = traceback.format_exception(t, v, tb)
    for x in exc:
        log.error(x)

sys.excepthook = _excepthook

def getlog(name):
    return logging.getLogger(name)
