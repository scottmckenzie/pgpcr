from snack import *
from . import gpg_ops, common_newt as common, disks_newt, smartcard_newt
from . import fmt, external
import logging

_log = logging.getLogger(__name__)

def new(screen, workdir):
    gk = gpg_ops.GPGKey(workdir)
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
        screen = common.screen()
        common.error(screen, _("Master Key generation error")+": "+str(g))
        return
    sprog = common.Progress(screen, _("Key Generation"),
                            _("Generating Sub Keys")+"...", 60)
    sprog.gk = gk
    gk.setprogress(_progress, sprog)
    try:
        gk.genseasubs(sprog.setText)
    except gpg_ops.GPGMEError as g:
        screen = common.screen()
        common.error(screen, _("Subkey generation error")+": "+str(g))
        return
    screen = common.screen()
    common.alert(screen, _("Key Generation"), _("Key Generation Complete!"))
    save(screen, workdir, gk)

def keyalgos(screen, gk):
    masteralgolist = list(gpg_ops.master_algos.keys())
    mlcw = common.LCW(screen, _("Master Key Algorithm"),_("Pick the"
        " algorithm you would like to use for your new master key. If you're"
        " unsure, the defaults are well chosen and should work for"
        " most people"), masteralgolist)
    if mlcw[0] == "cancel":
        return False
    masteralgo = masteralgolist[mlcw[1]]
    mastersizes = gpg_ops.master_algos[masteralgo]
    if mastersizes is not None:
        mks = common.LCW(screen, _("Master Key Size"), _("Pick the size of"
            " your new master key. If you're unsure the defaults are well"
            " chosen and should work for most people"), mastersizes)
        if mks[0] == "cancel":
            return False
        masteralgo += mastersizes[mks[1]]
    subalgolist = list(gpg_ops.sub_algos.keys())
    slcw = common.LCW(screen, _("Subkey Algorithm"),_("Pick the"
        " algorithm you would like to use for your new subkeys. If you're"
        " unsure, the defaults are well chosen and should work for"
        " most people"), subalgolist)
    if slcw[0] == "cancel":
        return False
    subalgo = subalgolist[slcw[1]]
    subsizes = gpg_ops.sub_algos[subalgo]
    if subsizes is not None:
        sks = common.LCW(screen, _("Master Key Size"), _("Pick the size of"
            " your new master key. If you're unsure the defaults are well"
            " chosen and should work for most people"), subsizes)
        if sks[0] == "cancel":
            return False
        subalgo += subsizes[sks[1]]

    gk.setalgorithms(masteralgo, subalgo)
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
        prog.screen = common.screen()
        prog.recreate()


def load(screen, workdir):
    d = disks_newt.mountdisk(screen, _("master key backup"))
    if d is None:
        return
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
    gk = gpg_ops.GPGKey(workdir, key, d.mountpoint+"/gpg/"+key)
    gk.setstatus(_status)
    running = True
    while running:
        screen.finish()
        screen = common.screen()
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
    s = disks_newt.mountdisk(screen, _("keys to sign"))
    if s is None:
        return
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
            screen = common.screen()
        common.alert(screen, _("Key Signing"), _("Signed %s") % k)
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
        text = common.EW(screen, fpr, _("Why are you revoking this key?"),
                [""])
        if text[0] == "cancel":
            return
        screen.finish()
        gk.revokekey(fpr, lcw[1], text[1][0])
        screen = common.screen()
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
        screen = common.screen()
        ew = common.EW(screen, fpr, _("When do you want this key to expire?"
            "(YYYY-MM-DD)"), [_("Expiration Date:")])
        if ew[0] == "cancel":
            return
        screen.finish()
        try:
            gk.expirekey(fpr, ew[1][0])
        except (ValueError, TypeError):
            common.error(common.screen(), _("Please enter a valid date in the"
                " future."))
            continue
        common.alert(common.screen(), fpr, _("Changed expiration date on %s")
                % fpr)
        invalid = False


def importkey(screen, workdir):
    gk = gpg_ops.GPGKey(workdir)
    importFail = True
    while importFail:
        ew = common.EW(screen, _("Import existing key"), _("Please mount an"
            " existing key backup, either an exported secret key or .gnupg and"
            " enter the path to it below"), ["Key Location"])
        if ew[0] == "cancel":
            return
        kl = None
        try:
            kl = gk.importbackup(ew[1][0])
        except ValueError as e:
            common.error(screen, str(e))
            continue
        importFail = False
        if kl is not None:
            lcw = common.LCW(screen, _("Master Key"),
                    _("Which key is your master key?"), kl)
            if lcw[0] == "cancel":
                return
            gk.setmaster(kl[lcw[1]])
    save(screen, workdir, gk)



def _status(keyword, args, hook=None):
    if keyword is None and args is None:
        return
    _log.info("Status {!s}({!s})".format(keyword, args))
