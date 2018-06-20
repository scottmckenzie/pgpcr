from snack import *
from time import sleep
from . import smartcard, common_newt as common


def pickcard(screen):
    s = smartcard.getsmartcard()
    if s is None:
        common.alert(_("Smartcards"),
                     _("No smartcards detected."
                       " Please connect one and press Ok."))
        sleep(1)
        return pickcard(screen)
    card = common.confirm(screen, _("Smartcard"), _("Is this your card?")+"\n"
            str(s))
    if card:
        return s
    return pickcard(screen)


def export(screen, gk):
    smart = pickcard(screen)
    keys = gk.keys
    ccw = common.CheckboxChoiceWindow(screen, gk.fpr,
                                      _("Which key(s) do you want to export?"),
                                      keys)
    if ccw[0] == "cancel":
        return
    for k in ccw[1]:
        lcw = ListboxChoiceWindow(screen, k, _("Which slot do you want to put"
            " this key in?"), smart.slots, buttons = [(_("Ok"), "ok"),
            (_("Cancel"), "cancel")])
        if lcw[0] == "cancel":
            continue
        slot = lcw[1]+1
        fpr = k.split(" ")[0]
        try:
            gk.keytocard(fpr, slot)
        except gpg_interact.OverwriteError:
            overwrite = common.dangerConfirm(screen, _("Overwrite?"),
                _("There is already a key in slot %d. Do you want to overwrite"
                "it?"))
            if overwrite:
                gk.keytocard(fpr, slot, True)

def generate(screen, workdir):
    common.NotImplementedYet(screen)
