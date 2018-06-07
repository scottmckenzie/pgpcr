from pgpcr import common_newt
import unittest
import snack
from time import sleep

class commonNewtTest(unittest.TestCase):
    def setUp(self):
        self.screen = snack.SnackScreen()

    def tearDown(self):
        self.screen.finish()

    def test_alert(self):
        common_newt.alert(self.screen, "test", "test alert")

    def test_progress(self):
        prog = common_newt.Progress(
            self.screen, "Test Progress", "This is a test", 100)
        for i in range(100):
            prog.set(i)
            prog.setText(str(i))
            sleep(0.01)

    def test_CatchCPE(self):
        e = _cpetest()
        self.assertIsInstance(e.stderr, bytes)
        common_newt.catchCPE(self.screen, e)


class _cpetest:
    def __init__(self):
        self.stdout = "test".encode()
        self.stderr = "test error".encode()
        self.cmd = ["this", "is", "a", "test"]
