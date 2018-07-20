import os
import tempfile
from . import external

def isInstalled():
    try:
        external.process(["lpstat"])
    except FileNotFoundError:
        return False
    return True

def install(workdir):
    cwd = os.getcwd()
    os.chdir(workdir)
    external.process(["install-printing"])
    os.chdir(cwd)

def printrevcert(gk):
    external.run(["lp", gk.revcert])

def printkey(gk):
    with tempfile.TemporaryFile() as tmp:
        gk.exportmasterkey(tmp)
        p = external.process(["paperkey"], {"stdin": tmp})
        external.process(["lp"], {"stdin": p.stdout})
