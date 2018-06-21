import gpg
import os
import logging

_log = logging.getLogger(__name__)

class NoSmartcardError(Exception):
    pass

def getsmartcard(gk):
    try:
        return Smartcard(gk._ctx, gk._master)
    except NoSmartcardError:
        return None

class Smartcard:
    def __init__(self, ctx, key):
        self._ctx = ctx
        self._key = key
        self._getprop()
        self.new = False
        if self.name == ["", ""]:
            self.new = True

    def _getprop(self):
        data = gpg.Data()
        self._ctx.interact(self._key, lambda status, args: "quit"
                if status == "GET_LINE" else None, data,
                gpg.constants.INTERACT_CARD)
        data.seek(0, os.SEEK_SET)
        props = data.read()
        _log.debug(props)
        proplist = props.decode().split("\n")
        if proplist[0] == "AID:::":
            raise NoSmartcardError
        self.reader = " ".join(proplist[0].split(":")[1].split(" ")[:3])
        self.vendor = proplist[2].split(":")[2]
        self.serial = proplist[3].split(":")[1]
        self._name = proplist[4].split(":")[1:3]
        self._lang = proplist[5].split(":")[1]
        self._sex = proplist[6].split(":")[1]
        self._url = proplist[7].split(":")[1]
        self._login = proplist[8].split(":")[1]

    def _setprop(self, prop, value):
        inter = _Property(prop, value)
        self._ctx.interact(self._key, _cardsetprop,
                flags=gpg.constants.INTERACT_CARD, fnc_value=inter)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        l = val.split(" ")
        self._setprop("name", l)
        self._getprop()

    @property
    def lang(self):
        return self._lang

    @lang.setter
    def lang(self, val):
        self._setprop("lang", val)
        self._getprop()

    @property
    def sex(self):
        return self._sex

    @sex.setter
    def sex(self, val):
        if val not in sexopt:
            raise ValueError("Sex must be either Male, Female, or Unknown")
        self._setprop("sex", val)
        self._getprop()

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, val):
        self._setprop("url", val)
        self._getprop()

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, val):
        self._setprop("login", val)
        self._getprop()

    def generate(self, uid, backup=False):
        inter = _Genkeys(uid, backup)
        self._ctx.interact(self._key, _cardgenkeys,
                flags=gpg.constants.INTERACT_CARD, fnc_value=inter)
    @property
    def defaultpins(self):
        return ["123456", "12345678"]

    @property
    def slots(self):
        if self.vendor == "Yubico":
            return ["Signing", "Encryption", "Authentication"]

    def __str__(self):
        return self.reader+" "+self.serial

    def setPIN(self):
        self._ctx.interact(self._key, _setpin,
                flags=gpg.constants.INTERACT_CARD, fnc_value=_Interact())

    def setAdminPIN(self):
        self._ctx.interact(self._key, _setadminpin,
                flags=gpg.constants.INTERACT_CARD, fnc_value=_Interact())


sexopt = ["m", "f", "u"]

class _Interact:
    def __init__(self):
        self.step = 0

class _Property(_Interact):
    def __init__(self, prop, val):
        super().__init__()
        self.prop = prop
        self.val = val

class _Genkeys(_Interact):
    def __init__(self, uid, backup):
        super().__init__()
        self.uid = uid
        self.backup = backup

def _cardsetprop(status, args, inter):
    _log.info("%s(%s)" % (status, args))
    if "GET_LINE" not in status:
        return None
    ret = ""
    if inter.step == 0:
        ret = "admin"
    elif inter.step == 1:
        ret = inter.prop
    elif inter.step == 2:
        if args == "keygen.smartcard.surname":
            ret = inter.val[1]
            inter.step -= 1
        elif args == "keygen.smartcard.givenname":
            ret = inter.val[0]
        else:
            ret = inter.val
    elif inter.step == 3:
        return "quit"
    _log.info("%d %s" % (inter.step, ret))
    inter.step += 1
    return ret

def _cardgenkeys(status, args, inter):
    if "GET" not in status:
        return None
    ret = ""
    if inter.step == 0:
        ret = "generate"
    #TODO: Doesn't seem like this works
    raise NotImplementedError
    inter.step += 1
    return ret

def _setpin(status, args, inter):
    _log.info("%s(%s)" % (status, args))
    if "GET_LINE" not in status:
        return None
    ret = ""
    if inter.step == 0:
        ret = "passwd"
    elif inter.step == 1:
        ret = "save"
    _log.info("%d %s" % (inter.step, ret))
    inter.step += 1
    return ret

def _setadminpin(status, args, inter):
    _log.info("%s(%s)" % (status, args))
    if "GET_LINE" not in status:
        return None
    ret = ""
    if inter.step == 0:
        ret = "passwd"
    elif inter.step == 1:
        ret = "3"
    elif inter.step == 2:
        ret = "save"
    _log.info("%d %s" % (inter.step, ret))
    inter.step += 1
    return ret
