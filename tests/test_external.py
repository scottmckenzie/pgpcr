from pgpcr import external

import unittest
import os
import tempfile
from tests.helpers import cmpfiles

class externalProcessTest(unittest.TestCase):

    def _checkrettype(self, ret, t):
        self.assertIsInstance(ret.stdout, t)
        self.assertIsInstance(ret.stderr, t)

    def setUp(self):
        os.environ["GNUPGHOME"] = "tests/data/testkey"
        self.export = "tests/data/testfile"
        self.cmd = ["gpg", "--export", "-a"]

    def test_ProcessB(self):
        ret = external.processb(self.cmd)
        self._checkrettype(ret, bytes)

    def test_Process(self):
        ret = external.process(self.cmd)
        self._checkrettype(ret, str)

    def test_ProcessToFile(self):
        temp = tempfile.NamedTemporaryFile()
        ret = external.processtofile(self.cmd, temp.name)
        cmpfiles(self, self.export, temp.name)
        temp.close()
