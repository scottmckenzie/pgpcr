import gpg

class GPGKey:

	def __init__(self, home):
		self._ctx = gpg.Context(home_dir=home)
		self._masteralgo = "rsa4096"
		self._subalgo = "rsa2048"

	def genmaster(self, userid):
		genkey = self._ctx.create_key(userid, algorithm=self._masteralgo, sign=True, certify=True, passphrase=True)
		self._master = self._ctx.get_key(genkey.fpr)

	def gensub(self):
		self._subsig = self._ctx.create_subkey(self._master, algorithm=self._subalgo, sign=True)
		self._subenc = self._ctx.create_subkey(self._master, algorithm=self._subalgo, encrypt=True)
		self._subauth = self._ctx.create_subkey(self._master, algorithm=self._subalgo, authenticate=True)

	def setprogress(self, progress, hook=None):
		self._ctx.set_progress_cb(progress, hook)

	def setpassword(self, password, hook=None):
		self._ctx.set_passphrase_cb(password, hook)

	def setalgorithms(self, master, sub):
		if master is not None:
			self._masteralgo = master
		if sub is not None:
			self._subalgo = sub

	def masterfpr(self):
		return self._master.fpr

GPGMEError = gpg.errors.GPGMEError
