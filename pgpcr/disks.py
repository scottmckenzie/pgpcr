import json, sys, subprocess

def getdisks():
	p = subprocess.run(["lsblk", "-d", "-o", "name,size,mountpoint,tran,model", "--json"], stdout=subprocess.PIPE)
	if p.returncode != 0:
		return None
	pstr = p.stdout.decode(sys.stdout.encoding)
	j = json.loads(p.stdout)
	return [x for x in j['blockdevices'] if x['tran'] == "usb"]


