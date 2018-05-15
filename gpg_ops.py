import gpg

class GPGKey:

	def __init__(self, home, progress):
		self.ctx = gpg.Context(home_dir=home)
		self.masteralgo = "rsa4096"
		self.subalgo = "rsa2048"
		self.ctx.set_progress_cb(progress)

	def genmaster(self, userid, password):
		self.master = ctx.create_key(userid, algorithm=masteralgo, sign=True, certify=True, passphrase=password)

	def gensub(master, algo=self.subalgo):
		self.subsig = ctx.create_subkey(master, algorithm=algo, sign=True)
		self.subenc = ctx.create_subkey(master, algorithm=algo, encrypt=True)
		self.subauth = ctx.create_subkey(master, algorithm=algo, authenticate=auth)
