from snack import *
from . import gpg_ops, common_newt as common

def new(screen, workdir):
	gk = gpg_ops.GPGKey(workdir.name)
	ew = EntryWindow(screen, "New GPG Key", "Enter User Information", ["Name", "Email Address"])
	name = ew[1][0]
	email = ew[1][1]
	pw = common.new_password(screen)
	common.alert(screen, "Key Generation", "GPG keys will now be generated. Progress is estimated and this may take a while. You will be prompted for your password several times.")
	gk.set_password(common.password, screen)
	mprog = common.Progress(screen, "Key Generation", "Generating Master Key...", 50)
	gk.set_progress(progress, mprog)
	gk.genmaster(name+" <"+email+">",pw)
	sprog = common.Progress(screen, "Key Generation", "Generating Sub Keys...", 50)
	gk.set_progress(progress, sprog)
	gk.gensub()
	screen = SnackScreen()
	common.alert(screen, "Key Generation", "Key Generation Complete!")

def progress(what, type, current, total, prog):
	if what == "primegen":
		prog.inc(1)
