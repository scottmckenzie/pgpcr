from snack import *
from . import common

def main():
	screen = SnackScreen()
	bcw = ButtonChoiceWindow(screen, "GPG", "What do you wish to do?", ["New GPG Key", "Mount GPG Key", "Quit to Main Menu"])
	screen.finish()
	if bcw == "new gpg key":
		gengpgkey()
		print("Not Implemented Yet")
	elif bcw == "mount gpg key":
		print("Not Implemented Yet")

def gengpgkey():
	screen = SnackScreen()
	ew = EntryWindow(screen, "New GPG Key", "Enter User Information", ["Name", "Email Address"])
	screen.finish()
	name = ew[1][0]
	email = ew[1][1]
	pw = common.password()
	print(name,email,pw)
