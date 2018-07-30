from time import sleep
from . import smartcard
from . import newt

def pickcard(screen, homedir):
    s = None
    try:
        s = smartcard.Smartcard(homedir)
    except smartcard.NoSmartcardDetected:
        newt.alert(screen, _("Smartcards"),
                     _("No smartcards detected."
                       " Please connect one and press Ok."))
        sleep(1)
        return pickcard(screen, homedir)
    card = newt.confirm(screen, _("Smartcard"), _("Is this your smartcard?")+
            "\n"+str(s))
    if card:
        return s
    return pickcard(screen, homedir)

def _keytocard(screen, gk, fpr, slot):
    success = True
    try:
        gk.keytocard(fpr, slot)
    except smartcard.OverwriteError:
        overwrite = newt.dangerConfirm(screen, _("Overwrite?"),
            _("There is already a key in slot %d. Do you want to overwrite"
            " it?") % slot)
        if overwrite:
            try:
                gk.keytocard(fpr, slot, True)
            except smartcard.SmartcardError as e:
                success = False
                newt.error(screen, str(e))
        else:
            success = False
    except smartcard.SmartcardError as e:
        success = False
        newt.error(screen, str(e))
    if success:
        newt.alert(screen, _("Smartcard Export"), _("Exported %s to slot"
        " %d") % (fpr, slot))

def export(screen, gk):
    smart = pickcard(screen, gk.homedir)
    if smart.new:
        ns = newt.confirm(screen, _("New Smartcard"), _("This appears to be"
        " a new smartcard. Would you like to set it up?"))
        newt.alert(screen, _("Default PINs"),
                _("The default PINs on your device are:")+"\n"+_("Admin PIN: ")
                +smart.defaultpins[1]+"\n"+_("PIN: ")+smart.defaultpins[0])
        if ns:
            setup(screen, smart)
            screen = newt.redraw(screen, gk.redraw)
    if gk.expert:
        keys = gk.keys
        ccw = newt.CCW(screen, gk.fpr, _("Which key(s) do you want to export?"),
                                          keys)
        if ccw[0]:
            return
        for k in ccw[1]:
            lcw = newt.LCW(screen, k, _("Which slot do you want to put"
                " this key in?"), smart.slots)
            if lcw[0]:
                continue
            slot = lcw[1]+1
            fpr = k.split(" ")[0]
            _keytocard(screen, gk, fpr, slot)
            screen = newt.redraw(screen, gk.redraw)
    else:
        newt.alert(screen, _("Export to Smartcard"), _("Your subkeys will"
        " now be exported to your smartcard"))
        for k in gk.subkeys:
            if k.fpr == gk.fpr:
                continue
            if k.can_sign:
                slot = 1
            elif k.can_encrypt:
                slot = 2
            elif k.can_authenticate:
                slot = 3
            else:
                continue
            _keytocard(screen, gk, k.fpr, slot)
    if smart.new:
        setpins(screen, smart)

def setup(screen, smart):
    screen = newt.redraw(screen, smart.redraw)
    setproperties(screen, smart)

def setpins(screen, smart):
    newt.alert(screen, _("Set PIN"), _("You will now be asked to set"
        " the Admin and user PINs on your smartcard."))
    smart.setAdminPIN()
    smart.setPIN()

def setproperties(screen, smart):
    while True:
        ew = newt.EW(screen, _("New Smartcard"),
                _("Setup your new smartcard"), [_("Given Name of Cardholder"),
                    _("Surname of Cardholder"), _("Language Preference"),
                    _("Sex (m/f/u)"), _("Login Data")])
        if ew[0]:
            return
        try:
            smart.name = ew[1][0]+" "+ew[1][1]
            smart.lang = ew[1][2]
            smart.sex = ew[1][3]
            smart.login = ew[1][4]
        except ValueError as v:
            newt.error(screen, str(v))
            continue
        except smartcard.SmartcardError as e:
            newt.error(screen, str(e))
            continue
        break

def generate(screen, workdir):
    smart = pickcard(screen, workdir)
    slot = 1
    for s in smart.slots:
        screen = newt.redraw(screen, smart.redraw)
        gen = newt.dangerConfirm(screen, _("Generate Key"), _("Do you want"
            " to generate a key in \nslot %d: %s?") % (slot, s))
        if gen:
            try:
                smart.generate(slot)
            except smartcard.OverwriteError:
                overwrite = newt.dangerConfirm(screen, _("Overwrite?"),
                    _("There is already a key in slot %d. Do you want to overwrite"
                    " it?") % slot)
                if overwrite:
                    try:
                        smart.generate(slot, True)
                    except smartcard.BadPIN:
                        newt.error(screen, _("Incorrect PIN"))
                    except smartcard.SmartcardError as e:
                        newt.error(screen, str(e))
        slot += 1
