from snack import *

width = 40
padding = (0, 0, 0, 1)

def password(screen):
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

def alert(screen, title, msg):
	ButtonChoiceWindow(screen, title, msg, ['Ok'])

def error(screen, msg):
	alert(screen, "Error", msg)

class Progress:
	def __init__(self, screen, title, text, total, current=0):
		self.screen = screen
		self.current = current
		g = GridFormHelp(self.screen, title, None, 1, 2)
		t = TextboxReflowed(width, text)
		b = ButtonBar(screen, ['Close'])
		self.p = Scale(width, total)
		self.p.set(current)
		g.add(t, 0, 0, padding=padding)
		g.add(self.p, 0, 1, padding=padding)
		g.draw()

	def set(self, prog):
		self.current = prog
		self.refresh()

	def refresh(self):
		self.p.set(self.current)
		self.screen.refresh()

	def inc(self, prog):
		self.current += prog
		self.refresh()


if __name__ == "__main__":
	screen = SnackScreen()
	prog = Progress(screen, "Test Progress", "This is a test", 100)
	from time import sleep
	for i in range(100):
		prog.set(i)
		sleep(0.05)
	screen.finish()
