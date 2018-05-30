from subprocess import *
import sys

def process(cmd):
	args = {}
	if sys.version_info.minor >= 6:
		args['encoding'] = sys.stdout.encoding
	ret = _process(cmd, args)
	if sys.version_info.minor <= 5:
		outputtostr(ret)
	return ret

def outputtostr(ret):
	if ret.stdout is not None:
		ret.stdout = ret.stdout.decode(sys.stdout.encoding)
	if ret.stderr is not None:
		ret.stderr = ret.stderr.decode(sys.stderr.encoding)

def processb(cmd):
	return _process(cmd, {})

def _process(cmd, args):
	default = {'args': cmd, 'check': True, 'stdout': PIPE, 'stderr': PIPE}
	default.update(args)
	return run(**default)
