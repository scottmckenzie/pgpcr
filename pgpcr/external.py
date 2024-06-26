from subprocess import *
import sys
import os


def process(cmd, args={}):
    if sys.version_info.minor >= 6:
        args["encoding"] = sys.stdout.encoding
    ret = processb(cmd, args)
    if sys.version_info.minor <= 5:
        outputtostr(ret)
    return ret


def outputtostr(ret):
    if ret.stdout is not None:
        ret.stdout = ret.stdout.decode(sys.stdout.encoding)
    if ret.stderr is not None:
        ret.stderr = ret.stderr.decode(sys.stderr.encoding)


def processb(cmd, args={}):
    default = {"args": cmd, "check": True, "stdout": PIPE, "stderr": PIPE}
    default.update(args)
    return run(**default)


def processtofile(cmd, file=None, inp=None):
    with open(file, "wb") as f:
        args = {"stdout": f, "stdin": inp}
        return processb(cmd, args)

def setuprundir():
    socketdir = "/run/user/"+str(os.getuid())
    if not os.path.exists(socketdir):
        run(["sudo", "mkdir", "-p", socketdir])
        run(["sudo", "chown", str(os.getuid()), socketdir])
