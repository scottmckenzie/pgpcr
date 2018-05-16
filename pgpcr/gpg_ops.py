import gpg

class GPGKey:

	def __init__(self, home, progress=None):
		self.ctx = gpg.Context(home_dir=home)
		self.masteralgo = "rsa4096"
		self.subalgo = "rsa2048"
		self.ctx.set_progress_cb(progress)

	def genmaster(self, userid, password):
		self.master = self.ctx.create_key(userid, algorithm=self.masteralgo, sign=True, certify=True, passphrase=password)

	def gensub(self):
		self.subsig = self.ctx.create_subkey(self.master, algorithm=self.subalgo, sign=True)
		self.subenc = self.ctx.create_subkey(self.master, algorithm=self.subalgo, encrypt=True)
		self.subauth = self.ctx.create_subkey(self.master, algorithm=self.subalgo, authenticate=True)
