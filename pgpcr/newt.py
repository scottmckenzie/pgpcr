from shutil import get_terminal_size
from os import scandir
import os.path
from time import sleep
from snack import *
from . import external
from . import valid


def getwidth():
    c, l = get_terminal_size((80, 40))
    return c // 2

def Screen():
    s = SnackScreen()
    s.helpCallback(helpCallback)
    s.pushHelpLine(_("   <Tab>/<Alt-Tab> between elements   |"
        "   <Space> checks box   |   <Enter> selects"))
    return s

def helpCallback(screen, text):
    alert(screen, _("Help"), text)

def BCW(screen, title, text, buttons = None, width = None, x = None, y = None,
        help = None):
    if buttons is None:
        buttons = [(_("Ok"), None), (_("Cancel"), True)]
    if width is None:
        width = getwidth()
    return ButtonChoiceWindow(screen, title, text, buttons, width, x, y, help)

def EW(screen, title, text, prompts, allowCancel = 1, width = None,
        entryWidth = None, buttons = None, help = None):
    if buttons is None:
        buttons = [(_("Ok"), None), (_("Cancel"), True)]
    if buttons is None and not allowCancel:
        buttons = [(_("Ok"), None)]
    if width is None:
        width = getwidth()
    if entryWidth is None:
        entryWidth = width // 2
    return EntryWindow(screen, title, text, prompts, allowCancel, width,
            entryWidth, buttons, help)

def LCW(screen, title, text, items, buttons = None, width = None, scroll = 0,
        height = -1, help = None):
    if buttons is None:
        buttons = [(_("Ok"), None), (_("Cancel"), True)]
    if width is None:
        width = getwidth()
    return ListboxChoiceWindow(screen, title, text, items, buttons, width,
            scroll, height, help)

# A ListboxChoiceWindow without the buttons
# Mostly borrowed from snack.py
def LCM(screen, title, text, items, help=None):
    height = len(items)
    t = TextboxReflowed(getwidth(), text)
    l = Listbox(height, returnExit = 1)
    count = 0
    for item in items:
        if type(item) == tuple:
            (text, key) = item
        else:
            text = item
            key = count
        l.append(text, key)
        count = count + 1
    g = GridFormHelp(screen, title, help, 1, 2)
    g.add(t, 0, 0)
    g.add(l, 0, 1, padding = (0, 1, 0, 1))
    g.runOnce()
    return l.current()

def CCW(screen, title, text, items, buttons = None, width = None, scroll = 0,
        height = -1, help = None):

    if buttons is None:
        buttons = [(_("Ok"), None), (_("Cancel"), True)]
    if width is None:
        width = getwidth()
    if (height == -1):
        height = len(items)+1
    bb = ButtonBar(screen, buttons)
    t = TextboxReflowed(width, text)
    c = CheckboxTree(height, scroll)
    count = 0
    c.append(_("All"), "all")
    allitems = []
    for item in items:
        if type(item) == tuple:
            c.append(*item)
            allitems.append(item[1])
        else:
            c.append(item)
            allitems.append(item)
        count += 1

    g = GridFormHelp(screen, title, help, 1, 3)
    g.add(t, 0, 0)
    g.add(c, 0, 1)
    g.add(bb, 0, 2,  growx = 1, padding = (0, 1, 0, 1))
    rc = g.runOnce()
    selected = c.getSelection()
    if selected and selected[0] == "all":
        selected = allitems
    return (bb.buttonPressed(rc), selected)

def new_password(screen):
    pass1 = Entry(20, password=1)
    pass2 = Entry(20, password=1)
    EW(screen, _("Password"), _("Enter your password"),
                     [(_("Password")+":", pass1),
                      (_("Password")+_("(again)")+":", pass2)
                     ], buttons = [(_("Ok"), None), (_("Cancel"), True)])
    if pass1.value() != pass2.value():
        error(_("Passwords do not match!"))
        return password()
    elif pass1.value() == "":
        error(_("Password cannot be empty!"))
        return password()
    return pass1.value()


def password(hint, desc, prev_bad, screen):
    if hint is None:
        hint = _("Password")
    if desc is None:
        desc = _("Enter your password")
    p = Entry(20, password=1)
    label = _("Password")
    if prev_bad:
        label += " "+_("(again)")
    label += ":"
    EW(screen, hint, desc, [(label, p)], allowCancel=0)
    return p.value()

def uid(screen, purpose):
    while True:
        ew = EW(screen, purpose, _("Enter User Information"),
                [_("Name"), _("Email Address"), _("Comment (Optional)")])
        if ew[0]:
            return None
        else:
            name = ew[1][0]
            email = ew[1][1]
            comment = ew[1][2]
            if name != "":
                ret = name
            else:
                error(screen, _("You must supply a name"))
                continue
            if comment != "":
                ret += " ("+ew[1][2]+")"
            if valid.email(email):
                ret += " <"+ew[1][1]+">"
            else:
                error(screen, _("You must supply a valid email address"))
                continue
            return ret

def alert(screen, title, msg):
    BCW(screen, title, msg, [(_("Ok"), None)])


def error(screen, msg):
    alert(screen, _("Error"), msg)

def confirm(screen, title, msg):
    return BCW(screen, title, msg, [(_("Yes"), True), (_("No"), False)])

def dangerConfirm(screen, title, msg):
    return BCW(screen, title, msg, [(_("No"), False), (_("Yes"), True)])

def ContinueSkipAbort(screen, title, msg):
    return BCW(screen, title, msg, [(_("Continue"), True), (_("Skip"), False),
        (_("Abort"), None)])

def NotImplementedYet(screen):
    alert(screen, "Not Implemented Yet",
          "This feature has not yet been implemented")

def redraw(screen, doIt):
    if doIt:
        screen.finish()
        screen = Screen()
    return screen

class Progress:
    def __init__(self, s, title, text, total, current=0):
        self.screen = Screen() if s is None else s
        self._create(title, text, total, current)

    def _create(self, title, text, total, current):
        self.current = current
        self.g = GridFormHelp(self.screen, title, None, 1, 2)
        width = getwidth()
        self.t = TextboxReflowed(width, text)
        self.p = Scale(width, total)
        self.p.set(current)
        padding = (0, 0, 0, 1)
        self.g.add(self.t, 0, 0, padding=padding)
        self.g.add(self.p, 0, 1, padding=padding)
        self.refresh()
        self._title = title
        self._text = text
        self._total = total

    def recreate(self):
        self._create(self._title, self._text, self._total, self.current)

    def set(self, prog):
        self.current = prog
        self.refresh()

    def refresh(self):
        self.p.set(self.current)
        self.g.draw()
        self.screen.refresh()

    def inc(self, prog=1):
        self.current += prog
        self.refresh()

    def setText(self, text):
        self._text = text
        self.t.setText(text)
        self.refresh()


def filepicker(screen, title, path="."):
    path = os.path.abspath(path)
    while True:
        sd = list(scandir(path))
        items = [".."]
        items.extend([x.name for x in sd])
        lcw = LCW(screen, title, path, items,
                buttons = [
                    (_("Open Directory"), None),
                    (_("Select"), "select"),
                    (_("Refresh"), "refresh"), (_("Cancel"), "cancel")
                    ])
        if lcw[1] == 0:
            path = os.path.dirname(path)
            continue
        index = lcw[1] - 1
        current = sd[index]
        if lcw[0]  == "cancel":
            return None
        elif lcw[0] == "select":
            return current.path
        elif lcw[0] is None:
            if current.is_dir():
                path = current.path
            else:
                error(screen, _("Not a directory"))
        elif lcw[0] == "refresh":
            sleep(1)

def catchCPE(screen, e):
    s = " ".join(e.cmd)
    if e.stderr is not None:
        if type(e.stderr) is bytes:
            external.outputtostr(e)
        alert(screen, s, e.stderr)
    else:
        error(screen, s)

def catchGPGMEErr(what, g):
    screen = Screen()
    if g.code_str == "Operation cancelled":
        cancel = dangerConfirm(screen, what, _("Are you sure you want to"
        " cancel")+" "+what+"?")
        if cancel:
            return False
        return True
    else:
        error(screen, what+_("error")+": "+str(g))
        return False
