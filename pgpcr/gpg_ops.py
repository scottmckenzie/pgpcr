import gpg

class GPGKey:

	def __init__(self, home):
		self.ctx = gpg.Context(home_dir=home)
		self.masteralgo = "rsa4096"
		self.subalgo = "rsa2048"

	def genmaster(self, userid):
		genkey = self.ctx.create_key(userid, algorithm=self.masteralgo, sign=True, certify=True, passphrase=True)
		self.master = self.ctx.get_key(genkey.fpr)

	def gensub(self):
		self.subsig = self.ctx.create_subkey(self.master, algorithm=self.subalgo, sign=True)
		self.subenc = self.ctx.create_subkey(self.master, algorithm=self.subalgo, encrypt=True)
		self.subauth = self.ctx.create_subkey(self.master, algorithm=self.subalgo, authenticate=True)

	def set_progress(self, progress, hook=None):
		self.ctx.set_progress_cb(progress, hook)

	def set_password(self, password, hook=None):
		self.ctx.set_passphrase_cb(password, hook)


error = gpg.errors.GPGMEError
