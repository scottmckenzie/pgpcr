from snack import *
from . import disks

def listdisks():
	screen = SnackScreen()
	d = disks.getdisks()
	dlist = [x['model']+" "+x['size'] for x in d] #if x['tran'] == "usb"]
	lcw = ListboxChoiceWindow(screen,"Disks", "Pick your disks", dlist)
	screen.finish()
	print(lcw)

def store(screen, workdir):
	pass
