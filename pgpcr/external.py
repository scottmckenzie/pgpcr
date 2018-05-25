from subprocess import *
from sys import stdout

def process(cmd):
	return run(cmd, check=True, stdout=PIPE, stderr=PIPE, encoding=stdout.encoding)
