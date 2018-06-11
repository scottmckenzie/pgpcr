from snack import *
from . import smartcard, common_newt as common


def pickcard(screen):
    s = smartcard.getsmartcards()
    if s == []:
        common.alert(_("Smartcards"),
                     _("No smartcards detected."
                       " Please connect one and press Ok."))
        sleep(1)
        return pickcard(screen)
    slist = [str(x) for x in s]
    lcw = ListboxChoiceWindow(screen, _("Smartcards"), _("Pick your smartcard"),
                              slist, buttons=[(_("Refresh"), "refresh")])
    if lcw[0] is None or lcw[0] == "ok":
        return s[lcw[1]]
    elif lcw[0] == "refresh":
        return pickcard(screen)
    else:
        return None


def export(screen, gk):
    smart = pickcard(screen)
    # TODO: Read over assuan commands used by GPA and figure out keytocard


def generate(screen, workdir):
    common.NotImplementedYet(screen)
