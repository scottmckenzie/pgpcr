from snack import *
def password():
	screen = SnackScreen()
	pass1 = Entry(20, password=1)
	pass2 = Entry(20, password=1)
	ew = EntryWindow(screen, "Password", "Enter your password", [("Password:", pass1), ("Password (again):", pass2)])
	screen.finish()
	if pass1.value() != pass2.value():
		error("Passwords do not match!")
		return password()
	elif pass1.value() == "":
		error("Password cannot be empty!")
		return password()
	return pass1.value()

def error(msg):
	screen = SnackScreen()
	ButtonChoiceWindow(screen, "Error", msg, ['Ok'])
	screen.finish()
