from shutil import copy
from os import makedirs
from . import newt
from . import ca
from . import disks_newt
from . import external
from . import time
from . import fmt

def new(screen, workdir):
    ew = newt.EW(screen, _("New CA"), _("Fill out the fields below to create"
        " a new Certificate Authority."), [
            _("Name of CA"),
            _("When the CA should expire (YYYY-MM-DD)"),
            _("Domain of CA"),
            _("Days Server certificates should be valid for")])
    if ew[0] == "cancel":
        return
    CA = ca.CA(workdir)
    CA.name = ew[1][0]
    delta = time.isostr2delta(ew[1][1])
    CA.CAValid = delta.days
    CA.domain = ew[1][2]
    CA.serverValid = ew[1][3]
    kt = list(ca.keyTypes.keys())
    ktlcw = newt.LCW(screen, _("CA Key Type"), _("Pick your key type"), kt)
    if ktlcw[0]:
        return
    CA.keyType = kt[ktlcw[1]]
    ks = list(ca.keyTypes[CA.keyType])
    kslcw = newt.LCW(screen, _("CA Key Size"), _("Pick your key size"), ks)
    if kslcw[0]:
        return
    CA.keySize = ks[kslcw[1]]
    digestlcw = newt.LCW(screen, _("Certificate Digest Type"), _("Pick your"
        " digest type"), ca.digests)
    if digestlcw[0]:
        return
    CA.digest = ca.digests[digestlcw[1]]

    CA.save()
    try:
        CA.genroot()
    except external.CalledProcessError as e:
        external.outputtostr(e)
        newt.error(screen, e.stderr)

    disks_newt.store(screen, workdir, "pki/"+CA.name,
            _("CA private key backup"), "PKICR Backup")
    disks_newt.export(screen, CA, _("certificate export"), "PKICR Export")
    newt.alert(screen, _("CA creation successful!"), _("You have now"
        " sucessfully created a Certificate Authority"))

def _loadCA(screen, workdir):
    d = disks_newt.mountdisk(screen, _("CA private key backup"))
    if d is None:
        return
    dirs = fmt.pki(d.mountpoint)
    if dirs is None:
        newt.error(screen, _("This disk does not contain a CA backup"))
        d.eject()
        load(screen, workdir)
    lcw = newt.LCW(screen, _("CA Backup"), _("Please select your CA"), dirs)
    if lcw[0]:
        return
    cafolder = d.mountpoint+"/pki/"+dirs[lcw[1]]
    return ca.CA(workdir, cafolder)

def signfile(screen, workdir):
    CA = _loadCA(screen, workdir)
    csr = newt.filepicker(screen, _("Open CSR"))
    sign = newt.dangerConfirm(screen, _("Sign Certificate"), _("Do you want to"
        " sign %s?" % csr))
    if sign:
        try:
            cert = CA.signserver(csr)
            newt.alert(screen, _("CSR"), _("Created certificate:\n%s") % cert)
        except external.CalledProcessError as e:
            newt.error(_("Certificate Signing Request Invalid. Please be sure"
                " it is in Base64 PEM format.\n"+e.stderr))
            return
        d = disks_newt.setup(screen, _("CSR"), "PKICR CSR")
        copy(cert, d.mountpoint)
        d.eject()

def load(screen, workdir):
    CA = _loadCA(screen, workdir)
    csrs = None
    while csrs is None:
        csrdisk = disks_newt.mountdisk(screen, _("CSR"))
        if csrdisk is None:
            return
        csrs = fmt.csr(csrdisk.mountpoint)
        if csrs is None:
            newt.alert(screen, _("CSR"), _("There are no CSRs on this disks."
                " Please be sure they are in the csr/ folder"))
    ccw = newt.CCW(screen, _("Certificate Signing Request"), _("Which CSRs"
        " would you like to issue certificates for?"), csrs)
    if ccw[0]:
        return
    export = csrdisk.mountpoint+"/certs"
    makedirs(export, exist_ok=True)
    for c in ccw[1]:
        path = csrdisk.mountpoint+"/csr/"+c
        cert = CA.signserver(path)
        copy(cert, export)
        newt.alert(screen, _("CSR"), _("Created certificate:\n%s") % cert)
    csrdisk.eject()
