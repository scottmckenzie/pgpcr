from snack import *
from . import disks, common_newt, external
from time import sleep

def pickdisks(screen, use):
	d = disks.getdisks()
	if d == []:
		common_newt.alert(screen, "Disks", "No removable storage connected. Please connect some and press OK.")
		sleep(1)
		return pickdisks(screen, use)
	dlist = [str(x) for x in d]
	lcw = ListboxChoiceWindow(screen, "Disks", "Pick your "+use+" disk", dlist, buttons = [("Refresh", 'refresh')])
	if lcw[0] is None or lcw[0] == 'ok':
		return d[lcw[1]]
	elif lcw[0] == 'refresh':
		return pickdisks(screen, use)
	else:
		return None

def store(screen, workdir, name):
	try:
		b1 = setup(screen, "master key backup")
		b1.backup(workdir, name)
		common_newt.alert(screen, str(b1), "Your backup to the above disk is now complete and the disk can be ejected.")
		b2 = setup(screen, "second master key backup")
		b2.backup(workdir, name)
		common_newt.alert(screen, str(b2), "Your backup to the above disk is now complete and the disk can be ejected.")
		public = setup(screen, "public key export")
	except disks.CopyError as e:
		s = " ".join(e)
		common_newt.error(s)
	except external.CalledProcessError as e:
		common_newt.catchCPE(screen, e)
	return public

def setup(screen, use):
	disk = pickdisks(screen, use)
	bcw = ButtonChoiceWindow(screen, "Warning", "Are you sure you want to use "+str(disk)+"? All the data currently on the device WILL BE WIPED!")
	if bcw == 'ok':
		try:
			ret = disk.setup()
		except external.CalledProcessError as e:
			common_newt.catchCPE(screen, e)
	else:
		disk = setup(screen, use)
	return disk
