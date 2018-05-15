from snack import *
from . import gpg_ops, common_newt as common

def new(screen, workdir):
	gk = gpg_ops.GPGKey(workdir.name, progress)
	ew = EntryWindow(screen, "New GPG Key", "Enter User Information", ["Name", "Email Address"])
	name = ew[1][0]
	email = ew[1][1]
	pw = common.password()
	gk.genmaster(name+" <"+email+">",pw)

def main():
	screen = SnackScreen()
	bcw = ButtonChoiceWindow(screen, "GPG", "What do you wish to do?", [("New GPG Key","new"), ("Mount GPG Key","mount"), ("Quit to Main Menu","quit")])
	screen.finish()
	if bcw == "new":
		gengpgkey()
		print("Not Implemented Yet")
	elif bcw == "mount":
		print("Not Implemented Yet")
	else:
		print(bcw)

def progress(what, type, current, total):
	print(what, type, current, "/", total)
