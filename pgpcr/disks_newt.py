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
                dlist, buttons=[(_("Refresh"), False),
                    (_("Unmount"), "umount"),
                    (_("Cancel"), True)])
        if lcw[0] is None:
            disk = d[lcw[1]]
            danger = newt.dangerConfirm(screen, _("Warning"), _("Are you"
                " sure you want to use this disk?"
                "\n%s (%s)") % (str(disk), disk.path))
            if danger:
                return disk
            else:
                continue
        elif lcw[0] == "umount":
            d[lcw[1]].eject()
        elif lcw[0]:
            return None
        else:
            sleep(1)
            continue

def store(screen, workdir, folder, kind, label, ignore=None):
    try:
        i = 1
        moredisks = True
        while moredisks:
            setupFail = True
            b = None
            while setupFail:
                b = setup(screen, kind+" "+str(i),
                        label+" "+str(i))
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
            b.backup(workdir, folder, ignore)
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
        store(screen, workdir, folder, kind, label, ignore)


def export(screen, obj, kind, label, secret=False):
    try:
        if secret:
            kind = secret
        publicFail = True
        while publicFail:
            public = setup(screen, kind, label)
            if public is None:
                exp = newt.dangerConfirm(screen, kind,
                        _("Are you sure you don't want to export your key?"))
                if exp:
                    return
            else:
                publicFail = False
        if "PGPCR" in label:
            copy("/etc/pgpcr/import.sh", public.mountpoint)
        try:
            mkdir(public.mountpoint+"/public")
        except FileExistsError:
            pass
        try:
            if secret:
                mkdir(public.mountpoint+"/private")
        except FileExistsError:
            pass
        obj.export(public.mountpoint+"/public")
        if secret:
            obj.exportsubkeys(public.mountpoint+"/private")
        public.eject()
    except disks.CopyError as e:
        s = " ".join(e)
        newt.error(s)
    except external.CalledProcessError as e:
        newt.catchCPE(screen, e)
        export(screen, obj, secret)


def setup(screen, use, label):
    disk = pickdisks(screen, use)
    if disk is None:
        return
    if disk.label is not None and ("PGPCR" in disk.label
            or "PKICR" in disk.label):
        reformat = newt.dangerConfirm(screen, _("Reformat"), _("Do you want"
            " to reformat this disk?\n%s") % str(disk))
        if not reformat:
            try:
                disk.mount()
                return disk
            except external.CalledProcessError as e:
                newt.catchCPE(screen, e)

    danger = newt.dangerConfirm(screen, _("Warning"), _("Are you sure you"
                                  " want to reformat this disk?"
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
