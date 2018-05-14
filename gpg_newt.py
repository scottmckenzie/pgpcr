from snack import *
from . import gpg_ops, common_newt as common
import tempfile

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

def gengpgkey():
	tmp = tempfile.TemporaryDirectory()
	gpg_ops.init(tmp.name)
	screen = SnackScreen()
	ew = EntryWindow(screen, "New GPG Key", "Enter User Information", ["Name", "Email Address"])
	screen.finish()
	name = ew[1][0]
	email = ew[1][1]
	pw = common.password()
	m = gpg_ops.genmaster(name+" <"+email+">", pw)
	#s, e, a = gpg_ops.gensub(m)
