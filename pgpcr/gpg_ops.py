import gpg

class GPGKey:

	def __init__(self, home):
		self.ctx = gpg.Context(home_dir=home, pinentry_mode=gpg.constants.PINENTRY_MODE_LOOPBACK)
		self.masteralgo = "rsa4096"
		self.subalgo = "rsa2048"

	def genmaster(self, userid, password):
		genkey = self.ctx.create_key(userid, algorithm=self.masteralgo, sign=True, certify=True, passphrase=password)
		self.master = self.ctx.get_key(genkey.fpr)

	def gensub(self):
		self.subsig = self.ctx.create_subkey(self.master, algorithm=self.subalgo, sign=True)
		self.subenc = self.ctx.create_subkey(self.master, algorithm=self.subalgo, encrypt=True)
		self.subauth = self.ctx.create_subkey(self.master, algorithm=self.subalgo, authenticate=True)

	def set_progress(self, progress, hook=None):
		self.ctx.set_progress_cb(progress, hook)

	def set_password(self, password, hook=None):
		self.ctx.set_passphrase_cb(password, hook)


# Below callbacks pulled directly from callbacks.py in GPGME
def _test_progress(what, type, current, total, hook=None):
	print("PROGRESS UPDATE: what = %s, type = %d, current = %d, total = %d" %\
		(what, type, current, total))

def _test_password(hint, desc, prev_bad, hook=None):
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

if __name__ == "__main__":
	import tempfile
	tmp = tempfile.TemporaryDirectory()
	gk = GPGKey(tmp.name)
	gk.set_progress(_test_progress)
	gk.set_password(_test_password)	
	print("Generating masterkey...")
	# if passphrase is true, gpgme will call the password callback to get a password
	gk.genmaster("Test <test@example.com>", True)
	print("Generating subkeys...")
	gk.gensub()
