from pgpcr import disks_newt
import unittest
from unittest.mock import patch
import snack
import tempfile
from os import environ
import tests.disks_mock

@unittest.skipUnless("PGPCRINTERACT" in environ.keys(), "Interactive tests"
        " disabled. Set PGPCRINTERACT to enable them")
class testDisksNewt(unittest.TestCase):
    def setUp(self):
        self.screen = snack.SnackScreen()
        self.tmp = tempfile.TemporaryDirectory()
        with open(self.tmp.name+"/testfile", "w") as f:
            f.write("this is a test. please ignore")

    def tearDown(self):
        self.screen.finish()
        self.tmp.cleanup()

    def test_pickdisks(self):
        disks_newt.pickdisks(self.screen, "PICKDISKS TEST")

    @patch.dict('sys.modules', {'pgpcr.disks': tests.disks_mock})
    @unittest.skip("Mocking doesn't actually work yet")
    def test_store(self):
        disks_newt.store(self.screen, self.tmp, "STORETEST")
