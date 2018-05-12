import json
import subprocess


def getdisks():
	p = subprocess.run(["lsblk", "-do", "name,size,type,mountpoint,tran,model", "--json"],stdout=subprocess.PIPE)
	if p.returncode != 0:
		return None
	j = json.loads(p.stdout)
	return j['blockdevices']
