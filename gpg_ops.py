import gpg

ctx = None

masteralgo = "rsa4096"
subalgo = masteralgo

def init(home):
	global ctx
	ctx = gpg.Context(home_dir=home)

def genmaster(userid):
	return ctx.create_key(userid, algorithm=masteralgo, sign=True, certify=True)

def gensub(master, algorithm=subalgo, sig=False, enc=False, auth=False):
	return ctx.create_subkey(master, algorithm=subkeyalgo, sign=sig, encrypt=enc, authenticate=auth)
