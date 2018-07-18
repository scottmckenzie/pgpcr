import gpg
import logging
from pgpcr import context

_log = logging.getLogger(__name__)

class NoSmartcardDetected(Exception):
    pass
class BadPIN(Exception):
    pass
class PINBlocked(BadPIN):
    pass
class OverwriteError(Exception):
    pass
class SocketNotFound(Exception):
    pass
class UnsupportedOperation(Exception):
    pass
class SmartcardError(Exception):
    def __init__(self, msg=""):
        self.msg = msg

    def __str__(self):
        return self.msg

def _raiseerr(err):
    _log.info("Smartcard Error: err.code_str")
    if err.code_str == "Card Removed" or err.code_str == "No such device":
        raise NoSmartcardDetected
    elif err.code_str == "Bad PIN":
        raise BadPIN
    elif err.code_str == "PIN Blocked":
        raise PINBlocked
    elif err.code_str == "File exists":
        raise OverwriteError
    elif err.code_str == "IPC connect call failed":
        raise SocketNotFound
    else:
        raise SmartcardError(str(err))

class Smartcard(context.Context):
    def __init__(self, homedir=None):
        self.__status = None
        self.__args = None
        context.launchagent(homedir)
        if homedir == context.defaulthome:
            homedir = None
        self._ctx = gpg.Context(protocol=gpg.constants.protocol.ASSUAN,
                home_dir=homedir)
        if homedir is not None:
            _log.info(homedir)
        try:
            err = self._ctx.assuan_transact("SCD LEARN --force",
                status_cb=self._assuanlearn)
        except gpg.errors.GPGMEError as e:
            err = e
        if err:
            _raiseerr(err)
        self.new = False
        if self.name is None:
            self.new = True

    def _assuanlearn(self, status, args):
        if status == "READER":
            self.reader = args.split(" ")[:3]
            self.vendor = self.reader[0]
            self.reader = " ".join(self.reader)

    def _scd(self, command):
        com = "SCD "
        com += command
        _log.info(com)
        err = self._ctx.assuan_transact(com, status_cb=self._assuanstatus)
        if err:
            _raiseerr(err)
        return (self.__status, self.__args)

    def _assuanstatus(self, status, args):
        _log.info("%s(%s)" % (status, args))
        self.__status = status
        self.__args = args

    def _getattr(self, attr):
        status, args = self._scd("GETATTR "+attr)
        if args == "":
            return None
        return args

    def _setattr(self, attr, value):
        self._scd("SETATTR "+attr+" "+value)

    @property
    def name(self):
        l = self._getattr("DISP-NAME")
        if l is None:
            return l
        return l.split("<<")

    @name.setter
    def name(self, val):
        l = val.split(" ")
        l[0], l[1] = l[1], l[0]
        l = "<<".join(l)
        self._setattr("DISP-NAME", l)

    @property
    def lang(self):
        return self._getattr("DISP-LANG")

    @lang.setter
    def lang(self, val):
        self._setattr("DISP-LANG", val)

    @property
    def sex(self):
        return sexoptsm[int(self._getattr("DISP-SEX"))]

    @sex.setter
    def sex(self, val):
        if val is not None and val not in sexopt.keys():
            raise ValueError("Sex must be either Male, Female, or Unknown")
        self._setattr("DISP-SEX", str(sexopt[val]))

    @property
    def url(self):
        return self._getattr("PUBKEY-URL")

    @url.setter
    def url(self, val):
        self._setattr("PUBKEY-URL", val)

    @property
    def login(self):
        return self._getattr("LOGIN-DATA")

    @login.setter
    def login(self, val):
        self._setattr("LOGIN-DATA", val)

    def generate(self, slot, force=False):
        gen = "GENKEY "
        if force:
            gen += "--force "
        gen += str(slot)
        self._scd(gen)

    @property
    def fullserial(self):
        return self._getattr("SERIALNO")

    @property
    def serial(self):
        return self.fullserial[-12:-4]


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
        self._scd("PASSWD 1")

    def setAdminPIN(self):
        self._scd("PASSWD 3")

sexopt = {"m": 1, "f": 2, "u": 9}
sexoptsm = {}
for k, v in sexopt.items():
    sexoptsm[v] = k
