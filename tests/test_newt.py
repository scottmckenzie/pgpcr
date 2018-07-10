from pgpcr import newt
import unittest
import snack
from time import sleep
from os import environ
import tests.helpers

@unittest.skipUnless("PGPCRINTERACT" in environ.keys(), "Interactive tests"
        " disabled. Set PGPCRINTERACT to enable them")
class newtTest(unittest.TestCase):
    def setUp(self):
        self.Screen = newt.Screen()

    def tearDown(self):
        self.Screen.finish()

    def test_alert(self):
        newt.alert(self.Screen, "test", "test alert")

    def test_dangerConfirm(self):
        d = newt.dangerConfirm(self.Screen, "TEST", "Press NO")
        self.assertTrue(not d)
    def test_progress(self):
        prog = newt.Progress(
            self.Screen, "Test Progress", "This is a test", 100)
        for i in range(100):
            prog.set(i)
            prog.setText(str(i))
            sleep(0.01)

    def test_checkboxchoicewindow(self):
        newt.CCW(self.Screen, "Test Checkboxes", "This is a test",
                ["one", "two", "three"], help="test help")

    def test_CatchCPE(self):
        e = _cpetest()
        self.assertIsInstance(e.stderr, bytes)
        newt.catchCPE(self.Screen, e)


class _cpetest:
    def __init__(self):
        self.stdout = "test".encode()
        self.stderr = "test error".encode()
        self.cmd = ["this", "is", "a", "test"]
