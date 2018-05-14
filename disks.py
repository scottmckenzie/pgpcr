import json, sys, subprocess


def getdisks():
	p = subprocess.run(["lsblk", "-do", "name,size,type,mountpoint,tran,model", "--json"],stdout=subprocess.PIPE)
	if p.returncode != 0:
		return None
	pstr = p.stdout.decode(sys.stdout.encoding)
	j = json.loads(p.stdout)
	return j['blockdevices']
