from snack import *
from . import gpg_ops, common_newt as common

def new(screen, workdir):
	gk = gpg_ops.GPGKey(workdir.name, progress)
	ew = EntryWindow(screen, "New GPG Key", "Enter User Information", ["Name", "Email Address"])
	name = ew[1][0]
	email = ew[1][1]
	pw = common.password(screen)
	gk.genmaster(name+" <"+email+">",pw)
	gk.gensub()

def progress(what, type, current, total):
	print(what, type, current, "/", total)
