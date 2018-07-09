from snack import *
from time import sleep
from . import smartcard, common_newt as common, gpg_interact, gpg_ops

def pickcard(screen, homedir):
    s = None
    try:
        s = smartcard.Smartcard(homedir)
    except smartcard.NoSmartcardDetected:
        common.alert(screen, _("Smartcards"),
                     _("No smartcards detected."
                       " Please connect one and press Ok."))
        sleep(1)
        return pickcard(screen, homedir)
    card = common.confirm(screen, _("Smartcard"), _("Is this your smartcard?")+
            "\n"+str(s))
    if card:
        return s
    return pickcard(screen, homedir)


def export(screen, gk):
    smart = pickcard(screen, gk.homedir)
    if smart.new:
        ns = common.confirm(screen, _("New Smartcard"), _("This appears to be"
        " a new smartcard. Would you like to set it up?"))
        common.alert(screen, _("Default PINs"),
                _("The default PINs on your device are:")+"\n"+_("Admin PIN: ")
                +smart.defaultpins[1]+"\n"+_("PIN: ")+smart.defaultpins[0])
        if ns:
            setup(screen, smart)
            screen = common.redraw(screen, gk.redraw)
    keys = gk.keys
    ccw = common.CheckboxChoiceWindow(screen, gk.fpr,
                                      _("Which key(s) do you want to export?"),
                                      keys)
    if ccw[0] == "cancel":
        return
    for k in ccw[1]:
        lcw = common.LCW(screen, k, _("Which slot do you want to put"
            " this key in?"), smart.slots)
        if lcw[0] == "cancel":
            continue
        slot = lcw[1]+1
        fpr = k.split(" ")[0]
        try:
            gk.keytocard(fpr, slot)
        except smartcard.OverwriteError:
            overwrite = common.dangerConfirm(screen, _("Overwrite?"),
                _("There is already a key in slot %d. Do you want to overwrite"
                " it?") % slot)
            if overwrite:
                try:
                    gk.keytocard(fpr, slot, True)
                except smartcard.SmartcardError as e:
                    common.error(screen, str(e))
        except smartcard.SmartcardError as e:
            common.error(screen, str(e))
        screen = common.redraw(screen, gk.redraw)

def setup(screen, smart):
    setpins(screen, smart)
    screen = common.redraw(screen, smart.redraw)
    setproperties(screen, smart)

def setpins(screen, smart):
    common.alert(screen, _("Set PIN"), _("You will now be asked to set"
        " the user and Admin PINs on your smartcard."))
    smart.setPIN()
    smart.setAdminPIN()

def setproperties(screen, smart):
    while True:
        ew = common.EW(screen, _("New Smartcard"),
                _("Setup your new smartcard"), [_("Given Name of Cardholder"),
                    _("Surname of Cardholder"), _("Language Preference"),
                    _("Sex (m/f/u)"), _("Login Data")])
        if ew[0] == "cancel":
            return
        try:
            smart.name = ew[1][0]+" "+ew[1][1]
            smart.lang = ew[1][2]
            smart.sex = ew[1][3]
            smart.login = ew[1][4]
        except ValueError as v:
            common.error(screen, str(v))
            continue
        except smartcard.SmartcardError as e:
            common.error(screen, str(e))
            continue
        break
    #yk_properties(screen, smart)

def yk_properties(screen, smart):
    if smart.vendor != "Yubico":
        return
    ccw = common.CheckboxChoiceWindow(screen, _("Yubikey Touch"), _("For which"
        " operations would you like to require a touch of the smartcard"
        " button?"), [(_("Signing"), "sig"), (_("Decryption"), "dec"),
            (_("Authentication"), "aut")])
    if ccw[0] == "cancel":
        return
    for op in ccw[1]:
        smart.yk_touch(op, True)
    fix = common.dangerConfirm(screen, _("Fix"), _("Would you like to make"
        " these settings permanent?"))
    if fix:
        smart.yk_fixtouch()

def generate(screen, workdir):
    smart = pickcard(screen, workdir)
    slot = 1
    for s in smart.slots:
        screen = common.redraw(screen, smart.redraw)
        gen = common.dangerConfirm(screen, _("Generate Key"), _("Do you want"
            " to generate a key in \nslot %d: %s?") % (slot, s))
        if gen:
            try:
                smart.generate(slot)
            except smartcard.OverwriteError:
                overwrite = common.dangerConfirm(screen, _("Overwrite?"),
                    _("There is already a key in slot %d. Do you want to overwrite"
                    " it?") % slot)
                if overwrite:
                    try:
                        smart.generate(slot, True)
                    except smartcard.BadPIN:
                        common.error(screen, _("Incorrect PIN"))
                    except smartcard.SmartcardError as e:
                        common.error(screen, str(e))
        slot += 1
