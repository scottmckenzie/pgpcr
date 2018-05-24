import json, sys, subprocess, shutil, os

def getdisks():
	j = lsblk(["-p", "-d", "-o", "tran,name,model,size,serial", "--json"])
	d = []
	for x in j:
		if x['tran'] == "usb":
			d.append(Disk(x))
	return d

def lsblk(options):
	com = ["lsblk"]
	com.append(options)
	p = subprocess.run(com, stdout=subprocess.PIPE)
	if p.returncode != 0:
		return None
	pstr = p.stdout.decode(sys.stdout.encoding)
	return json.loads(pstr)['blockdevices']

class Disk:

	def __init__(self, blkdev):
		self.name = blkdev['name']
		self.model = blkdev['model']
		self.size = blkdev['size']
		self.serial = blkdev['serial']
		self.mountpoint = None
		self.display = self.model+" "+self.size
		if self.ismounted():
			self.display += "[IN USE]"

	def _getchildren(self):
		j = lsblk(["-p", "-o", "name,mountpoint", self.name])
		if "children" not in j:
			return None
		else:
			return j["children"]

	def ismounted(self):
		if self.mountpoint is not None:
			return True
		children = self._getchildren()
		if children is None:
			return False
		else:
			for x in children:
				if x['mountpoint'] is not None:
					self.mountpoint = x['mountpoint']
					return True

	def setup(self):
		p = self._partition()
		m = self._mount()
		return (p, m)

	def _partition(self):
		ret = subprocess.run(["sudo", "pgpcr-part", device['name']], stdout=subprocess.PIPE)
		if ret.returncode() == 0:
			self.children = self.getchildren()
			return True
		return False

	def _mount(self):
		mountdir = "/mnt/"+device['serial']
		ret = subprocess.run(["sudo", "mkdir", "-p", mountdir])
		if ret == 0:
			self.mountpoint = mountdir
			chown = subprocess.run(["sudo", "chown", "-R", str(os.getuid()), mountdir])
			return True
		else:
			self.mountpoint = False
		return False

	def backup(self, workdir, name):
		if not self.ismounted():
			return None
		else:
			return shutil.copytree(workdir.name, self.mountpoint+"/"+name)
