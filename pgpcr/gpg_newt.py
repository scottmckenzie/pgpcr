from snack import *
from . import gpg_ops, common_newt as common, disks_newt, smartcard_newt

def new(screen, workdir):
	gk = gpg_ops.GPGKey(workdir.name)
	ew = EntryWindow(screen, "New GPG Key", "Enter User Information", ["Name", "Email Address"])
	if ew[0] != 'ok':
		return
	name = ew[1][0]
	email = ew[1][1]
	common.alert(screen, "Key Generation", "GPG keys will now be generated. Progress is estimated and this may take a while. You will be prompted for your password several times.")
	mprog = common.Progress(screen, "Key Generation", "Generating Master Key...", 40)
	gk.setprogress(_progress, mprog)
	try:
		gk.genmaster(name+" <"+email+">")
	except gpg_ops.GPGMEError as g:
		screen = SnackScreen()
		common.error(screen, "Master Key generation error: "+str(g))
		return
	sprog = common.Progress(screen, "Key Generation", "Generating Sub Keys...", 60)
	gk.setprogress(_progress, sprog)
	try:
		gk.gensub()
	except gpg_ops.GPGMEError as g:
		screen = SnackScreen()
		common.error(screen, "Subkey generation error: "+str(g))
		return
	screen = SnackScreen()
	common.alert(screen, "Key Generation", "Key Generation Complete!")
	disks_newt.store(screen, workdir, gk.masterfpr())
	export = ButtonChoiceWindow(screen, "Key Export", "How would you like to export your key?", [("External Storage", "storage"), ("Smartcard", "smartcard")])
	if export == "storage":
		disks_newt.export(screen, gk)
	elif export == "smartcard":
		smartcard_newt.export(screen, gk)
	common.alert(screen, "New Key Creation Complete", "You can now store your backups in a safe place")
	if export == "storage":
		common.alert(screen, "IMPORTANT", "Don't forget to import your new key to your main computer by running import.sh from your public export disk.")

def _progress(what, type, current, total, prog):
	if what == "primegen":
		prog.inc(1)
