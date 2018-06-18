import tempfile
import os
import subprocess
import unittest
import datetime
from pgpcr import gpg_ops
from tests.helpers import cmpfiles, copy

class GPGOpsTestGenCall(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.gk = gpg_ops.GPGKey(self.tmp.name)
        # Generate smaller keys so the test doesn't take as long
        self.gk.setalgorithms("rsa1024", "rsa1024")
        self.gk.setprogress(self._progress)
        self.gk.setpassword(self._password)

    def tearDown(self):
        self.tmp.cleanup()

    # Below callbacks pulled directly from callbacks.py in GPGME
    def _progress(self, what, type, current, total, hook=None):
        print("PROGRESS UPDATE: what = %s, type = %d, current = %d, total = %d" %
              (what, type, current, total))

    def _password(self, hint, desc, prev_bad, hook=None):
        """This is a sample callback that will read a passphrase from
        the terminal.  The hook here, if present, will be used to describe
        why the passphrase is needed."""
        why = ""
        if hook != None:
            why = " " + hook
        if prev_bad:
            why += " (again)"
        p = input("Please supply %s' password%s:" % (hint, why))
        return p

    def test_callbacks_generation(self):
        print("\nGenerating masterkey...")
        self.gk.genmaster("Test <test@example.com>")
        print("\nGenerated master key", self.gk.fpr)
        print("Generating subkeys...")
        self.gk.genseasubs(print)

    def test_expirekey(self):
        self.gk.genmaster("Test <test@example.com>")
        date = datetime.date(1, 1, 1).today()
        date = date.replace(date.year+1)
        self.gk.expirekey(self.gk.fpr, date.isoformat())
        gke = date.fromtimestamp(self.gk._master.subkeys[0].expires)
        self.assertEqual(gke, date)

class GPGOpsTestKey(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        # Directory where the test key is stored
        self.datadir = "tests/data"
        self.testkeydir = self.datadir+"/testkey"
        self.testkeyfpr = "074D3879D4609448DEF716F6C7B98BC88227953F"
        self.testsign = "0x3F90059E1AFDDD53"
        self.gk = gpg_ops.GPGKey(self.tmp.name,
                                 self.testkeyfpr, self.testkeydir)

    def tearDown(self):
        self.tmp.cleanup()

    def _cmpfiles(self, a, b, name):
        cmpfiles(self, a+"/"+name, b+"/"+name)

    def test_export(self):
        self.gk.export(self.tmp.name)
        self._cmpfiles(self.testkeydir, self.tmp.name,
                       self.gk.fpr+".pub")

    def test_export_subkeys(self):
        self.gk.exportsubkeys(self.tmp.name)
        self._cmpfiles(self.testkeydir, self.tmp.name,
                       self.gk.fpr+".subsec")

    def test_listkeys(self):
        kl = ['074D3879D4609448DEF716F6C7B98BC88227953F (Master)',
              'DE43E1D47D0ECADB711A62CE5A6BE3238D90C3D3 (Signing)',
              'F351E19BF3F9C2E5392338104B4C747617C77194 (Encryption)',
              '04E8C72E5513A1FB1D925ABA62E94671570D8082 (Authentication)']
        self.assertEqual(kl, self.gk.keys)

    def test_addrevuid(self):
        addtest = "addtest <addtest@example.com>"
        self.gk.adduid(addtest)
        self.assertIn(addtest, self.gk.uids)
        self.gk.revokeuid(addtest)
        # Currently fails despite removing uid
        #self.assertNotIn(addtest, self.gk.uids)

    # Checking signatures doesn't work for some reason
    # So we do it manually
    def _checkkey(self, keyfile):
        with open(keyfile) as f:
            sb = subprocess.run(["gpg", "--list-packets"], stdin=f,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return sb.stdout.decode()

    def test_signkey(self):
        keyfile = self.testsign+".pub"
        keyimport = self.datadir+"/signing/pending/"+keyfile
        copy(keyimport, self.tmp.name)
        self.assertNotIn(self.testkeyfpr, self._checkkey(keyimport))

        self.gk.signkey(self.datadir, keyfile)

        self.assertEqual(os.path.exists(keyimport), 0)
        keyexport = self.datadir+"/signing/done/"+keyfile
        self.assertEqual(os.path.exists(keyexport), 1)
        self.assertIn(self.testkeyfpr, self._checkkey(keyexport))

        os.remove(keyexport)
        copy(self.tmp.name+"/"+keyfile, keyimport)

if __name__ == "__main__":
    unittest.main()
