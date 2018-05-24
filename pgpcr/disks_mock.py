import json, sys, subprocess, shutil, os
# Pretend three usb devices of size 1G are attached

def getdisks():
	return [
		{"name": "/tmp/test1", "tran": "usb", "model": "TEST", "serial":"1", "mountpoint": None},
		
		{"name": "/tmp/test2", "tran": "usb", "model": "TEST", "serial":"2", "mountpoint": None},
		{"name": "/tmp/test3", "tran": "usb", "model": "TEST", "serial":"3", "mountpoint": None}
	]

def setupdevice(device):
	os.mkdir(device['name'])
	return device['name']

def backup(workdir, destdir, name):
	return shutil.copytree(workdir.name, destdir+"/"+name)

# check if the given device has any mounted child devices
def checkmounted(device):
	return False
