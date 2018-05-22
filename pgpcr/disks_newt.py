from snack import *
from . import disks, common_newt
from time import sleep

def listdisks(screen, use):
	d = disks.getdisks()
	if d == []:
		common_newt.alert(screen, "Disks", "No removable storage connected. Please connect some and press OK.")
		sleep(1)
		listdisks(screen)
		return
	for x in d:
		x['displayname'] = x['model']+" "+x['size']
	dlist = [x['displayname'] for x in d]
	lcw = ListboxChoiceWindow(screen,"Disks", "Pick your "+use+" disk", dlist)
	if lcw[0] is None or lcw[0] == 'ok':
		return d[lcw[1]]
	else:
		return None

def store(screen, workdir):
	pass
