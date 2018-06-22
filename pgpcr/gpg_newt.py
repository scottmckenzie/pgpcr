from snack import *
from . import gpg_ops, common_newt as common, disks_newt, smartcard_newt
from . import fmt, external
import logging

_log = logging.getLogger(__name__)

def new(screen, workdir):
    gk = gpg_ops.GPGKey(workdir.name)
    gk.setstatus(_status)
    uid = common.uid(screen, _("New GPG Key"))
    if uid is None:
        return
    k = keyalgos(screen, gk)
    if not k:
        return
    common.alert(screen, _("Key Generation"),
                 _("GPG keys will now be generated."
                 " Progress is estimated and this may take a while."
                 " You will be prompted for your password several times."))
    mprog = common.Progress(screen, _("Key Generation"),
                            _("Generating Master Key")+"...", 40)
    mprog.gk = gk
    gk.setprogress(_progress, mprog)
    try:
        gk.genmaster(uid)
    except gpg_ops.GPGMEError as g:
        screen = SnackScreen()
        common.error(screen, _("Master Key generation error")+": "+str(g))
        return
    sprog = common.Progress(screen, _("Key Generation"),
                            _("Generating Sub Keys")+"...", 60)
    sprog.gk = gk
    gk.setprogress(_progress, sprog)
    try:
        gk.genseasubs(sprog.setText)
    except gpg_ops.GPGMEError as g:
        screen = SnackScreen()
        common.error(screen, _("Subkey generation error")+": "+str(g))
        return
    screen = SnackScreen()
    common.alert(screen, _("Key Generation"), _("Key Generation Complete!"))
    save(screen, workdir, gk)

def keyalgos(screen, gk):
    mlcw = common.LCW(screen, _("Master Key Algorithm"),_("Pick the"
        " algorithm you would like to use for your new master key. If you're"
        " unsure, the defaults are well chosen and should work for"
        " most people"), gpg_ops.master_algos)
    if mlcw[0] == "cancel":
        return False
    slcw = common.LCW(screen, _("Subkey Algorithm"),_("Pick the"
        " algorithm you would like to use for your new subkeys. If you're"
        " unsure, the defaults are well chosen and should work for"
        " most people"), gpg_ops.sub_algos)
    if slcw[0] == "cancel":
        return False
    gk.setalgorithms(gpg_ops.master_algos[mlcw[1]], gpg_ops.sub_algos[slcw[1]])
    return True

def save(screen, workdir, gk):
    disks_newt.store(screen, workdir, "gpg/"+gk.fpr)
    export = ButtonChoiceWindow(screen, _("Key Export"),
                                _("How would you like to export your"
                                " subkeys?"),
                                [(_("External Storage"), "storage"),
                                (_("Smartcard"), "smartcard")])
    secret = False
    if export == "storage":
        secret = True
    elif export == "smartcard":
        smartcard_newt.export(screen, gk)
    disks_newt.export(screen, gk, secret)
    common.alert(screen, _("New Key Creation Complete"),
                 _("You can now store your backups in a safe place"))
    common.alert(screen, _("IMPORTANT"),
        _("Don't forget to import your new key to your main"
            " computer by running import.sh from your public export disk."))

def _progress(what, type, current, total, prog):
    if what == "primegen":
        prog.inc()
    if prog.gk.redraw:
        prog.screen.finish()
        prog.screen = SnackScreen()
        prog.recreate()


def load(screen, workdir):
    d = disks_newt.mountdisk(screen, _("master key backup"))
    dirs = None
    if d is not None:
        dirs = fmt.backups(d.mountpoint)
    if dirs is None:
        common.error(screen, _("This disk does not contain a master key"
                               " backup."))
        d.eject()
        load(screen, workdir)
    lcw = common.LCW(screen, _("Key Fingerprint"),
                              _("Please select your key."), dirs)
    if lcw[0] == "cancel":
        return
    key = dirs[lcw[1]]
    gk = gpg_ops.GPGKey(workdir.name, key, d.mountpoint+"/gpg/"+key)
    running = True
    while running:
        screen.finish()
        screen = SnackScreen()
        lm = common.listmenu(screen, key, _("What would you like to do?"),
                                 [(_("Sign GPG Public Keys"), "sign"),
                                  (_("Associate a UID with your master key"),
                                     "adduid"),
                                  (_("Revoke a UID associated with your master"
                                     " key"), "revuid"),
                                  (_("Revoke your master key or a subkey"),
                                     "revkeys"),
                                  (_("Change the expiration date on your"
                                      " master key or a subkey"),
                                      "expirekeys"),
                                  (_("Quit"), "quit")
                                 ])
        if lm == "sign":
            sign(screen, gk, d.mountpoint)
        elif lm == "adduid":
            adduid(screen, gk)
        elif lm == "revuid":
            revuid(screen, gk)
        elif lm == "revkeys":
            revokekey(screen, gk)
        elif lm == "expirekeys":
            expirekey(screen, gk)
        elif lm == "quit":
            d.eject()
            running = False
    confirm = common.confirm(screen, _("Save"), _("Do you want to save the"
        " changes you've made?"))
    if confirm:
        save(screen, workdir, gk)


def sign(screen, gk, path):
    s = disks_newt.mountdisk(screen, _("keys to sign disk"))
    keys = fmt.signing(s.mountpoint)
    if keys is None:
        common.alert(screen, _("Key Signing"),
                     _("There are no keys to sign on this disk. Please be sure"
                       " they are in the signing/pending folder."))
        sign(screen, gk, path)
        return
    rw = common.CheckboxChoiceWindow(screen, _("Key Signing"), _("Which keys"
                                     " do you want to sign?"), keys)
    if rw[0] == "cancel":
        return
    for k in rw[1]:
        gk.signkey(s.mountpoint, k)
        if gk.redraw:
            screen.finish()
            screen = SnackScreen()
        common.alert(screen, _("Key signing"), _("Signed %s") % k)
    s.eject()

def revokekey(screen, gk):
    keys = gk.keys
    ccw = common.CheckboxChoiceWindow(screen, gk.fpr,
                                      _("Which key(s) do you want to revoke?"),
                                      keys)
    for k in ccw[1]:
        fpr = k.split(" ")[0]
        lcw = common.LCW(screen, fpr, _("Why do you want to revoke %s") % k,
                gpg_ops.revoke_reasons)
        if lcw[0] == "cancel":
            return
        text = EntryWindow(screen, fpr, _("Why are you revoking this key?"),
                [""], buttons = buttons)
        if text[0] == "cancel":
            return
        screen.finish()
        gk.revokekey(fpr, lcw[1], text[1][0])
        screen = SnackScreen()
        common.alert(screen, k, _("Revoked %s") % k)

def adduid(screen, gk):
    uid = common.uid(screen, _("Add UID")+" "+gk.fpr)
    if uid is None:
        return
    gk.adduid(uid)
    common.alert(screen, gk.fpr, _("Added %s to your key") % uid)

def revuid(screen, gk):
    uids = gk.uids
    lcw = common.LCW(screen, gk.fpr, _("Which UID would you like to"
                              " revoke?"), uids)
    if lcw[0] == "cancel":
        return
    gk.revokeuid(uids[lcw[1]])
    common.alert(screen, gk.fpr, _("Removed %s from your key") % uids[lcw[1]])

def expirekey(screen, gk):
    lcw = common.LCW(screen, _("Key expiration"), _("Which key do you"
        " want to expire?"), gk.keys)
    if lcw[0] == "cancel":
        return
    fpr = gk.keys[lcw[1]].split(" ")[0]
    invalid = True
    while invalid:
        screen = SnackScreen()
        ew = EntryWindow(screen, fpr, _("When do you want this key to expire?"
            "(YYYY-MM-DD)"), [_("Expiration Date:")], buttons=[(_("Ok"), "ok"),
            (_("Cancel"), "cancel")])
        if ew[0] == "cancel":
            return
        screen.finish()
        try:
            gk.expirekey(fpr, ew[1][0])
        except (ValueError, TypeError):
            common.error(SnackScreen(), _("Please enter a valid date in the"
                " future."))
            continue
        common.alert(SnackScreen(), fpr, _("Changed expiration date on %s")
                % fpr)
        invalid = False


def importkey(screen, workdir):
    #TODO: Import keys from secret key or .gnupg backups
    common.NotImplementedYet(screen)

def _status(keyword, args, hook=None):
    if keyword is None and args is None:
        return
    _log.info("{!s}({!s})\n".format(keyword, args))
