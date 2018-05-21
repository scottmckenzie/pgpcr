from snack import *
from . import disks, common_newt
from time import sleep

def listdisks(screen):
	d = disks.getdisks()
	if d == []:
		common_newt.alert(screen, "Disks", "No removable storage connected. Please connect some and press OK.")
		sleep(1)
		listdisks(screen)
		return
	dlist = [x['model']+" "+x['size'] for x in d]
	lcw = ListboxChoiceWindow(screen,"Disks", "Pick your disks", dlist)
	print(lcw)

def store(screen, workdir):
	pass
