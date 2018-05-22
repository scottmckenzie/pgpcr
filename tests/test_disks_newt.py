from pgpcr import disks_newt
import unittest, snack

class testDisksNewt(unittest.TestCase):
	def setUp(self):
		self.screen = snack.SnackScreen()

	def tearDown(self):
		self.screen.finish()

	def test_pickdisks(self):
		disks_newt.pickdisks(self.screen, "TEST")
