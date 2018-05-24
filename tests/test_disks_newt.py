from pgpcr import disks_newt
import unittest, snack, tempfile

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

	@unittest.skip
	def test_store(self):
		disks_newt.store(self.screen, self.tmp, "STORETEST")
