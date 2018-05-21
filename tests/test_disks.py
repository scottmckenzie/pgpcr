from pgpcr import disks
import unittest

class testDisks(unittest.TestCase):
	def test_getdisks(self):
		gd = disks.getdisks()
		self.assertNotEqual(gd, [])
		for x in gd:
			self.assertEqual(x['tran'], "usb")
