from . import gpg_ops
from . import newt
from . import disks_newt
from . import smartcard_newt
from . import fmt
from . import printing
from . import log

_log = log.getlog(__name__)

def new(screen, workdir, expert):
    gk = gpg_ops.GPGKey(workdir)
    if expert:
        gk.expert = True
    uid = newt.uid(screen, _("New GPG Master Key Pair"))
    if uid is None:
        return
    if expert:
        k = keyalgos(screen, gk)
        if not k:
            return
    newt.alert(screen, _("Master Key Pair Generation"),
                 _("A new GPG master key pair (a private key and a public key)"
                 " will now be generated. Progress is estimated and key pair"
                 " generation may take a considerable amount of time depending"
                 " on the amount of entropy available. You will be prompted"
                 " for a passphrase with which to protect your key pair."))
    mprog = newt.Progress(screen, _("Key Generation"),
                            _("Generating Master Key Pair..."), 40)
    mprog.gk = gk
    gk.setprogress(_progress, mprog)
    while True:
        try:
            gk.genmaster(uid)
        except gpg_ops.GPGMEError as g:
            cont = newt.catchGPGMEErr(_("Master key pair generation"), g)
            if cont:
                continue
            return
        break
    screen = newt.redraw(screen, gk.redraw)
    newt.alert(screen, _("Subkey generation"), _("A set of subkeys will now"
        " be generated. These are the keys you will actually use, while the"
        " private part of your key pair is stored safely offline and away from"
        " your main computer."))
    newt.alert(screen, _("Passphrase prompt"), _("You will be prompted"
        " for your passphrase twice when you generate your first subkey."))
    sprog = newt.Progress(screen, _("Key Generation"),
                            _("Generating Sub Keys..."), 60)
    sprog.gk = gk
    gk.setprogress(_progress, sprog)
    while True:
        try:
            gk.genseasubs(sprog.setText, newt.ContinueSkipAbort,
                    newt.redraw, screen)
        except gpg_ops.GPGMEError as g:
            cancel = newt.catchGPGMEErr(_("Subkey generation"), g)
            if not cancel:
                continue
            return
        break
    screen = newt.Screen()
    newt.alert(screen, _("Key Generation Complete"),
            _("Sucessfully generated master key pair and subkeys."))
    save(screen, workdir, gk)

def keyalgos(screen, gk):
    masteralgolist = list(gpg_ops.master_algos.keys())
    mlcw = newt.LCW(screen, _("Master Key Pair Algorithm"),_("Pick the"
        " algorithm you would like to use for your new master key pair. If"
        " you're unsure, the defaults are well chosen and should work for"
        " most people"), masteralgolist)
    if mlcw[0]:
        return False
    masteralgo = masteralgolist[mlcw[1]]
    mastersizes = gpg_ops.master_algos[masteralgo]
    if mastersizes is not None:
        mks = newt.LCW(screen, _("Master Key Pair Size"), _("Pick the size of"
            " your new master key pair. If you're unsure the defaults are well"
            " chosen and should work for most people"), mastersizes)
        if mks[0]:
            return False
        masteralgo += mastersizes[mks[1]]
    subalgolist = list(gpg_ops.sub_algos.keys())
    slcw = newt.LCW(screen, _("Subkey Algorithm"),_("Pick the"
        " algorithm you would like to use for your new subkeys. If you're"
        " unsure, the defaults are well chosen and should work for"
        " most people"), subalgolist)
    if slcw[0]:
        return False
    subalgo = subalgolist[slcw[1]]
    subsizes = gpg_ops.sub_algos[subalgo]
    if subsizes is not None:
        sks = newt.LCW(screen, _("Subkey Size"), _("Pick the size of"
            " your new subkeys. If you're unsure the defaults are well"
            " chosen and should work for most people"), subsizes)
        if sks[0]:
            return False
        subalgo += subsizes[sks[1]]

    gk.setalgorithms(masteralgo, subalgo)
    return True

def save(screen, workdir, gk):
    disks_newt.store(screen, workdir, "gpg/"+gk.fpr, _("master key backup"),
            "PGPCR Backup", gpg_ops.ignore)
    screen = newt.redraw(screen, True)
    export = newt.BCW(screen, _("Key Export"),
                                _("How would you like to export your"
                                " subkeys?"),
                                [(_("External Storage"), "storage"),
                                (_("Smartcard"), "smartcard")])
    secret = False
    if export == "storage":
        secret = _("subkey and public key export")
    elif export == "smartcard":
        smartcard_newt.export(screen, gk)
    disks_newt.export(screen, gk, _("public key export"), "PGPCR Export",
            secret)
    screen = newt.redraw(screen, True)
    newt.alert(screen, _("New Key Pair Creation Complete"),
                 _("You can now store your backups in a safe place"))
    newt.alert(screen, _("IMPORTANT"),
        _("Don't forget to import your new public key to your main"
            " computer by running import.sh from your public key export"
            " disk."))

def _progress(what, type, current, total, prog):
    if what == "primegen":
        prog.inc()
    else:
        _log.info(what, type, current, total)
    if prog.gk.redraw:
        prog.screen.finish()
        prog.screen = newt.Screen()
        prog.recreate()


def load(screen, workdir, expert):
    d = disks_newt.mountdisk(screen, _("master key pair backup"))
    if d is None:
        return
    dirs = fmt.backups(d.mountpoint)
    if dirs is None:
        newt.error(screen, _("This disk does not contain a master key pair"
                               " backup. Please be sure it is in the gpg/"
                               " folder."))
        d.eject()
        load(screen, workdir, expert)
    lcw = newt.LCW(screen, _("Key Fingerprint"),
                              _("Please select your master key fingerprint."),
                              dirs)
    if lcw[0]:
        return
    key = dirs[lcw[1]]
    gk = gpg_ops.GPGKey(workdir, key, d.mountpoint+"/gpg/"+key)
    if expert:
        gk.expert = True
    d.eject()
    running = True
    while running:
        screen.finish()
        screen = newt.Screen()
        title = key
        if expert:
            title += " "+_("EXPERT MODE")
        lm = newt.LCM(screen, title, gk.info,
                                 [(_("Sign GPG Public Keys"), "sign"),
                                  (_("Associate a UID with your master key"
                                  " pair"),
                                     "adduid"),
                                  (_("Revoke a UID associated with your master"
                                  " key pair"), "revuid"),
                                  (_("Revoke your master key pair or one of"
                                  " its subkeys"), "revkeys"),
                                  (_("Change the expiration date on your"
                                      " master key pair or a subkey"),
                                      "expirekeys"),
                                  (_("Add a new subkey to your master key"
                                      " pair"), "newsub"),
                                  (_("Refresh Key"), "refresh"),
                                  (_("Quit"), "quit")
                                 ])
        try:
            if lm == "sign":
                sign(screen, gk, d.mountpoint, expert)
            elif lm == "adduid":
                adduid(screen, gk)
            elif lm == "revuid":
                revuid(screen, gk)
            elif lm == "revkeys":
                revokekey(screen, gk)
            elif lm == "expirekeys":
                expirekey(screen, gk)
            elif lm == "newsub":
                newsub(screen, gk)
            elif lm == "refresh":
                gk.refreshmaster()
                continue
            elif lm == "quit":
                running = False
        except gpg_ops.PinentryCancelled:
            continue
    if gk.changed:
        confirm = newt.confirm(screen, _("Save"), _("Do you want to save the"
            " changes you've made?"))
        if confirm:
            save(screen, workdir, gk)


def sign(screen, gk, path, expert):
    s = disks_newt.mountdisk(screen, _("public keys to sign"))
    if s is None:
        return
    keys = fmt.signpending(s.mountpoint)
    if keys is None:
        newt.alert(screen, _("Key Signing"),
                     _("There are no public keys to sign on this disk."
                     " Please be sure they are in the"
                     " signing/pending folder."))
        sign(screen, gk, path, expert)
        return
    rw = newt.CCW(screen, _("Key Signing"), _("Which public key(s)"
                                     " do you want to sign?"), keys)
    if rw[0]:
        return
    if gk.expert:
        exp = newt.EW(screen, _("Signature Expiry"), _("Optionally you can"
        " set an expiration date on your signature"), ["YYYY/MM/DD"])
        if exp[1][0] == "":
            expires = False
        else:
            expires = exp[1][0]
    else:
        expires = False
    for k in rw[1]:
        if gk.expert:
            gk.signkey(s.mountpoint, k, expires, newt.CCW, screen)
        else:
            gk.signkey(s.mountpoint, k, expires)
        screen = newt.redraw(screen, gk.redraw)
        newt.alert(screen, _("Key Signing"), _("Signed %s") % k)
    s.eject()

def revokekey(screen, gk):
    keys = gk.keys
    ccw = newt.CCW(screen, gk.fpr, _("Which key(s) do you want to revoke?"),
                                      keys)
    for k in ccw[1]:
        fpr = k.split(" ")[0]
        lcw = newt.LCW(screen, fpr, _("Why do you want to revoke %s") % k,
                gpg_ops.revoke_reasons())
        if lcw[0]:
            return
        text = newt.EW(screen, fpr, _("Why are you revoking this key?"),
                [""])
        if text[0]:
            return
        screen.finish()
        gk.revokekey(fpr, lcw[1], text[1][0])
        screen = newt.Screen()
        newt.alert(screen, k, _("Revoked %s") % k)

def adduid(screen, gk):
    uid = newt.uid(screen, _("Add UID")+" "+gk.fpr)
    if uid is None:
        return
    gk.adduid(uid)
    newt.alert(screen, gk.fpr, _("Added %s to your master key pair") % uid)

def revuid(screen, gk):
    uids = gk.uids
    lcw = newt.LCW(screen, gk.fpr, _("Which UID would you like to"
                              " revoke?"), uids)
    if lcw[0]:
        return
    gk.revokeuid(uids[lcw[1]])
    newt.alert(screen, gk.fpr, _("Removed %s from your master key"
        " pair") % uids[lcw[1]])

def expirekey(screen, gk):
    lcw = newt.LCW(screen, _("Key expiration"), _("Which key do you"
        " want to expire?"), gk.keys)
    if lcw[0]:
        return
    fpr = gk.keys[lcw[1]].split(" ")[0]
    invalid = True
    while invalid:
        screen = newt.Screen()
        ew = newt.EW(screen, fpr, _("When do you want this key to expire?"
            "(YYYY-MM-DD)"), [_("Expiration Date:")])
        if ew[0]:
            return
        screen.finish()
        try:
            gk.expirekey(fpr, ew[1][0])
        except (ValueError, TypeError):
            newt.error(newt.Screen(), _("Please enter a valid date in the"
                " future."))
            continue
        newt.alert(newt.Screen(), fpr, _("Changed expiration date on %s")
                % fpr)
        invalid = False


def setmasterkey(screen, gk, kl):
        if kl is not None:
            lcw = newt.LCW(screen, _("Public Key"),
                    _("Which key is your public key?"), kl)
            if lcw[0]:
                return
            gk.setmaster(kl[lcw[1]])

def importkey(screen, workdir, keyloc=None):
    gk = gpg_ops.GPGKey(workdir)
    importFail = True
    while importFail:
        newt.alert(screen, _("Import existing key"), _("Please select an"
            " existing key backup, either an exported secret key or"
            " .gnupg"))
        fp = newt.filepicker(screen, _("Import existing key"))
        if fp is None:
            return
        keyloc = fp
        try:
            kl = gk.importbackup(keyloc)
        except ValueError as e:
            newt.error(screen, str(e))
            continue
        importFail = False
    setmasterkey(screen, gk, kl)
    save(screen, workdir, gk)

def newsub(screen, gk):
    cap = newt.CCW(screen, _("Generate a new subkey"), _("Please select the"
    " capabilities of your new subkey"), [(_("Signing"), "sig"),
        (_("Encryption"), "enc"), (_("Authentication"), "auth")])
    if cap[0]:
        return
    sig = False
    enc = False
    auth = False
    for c in cap[1]:
        if c == "sig":
            sig = True
        elif c == "enc":
            enc = True
        elif c == "auth":
            auth = True
    confirm = newt.dangerConfirm(screen, _("Generate a new subkey"),
            _("Are you sure you want to generate a new subkey for"
            " %s?") % gk.fpr)
    if confirm:
        gk.gensub(sign=sig, encrypt=enc, authenticate=auth)

def printkey(screen, gk):
    if not printing.isInstalled():
        newt.error(screen, _("CUPS is not installed"))
        return
    p = newt.confirm(screen, _("Are you sure you want to print the private"
        " key and revocation certificate for this key?\n%s") % str(gk))
    if p:
        printing.printrevcert(gk)
        printing.printmasterkey(gk)
