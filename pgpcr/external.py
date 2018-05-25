from subprocess import *
import sys

def process(cmd):
	args = {check: True, stdout: PIPE, stderr: PIPE}j
	if sys.version_info.minor >= 6:
		args.encoding = sys.stdout.encoding
	ret = run(cmd, **args)
	if sys.version_info.minor <= 5:
		ret.stdout = ret.stdout.decode(sys.stdout.encoding)
	return ret
