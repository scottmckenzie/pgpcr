import tempfile
import unittest
from pgpcr import gpg_ops


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
        why = ''
        if hook != None:
            why = ' ' + hook
        if prev_bad:
            why += ' (again)'
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
        print("\nGenerated master key", self.gk.masterfpr())
        print("Generating subkeys...")
        self.gk.gensub()


class GPGOpsTestKey(unittest.TestCase):

    def test_export(self):
        self.gk.export(self.tmp.name)
        self._cmpfiles(self.testkeydir, self.tmp.name,
                       self.gk.masterfpr()+".pub")

    def test_export_subkeys(self):
        self.gk.exportsubkeys(self.tmp.name)
        self._cmpfiles(self.testkeydir, self.tmp.name,
                       self.gk.masterfpr()+".subsec")

    def _cmpfiles(self, a, b, name):
        with open(a+"/"+name, "rb") as f1, open(b+"/"+name, "rb") as f2:
            self.assertEqual(f1.read(), f2.read())

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        # Directory where the test key is stored
        self.testkeydir = "tests/testkey"
        self.testkeyfpr = "074D3879D4609448DEF716F6C7B98BC88227953F"
        self.gk = gpg_ops.GPGKey(self.tmp.name+"/"+self.testkeyfpr,
                                 self.testkeyfpr, self.testkeydir)

    def tearDown(self):
        self.tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
