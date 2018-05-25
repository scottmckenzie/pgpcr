import shutil, os
# Pretend three usb devices of size 1G are attached

def getdisks():
	d = []
	for x in range(3):
		d.append(Disk({"name": "/tmp/test"+str(x), "model": "TEST"+str(x), "serial":str(x), "size": "1G"}))
	return d

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

	def ismounted(self):
		if self.mountpoint is not None:
			return True
		return False

	def setup(self):
		os.mkdir(self.path)
		self.mountpoint = self.path
		return (True, True)

	def backup(self, workdir, name):
		if not self.ismounted():
			return None
		else:
			return shutil.copytree(workdir.name, self.mountpoint+"/"+name)
