import json, sys, subprocess

def getdisks():
	p = subprocess.run(["lsblk", "-p", "-d", "-o", "tran,name,model,size,serial,mountpoint", "--json"], stdout=subprocess.PIPE)
	if p.returncode != 0:
		return None
	pstr = p.stdout.decode(sys.stdout.encoding)
	j = json.loads(p.stdout)
	return [x for x in j['blockdevices'] if x['tran'] == "usb"]


