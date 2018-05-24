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
	com.extend(options)
	p = subprocess.run(com, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.check_returncode()
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
			shutil.copytree(workdir.name, self.mountpoint+"/"+name)
			self._eject()

	def _partition(self):
		ret = subprocess.run(["sudo", "pgpcr-part", self.path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		ret.check_returncode()

	def _mount(self):
		mountdir = "/mnt/"+self.serial
		ret = subprocess.run(["sudo", "mkdir", "-p", mountdir], stderr=subprocess.PIPE)
		ret.check_returncode()
		self.mountpoint = mountdir
		chown = subprocess.run(["sudo", "chown", "-R", str(os.getuid()), mountdir], stderr=subprocess.PIPE)
		chown.check_returncode()

	def _eject(self):
		ret = subprocess.run(['sudo', 'eject', self.path], stderr=subprocess.PIPE)
		ret.check_returncode()

CalledProcessError = subprocess.CalledProcessError
