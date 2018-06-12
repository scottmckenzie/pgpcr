from snack import *
from . import disks, common_newt as common, external
from time import sleep
from shutil import copy


def pickdisks(screen, use):
    d = disks.getdisks()
    if d == []:
        common.alert(screen, _("Disks"),
                          _("No removable storage connected."
                          " Please connect some and press OK."))
        sleep(1)
        return pickdisks(screen, use)
    dlist = [str(x) for x in d]
    lcw = ListboxChoiceWindow(screen, _("Disks"), _("Pick your %s disk") % use,
                              dlist, buttons=[(_("Refresh"), "refresh")])
    if lcw[0] is None or lcw[0] == "ok":
        return d[lcw[1]]
    elif lcw[0] == "refresh":
        return pickdisks(screen, use)
    else:
        return None


def store(screen, workdir, name):
    try:
        i = 1
        moredisks = True
        while moredisks:
            b = setup(screen, _("master key backup"), "PGPCR Backup "+str(i))
            b.backup(workdir, name)
            common.alert(screen, str(b),
                         _("Your backup to the above disk is now complete "
                         "and the disk can be ejected."))
            i += 1
            if i > 2:
                moredisks = common.dangerConfirm(screen, _("Backups"),
                                                 _("Would you like to backup"
                                                   "  to another disk?"))
    except disks.CopyError as e:
        s = " ".join(e)
        common.error(s)
    except external.CalledProcessError as e:
        common.catchCPE(screen, e)
        store(screen, workdir, name)


def export(screen, gk):
    try:
        public = setup(screen, _("public key export"), "PGPCR Export")
        copy("/etc/pgpcr/import.sh", public.mountpoint)
        gk.export(public.mountpoint)
        gk.exportsubkeys(public.mountpoint)
        public.eject()
    except disks.CopyError as e:
        s = " ".join(e)
        common.error(s)
    except external.CalledProcessError as e:
        common.catchCPE(screen, e)
        export(screen, gk)


def setup(screen, use, label):
    disk = pickdisks(screen, use)
    if disk.label is not None and "PGPCR" in disk.label:
        try:
            disk.mount()
            return disk
        except external.CalledProcessError as e:
            common.catchCPE(screen, e)

    danger = common.dangerConfirm(screen, _("Warning"), _("Are you sure you"
                                  " want to use %s? All the data currently on"
                                  " the device WILL BE WIPED!" % str(disk)))
    if danger:
        try:
            disk.setup(label)
        except external.CalledProcessError as e:
            common.catchCPE(screen, e)
            setup(screen, use, label)
    else:
        disk = setup(screen, use, label)
    return disk


def load(screen):
    d = pickdisks(screen, _("master key backup"))
    try:
        d.mount()
        return d
    except external.CalledProcessError as e:
        common.catchCPE(screen, e)
        load(screen)
