import json, sys, subprocess

def getdisks():
	p = subprocess.run(["lsblk", "-p", "-d", "-o", "tran,name,model,size,serial,mountpoint", "--json"], stdout=subprocess.PIPE)
	if p.returncode != 0:
		return None
	pstr = p.stdout.decode(sys.stdout.encoding)
	j = json.loads(pstr)
	return [x for x in j['blockdevices'] if x['tran'] == "usb"]

def format(device):
	ret = subprocess.run(["sudo", "pgpcr-part", device['name']])
	return ret.returncode

def mount(device):
	mountdir = "/mnt/"+device['serial']
	subprocess.run(["sudo", "mkdir", "-p", mountdir])
	ret = subprocess.run(["sudo", "mount", device['name']+"1", mountdir])
	if ret == 0:
		device['mountpoint'] = mountdir
