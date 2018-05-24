from snack import *
from . import disks, common_newt
from time import sleep

def pickdisks(screen, use):
	d = disks.getdisks()
	if d == []:
		common_newt.alert(screen, "Disks", "No removable storage connected. Please connect some and press OK.")
		sleep(1)
		return pickdisks(screen, use)
	dlist = [str(x) for x in d]
	lcw = ListboxChoiceWindow(screen, "Disks", "Pick your "+use+" disk", dlist)
	if lcw[0] is None or lcw[0] == 'ok':
		return d[lcw[1]]
	else:
		return None

def store(screen, workdir, name):
	try:
		b1 = setup(screen, "master key backup")
		b1.backup(workdir, name)
		b2 = setup(screen, "second master key backup")
		b2.backup(workdir, name)
		public = setup(screen, "public key export")
	except disks.CopyError as e:
		s = " ".join(e)
		common_newt.error(s)
	return public

def setup(screen, use):
	disk = pickdisks(screen, use)
	bcw = ButtonChoiceWindow(screen, "Warning", "Are you sure you want to use "+str(disk)+"? All the data currently on the device WILL BE WIPED!")
	if bcw == 'ok':
		try:
			ret = disk.setup()
		except disks.CalledProcessError as e:
			s = " ".join(e.cmd)
			if e.stderr is not None:
				common_newt.alert(screen, s, e.stderror)
			else:
				common_newt.error(screen, s)
	else:
		disk = setup(screen, use)
	return disk
