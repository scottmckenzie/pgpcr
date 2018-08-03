import json
import shutil
from collections import OrderedDict
from . import external
from . import log
from . import time


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

keyTypes = OrderedDict([
    ("rsa", ["4096", "3072", "2048"]),
    ("ecdsa", ["521", "384", "256"])
    ])
digests = ["sha256", "sha512", "sha384", "sha224", "sha1", "md5"]

class CA:
    def __init__(self, workdir, loaddir=None):
        self._workdir = workdir

        if loaddir is not None:
            shutil.rmtree(workdir)
            shutil.copytree(loaddir, workdir)
            f = open(workdir+"/ca.json")
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
            self._dict[prop] = str(value)

    def _pki(self, options, filename=None):
        com = ["pki"]
        com.extend(options)
        if filename is not None:
            try:
                external.processtofile(com, filename)
            except external.CalledProcessError as e:
                _log.info(e.stderr)
                raise e
        else:
            try:
                return external.process(com)
            except external.CalledProcessError as e:
                _log.info(e.stderr)
                raise e

    def genroot(self):
        self._pki(["--gen", "--type", self.keyType, "--size", self.keySize,
            "--outform", "pem"], self._key)
        self._pki(["--self", "--type", self.keyType, "--digest", self.digest,
            "--in", self._key, "--dn", "CN="+self.domain,
            "--lifetime", self.CAValid, "--ca", "--outform", "pem"],
            self._cert)

    def signserver(self, csr):
        subject = external.process(["openssl", "req", "-noout", "-in", csr,
            "-subject"])
        domain = subject.stdout[13:-1]
        _log.info("subject %s domain=%s" % (subject.stdout, domain))
        servercert = self._workdir+time.today()+"_"+domain+"_cert.pem"
        csrpub = self._pki(["--pub", "--type", "pkcs10", "--outform", "pem",
            "--in", csr])
        _log.info(csrpub.stdout)
        self._pki(["--issue", "--cacert", self._cert, "--cakey", self._key,
            "--digest", self.digest, "--lifetime", self.serverValid,
            "--flag", "serverAuth", "--flag", "clientAuth", "--san", domain,
            "--dn", "CN="+domain, "--outform", "pem"], servercert)
