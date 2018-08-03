import json
from . import external
from . import log

_log = log.getlog(__name__)

_prop = {
    "name": "CA_NAME",
    "CAValid": "CA_VALIDITY_DAYS",
    "domain": "CA_DN",
    "serverValid": "SERVER_VALIDITY_DAYS",
    "keyType": "KEY_TYPE",
    "keySize": "KEY_SIZE",
    "digest": "CERT_DIGEST"
}

class CA:
    def __init__(self, workdir, filename=None):
        self._workdir = workdir

        if filename is not None:
            f = open(filename)
            j = json.load(f)
            f.close()
            self._dict = j
        else:
            self._dict = {}


    @property
    def _key(self):
        return self._workdir+"/"+self.name+"Key.pem"

    @property
    def _cert(self):
        return self._workdir+"/"+self.name+"Cert.pem"

    def save(self):
        with open(self._workdir+"/ca.json", "w+") as f:
            json.dump(self._dict, f)

    def __getattr__(self, name):
        _log.info("Get %s" % name)
        prop = _prop[name]
        return self._dict[prop]

    def __setattr__(self, name, value):
        _log.info("Set %s = %s" % (name, str(value)))
        if name not in _prop:
            super().__setattr__(name, value)
        else:
            prop = _prop[name]
            self._dict[prop] = value

    def _pki(self, options, filename):
        com = ["pki"]
        com.extend(options)
        external.processtofile(com, filename)

    def genroot(self):
        self._pki(["--gen", "--type", self.keyType, "--size", self.keySize,
            "--outform", "pem"], self._key)
        self._pki(["--self", "--type", self.keyType, "--digest", self.digest,
            "--in", self._key, "--dn", self.domain, "--lifetime", self.CAValid,
            "--ca", "--outform", "pem"], self._cert)

    def signserver(self, csr):
        pass
