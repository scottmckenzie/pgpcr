import gpg
import datetime
import logging

_log = logging.getLogger(__name__)

class _Interact:
    def __init__(self, master, fpr):
        self.step = 0
        self.fpr = fpr
        self.keynum = 0
        self.log = _log
        for sk in master.subkeys:
            if fpr == sk.fpr:
                return
            self.keynum += 1
        raise NoKeyError

class _Revoke(_Interact):
    def __init__(self, master, fpr, code, text):
        super().__init__(master, fpr)
        self.code = code
        self.text = text

class _Expire(_Interact):
    def __init__(self, master, fpr, datestr):
        super().__init__(master, fpr)
        dl = datestr.split("-")
        i = 0
        for t in dl:
            dl[i] = int(t)
            i += 1
        date = datetime.date(*dl)
        delta = date - date.today()
        if delta.days < 0:
            raise ValueError
        self.expire = delta.days

class _KeytoCard(_Interact):
    def __init__(self, master, fpr, slot, overwrite):
        super().__init__(master, fpr)
        self.slot = slot
        self.overwrite = overwrite

def _revokekey(status, args, rk):
    rk.log.info("%s(%s)" % (status, args))
    ret = ""
    if "GET" not in status:
        return None
    elif rk.step == 0:
        ret = "key %d" % rk.keynum
    elif rk.step == 1:
        ret = "revkey"
    elif rk.step == 2:
        ret = "yes"
    elif rk.step == 3:
        ret = rk.code
    elif rk.step == 4:
        ret = rk.text
    elif rk.step == 5:
        pass
    elif rk.step == 6:
        ret = "yes"
    elif rk.step == 7:
        ret = "save"
    rk.log.info("%d: %s" % (rk.step, ret))
    rk.step += 1
    return ret

def revokekey(gk, fpr, code, text):
    rk = _Revoke(gk._master, fpr, code, text)
    gk._ctx.interact(gk._master, _revokekey, fnc_value=rk)

def _expirekey(status, args, exp):
    exp.log.info("%s(%s)" % (status, args))
    ret = ""
    if "GET" not in status:
        return None
    elif exp.step == 0:
        ret = "key %d" % exp.keynum
    elif exp.step == 1:
        ret = "expire"
    elif exp.step == 2:
        ret = str(exp.expire)
    elif exp.step == 3:
        ret = "save"
    exp.log.info("%d: %s" % (exp.step, ret))
    exp.step += 1
    return ret

def expirekey(gk, fpr, date):
    exp = _Expire(gk._master, fpr, date)
    gk._ctx.interact(gk._master, _expirekey, fnc_value=exp)

def _keytocard(status, args, kc):
    kc.log.info("%s(%s)" % (status, args))
    ret = ""
    if "GET" not in status:
        return None
    if args == "cardedit.genkeys.replace_key":
        if kc.overwrite:
            return "yes"
        else:
            raise OverwriteError
    elif kc.step == 0:
        ret = "key %d" % kc.keynum
    elif kc.step == 1:
        ret = "keytocard"
    elif kc.step == 2:
        ret = kc.slot
    elif kc.step == 3:
        ret = "save"
    kc.log.info("%d: %s" % (kc.step, ret))
    kc.step += 1
    return ret

def keytocard(gk, fpr, slot, overwrite=False):
    kc = _KeytoCard(gk._master, fpr, slot, overwrite)
    gk._ctx.interact(gk._master, _keytocard, fnc_value=kc)

class OverwriteError(Exception):
    pass
class NoKeyError(ValueError):
    pass
