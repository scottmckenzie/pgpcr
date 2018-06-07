import gpg
import os
from distutils.dir_util import copy_tree
from . import external

class GPGKey:

    def __init__(self, home,  loadfpr=None, loaddir=None):
        if loaddir:
            copy_tree(loaddir, home, verbose=0)
        self._ctx = gpg.Context(home_dir=home)
        self._masteralgo = "rsa4096"
        self._subalgo = "rsa2048"
        if loadfpr:
            self._master = self._ctx.get_key(loadfpr)

    def genmaster(self, userid):
        genkey = self._ctx.create_key(userid, algorithm=self._masteralgo,
                                      sign=True, certify=True, passphrase=True)
        self._master = self._ctx.get_key(genkey.fpr)

    def gensub(self):
        self._ctx.create_subkey(self._master, sign=True,
                                algorithm=self._subalgo)
        self._ctx.create_subkey(self._master, encrypt=True,
                                algorithm=self._subalgo)
        self._ctx.create_subkey(self._master, authenticate=True,
                                algorithm=self._subalgo)

    def setprogress(self, progress, hook=None):
        self._ctx.set_progress_cb(progress, hook)

    def setpassword(self, password, hook=None):
        self._ctx.set_passphrase_cb(password, hook)

    def setalgorithms(self, master, sub):
        if master is not None:
            self._masteralgo = master
        if sub is not None:
            self._subalgo = sub

    @property
    def fpr(self):
        return self._master.fpr

    def _readdata(self, data):
        data.seek(0, os.SEEK_SET)
        return data.read()

    def _export(self, pattern, mode=0, file=None):
        # 0 is the normal mode
        open(file, "wb").close()
        data = gpg.Data()
        self._ctx.op_export(pattern, mode, data)
        if file is not None:
            with open(file, "wb") as f:
                f.write(self._readdata(data))

    def export(self, dir):
        d = self._export(self.fpr, file=dir +
                         "/"+self.fpr+".pub")

    def _callgpg(self, args, file):
        os.environ["GNUPGHOME"] = self._ctx.engine_info.home_dir
        gpgargv = [self._ctx.engine_info.file_name]
        gpgargv.extend(args)
        ret = external.processtofile(gpgargv, file)

    def exportsubkeys(self, dir):
        # Exporting only the secret subkeys isn't directly available
        # so we have to call gpg directly
        # gpg --export-secret-subkeys
        k = self._callgpg(["--export-secret-subkeys"],
                          dir+"/"+self.fpr+".subsec")

    def listkeys(self):
        keys = []
        for k in self._master.subkeys:
            s = k.fpr
            if k.fpr == self.fpr:
                s += " (Master)"
                keys.append(s)
                continue
            if k.can_certify:
                s += " (Certification)"
            if k.can_sign:
                s += " (Signing)"
            if k.can_encrypt:
                s += " (Encryption)"
            if k.can_authenticate:
                s += " (Authentication)"
            keys.append(s)
        return keys

    def adduid(self, uid):
        self._ctx.key_add_uid(self._master, uid)

    def revokeuid(self, uid):
        self._ctx.key_revoke_uid(self._master, uid)

    def listuids(self):
        return [x.uid for x in self._master.uids]

# Check if a directory contains gpg backups
# If so return a list of keys backed up
def backups(path):
    if "gpg" not in os.listdir(path):
        return None
    else:
        return os.listdir(path+"/gpg")


GPGMEError = gpg.errors.GPGMEError
