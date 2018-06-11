from snack import *
from . import gpg_ops, common_newt as common, disks_newt, smartcard_newt


def new(screen, workdir):
    gk = gpg_ops.GPGKey(workdir.name)
    uid = common.uid(screen, _("New GPG Key"))
    if uid is None:
        return
    common.alert(screen, _("Key Generation"),
                 _("GPG keys will now be generated."
                 " Progress is estimated and this may take a while."
                 " You will be prompted for your password several times."))
    mprog = common.Progress(screen, _("Key Generation"),
                            _("Generating Master Key")+"...", 40)
    gk.setprogress(_progress, mprog)
    try:
        gk.genmaster(uid)
    except gpg_ops.GPGMEError as g:
        screen = SnackScreen()
        common.error(screen, _("Master Key generation error")+": "+str(g))
        return
    sprog = common.Progress(screen, _("Key Generation"),
                            _("Generating Sub Keys")+"...", 60)
    gk.setprogress(_progress, sprog)
    try:
        gk.gensub()
    except gpg_ops.GPGMEError as g:
        screen = SnackScreen()
        common.error(screen, _("Subkey generation error")+": "+str(g))
        return
    screen = SnackScreen()
    common.alert(screen, _("Key Generation"), _("Key Generation Complete!"))
    save(screen, workdir, gk)

def save(screen, workdir, gk):
    disks_newt.store(screen, workdir, "gpg/"+gk.fpr)
    export = ButtonChoiceWindow(screen, _("Key Export"),
                                _("How would you like to export your key?"),
                                [(_("External Storage"), "storage"),
                                (_("Smartcard"), "smartcard")])
    if export == "storage":
        disks_newt.export(screen, gk)
    elif export == "smartcard":
        smartcard_newt.export(screen, gk)
    common.alert(screen, _("New Key Creation Complete"),
                 _("You can now store your backups in a safe place"))
    if export == "storage":
        common.alert(screen, _("IMPORTANT"),
                     _("Don't forget to import your new key to your main"
                       " computer by running import.sh from your public export"
                       " disk."))


def _progress(what, type, current, total, prog):
    if what == "primegen":
        prog.inc()


def load(screen, workdir):
    d = disks_newt.load(screen)
    dirs = gpg_ops.backups(d.mountpoint)
    if dirs is None:
        common.error(screen, _("This disk does not contain a master key"
                               " backup."))
        d.eject()
        load(screen, workdir)
    lcw = ListboxChoiceWindow(screen, _("Key Fingerprint"),
                              _("Please select your key."), dirs)
    if lcw[0] == "cancel":
        return
    key = dirs[lcw[1]]
    gk = gpg_ops.GPGKey(workdir.name, key, d.mountpoint+"/gpg/"+key)
    running = True
    while running:
        bcw = ButtonChoiceWindow(screen, key, _("What would you like to do?"),
                                 [(_("Sign Keys"), "sign"),
                                  (_("Add UID"), "adduid"),
                                  (_("Revoke UID"), "revuid"),
                                  (_("Revoke Keys"), "revkeys"),
                                  (_("Quit"), "quit")
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
    save(screen, workdir, gk)


def sign(screen, gk, path):
    #TODO: Load, confirm and sign any keys listed in the signing directory
    common.NotImplementedYet(screen)

def revokekey(screen, gk):
    keys = gk.keys
    lcw = ListboxChoiceWindow(screen, gk.fpr,
                              _("Which key do you want to revoke?"), keys)
    #TODO: Revoke a key given a fingerprint
    key = keys[lcw[1]]
    common.NotImplementedYet(screen)

def adduid(screen, gk):
    uid = common.uid(screen, _("Add UID")+" "+gk.fpr)
    if uid is None:
        return
    gk.adduid(uid)
    common.alert(screen, gk.fpr, _("Added %s to your key") % uid)

def revuid(screen, gk):
    uids = gk.uids
    lcw = ListboxChoiceWindow(screen, gk.fpr, _("Which UID would you like to"
                              " revoke?"), uids)
    if lcw[0] == "cancel":
        return
    gk.revokeuid(uids[lcw[1]])
    common.alert(screen, gk.fpr, _("Removed %s from your key") % uids[lcw[1]])

def importkey(screen, workdir):
    #TODO: Import keys from secret key or .gnupg backups
    common.NotImplementedYet(screen)
