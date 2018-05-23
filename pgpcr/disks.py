import json, sys, subprocess, shutil, os

def getdisks():
	j = lsblk(["-p", "-d", "-o", "tran,name,model,size,serial,mountpoint", "--json"])
	return [x for x in j if x['tran'] == "usb"]

def setup(device):
	# TODO: Remove skeleton code
	#partret = subprocess.run(["sudo", "pgpcr-part", device['name']], stdout=subprocess.PIPE)
	mountdir = "/mnt/"+device['serial']
	subprocess.run(["sudo", "mkdir", "-p", mountdir])
	#mountret = subprocess.run(["sudo", "mount", device['name']+"1", mountdir])
	#if partret == 0 and mountret == 0:
	#	device['mountpoint'] = mountdir
	#	subprocess.run(["sudo", "chown", "-R", str(os.getuid()), mountdir])
	#else:
	#	device['mountpoint'] = False
	device['mountpoint'] = mountdir
	subprocess.run(["sudo", "chown", "-R", str(os.getuid()), mountdir])

def backup(workdir, destdir, name):
	return shutil.copytree(workdir.name, destdir+"/"+name)

# check if the given device has any mounted child devices
def checkmounted(device):
	j = lsblk(["-p", "-o", "name,mountpoint", device])
	if "children" not in j:
		return False
	for x in j["children"]:
		if x['mountpoint'] is not None:
			return True
	return False

def lsblk(options):
	com = ["lsblk"].append(options)
	p = subprocess.run(com, stdout=subprocess.PIPE)
	if p.returncode != 0:
		return None
	pstr = p.stdout.decode(sys.stdout.encoding)
	return json.loads(pstr)['blockdevices']
