from snack import *

width = 40
padding = (0, 0, 0, 1)

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

class Progress:
	def __init__(self, title, text, total, current=0):
		self.title = title
		self.text = text
		self.total = total
		self.current = current
		self.screen = SnackScreen()
		g = GridFormHelp(self.screen, title, None, 1, 2)
		t = TextboxReflowed(width, text)
		self.p = Scale(width, total)
		self.p.set(current)
		g.add(t, 0, 0, padding=padding)
		g.add(p, 0, 1, padding=padding)
		g.runOnce()
		self.screen.finish()

	def progress(prog):
		self.p.set(prog)
		self.screen.refresh()
