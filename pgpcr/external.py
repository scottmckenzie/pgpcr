from subprocess import *

def process(cmd):
	return run(cmd, check=True, stdout=PIPE, stderr=PIPE)
