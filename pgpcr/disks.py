import json
import shutil
import os
import logging
from . import external

CopyError = shutil.Error

_log = logging.getLogger(__name__)

def getdisks():
    j = lsblk(["-p", "-d", "-o", "tran,name,model,size,serial"])
    d = []
    for x in j:
        if x["tran"] == "usb":
            d.append(Disk(x))
    return d

def lsblk(options):
    com = ["lsblk"]
    com.extend(options)
    com.append("--json")
    p = external.process(com)
    _log.debug(p.stdout)
    return json.loads(p.stdout)["blockdevices"]

class NotMountable(Exception):
    pass

class Disk:

    def __init__(self, blkdev):
        self.path = blkdev["name"]
        self.model = blkdev["model"]
        self.size = blkdev["size"]
        self.serial = blkdev["serial"]
        self.label = self._getlabel()
        self.mountpoint = None

    def __str__(self):
        self.label = self._getlabel()
        s = ""
        if self.label is not None:
            s = self.label
        else:
            s = self.model+" "+self.size
        if self.ismounted():
            s = _("[IN USE]")+" "+s
        return s

    def _getchildren(self):
        j = lsblk(["-p", "-o", "name,mountpoint,label", self.path])
        if "children" not in j[0]:
            return None
        else:
            return j[0]["children"]

    def _getlabel(self):
        c = self._getchildren()
        if c is None:
            return None
        for p in c:
            if p["label"] is not None:
                return p["label"]

    def ismounted(self):
        if self.mountpoint is not None:
            return True
        children = self._getchildren()
        if children is None:
            return False
        else:
            for x in children:
                if x["mountpoint"] is not None:
                    self.mountpoint = x["mountpoint"]
                    return True

    def setup(self, label):
        self._partition(label)
        self.mount()

    def backup(self, workdir, name, ignore=None):
        if not self.ismounted():
            return None
        else:
            if ignore is not None:
                ig = shutil.ignore_patterns(ignore)
            else:
                ig = None
            dest = self.mountpoint+"/"+name
            shutil.rmtree(dest, ignore_errors=True)
            shutil.copytree(workdir, dest, ignore=ig)
            self.eject()

    def _partition(self, label):
        external.process(
            ["sudo", "pgpcr-part", self.path, label], {"stdout": None})

    def mount(self):
        children = self._getchildren()
        if children is None:
            raise NotMountable
        mountdir = "/mnt/"+self.serial
        external.process(["sudo", "mkdir", "-p", mountdir])
        external.process(
            ["sudo", "mount", children[0]["name"], mountdir])
        self.mountpoint = mountdir
        chown = external.process(
            ["sudo", "chown", "-R", str(os.getuid()), mountdir])

    def eject(self):
        external.process(["sync"])
        external.process(["sudo", "umount", self.mountpoint])
        self.mountpoint = None
