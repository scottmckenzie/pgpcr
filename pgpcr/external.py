from subprocess import *
import sys

def process(cmd):
	args = {'check': True, 'stdout': PIPE, 'stderr': PIPE}
	if sys.version_info.minor >= 6:
		args['encoding'] = sys.stdout.encoding
	ret = run(cmd, **args)
	if sys.version_info.minor <= 5:
		outputtostr(ret)
	return ret

def outputtostr(ret):
	if ret.stdout is not None:
		ret.stdout = ret.stdout.decode(sys.stdout.encoding)
	if ret.stderr is not None:
		ret.stderr = ret.stderr.decode(sys.stderr.encoding)
