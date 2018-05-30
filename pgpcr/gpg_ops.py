import gpg, os

class GPGKey:

	def __init__(self, home,  loadfpr=None):
		self._ctx = gpg.Context(home_dir=home)
		self._masteralgo = "rsa4096"
		self._subalgo = "rsa2048"
		if loadfpr:
			self._master = self._ctx.get_key(loadfpr)
			for k in self._master.subkeys:
				if k.can_certify:
					continue
				if k.can_sign:
					self._subsig = k
				elif k.can_encrypt:
					self._subenc = k
				elif k.can_authenticate:
					self._subauth = k

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

	def _export(self, pattern, mode=0):
		# 0 is the normal mode
		data = gpg.Data()
		self._ctx.op_export(pattern, mode, data)
		data.seek(0, os.SEEK_SET)
		return data.read()

	def export(self, dir):
		d = self._export(self.masterfpr())
		with open(dir+"/"+self.masterfpr()+".pub", "wb") as f:
			f.write(d)

	def exportsubkeys(self, dir):
		for k in [self._subsig, self._subenc, self._subauth]:
			d = self._export(k.fpr, gpg.constants.EXPORT_MODE_SECRET)
			with open(dir+"/"+k.fpr+".sec", "wb") as f:
				f.write(d)

GPGMEError = gpg.errors.GPGMEError
