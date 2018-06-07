from snack import *
from . import gpg_ops, common_newt as common, disks_newt, smartcard_newt


def new(screen, workdir):
    gk = gpg_ops.GPGKey(workdir.name)
    uid = common.uid(screen, "New GPG Key")
    if uid is None:
        return
    common.alert(screen, "Key Generation",
                 "GPG keys will now be generated. "
                 "Progress is estimated and this may take a while. "
                 "You will be prompted for your password several times.")
    mprog = common.Progress(screen, "Key Generation",
                            "Generating Master Key...", 40)
    gk.setprogress(_progress, mprog)
    try:
        gk.genmaster(uid)
    except gpg_ops.GPGMEError as g:
        screen = SnackScreen()
        common.error(screen, "Master Key generation error: "+str(g))
        return
    sprog = common.Progress(screen, "Key Generation",
                            "Generating Sub Keys...", 60)
    gk.setprogress(_progress, sprog)
    try:
        gk.gensub()
    except gpg_ops.GPGMEError as g:
        screen = SnackScreen()
        common.error(screen, "Subkey generation error: "+str(g))
        return
    screen = SnackScreen()
    common.alert(screen, "Key Generation", "Key Generation Complete!")
    disks_newt.store(screen, workdir, "gpg/"+gk.fpr)
    export = ButtonChoiceWindow(screen, "Key Export",
                                "How would you like to export your key?",
                                [("External Storage", "storage"),
                                ("Smartcard", "smartcard")])
    if export == "storage":
        disks_newt.export(screen, gk)
    elif export == "smartcard":
        smartcard_newt.export(screen, gk)
    common.alert(screen, "New Key Creation Complete",
                 "You can now store your backups in a safe place")
    if export == "storage":
        common.alert(screen, "IMPORTANT",
                     "Don't forget to import your new key to your main computer "
                     "by running import.sh from your public export disk.")


def _progress(what, type, current, total, prog):
    if what == "primegen":
        prog.inc()


def load(screen, workdir):
    d = disks_newt.load(screen)
    dirs = gpg_ops.backups(d.mountpoint)
    if dirs is None:
        common.error(screen, "This disk does not contain a master key backup.")
        d.eject()
        load(screen, workdir)
    lcw = ListboxChoiceWindow(screen, "Key Fingerprint", "Please select your key.",
                              dirs)
    if lcw[0] == "cancel":
        return
    key = dirs[lcw[1]]
    gk = gpg_ops.GPGKey(workdir.name, key, d.mountpoint+"/gpg/"+key)
    running = True
    while running:
        bcw = ButtonChoiceWindow(screen, key, "What would you like to do?",
                                 [("Sign Keys", "sign"),
                                  ("Add UID", "adduid"),
                                  ("Revoke UID", "revuid"),
                                  ("Revoke Keys", "revkeys"),
                                  ("Quit", "quit")
                                 ])
        if bcw == "sign":
            sign(screen, gk, d.mountpoint)
        elif bcw == "adduid":
            adduid(screen, gk)
        elif bcw == "revuid":
            revuid(screen, gk)
        elif bcw == "revkey":
            revokekey(screen, gk)
        elif bcw == "quit":
            d.eject()
            running = False
    disks_newt.store(screen, workdir, "gpg/"+gk.fpr)


def sign(screen, gk, path):
    common.NotImplementedYet(screen)

def revokekey(screen, gk):
    keys = gk.listkeys()
    lcw = ListboxChoiceWindow(screen, gk.fpr,
                              "Which key do you want to revoke?", keys)
    #TODO: Revoke a key given a fingerprint
    key = keys[lcw[1]]
    common.NotImplementedYet(screen)

def adduid(screen, gk):
    uid = common.uid(screen, "Add UID "+gk.fpr)
    if uid is None:
        return
    gk.adduid(uid)
    common.alert(screen, gk.fpr, "Added "+uid+" to your key")

def revuid(screen, gk):
    uids = gk.listuids()
    lcw = ListboxChoiceWindow(screen, gk.fpr, "Which UID would you like to "
                              "revoke?", uids)
    if lcw[0] == "cancel":
        return
    gk.revokeuid(uids[lcw[1]])
    common.alert(screen, gk.fpr, "Removed "+uids[lcw[1]]+" from your key")

def importkey(screen, workdir):
    common.NotImplementedYet(screen)
