import gpg
import os
import logging
import tempfile
import shutil
from distutils.dir_util import copy_tree
from collections import OrderedDict
from . import external, gpg_interact

_log = logging.getLogger(__name__)

class GPGKey:

    def __init__(self, home,  loadfpr=None, loaddir=None):
        if loaddir:
            copy_tree(loaddir, home, verbose=0)
        self._ctx = gpg.Context(home_dir=home)
        self._masteralgo = "rsa4096"
        self._subalgo = "rsa2048"
        self.revcert = None
        if loadfpr:
            self._master = self._ctx.get_key(loadfpr)
        # Ensure a gpg-agent is running and a socketdir is created
        os.environ["GNUPGHOME"] = self.homedir
        external.process(["gpgconf", "--launch", "gpg-agent"])
        if self.homedir != defaulthome:
            external.process(["gpgconf", "--create-socketdir"])

    def __del__(self):
        try:
            external.process(["gpgconf", "--kill", "gpg-agent"])
            os.environ.pop("GNUPGHOME", None)
            if self.homedir != defaulthome:
                external.process(["gpgconf", "--remove-socketdir"])
        except external.CalledProcessError as e:
            _log.debug(e.stderr)

    def genmaster(self, userid, passphrase=True):
        genkey = self._ctx.create_key(userid, algorithm=self._masteralgo,
                                      sign=True, certify=True,
                                      passphrase=passphrase)
        self._master = self._ctx.get_key(genkey.fpr)

    def _refreshmaster(self):
        self._master = self._ctx.get_key(self._master.fpr)

    def gensub(self, sign=False, encrypt=False, authenticate=False):
        algo = self._subalgo
        if encrypt and algo == "ed25519":
            # Special algorithm needed for ed25519 encryption subkeys
            algo = "cv25519"
        if "brainpool" in algo or "nistp" in algo:
            # Workaround for GPGME bug
            # https://lists.gnupg.org/pipermail/gnupg-users/2018-July/060755.html
            if sign or authenticate:
                algo += "/ecdsa"
        sk = self._ctx.create_subkey(self._master, algorithm=algo,
                                       sign=sign, encrypt=encrypt,
                                       authenticate=authenticate)
        self._refreshmaster()
        return sk

    def genseasubs(self, status, explain, redraw, data):
        # Force a redraw
        data = redraw(data, True)
        s = explain(data, _("Signing Subkey"), _("A signing subkey will now be"
            " generated. This is used to  ensure what you send across the"
            " Internet, like emails or Debian packages, has not been tampered"
            " with."))
        if s is None:
            return
        if s:
            status(_("Generating signing subkey")+"...")
            self.gensub(sign=True)
            data = redraw(data, self.redraw)
        e = explain(data, _("Encryption Subkey"), _("An encryption subkey will"
            " now be generated. This is used to protect your data, like emails"
            " or backups, from being viewed by anyone else."))
        if e is None:
            self._refreshmaster()
            return
        if e:
            status(_("Generating encryption subkey")+"...")
            self.gensub(encrypt=True)
            data = redraw(data, self.redraw)
        a = explain(data, _("Authentication Subkey"), _("An authentication"
            " subkey will now be generated. This is used to prove your"
            " identity and can be used as an ssh key."))
        if a is None:
            self._refreshmaster()
            return
        if a:
            status(_("Generating authentication subkey")+"...")
            self.gensub(authenticate=True)
        self._refreshmaster()

    def setprogress(self, progress, hook=None):
        self._ctx.set_progress_cb(progress, hook)

    def setpassword(self, password, hook=None):
        self._ctx.set_passphrase_cb(password, hook)

    def setstatus(self, status, hook=None):
        self._ctx.set_ctx_flag("full-status", "1")
        self._ctx.set_status_cb(status, hook)

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

    def _export(self, pattern, mode=0, outfile=None):
        # 0 is the normal mode
        data = gpg.Data()
        self._ctx.op_export(pattern, mode, data)
        if outfile is not None:
            with open(outfile, "wb") as f:
                f.write(self._readdata(data))

    def export(self, dir, fpr=None, name=None):
        if fpr is None:
            fpr = self.fpr
        if name is None:
            name = fpr+".pub"
        if self.revcert is not None:
            shutil.copy(self.revcert, dir)
        d = self._export(fpr, outfile=dir +
                         "/"+name)

    def _callgpg(self, args, outfile, infile=None):
        gpgargv = [self._ctx.engine_info.file_name, "--no-tty", "--yes",
                "--status-fd", "2", "--output", outfile]
        if infile is not None:
            gpgargv.extend(["--command-file", infile])
        gpgargv.extend(args)
        external.run(gpgargv, stderr=external.PIPE, check=True)

    def exportsubkeys(self, dir):
        # Exporting only the secret subkeys isn't directly available
        # so we have to call gpg directly
        # gpg --export-secret-subkeys
        k = self._callgpg(["--export-secret-subkeys"],
                          dir+"/"+self.fpr+".subsec")

    @property
    def keys(self):
        keys = []
        for k in self._master.subkeys:
            s = k.fpr
            if k.fpr == self.fpr:
                s += " "+_("(Master)")
                keys.append(s)
                continue
            if k.can_certify:
                s += " "+_("(Certification)")
            if k.can_sign:
                s += " "+_("(Signing)")
            if k.can_encrypt:
                s += " "+_("(Encryption)")
            if k.can_authenticate:
                s += " "+_("(Authentication)")
            keys.append(s)
        return keys

    def adduid(self, uid):
        self._ctx.key_add_uid(self._master, uid)
        self._refreshmaster()

    def revokeuid(self, uid):
        self._ctx.key_revoke_uid(self._master, uid)
        self._refreshmaster()

    @property
    def uids(self):
        return [x.uid for x in self._master.uids]

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
        return self._ctx.engine_info.home_dir

    def __str__(self):
        s = str(self.uids[0])
        s += " "
        s += self.fpr[-17:]
        return s

    def _import(self, keyfile):
        keydata = gpg.Data(file=keyfile)
        self._ctx.op_import(keydata)
        result = self._ctx.op_import_result()
        return result.imports

    def setmaster(self, fpr):
        self._master = self._ctx.get_key(fpr)

    def signkey(self, folder, keyfile):
        pending = folder+"/signing/pending"
        done = folder+"/signing/done"
        try:
            os.mkdir(done)
        except FileExistsError:
            pass
        keys = self._import(pending+"/"+keyfile)
        for k in keys:
            sk = self._ctx.get_key(k.fpr)
            self._ctx.key_sign(sk)
            self.export(done, sk.fpr, keyfile)
            os.remove(pending+"/"+keyfile)

    def revokekey(self, fpr, reason, text):
        gpg_interact.revokekey(self, fpr, reason, text)
        self._refreshmaster()

    def expirekey(self, fpr, datestr):
        gpg_interact.expirekey(self, fpr, datestr)
        self._refreshmaster()

    def keytocard(self, fpr, slot, overwrite=False):
        gpg_interact.keytocard(self, fpr, slot, overwrite)
        self._refreshmaster()

    def importbackup(self, backup):
        if not os.path.exists(backup):
            raise ValueError(_("No valid backup found at '%s'") % backup)
        if os.path.isfile(backup):
            self._import(backup)
        else:
            self.__init__(self.homedir, loaddir=backup)
        kl = list(self._ctx.keylist(secret=True))
        if len(kl) == 1:
            self.setmaster(kl[0])
            return None
        return [x.fpr for x in kl]

    def genrevoke(self):
        self.revcert = self.homedir+"/"+self.fpr+".rev"
        with tempfile.NamedTemporaryFile() as f:
            f.write("y\n0\nGeneral Revocation Certificate\n\ny\n\n".encode())
            f.flush()
            self._callgpg(["--gen-revoke", self.fpr], self.revcert, f.name)

GPGMEError = gpg.errors.GPGMEError

revoke_reasons = ["No reason specified", "Key has been compromised",
                  "Key is superseded", "Key is no longer used"]
master_algos = OrderedDict([
    ("rsa", ["4096", "3072", "2048"]),
    ("ed25519", None),
    ("nistp", ["521", "384", "256"]),
    ("brainpoolP", ["512r1", "384r1", "256r1"])
    ])
sub_algos = OrderedDict([
    ("rsa", ["2048", "4096", "3072"]),
    ("ed25519", None),
    ("nistp", ["521", "384", "256"]),
    ("brainpoolP", ["512r1", "384r1", "256r1"])
    ])
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
