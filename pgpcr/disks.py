import json, sys, subprocess, shutil

def getdisks():
	p = subprocess.run(["lsblk", "-p", "-d", "-o", "tran,name,model,size,serial,mountpoint", "--json"], stdout=subprocess.PIPE)
	if p.returncode != 0:
		return None
	pstr = p.stdout.decode(sys.stdout.encoding)
	j = json.loads(pstr)
	return [x for x in j['blockdevices'] if x['tran'] == "usb"]

def setup(device):
	# TODO: Remove skeleton code
	#partret = subprocess.run(["sudo", "pgpcr-part", device['name']], stdout=subprocess.PIPE)
	mountdir = "/mnt/"+device['serial']
	subprocess.run(["sudo", "mkdir", "-p", mountdir])
	#mountret = subprocess.run(["sudo", "mount", device['name']+"1", mountdir])
	#if partret == 0 and mountret == 0:
	#	device['mountpoint'] = mountdir
		# TODO: Don't hardcode user
	#	subprocess.run(["sudo", "chown", "-R", "pgp", mountdir])
	#else:
	#	device['mountpoint'] = False
	device['mountpoint'] = mountdir
	subprocess.run(["sudo", "chown", "-R", "pgp", mountdir])

def backup(workdir, destdir, name):
	return shutil.copyfile(workdir, destdir+"/"+name)
