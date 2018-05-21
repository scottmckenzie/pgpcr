from pgpcr import common_newt
import unittest, snack
from time import sleep

class commonNewtTest(unittest.TestCase):
	def setUp(self):
		self.screen = snack.SnackScreen()

	def tearDown(self):
		self.screen.finish()

	def test_alert(self):	
		common_newt.alert(self.screen, "test", "test alert")

	def test_progress(self):
		prog = common_newt.Progress(self.screen, "Test Progress", "This is a test", 100)
		for i in range(100):
			prog.set(i)
			sleep(0.05)
