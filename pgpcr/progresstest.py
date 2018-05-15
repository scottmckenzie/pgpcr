import gpg, tempfile

# Borrowed from callbacks.py 
def progress_stdout(what, type, current, total, hook=None):
	print("PROGRESS UPDATE: what = %s, type = %d, current = %d, total = %d" %\
		(what, type, current, total))

tmp = tempfile.TemporaryDirectory()
ctx = gpg.Context(home_dir=tmp.name)
ctx.set_progress_cb(progress_stdout)
ctx.create_key("Test <test@example.com>", algorithm="rsa4096")
