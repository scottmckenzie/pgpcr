import os
import tempfile
from . import external

def isInstalled():
    try:
        external.process(["lpstat"])
    except FileNotFoundError:
        return False
    return True

def printrevcert(gk):
    external.run(["lp", gk.revcert])

def printkey(gk):
    with tempfile.TemporaryFile() as tmp:
        gk.exportmasterkey(tmp)
        p = external.process(["paperkey"], {"stdin": tmp})
        external.process(["lp"], {"stdin": p.stdout})
