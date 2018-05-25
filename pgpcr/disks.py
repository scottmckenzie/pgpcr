from . import external
import json, sys, shutil, os

def getdisks():
	j = lsblk(["-p", "-d", "-o", "tran,name,model,size,serial", "--json"])
	d = []
	for x in j:
		if x['tran'] == "usb":
			d.append(Disk(x))
	return d

def lsblk(options):
	com = ["lsblk"]
	com.extend(options)
	p = external.process(com)
	pstr = p.stdout.decode(sys.stdout.encoding)
	return json.loads(pstr)['blockdevices']

class Disk:

	def __init__(self, blkdev):
		self.path = blkdev['name']
		self.model = blkdev['model']
		self.size = blkdev['size']
		self.serial = blkdev['serial']
		self.mountpoint = None

	def __str__(self):
		s = self.model+" "+self.size
		if self.ismounted():
			s += "[IN USE]"
		return s

	def _getchildren(self):
		j = lsblk(["-p", "-o", "name,mountpoint", self.path, "--json"])
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
		self._partition()
		self._mount()

	def backup(self, workdir, name):
		if not self.ismounted():
			return None
		else:
			shutil.copytree(workdir.name, self.mountpoint+"/"+name, ignore=shutil.ignore_patterns('S.*'))
			self._eject()

	def _partition(self):
		external.process(["sudo", "pgpcr-part", self.path])

	def _mount(self):
		mountdir = "/mnt/"+self.serial
		ret = external.process(["sudo", "mkdir", "-p", mountdir])
		self.mountpoint = mountdir
		chown = external.process(["sudo", "chown", "-R", str(os.getuid()), mountdir])

	def _eject(self):
		external.process(['sudo', 'umount', self.mountpoint])
		external.process((['sudo', 'eject', self.path])

CopyError = shutil.Error
