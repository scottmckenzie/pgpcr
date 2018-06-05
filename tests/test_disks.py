from pgpcr import disks
import unittest


class testDisks(unittest.TestCase):
    def test_getdisks(self):
        gd = disks.getdisks()
        self.assertIsNotNone(gd)
