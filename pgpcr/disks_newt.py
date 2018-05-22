from snack import *
from . import disks, common_newt
from time import sleep

def pickdisks(screen, use):
	d = disks.getdisks()
	if d == []:
		common_newt.alert(screen, "Disks", "No removable storage connected. Please connect some and press OK.")
		sleep(1)
		pickdisks(screen)
		return
	for x in d:
		x['displayname'] = x['model']+" "+x['size']
	dlist = [x['displayname'] for x in d if x['mountpoint'] is None]
	lcw = ListboxChoiceWindow(screen,"Disks", "Pick your "+use+" disk", dlist)
	if lcw[0] is None or lcw[0] == 'ok':
		return d[lcw[1]]
	else:
		return None

def store(screen, workdir):
	b1 = setup(screen, "master key backup")
	b2 = setup(screen, "second master key backup")
	public = setup(screen, "public key export")

def setup(screen, use):
	dev = pickdisks(screen, use)
	bcw = ButtonChoiceWindow(screen, "Warning", "Are you sure you want to use "+ dev['displayname']+"? All the data currently on the device WILL BE WIPED!")
	if bcw == 'ok':
		disks.setup(dev)
		return dev['mountpoint']
	else:
		return None
