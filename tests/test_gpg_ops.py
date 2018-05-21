import tempfile, unittest
from pgpcr import gpg_ops

class GPGOpsTests(unittest.TestCase):
	def setUp(self):
		self.tmp = tempfile.TemporaryDirectory()
		self.gk = gpg_ops.GPGKey(self.tmp.name)

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
		self.gk.set_progress(self._progress)
		self.gk.set_password(self._password)
		print("\nGenerating masterkey...")
		self.gk.genmaster("Test <test@example.com>")
		print("Generating subkeys...")
		self.gk.gensub()

if __name__ == "__main__":
	unittest.main()
