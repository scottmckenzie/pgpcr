from pgpcr import common_newt
import unittest
import snack
from time import sleep
from os import environ
import tests.helpers

@unittest.skipIf("PGPCRINTERACT" not in environ.keys(), "Interactive tests"
        " disabled. Set PGPCRINTERACT to enable them")
class commonNewtTest(unittest.TestCase):
    def setUp(self):
        self.screen = snack.SnackScreen()

    def tearDown(self):
        self.screen.finish()

    def test_alert(self):
        common_newt.alert(self.screen, "test", "test alert")

    def test_dangerConfirm(self):
        d = common_newt.dangerConfirm(self.screen, "TEST", "Press NO")
        self.assertTrue(not d)
    def test_progress(self):
        prog = common_newt.Progress(
            self.screen, "Test Progress", "This is a test", 100)
        for i in range(100):
            prog.set(i)
            prog.setText(str(i))
            sleep(0.01)

    def test_checkboxchoicewindow(self):
        common_newt.CheckboxChoiceWindow(self.screen, "Test Checkboxes",
                                               "This is a test",
                                               ["one", "two", "three"])

    def test_CatchCPE(self):
        e = _cpetest()
        self.assertIsInstance(e.stderr, bytes)
        common_newt.catchCPE(self.screen, e)


class _cpetest:
    def __init__(self):
        self.stdout = "test".encode()
        self.stderr = "test error".encode()
        self.cmd = ["this", "is", "a", "test"]
