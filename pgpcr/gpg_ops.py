import gpg
import os
import tempfile
import shutil
from collections import OrderedDict
from . import external
from . import gpg_interact
from . import time
from . import context
from . import log

_log = log.getlog(__name__)

class GPGKey(context.Context):

    def __init__(self, home=None,  loadfpr=None, loaddir=None):
        self.changed = True
        self.expert = False
        if loaddir:
            self.changed = False
            shutil.rmtree(home)
            shutil.copytree(loaddir, home, ignore=ignore)
        else:
            context.setupworkdir(home)
        if home == context.defaulthome:
            home = None
        else:
            external.setuprundir()
        self._ctx = gpg.Context(home_dir=home, armor=True)
        self._master = None
        self._masteralgo = "rsa4096"
        self._subalgo = "rsa2048"
        log.status(self)
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
        self.refreshmaster()
        return sk

    def refreshmaster(self):
        self._master = self._ctx.get_key(self._master.fpr)
        self.changed = True

    def setmaster(self, fpr):
        self._master = self._ctx.get_key(fpr)

    def getmaster(self):
        kl = list(self._ctx.keylist(secret=True))
        if len(kl) == 1:
            self.setmaster(kl[0].fpr)
            return None
        return [x.fpr for x in kl]

    @property
    def fpr(self):
        if self._master is None:
            return None
        return self._master.fpr

    @property
    def revcert(self):
        if self._master is None:
            return None
        return self.homedir+"/openpgp-revocs.d/"+self.fpr+".rev"

    @property
    def uids(self):
        uids = []
        if self._master is None:
            return uids
        for u in self._master.uids:
            s = u.uid
            if u.revoked:
                s += " "+_("REVOKED")
            uids.append(s)
        return uids

    def __str__(self):
        if self._master is None:
            return ""
        s = str(self.uids[0])
        s += " "
        s += self.fpr[-17:]
        return s

    @property
    def keys(self):
        if self._master is None:
            return None
        keys = []
        for k in self._master.subkeys:
            s = k.fpr
            if k.revoked:
                s += " "+_("REVOKED")
            if k.expires:
                if k.expired:
                    s += " ["+_("Expired")+"]"
                else:
                    s += " ["+time.timestamp2iso(k.expires)+"]"
            if k.fpr == self.fpr:
                s += " ("+_("Master")+")"
                keys.append(s)
                continue
            if k.can_certify:
                s += " ("+_("Certification")+")"
            if k.can_sign:
                s += " ("+_("Signing")+")"
            if k.can_encrypt:
                s += " ("+_("Encryption")+")"
            if k.can_authenticate:
                s += " ("+_("Authentication")+")"
            keys.append(s)
        return keys

    @property
    def subkeys(self):
        return self._master.subkeys

    @property
    def info(self):
        if self._master is None:
            return ""
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

    def genseasubs(self, status, explain, redraw, data=None):
        # Force a redraw
        data = redraw(data)
        s = explain(data, _("Signing Subkey"), _("A signing subkey will now be"
            " generated. This is used to ensure what you send across the"
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
            self.refreshmaster()
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
            self.refreshmaster()
            return
        if a:
            status(_("Generating authentication subkey..."))
            try:
                self.gensub(authenticate=True)
            except PinentryCancelled:
                pass
        self.refreshmaster()

    def _readdata(self, data):
        data.seek(0, os.SEEK_SET)
        return data.read()

    def _export(self, pattern, mode=0, outfile=None):
        # 0 is the normal mode
        data = gpg.Data()
        self._ctx.op_export(pattern, mode, data)
        rd = self._readdata(data)
        if hasattr(outfile, "write"):
            outfile.write(rd)
        elif type(outfile) is str:
            with open(outfile, "wb") as f:
                f.write(rd)

    def export(self, exportdir, fpr=None, name=None):
        if fpr is None:
            fpr = self.fpr
        if name is None:
            name = fpr+".pub"
        if fpr == self.fpr:
            shutil.copy(self.revcert, exportdir)
            self.exportownertrust(exportdir)
        self._export(fpr, outfile=exportdir+"/"+name)

    def _callgpg(self, args, outfile):
        gpgargv = [self._ctx.engine_info.file_name, "--no-tty", "--yes",
                "--armor", "--status-fd", "2"]
        gpgargv.extend(args)
        external.processtofile(gpgargv, outfile)

    def exportsubkeys(self, exportdir):
        # Exporting only the secret subkeys isn't directly available
        # so we have to call gpg directly
        # gpg --export-secret-subkeys
        self._callgpg(["--export-secret-subkeys"],
                          exportdir+"/"+self.fpr+".subsec")

    def exportownertrust(self, exportdir):
        self._callgpg(["--export-ownertrust"], exportdir+"/ownertrust")

    def exportmasterkey(self, exportfile):
        self._export(self.fpr, gpg.constants.EXPORT_MODE_SECRET, exportfile)

    def adduid(self, uid):
        try:
            self._ctx.key_add_uid(self._master, uid)
        except GPGMEError as e:
            _pinentrycancel(e)
        self.refreshmaster()

    def revokeuid(self, uid):
        try:
            self._ctx.key_revoke_uid(self._master, uid)
        except GPGMEError as e:
            _pinentrycancel(e)
        self.refreshmaster()


    def _import(self, keyfile):
        keydata = gpg.Data(file=keyfile)
        self._ctx.op_import(keydata)
        result = self._ctx.op_import_result()
        return result.imports

    def importpublic(self, keyfile):
        result = self._import(keyfile)
        if len(result) > 1:
            raise ValueError(_("Multiple keys found in '%s'") % keyfile)
        key = self._ctx.get_key(result[0].fpr)
        return key

    def importbackup(self, backup):
        invalid = ValueError(_("No valid backup found at '%s'") % backup)
        if not os.path.exists(backup):
            raise invalid
        if os.path.isfile(backup):
            res = self._import(backup)
            if not res: # Empty list
                raise invalid
        else:
            self.__init__(self.homedir, loaddir=backup)
        return self.getmaster()

    def _signkeyfolders(self, folder):
        pending = folder+"/signing/pending"
        done = folder+"/signing/done"
        os.makedirs(pending, exist_ok=True)
        os.makedirs(done, exist_ok=True)
        return (pending, done)

    def signkey(self, folder, keyfile, expires=False, uidpick=None, hook=None):
        self._ctx.signers = [self._master]
        pending, done = self._signkeyfolders(folder)
        keys = self._import(pending+"/"+keyfile)
        if expires:
            delta = time.isostr2delta(expires)
            expires = int(delta.total_seconds())
        for k in keys:
            sk = self._ctx.get_key(k.fpr)
            uidlist = [x.uid for x in sk.uids if x.revoked == 0]
            uids = None
            if uidpick is not None:
                cancel, uids = uidpick(hook, _("Sign UIDs"), _("Pick UIDs of"
                " %s to sign") % sk.fpr, uidlist)
                if cancel:
                    return
                if set(uids) == set(uidlist):
                    uids = None
            try:
                self._ctx.key_sign(sk, uids, expires_in=expires)
            except GPGMEError as e:
                _pinentrycancel(e)
            self.export(done, sk.fpr, keyfile)
            os.remove(pending+"/"+keyfile)

    def findkey(self, fpr):
        kl = self._ctx.keylist(fpr, mode=gpg.constants.keylist.mode.LOCATE)
        kl = list(kl)
        return kl

    def importkey(self, key):
        self._ctx.op_import_keys([key])

    def exporttosign(self, dest, fprs):
        pending, _ = self._signkeyfolders(dest)
        for f in fprs:
            self.export(pending, fpr=f)

    def revokekey(self, fpr, reason, text):
        try:
            revoke_reasons()[reason]
        except IndexError:
            raise ValueError(_("%d is not a valid revocation reason!") % reason)
        gpg_interact.revokekey(self, fpr, reason, text)
        self.refreshmaster()

    def expirekey(self, fpr, datestr):
        gpg_interact.expirekey(self, fpr, datestr)
        self.refreshmaster()

    def keytocard(self, fpr, slot, overwrite=False):
        gpg_interact.keytocard(self, fpr, slot, overwrite)
        self.refreshmaster()

    def encrypt(self, plaintext, recipients):
        if type(plaintext) is str:
            plaintext = plaintext.encode()
        keys = []
        for r in recipients:
            kl = self._ctx.keylist(r)
            keys.append(next(kl))
        c, _, _ =  self._ctx.encrypt(plaintext, keys)
        return c

GPGMEError = gpg.errors.GPGMEError

class PinentryCancelled(Exception):
    pass

def _pinentrycancel(e):
    if e.code_str == "Operation cancelled":
        raise PinentryCancelled
    else:
        raise e

def revoke_reasons():
    return [_("No reason specified"), _("Key has been compromised"),
            _("Key is superseded"), _("Key is no longer used")]

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
