from . import external
import json, shutil, os

CopyError = shutil.Error

def getdisks():
	j = lsblk(["-p", "-d", "-o", "tran,name,model,size,serial,label"])
	d = []
	for x in j:
		if x['tran'] == "usb":
			d.append(Disk(x))
	return d

def lsblk(options):
	com = ["lsblk"]
	com.extend(options)
	com.append("--json")
	p = external.process(com)
	return json.loads(p.stdout)['blockdevices']

class Disk:

	def __init__(self, blkdev):
		self.path = blkdev['name']
		self.model = blkdev['model']
		self.size = blkdev['size']
		self.serial = blkdev['serial']
		self.label = blkdev['label']
		self.label = self._getlabel()
		self.mountpoint = None

	def __str__(self):
		s = ""
		if self.label is not None:
			s = self.label
		else:
			s = self.model+" "+self.size
		if self.ismounted():
			s = "[IN USE] "+s
		return s

	def _getchildren(self):
		j = lsblk(["-p", "-o", "name,mountpoint,label", self.path])
		if "children" not in j[0]:
			return None
		else:
			return j[0]["children"]

	def _getlabel(self):
		if self.label is not None:
			return self.label
		c = self._getchildren()
		if c is None:
			return None
		for p in c:
			if p['label'] is not None:
				return p['label']

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

	def setup(self, label):
		self._partition(label)
		self._mount()

	def backup(self, workdir, name):
		if not self.ismounted():
			return None
		else:
			shutil.copytree(workdir.name, self.mountpoint+"/"+name, ignore=shutil.ignore_patterns('S.*'))
			self._eject()

	def _partition(self, label):
		external.process(["sudo", "pgpcr-part", self.path, label])

	def _mount(self):
		mountdir = "/mnt/"+self.serial
		external.process(["sudo", "mkdir", "-p", mountdir])
		external.process(["sudo", "mount", self._getchildren()[0]['name'], mountdir])
		self.mountpoint = mountdir
		chown = external.process(["sudo", "chown", "-R", str(os.getuid()), mountdir])

	def _eject(self):
		external.process(['sync'])
		external.process(['sudo', 'umount', self.mountpoint])
