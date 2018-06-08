from snack import *
from . import disks, common_newt as common, external
from time import sleep
from shutil import copy


def pickdisks(screen, use):
    d = disks.getdisks()
    if d == []:
        common.alert(screen, "Disks",
                          "No removable storage connected. "
                          "Please connect some and press OK.")
        sleep(1)
        return pickdisks(screen, use)
    dlist = [str(x) for x in d]
    lcw = ListboxChoiceWindow(screen, "Disks", "Pick your "+use+" disk", dlist,
                              buttons=[("Refresh", "refresh")])
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
            b = setup(screen, "master key backup", "master backup "+str(i))
            b.backup(workdir, name)
            common.alert(screen, str(b),
                         "Your backup to the above disk is now complete "
                         "and the disk can be ejected.")
            i += 1
            if i > 2:
                moredisks = common.dangerConfirm(screen, "Backups",
                                                 "Would you like to backup to "
                                                 "another disk?")
    except disks.CopyError as e:
        s = " ".join(e)
        common.error(s)
    except external.CalledProcessError as e:
        common.catchCPE(screen, e)
        store(screen, workdir, name)


def export(screen, gk):
    try:
        public = setup(screen, "public key export", "public export")
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
    danger = common.dangerConfirm(screen, "Warning",
                                  "Are you sure you want to use "+str(disk)+"?"
                                  " All the data currently on the device"
                                  " WILL BE WIPED!")
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
    d = pickdisks(screen, "master backup")
    try:
        d.mount()
        return d
    except external.CalledProcessError as e:
        common.catchCPE(screen, e)
        load(screen)
