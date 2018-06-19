from snack import *
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
    # TODO: Read over assuan commands used by GPA and figure out keytocard


def generate(screen, workdir):
    common.NotImplementedYet(screen)
