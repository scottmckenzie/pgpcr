from time import sleep
from shutil import copy
from os import mkdir
from . import disks
from . import newt
from . import external

def pickdisks(screen, use):
    while True:
        d = disks.getdisks()
        if d == []:
            newt.alert(screen, _("Disks"),
                    _("No removable storage connected."
                        " Please connect some and press OK."))
            sleep(1)
            continue
        dlist = [str(x) for x in d]
        lcw = newt.LCW(screen, _("Disks"), _("Pick your %s disk") % use,
                dlist, buttons=[(_("Refresh"), "refresh"),
                    (_("Cancel"), "cancel")])
        if lcw[0]:
            disk = d[lcw[1]]
            danger = newt.dangerConfirm(screen, _("Warning"), _("Are you"
                " sure you want to use this disk?"
                "\n%s (%s)") % (str(disk), disk.path))
            if danger:
                return disk
            else:
                continue
        elif lcw[0] == "refresh":
            continue
        else:
            return None


def store(screen, workdir, name, ignore=None):
    try:
        i = 1
        moredisks = True
        while moredisks:
            setupFail = True
            b = None
            while setupFail:
                b = setup(screen, _("master key backup")+" "+str(i),
                        "PGPCR Backup "+str(i))
                if b is None:
                    skip = newt.dangerConfirm(screen, _("Danger!"),
                            _("Are you sure you don't want to make any more"
                                " backups?"))
                    if skip:
                        setupFail = False
                else:
                    setupFail = False
            if b is None:
                return
            b.backup(workdir, name, ignore)
            newt.alert(screen, str(b),
                         _("Your backup to the above disk is now complete "
                         "and the disk can be ejected."))
            i += 1
            if i > 2:
                moredisks = newt.dangerConfirm(screen, _("Backups"),
                                                 _("Would you like to backup"
                                                   " to another disk?"))
    except disks.CopyError as e:
        s = " ".join(e)
        newt.error(s)
    except external.CalledProcessError as e:
        newt.catchCPE(screen, e)
        store(screen, workdir, name)


def export(screen, gk, secret=False):
    try:
        label = _("Public Key Export")
        if secret:
            label = _("Subkey and Public Key Export")
        publicFail = True
        while publicFail:
            public = setup(screen, label, "PGPCR Export")
            if public is None:
                exp = newt.dangerConfirm(screen, label,
                        _("Are you sure you don't want to export your key?"))
                if exp:
                    return
            else:
                publicFail = False
        copy("/etc/pgpcr/import.sh", public.mountpoint)
        try:
            mkdir(public.mountpoint+"/public")
            if secret:
                mkdir(public.mountpoint+"/private")
        except FileExistsError:
            pass
        gk.export(public.mountpoint+"/public")
        if secret:
            gk.exportsubkeys(public.mountpoint+"/private")
        public.eject()
    except disks.CopyError as e:
        s = " ".join(e)
        newt.error(s)
    except external.CalledProcessError as e:
        newt.catchCPE(screen, e)
        export(screen, gk)


def setup(screen, use, label):
    disk = pickdisks(screen, use)
    if disk is None:
        return
    if disk.label is not None and "PGPCR" in disk.label:
        try:
            disk.mount()
            return disk
        except external.CalledProcessError as e:
            newt.catchCPE(screen, e)

    danger = newt.dangerConfirm(screen, _("Warning"), _("Are you sure you"
                                  " want to use this disk?"
                                  "\n%s"
                                  "\nAll the data currently on the disk"
                                  " WILL BE WIPED!") % str(disk))
    if danger:
        try:
            disk.setup(label)
        except external.CalledProcessError as e:
            newt.catchCPE(screen, e)
            setup(screen, use, label)
    else:
        disk = setup(screen, use, label)
    return disk


def mountdisk(screen, use):
    d = pickdisks(screen, use)
    if d is None:
        return
    try:
        d.mount()
        return d
    except external.CalledProcessError as e:
        newt.catchCPE(screen, e)
    except disks.NotMountable:
        newt.error(screen, _("No mountable partitions found on this disk"))
    mountdisk(screen, use)
