import os
import shutil
from pgpcr import external

class Context:
    @property
    def redraw(self):
        r = self._ctx.get_ctx_flag("redraw")
        if r != "":
            self._ctx.set_ctx_flag("redraw", "")
            return True
        else:
            return False

    @property
    def homedir(self):
        h = self._ctx.engine_info.home_dir
        if h is None:
            return defaulthome
        else:
            return h

defaulthome = os.environ["HOME"]+"/.gnupg"

def _agent(homedir, opt):
    if homedir is not None:
        os.environ["GNUPGHOME"] = homedir
    external.process(["gpgconf", opt, "gpg-agent"])

def launchagent(homedir):
    _agent(homedir, "--launch")

def killagent(homedir):
    _agent(homedir, "--kill")

def setupworkdir(workdir):
    shutil.copyfile("/etc/pgpcr/gpg.conf", workdir+"/gpg.conf")
    shutil.copyfile("/etc/pgpcr/gpg-agent.conf", workdir+"/gpg-agent.conf")
    killagent(workdir)
