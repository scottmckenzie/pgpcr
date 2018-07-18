import gpg
import os
import logging
import tempfile
import shutil
from collections import OrderedDict
from . import external
from . import gpg_interact
from . import context

_log = logging.getLogger(__name__)

class GPGKey(context.Context):

    def __init__(self, home=None,  loadfpr=None, loaddir=None):
        if loaddir:
            shutil.rmtree(home)
            shutil.copytree(loaddir, home, ignore=ignore)
        else:
            context.setupworkdir(home)
        if home == context.defaulthome:
            home = None
        else:
            external.setuprundir()
        self._ctx = gpg.Context(home_dir=home)
        self._masteralgo = "rsa4096"
        self._subalgo = "rsa2048"
        if loadfpr:
            self._master = self._ctx.get_key(loadfpr)
        # Ensure a gpg-agent is running and a socketdir is created
        if home is not None:
            os.environ["GNUPGHOME"] = self.homedir
            external.process(["gpgconf", "--create-socketdir"])
        external.process(["gpgconf", "--launch", "gpg-agent"])

    def __del__(self):
        try:
            external.process(["gpgconf", "--kill", "gpg-agent"])
            os.environ.pop("GNUPGHOME", None)
            if self.homedir != context.defaulthome:
                external.process(["gpgconf", "--remove-socketdir"])
        except external.CalledProcessError as e:
            _log.debug(e.stderr)
        except Exception as e:
            _log.debug(str(e))

    def genmaster(self, userid, passphrase=True):
        try:
            genkey = self._ctx.create_key(userid, algorithm=self._masteralgo,
                    sign=True, certify=True, passphrase=passphrase)
        except GPGMEError as e:
            _pinentrycancel(e)

        self._master = self._ctx.get_key(genkey.fpr)

    def gensub(self, sign=False, encrypt=False, authenticate=False):
        algo = self._subalgo
        if encrypt and algo == "ed25519":
            # Special algorithm needed for ed25519 encryption subkeys
            algo = "cv25519"
        if "brainpool" in algo or "nistp" in algo:
            # Workaround for GPG bug
            # https://dev.gnupg.org/T4052
            # https://lists.gnupg.org/pipermail/gnupg-users/2018-July/060755.html
            if sign or authenticate:
                algo += "/ecdsa"
        try:
            sk = self._ctx.create_subkey(self._master, algorithm=algo,
                    sign=sign, encrypt=encrypt, authenticate=authenticate)
        except GPGMEError as e:
            _pinentrycancel(e)
        self._refreshmaster()
        return sk

    def _refreshmaster(self):
        self._master = self._ctx.get_key(self._master.fpr)

    def setmaster(self, fpr):
        self._master = self._ctx.get_key(fpr)

    @property
    def fpr(self):
        return self._master.fpr

    @property
    def revcert(self):
        return self.homedir+"/openpgp-revocs.d/"+self.fpr+".rev"

    @property
    def uids(self):
        return [x.uid for x in self._master.uids]

    def __str__(self):
        s = str(self.uids[0])
        s += " "
        s += self.fpr[-17:]
        return s

    @property
    def keys(self):
        keys = []
        for k in self._master.subkeys:
            s = k.fpr
            if k.expires:
                s += " ["+context.timestamp2iso(k.expires)+"]"
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

    @property
    def info(self):
        s = "\n"
        k = s.join(self.keys)
        u = s.join(self.uids)
        return k+s+u

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
            status(_("Generating signing subkey..."))
            try:
                self.gensub(sign=True)
            except PinentryCancelled:
                pass
            data = redraw(data, self.redraw)
        e = explain(data, _("Encryption Subkey"), _("An encryption subkey will"
            " now be generated. This is used to protect your data, like emails"
            " or backups, from being viewed by anyone else."))
        if e is None:
            self._refreshmaster()
            return
        if e:
            status(_("Generating encryption subkey..."))
            try:
                self.gensub(encrypt=True)
            except PinentryCancelled:
                pass
            data = redraw(data, self.redraw)
        a = explain(data, _("Authentication Subkey"), _("An authentication"
            " subkey will now be generated. This is used to prove your"
            " identity and can be used as an ssh key."))
        if a is None:
            self._refreshmaster()
            return
        if a:
            status(_("Generating authentication subkey..."))
            try:
                self.gensub(authenticate=True)
            except PinentryCancelled:
                pass
        self._refreshmaster()

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

    def export(self, exportdir, fpr=None, name=None):
        if fpr is None:
            fpr = self.fpr
        if name is None:
            name = fpr+".pub"
        if fpr == self.fpr:
            shutil.copy(self.revcert, exportdir)
        self._export(fpr, outfile=exportdir+"/"+name)

    def _callgpg(self, args, outfile):
        gpgargv = [self._ctx.engine_info.file_name, "--no-tty", "--yes",
                "--status-fd", "2", "--output", outfile]
        gpgargv.extend(args)
        external.run(gpgargv, stderr=external.PIPE, check=True)

    def exportsubkeys(self, exportdir):
        # Exporting only the secret subkeys isn't directly available
        # so we have to call gpg directly
        # gpg --export-secret-subkeys
        self._callgpg(["--export-secret-subkeys"],
                          exportdir+"/"+self.fpr+".subsec")

    def adduid(self, uid):
        try:
            self._ctx.key_add_uid(self._master, uid)
        except GPGMEError as e:
            _pinentrycancel(e)
        self._refreshmaster()

    def revokeuid(self, uid):
        try:
            self._ctx.key_revoke_uid(self._master, uid)
        except GPGMEError as e:
            _pinentrycancel(e)
        self._refreshmaster()


    def _import(self, keyfile):
        keydata = gpg.Data(file=keyfile)
        self._ctx.op_import(keydata)
        result = self._ctx.op_import_result()
        return result.imports

    def importbackup(self, backup):
        if not os.path.exists(backup):
            raise ValueError(_("No valid backup found at '%s'") % backup)
        if os.path.isfile(backup):
            self._import(backup)
        else:
            self.__init__(self.homedir, loaddir=backup)
        kl = list(self._ctx.keylist(secret=True))
        if len(kl) == 1:
            self.setmaster(kl[0].fpr)
            return None
        return [x.fpr for x in kl]

    def _signkeyfolders(self, folder):
        pending = folder+"/signing/pending"
        done = folder+"/signing/done"
        os.makedirs(pending, exist_ok=True)
        os.makedirs(done, exist_ok=True)
        return (pending, done)

    def signkey(self, folder, keyfile):
        pending, done = self._signkeyfolders(folder)
        keys = self._import(pending+"/"+keyfile)
        for k in keys:
            sk = self._ctx.get_key(k.fpr)
            try:
                self._ctx.key_sign(sk)
            except GPGMEError as e:
                _pinentrycancel(e)
            self.export(done, sk.fpr, keyfile)
            os.remove(pending+"/"+keyfile)

    def findkey(self, fpr):
        kl = self._ctx.keylist(fpr, mode=gpg.constants.keylist.mode.EXTERN)
        kl = list(kl)
        if len(kl) == 1:
            self._ctx.op_import_keys(kl)
        return kl

    def exporttosign(self, dest, keys):
        pending, _ = self._signkeyfolders(dest)
        for f in [k.fpr for k in keys]:
            self.export(pending, fpr=f)

    def revokekey(self, fpr, reason, text):
        gpg_interact.revokekey(self, fpr, reason, text)
        self._refreshmaster()

    def expirekey(self, fpr, datestr):
        gpg_interact.expirekey(self, fpr, datestr)
        self._refreshmaster()

    def keytocard(self, fpr, slot, overwrite=False):
        gpg_interact.keytocard(self, fpr, slot, overwrite)
        self._refreshmaster()

GPGMEError = gpg.errors.GPGMEError

class PinentryCancel(Exception):
    pass

def _pinentrycancel(e):
    if e.code_str == "Operation cancelled":
        raise PinentryCancel
    else:
        raise e

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

# Files to ignore when backing up gpg home directories
ignore = shutil.ignore_patterns("S.*")
