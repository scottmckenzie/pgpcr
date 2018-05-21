from snack import *
from . import disks

def listdisks(screen):
	d = disks.getdisks()
	dlist = [x['model']+" "+x['size'] for x in d]
	lcw = ListboxChoiceWindow(screen,"Disks", "Pick your disks", dlist)
	print(lcw)

def store(screen, workdir):
	pass
