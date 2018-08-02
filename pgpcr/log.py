import logging
import traceback
import sys
from os import environ
from snack import SnackScreen

def init():
    log = logging.getLogger("pgpcr")
    log.setLevel(logging.INFO)
    fh = logging.FileHandler(environ["HOME"]+"/pgpcr.log")
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    fh.setFormatter(formatter)
    log.addHandler(fh)

def _excepthook(t, v, tb):
    log = logging.getLogger("pgpcr")
    SnackScreen().finish()
    traceback.print_exception(t, v, tb)
    exc = traceback.format_exception(t, v, tb)
    for x in exc:
        log.error(x)

sys.excepthook = _excepthook

def getlog(name):
    return logging.getLogger(name)

def _status(keyword, args, hook=None):
    if keyword is None and args is None:
        return
    if hook is not None:
        hook.info("Status {!s}({!s})".format(keyword, args))

def status(gk):
    gklog = getlog("pgpcr.GPGKey")
    gk.setstatus(_status, gklog)
