import tempfile, unittest
from pgpcr import gpg_ops

class GPGOpsTests(unittest.TestCase):
	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		# Directory where the test key is stored
		self.testkeydir = "tests/testkey"
		self.testkeyfpr = "074D3879D4609448DEF716F6C7B98BC88227953F"

	def tearDown(self):
		self.tmp.cleanup()

	# Below callbacks pulled directly from callbacks.py in GPGME
	def _progress(self, what, type, current, total, hook=None):
		print("PROGRESS UPDATE: what = %s, type = %d, current = %d, total = %d" %\
			(what, type, current, total))

	def _password(self, hint, desc, prev_bad, hook=None):
		"""This is a sample callback that will read a passphrase from
		the terminal.  The hook here, if present, will be used to describe
		why the passphrase is needed."""
		why = ''
		if hook != None:
			why = ' ' + hook
		if prev_bad:
			why += ' (again)'
		p = input("Please supply %s' password%s:" % (hint, why))
		return p
	
	def test_callbacks_generation(self):
		self.gk = gpg_ops.GPGKey(self.tmp.name)
		self.gk.setprogress(self._progress)
		self.gk.setpassword(self._password)
		# Generate smaller keys so the test doesn't take as long
		self.gk.setalgorithms("rsa1024", "rsa1024")
		print("\nGenerating masterkey...")
		self.gk.genmaster("Test <test@example.com>")
		print("\nGenerated master key", self.gk.masterfpr())
		print("Generating subkeys...")
		self.gk.gensub()

	def test_export(self):
		self.gk = gpg_ops.GPGKey(self.testkeydir, self.testkeyfpr)
		self.gk.export(self.tmp.name)
		with open(self.tmp.name+"/"+self.gk.masterfpr()+".pub", "rb") as f:
			with  open(self.testkeydir+"/"+self.testkeyfpr+".pub", "rb") as a:
				self.assertEqual(a.read(), f.read())

if __name__ == "__main__":
	unittest.main()
