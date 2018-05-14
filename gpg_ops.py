import gpg

ctx = None

masteralgo = "rsa4096"
subalgo = masteralgo

def init(home):
	global ctx
	ctx = gpg.Context(home_dir=home)

def genmaster(userid, password):
	return ctx.create_key(userid, algorithm=masteralgo, sign=True, certify=True, passphrase=password)

def gensub(master, algo=subalgo):
	s = ctx.create_subkey(master, algorithm=algo, sign=True)
	e = ctx.create_subkey(master, algorithm=algo, encrypt=True)
	a = ctx.create_subkey(master, algorithm=algo, authenticate=auth)
	return (s, e, a)
