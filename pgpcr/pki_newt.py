from . import newt
from . import ca
from . import disks_newt
from . import external
from . import time

def new(workdir):
    screen = newt.Screen()
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
