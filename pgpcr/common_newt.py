from snack import *

width = 40
padding = (0, 0, 0, 1)

def new_password(screen):
	pass1 = Entry(20, password=1)
	pass2 = Entry(20, password=1)
	ew = EntryWindow(screen, "Password", "Enter your password", [("Password:", pass1), ("Password (again):", pass2)])
	if pass1.value() != pass2.value():
		error("Passwords do not match!")
		return password()
	elif pass1.value() == "":
		error("Password cannot be empty!")
		return password()
	return pass1.value()

def password(hint, desc, prev_bad, screen):
	if hint is None:
		hint = "Password"
	if desc is None:
		desc = "Enter your password"
	p = Entry(20, password=1)
	label = "Password"
	if prev_bad:
		label += " (again)"
	label += ":"
	ew = EntryWindow(screen, hint, desc, [(label, p)], allowCancel=0)
	return p.value()

def alert(screen, title, msg):
	ButtonChoiceWindow(screen, title, msg, ['Ok'])

def error(screen, msg):
	alert(screen, "Error", msg)

class Progress:
	def __init__(self, screen, title, text, total, current=0):
		self.screen = screen
		self.current = current
		self.g = GridFormHelp(self.screen, title, None, 1, 2)
		t = TextboxReflowed(width, text)
		self.p = Scale(width, total)
		self.p.set(current)
		self.g.add(t, 0, 0, padding=padding)
		self.g.add(self.p, 0, 1, padding=padding)
		self.refresh()

	def set(self, prog):
		self.current = prog
		self.refresh()

	def refresh(self):
		self.p.set(self.current)
		self.g.draw()
		self.screen.refresh()

	def inc(self, prog):
		self.current += prog
		self.refresh()

def catchCPE(e):
	s = " ".join(e.cmd)
	if e.stderr is not None:
		alert(screen, s, e.stderror)
	else:
		error(screen, s)
