import json
from pgpcr import external

class CA:
    def __init__(self, workdir, filename=None):
        self._prop = {
                "name": "CA_NAME",
                "CAValid": "CA_VALIDITY_DAYS",
                "DN": "CA_DN",
                "ServerValid": "SERVER_VALIDITY_DAYS",
                "keyType": "KEY_TYPE",
                "keySize": "KEY_SIZE",
                "digest": "CERT_DIGEST"
                }
        self._workdir = workdir
        self._key = workdir+"/"+self.name+"Key.pem"
        self._cert = workdir+"/"+self.name+"Cert.pem"

        if filename is not None:
            f = open(filename)
            j = json.load(f)
            f.close()
            self._dict = j
        else:
            self._dict = {}

    def save(self, filename):
        with open(filename) as f:
            json.dump(self._dict,f)

    def __getattr__(self, name):
        prop = self._prop[name]
        return self._dict[prop]

    def __setattr__(self, name, value):
        prop = self._prop[name]
        self._dict[prop] = value

    def _pki(options, filename):
        com = ["pki"]
        com.extend(options)
        external.processtofile(com, filename)

    def genroot(self, workdir):
        self._pki(["--gen", "--type", self.keyType, "--size", self.keySize,
            "--outform", "pem"], self._key)
        self._pki(["--self", "--type", self.keyType, "--digest", self.digest,
            "--in", self._key, "--dn", self.DN, "--lifetime", self.CAValid,
            "--ca", "--outform", "pem"], self._cert)

    def signserver(self, csr):
        pass
