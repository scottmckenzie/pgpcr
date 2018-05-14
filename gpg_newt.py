from snack import *
from . import common_newt

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
	screen = SnackScreen()
	ew = EntryWindow(screen, "New GPG Key", "Enter User Information", ["Name", "Email Address"])
	screen.finish()
	name = ew[1][0]
	email = ew[1][1]
	pw = common.password()
	print(name,email,pw)
