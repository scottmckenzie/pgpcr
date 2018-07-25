import os
import shutil
import datetime
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
    gpgconf = "/etc/pgpcr/gpg.conf"
    agentconf = "/etc/pgpcr/gpg-agent.conf"
    if workdir is None:
        workdir = defaulthome
    if not os.path.exists(workdir+"/gpg.conf") and os.path.exists(gpgconf):
        shutil.copyfile(gpgconf, workdir+"/gpg.conf")
    if (not os.path.exists(workdir+"/gpg-agent.conf")
            and os.path.exists(agentconf)):
        shutil.copyfile(agentconf, workdir+"/gpg-agent.conf")
    killagent(workdir)

def timestamp2iso(ts):
    d = datetime.datetime.fromtimestamp(int(ts))
    return d.strftime("%Y-%m-%d")
