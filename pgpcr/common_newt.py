from snack import *
from . import external, valid

width = 40
padding = (0, 0, 0, 1)


def screen():
    s = SnackScreen()
    s.helpCallback(helpCallback)
    s.pushHelpLine(_("   <Tab>/<Alt-Tab> between elements   |"
        "   <Space> check box   |   <Enter> next screen"))
    return s

def helpCallback(screen, text):
    alert(screen, _("Help"), text)

def new_password(screen):
    pass1 = Entry(20, password=1)
    pass2 = Entry(20, password=1)
    ew = EW(screen, _("Password"), _("Enter your password"),
                     [(_("Password")+":", pass1),
                      (_("Password")+_("(again)")+":", pass2)
                     ], buttons = [(_("Ok"), "ok"), (_("Cancel"), "cancel")])
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
    ew = EW(screen, hint, desc, [(label, p)], allowCancel=0)
    return p.value()

def uid(screen, purpose):
    while True:
        ew = EW(screen, purpose, _("Enter User Information"),
                [_("Name"), _("Email Address")])
        if ew[0] != "ok":
            return None
        else:
            if valid.email(ew[1][1]):
                return ew[1][0]+" <"+ew[1][1]+">"
            else:
                error(screen, _("You must supply a valid email address"))

def alert(screen, title, msg):
    ButtonChoiceWindow(screen, title, msg, [(_("Ok"), "ok")])


def error(screen, msg):
    alert(screen, _("Error"), msg)

def confirm(screen, title, msg):
    return ButtonChoiceWindow(screen, title, msg, [(_("Yes"), True),
                                                   (_("No"), False)])

def dangerConfirm(screen, title, msg):
    return ButtonChoiceWindow(screen, title, msg, [(_("No"), False),
                                                   (_("Yes"), True)])

def ContinueSkipAbort(screen, title, msg):
    return ButtonChoiceWindow(screen, title, msg, [(_("Continue"), True),
        (_("Skip"), False), (_("Abort"), None)])

def NotImplementedYet(screen):
    alert(screen, "Not Implemented Yet",
          "This feature has not yet been implemented")

def redraw(s, doIt):
    if doIt:
        s.finish()
        s = screen()
    return s

class Progress:
    def __init__(self, s, title, text, total, current=0):
        self.screen = screen() if s is None else s
        self._create(title, text, total, current)

    def _create(self, title, text, total, current):
        self.current = current
        self.g = GridFormHelp(self.screen, title, None, 1, 2)
        self.t = TextboxReflowed(width, text)
        self.p = Scale(width, total)
        self.p.set(current)
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


def catchCPE(screen, e):
    s = " ".join(e.cmd)
    if e.stderr is not None:
        if type(e.stderr) is bytes:
            external.outputtostr(e)
        alert(screen, s, e.stderr)
    else:
        error(screen, s)

# A ListboxChoiceWindow without the buttons
# Mostly borrowed from snack.py
def listmenu(screen, title, text, items, help=None):
    height = len(items)
    t = TextboxReflowed(width, text)
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

def CheckboxChoiceWindow(screen, title, text, items, buttons = None,
                      width = 40, scroll = 0, height = -1, help = None):

    if buttons is None:
        buttons = [(_("Ok"), "ok"), (_("Cancel"), "cancel")]
    if (height == -1): height = len(items)
    bb = ButtonBar(screen, buttons)
    t = TextboxReflowed(width, text)
    c = CheckboxTree(height, scroll)
    count = 0
    for item in items:
        if type(item) == tuple:
            c.append(*item)
        else:
            c.append(item)
        count += 1

    g = GridFormHelp(screen, title, help, 1, 3)
    g.add(t, 0, 0)
    g.add(c, 0, 1)
    g.add(bb, 0, 2,  growx = 1, padding = (0, 1, 0, 1))
    rc = g.runOnce()
    return (bb.buttonPressed(rc), c.getSelection())

def LCW(screen, title, text, items, buttons = None, width = 40, scroll = 0,
        height = -1, help = None):
    if buttons is None:
        buttons = [(_("Ok"), "ok"), (_("Cancel"), "cancel")]
    return ListboxChoiceWindow(screen, title, text, items, buttons, width,
            scroll, height, help)

def EW(screen, title, text, prompts, allowCancel = 1, width = 40,
        entryWidth = 20, buttons = None, help = None):
    if buttons is None:
        buttons = [(_("Ok"), "ok"), (_("Cancel"), "cancel")]
    if buttons is None and not allowCancel:
        buttons = [(_("Ok"), "ok")]
    return EntryWindow(screen, title, text, prompts, allowCancel, width,
            entryWidth, buttons, help)
