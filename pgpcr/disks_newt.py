from snack import *
from . import disks, common_newt
from time import sleep

def pickdisks(screen, use):
	d = disks.getdisks()
	if d == []:
		common_newt.alert(screen, "Disks", "No removable storage connected. Please connect some and press OK.")
		sleep(1)
		return pickdisks(screen, use)
	dlist = [x.display for x in d]
	lcw = ListboxChoiceWindow(screen, "Disks", "Pick your "+use+" disk", dlist)
	if lcw[0] is None or lcw[0] == 'ok':
		return d[lcw[1]]
	else:
		return None

def store(screen, workdir, name):
	b1 = setup(screen, "master key backup")
	disks.backup(workdir, b1, name)
	b2 = setup(screen, "second master key backup")
	disks.backup(workdir, b2, name)
	public = setup(screen, "public key export")
	return public

def setup(screen, use):
	disk = pickdisks(screen, use)
	bcw = ButtonChoiceWindow(screen, "Warning", "Are you sure you want to use "+disk.display+"? All the data currently on the device WILL BE WIPED!")
	if bcw == 'ok':
		ret = disk.setup()
	else:
		ret = False
	if ret:
		return ret
	setup(screen, use)
