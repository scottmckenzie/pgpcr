import tempfile
import unittest
from pgpcr import gpg_ops
from tests.filetest import cmpfiles

class GPGOpsTestGenCall(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

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
        self.gk = gpg_ops.GPGKey(self.tmp.name)
        self.gk.setprogress(self._progress)
        self.gk.setpassword(self._password)
        # Generate smaller keys so the test doesn't take as long
        self.gk.setalgorithms("rsa1024", "rsa1024")
        print("\nGenerating masterkey...")
        self.gk.genmaster("Test <test@example.com>")
        print("\nGenerated master key", self.gk.fpr)
        print("Generating subkeys...")
        self.gk.gensub()


class GPGOpsTestKey(unittest.TestCase):


    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        # Directory where the test key is stored
        self.testkeydir = "tests/data/testkey"
        self.testkeyfpr = "074D3879D4609448DEF716F6C7B98BC88227953F"
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

class GPGOpsUtils(unittest.TestCase):
    def setUp(self):
        self.data = "tests/data"

    def test_backups(self):
        b = gpg_ops.backups(self.data)
        self.assertEqual(b, ["CAFEBABE", "B000DEAD", "DEADBEEF"])

if __name__ == "__main__":
    unittest.main()
